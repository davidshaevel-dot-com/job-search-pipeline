# Python Virtual Environment Setup

**Date:** November 21, 2025
**Python Version:** 3.12.11

---

## Quick Start

### Create Virtual Environment

```bash
cd /Users/dshaevel/workspace-ds/job-search-pipeline
python3 -m venv venv
```

### Activate Virtual Environment

```bash
# Activate (run this every time you start a new terminal session)
source venv/bin/activate

# Verify activation (you should see "(venv)" in your prompt)
which python  # Should show: /Users/dshaevel/workspace-ds/job-search-pipeline/venv/bin/python
```

### Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all project dependencies
pip install -r requirements.txt
```

### Deactivate (when done)

```bash
deactivate
```

---

## Verification

### Check Installed Packages

```bash
# List all installed packages
pip list

# Check specific packages for Phase 1
pip list | grep -E "(requests|pyyaml|python-dateutil)"
```

**Expected output:**
```
pyyaml                 6.0.3
python-dateutil        2.9.0.post0
requests               2.32.5
```

### Test Import

```bash
# Test that core dependencies import correctly
python -c "import requests; import yaml; print('✅ Core dependencies OK')"
```

---

## Virtual Environment Details

**Location:** `/Users/dshaevel/workspace-ds/job-search-pipeline/venv/`

**Python Version:** 3.12.11

**Total Packages Installed:** 60+

**Key Dependencies:**
- **requests** - HTTP library for API calls
- **pyyaml** - YAML configuration parsing
- **python-dateutil** - Date parsing utilities
- **pydantic** - Data validation
- **anthropic** - Claude API (Phase 4)
- **slack-sdk** - Slack integration (Phase 6)
- **pytest** - Testing framework
- **black, flake8, mypy** - Code quality tools

**Git Status:** `venv/` directory is excluded via `.gitignore`

---

## Troubleshooting

### Issue: "python3: command not found"

**Solution:** Install Python 3.12 via Homebrew:
```bash
brew install python@3.12
```

### Issue: "No module named 'venv'"

**Solution:** Ensure you're using Python 3.3+ (venv is built-in):
```bash
python3 --version  # Should be 3.12.11
```

### Issue: "Permission denied" when creating venv

**Solution:** Check directory permissions:
```bash
ls -la /Users/dshaevel/workspace-ds/job-search-pipeline
```

### Issue: Virtual environment not activating

**Symptoms:** No "(venv)" in prompt after `source venv/bin/activate`

**Solutions:**
1. Check you're in the correct directory
2. Try absolute path: `source /Users/dshaevel/workspace-ds/job-search-pipeline/venv/bin/activate`
3. Check venv was created successfully: `ls venv/bin/activate`

### Issue: "pip: command not found" after activating

**Solution:** Recreate virtual environment:
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

---

## IDE Integration

### VS Code

Add to `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.terminal.activateEnvironment": true
}
```

VS Code should automatically detect and use the virtual environment.

### PyCharm

1. Open: **Preferences** → **Project** → **Python Interpreter**
2. Click gear icon → **Add**
3. Select **Existing Environment**
4. Navigate to: `/Users/dshaevel/workspace-ds/job-search-pipeline/venv/bin/python`

---

## Best Practices

### Always Activate Before Working

```bash
# Add to your shell profile (~/.zshrc or ~/.bashrc)
alias jobsearch='cd /Users/dshaevel/workspace-ds/job-search-pipeline && source venv/bin/activate'

# Then just run:
jobsearch
```

### Verify Activation

```bash
# Check you're using venv Python
which python
# Should show: /Users/dshaevel/workspace-ds/job-search-pipeline/venv/bin/python

# NOT system Python:
# /usr/local/bin/python  ❌
# /usr/bin/python  ❌
```

### Update Dependencies

```bash
# If requirements.txt changes:
source venv/bin/activate
pip install -r requirements.txt

# Or to upgrade all packages:
pip install --upgrade -r requirements.txt
```

### Clean Installation

```bash
# If dependencies get corrupted, recreate:
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Environment Variables

Create `.env` file (not committed to git):

```bash
# Copy template
cp .env.example .env

# Edit with your keys
nano .env
```

**Required for Phase 1:**
```bash
# RapidAPI Key for JSearch
RAPIDAPI_KEY="your-rapidapi-key-here"
```

**Load environment variables:**
```bash
# Option 1: Export in shell
export $(cat .env | xargs)

# Option 2: Use python-dotenv (install separately)
pip install python-dotenv
```

---

## Phase 1 Testing Checklist

Before running tests:

- [ ] Virtual environment created: `ls venv/`
- [ ] Virtual environment activated: `which python` shows venv path
- [ ] Dependencies installed: `pip list | grep requests`
- [ ] RAPIDAPI_KEY set: `echo $RAPIDAPI_KEY`
- [ ] Test script exists: `ls scripts/test_jsearch_adapter.py`

Now ready to run:
```bash
python scripts/test_jsearch_adapter.py
```

---

**Last Updated:** November 21, 2025
**Status:** Virtual environment configured and ready for testing
