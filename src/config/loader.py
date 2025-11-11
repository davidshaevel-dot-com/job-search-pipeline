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
    
    Supports ${VAR_NAME} syntax. If variable is not found, returns the
    original string with ${} intact.
    """
    if isinstance(value, str):
        # Match ${VAR_NAME} pattern
        pattern = r'\$\{([^}]+)\}'
        
        def replace(match):
            var_name = match.group(1)
            env_value = os.getenv(var_name)
            if env_value is not None:
                return env_value
            # Return original if not found (don't fail silently)
            return match.group(0)
        
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
    filters_file: str = "filters.yaml",
    evaluation_thresholds_file: str = "evaluation-thresholds.yaml",
) -> Config:
    """
    Load all configuration files and return Config object.
    
    Note: This implementation uses explicit handling for each config file.
    If the number of config files grows significantly, consider refactoring
    to a more generic, data-driven approach where each file is loaded into
    a dictionary key derived from its filename.
    
    Args:
        config_dir: Directory containing config files (defaults to project config/)
        search_criteria_file: Name of search criteria config file
        job_boards_file: Name of job boards config file
        filters_file: Name of filters config file
        evaluation_thresholds_file: Name of evaluation thresholds config file
        
    Returns:
        Config object containing all configuration
        
    Raises:
        FileNotFoundError: If required config files don't exist
        yaml.YAMLError: If config files are invalid YAML
    """
    if config_dir is None:
        # Default to config/ directory relative to project root
        project_root = Path(__file__).parent.parent.parent
        config_dir = project_root / "config"
    
    config_dir = Path(config_dir)
    
    # Load all config files
    config_data = {}
    
    # Search criteria (required)
    search_criteria_path = config_dir / search_criteria_file
    config_data["search"] = load_yaml_file(search_criteria_path).get("search", {})
    
    # Job boards (required)
    # Note: job-boards.yaml contains both 'boards' and 'slack' configs
    job_boards_path = config_dir / job_boards_file
    boards_data = load_yaml_file(job_boards_path)
    config_data["boards"] = boards_data.get("boards", [])
    config_data["slack"] = boards_data.get("slack", {})
    
    # Filters (optional for Phase 1, but good to have structure)
    filters_path = config_dir / filters_file
    if filters_path.exists():
        filters_data = load_yaml_file(filters_path)
        config_data["filters"] = filters_data
    else:
        config_data["filters"] = {}
    
    # Evaluation thresholds (optional for Phase 1, but good to have structure)
    eval_path = config_dir / evaluation_thresholds_file
    if eval_path.exists():
        eval_data = load_yaml_file(eval_path)
        config_data["evaluation"] = eval_data.get("evaluation", {})
    else:
        config_data["evaluation"] = {}
    
    # Substitute environment variables
    config_data = _substitute_env_vars(config_data)
    
    return Config(config_data)

