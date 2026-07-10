"""
Configuration management module for the browserAPI project.
Handles loading, saving, updating, resetting, and validating the config.json file.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

# Supported browser list for validation
SUPPORTED_BROWSERS = {"chrome", "firefox", "edge", "safari", "opera", "brave", "chromium", "vivaldi", "librewolf", "waterfox"}

# Default configuration template as defined in the specifications
DEFAULT_CONFIG: Dict[str, Any] = {
    "server": {
        "host": "127.0.0.1",
        "port": 4747
    },
    "cookies": {
        "default_browser": None,
        "browser_path": None,
        "__Secure-1PSID": None,
        "__Secure-1PSIDTS": None
    },
    "gemini": {
        "default_model": "flash",
        "strong_model": "pro",
        "weak_model": "flash-lite",
        "language": None
    },
    "meta": {
        "max_files": 20,
        "cookie_update": 600
    }
}

def get_config_path() -> Path:
    """
    Resolves the absolute path to the config.json file in the project root.
    
    Returns:
        Path: Path object pointing to the config.json file.
    """
    # config.json sits in the project root (two levels up from src/core/config.py)
    return Path(__file__).parent.parent.parent / "config.json"

def load_config() -> Dict[str, Any]:
    """
    Loads the config.json file. If the file is missing or contains invalid JSON,
    it automatically generates a new one with the factory default values.
    
    Returns:
        dict: The loaded configuration dictionary.
    """
    config_path = get_config_path()
    if not config_path.exists():
        reset_config()
        return DEFAULT_CONFIG.copy()
        
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # On corruption or failure to read, restore default configuration
        reset_config()
        return DEFAULT_CONFIG.copy()

def reset_config() -> None:
    """
    Resets the entire configuration file, restoring all fields back
    to their original factory default values.
    """
    config_path = get_config_path()
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
    except IOError as e:
        print(f" \033[91m[-] Critical: Failed to write configuration file: {e}\033[0m")

def get_config(section: str, key: str) -> Any:
    """
    Retrieves a specific configuration value from the JSON structure
    based on the provided section and key.
    
    Args:
        section (str): The main config section (e.g., 'server', 'cookies').
        key (str): The configuration setting name.
        
    Returns:
        Any: The configured value, or None if the section/key does not exist.
    """
    config = load_config()
    return config.get(section, {}).get(key)

def set_config(section: str, key: str, value: Any) -> None:
    """
    Updates or writes a specific configuration value within a designated
    section of the JSON file.
    
    Args:
        section (str): The main config section (e.g., 'server', 'cookies').
        key (str): The configuration setting name.
        value (Any): The new value to set.
    """
    config = load_config()
    if section not in config:
        config[section] = {}
    config[section][key] = value
    
    config_path = get_config_path()
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except IOError as e:
        print(f" \033[91m[-] Error: Failed to save updated configuration: {e}\033[0m")

def test_config() -> bool:
    """
    Validates essential configuration fields at startup.
    Ensures correct structure, valid types, and value sanity.
    
    Returns:
        bool: True if configuration is fully valid, False otherwise.
    """
    try:
        config = load_config()
        
        # Verify all mandatory sections exist
        for section in DEFAULT_CONFIG:
            if section not in config:
                return False
                
        # Validate server host and port
        host = config.get("server", {}).get("host")
        port = config.get("server", {}).get("port")
        if not isinstance(host, str) or not host:
            return False
        if not isinstance(port, int) or not (1 <= port <= 65535):
            return False
            
        # Validate cookies: default_browser must be either None or in supported list
        browser = config.get("cookies", {}).get("default_browser")
        if browser is not None:
            if not isinstance(browser, str) or browser.lower() not in SUPPORTED_BROWSERS:
                return False
                
        # Validate gemini model strings
        default_model = config.get("gemini", {}).get("default_model")
        strong_model = config.get("gemini", {}).get("strong_model")
        weak_model = config.get("gemini", {}).get("weak_model")
        if not isinstance(default_model, str) or not default_model:
            return False
        if not isinstance(strong_model, str) or not strong_model:
            return False
        if not isinstance(weak_model, str) or not weak_model:
            return False
            
        # Validate meta fields
        max_files = config.get("meta", {}).get("max_files")
        cookie_update = config.get("meta", {}).get("cookie_update")
        if not isinstance(max_files, int) or max_files <= 0:
            return False
        if not isinstance(cookie_update, int) or cookie_update <= 0:
            return False
            
        return True
    except Exception:
        # Any unexpected failure results in validation fail
        return False
