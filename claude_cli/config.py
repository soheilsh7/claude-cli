import os
import yaml
from pathlib import Path

CONFIG_DIR = os.path.expanduser("~/.config/claude-cli")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.yaml")

def ensure_config_dir():
    """Ensure the config directory exists"""
    os.makedirs(CONFIG_DIR, exist_ok=True)

def load_config():
    """Load configuration from file or return default"""
    ensure_config_dir()
    
    if not os.path.exists(CONFIG_PATH):
        return {}
    
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

def save_config(config):
    """Save configuration to file"""
    ensure_config_dir()
    
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(config, f)

def get_cookie():
    """Get the Claude cookie from config or environment variable"""
    # First check environment variable
    cookie = os.environ.get('CLAUDE_COOKIE')
    if cookie:
        return cookie
    
    # Then check config file
    config = load_config()
    return config.get('cookie')