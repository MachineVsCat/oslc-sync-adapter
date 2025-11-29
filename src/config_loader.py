"""Configuration loader for sync adapter settings."""

import yaml
from pathlib import Path


class ConfigError(Exception):
    pass


def load_config(config_path):
    """Load and validate YAML configuration file."""
    path = Path(config_path)
    if not path.exists():
        raise ConfigError(f"Config file not found: {config_path}")

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    _validate_config(config)
    return config


def _validate_config(config):
    """Check required configuration sections."""
    required = ["jazz_server", "sync_rules"]
    for key in required:
        if key not in config:
            raise ConfigError(f"Missing required config section: {key}")
    server = config["jazz_server"]
    for field in ["url", "username", "password"]:
        if field not in server:
            raise ConfigError(f"Missing jazz_server.{field}")
