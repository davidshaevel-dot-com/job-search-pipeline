"""
Configuration loader for job search pipeline.

Handles loading YAML configuration files and environment variable substitution.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class Config:
    """Configuration container."""
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize config with data dictionary."""
        self._data = data
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)."""
        keys = key.split(".")
        value = self._data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def __getitem__(self, key: str) -> Any:
        """Get configuration value using bracket notation."""
        return self._data[key]
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists in config."""
        return key in self._data
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self._data.copy()


def _substitute_env_vars(value: Any) -> Any:
    """
    Recursively substitute environment variables in configuration values.
    
    Supports ${VAR_NAME} syntax. Raises ValueError if a required environment
    variable is not set, ensuring fail-fast behavior for configuration errors.
    
    Note: Future enhancement could support default values using ${VAR_NAME:default}
    syntax (similar to Docker Compose) for optional/non-sensitive configuration
    values. This would allow fallback values directly in YAML files.
    
    Raises:
        ValueError: If an environment variable referenced in config is not set
    """
    if isinstance(value, str):
        # Match ${VAR_NAME} pattern
        pattern = r'\$\{([^}]+)\}'
        
        def replace(match):
            var_name = match.group(1)
            env_value = os.getenv(var_name)
            if env_value is not None:
                return env_value
            # Fail fast if an environment variable is not set
            raise ValueError(
                f"Environment variable '{var_name}' is not set but is required "
                f"in the configuration."
            )
        
        return re.sub(pattern, replace, value)
    elif isinstance(value, dict):
        return {k: _substitute_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_substitute_env_vars(item) for item in value]
    else:
        return value


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """
    Load YAML file and return as dictionary.
    
    Args:
        file_path: Path to YAML file
        
    Returns:
        Dictionary containing YAML data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If file is invalid YAML
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    if data is None:
        return {}
    
    return data


def load_config(
    config_dir: Optional[Path] = None,
    search_criteria_file: str = "search-criteria.yaml",
    job_boards_file: str = "job-boards.yaml",
    slack_file: str = "slack.yaml",
    filters_file: str = "filters.yaml",
    evaluation_thresholds_file: str = "evaluation-thresholds.yaml",
) -> Config:
    """
    Load all configuration files and return Config object.
    
    All configuration files follow a consistent schema where each file has a single
    top-level key matching its purpose (e.g., 'search', 'boards', 'slack', 'filters',
    'evaluation'). This consistency simplifies loading logic and makes the system
    easier to maintain and extend.
    
    Args:
        config_dir: Directory containing config files (defaults to project config/)
        search_criteria_file: Name of search criteria config file
        job_boards_file: Name of job boards config file
        slack_file: Name of slack config file
        filters_file: Name of filters config file
        evaluation_thresholds_file: Name of evaluation thresholds config file
        
    Returns:
        Config object containing all configuration
        
    Raises:
        FileNotFoundError: If required config files don't exist
        yaml.YAMLError: If config files are invalid YAML
        ValueError: If required environment variables are not set
    """
    if config_dir is None:
        # Default to config/ directory relative to project root
        project_root = Path(__file__).parent.parent.parent
        config_dir = project_root / "config"
    
    config_dir = Path(config_dir)
    
    # Load all config files with consistent schema
    # Each file has a single top-level key matching its purpose
    config_data = {}
    
    # Search criteria (required)
    search_criteria_path = config_dir / search_criteria_file
    config_data["search"] = load_yaml_file(search_criteria_path).get("search", {})
    
    # Job boards (required)
    job_boards_path = config_dir / job_boards_file
    config_data["boards"] = load_yaml_file(job_boards_path).get("boards", [])
    
    # Optional configurations
    optional_configs = {
        "slack": slack_file,
        "filters": filters_file,
        "evaluation": evaluation_thresholds_file,
    }
    
    for key, filename in optional_configs.items():
        path = config_dir / filename
        if path.exists():
            config_data[key] = load_yaml_file(path).get(key, {})
        else:
            config_data[key] = {}
    
    # Substitute environment variables (will raise ValueError if missing)
    config_data = _substitute_env_vars(config_data)
    
    return Config(config_data)

