"""Configuration loader for sync adapter settings."""

import os
import yaml
import logging
from pathlib import Path

log = logging.getLogger(__name__)


class ConfigError(Exception):
    pass


VALID_DIRECTIONS = ["source_to_target", "target_to_source", "bidirectional"]
VALID_CONFLICT_MODES = ["source_wins", "target_wins", "newest_wins", "manual"]


def load_config(config_path):
    """Load and validate YAML configuration file."""
    path = Path(config_path)
    if not path.exists():
        raise ConfigError(f"Config file not found: {config_path}")

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    config = _resolve_env_vars(config)
    _validate_config(config)
    return config


def _resolve_env_vars(config):
    """Replace ${VAR} placeholders with environment variable values."""
    if isinstance(config, dict):
        return {k: _resolve_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [_resolve_env_vars(item) for item in config]
    elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
        var_name = config[2:-1]
        value = os.environ.get(var_name)
        if value is None:
            log.warning(f"Environment variable {var_name} not set")
        return value or config
    return config


def _validate_config(config):
    """Check required configuration sections and field mappings."""
    required = ["jazz_server", "sync_rules"]
    for key in required:
        if key not in config:
            raise ConfigError(f"Missing required config section: {key}")

    server = config["jazz_server"]
    for field in ["url", "username", "password"]:
        if field not in server:
            raise ConfigError(f"Missing jazz_server.{field}")

    for i, rule in enumerate(config.get("sync_rules", [])):
        if "source" not in rule or "target" not in rule:
            raise ConfigError(f"sync_rules[{i}]: missing source or target")
        if "mapping" not in rule:
            raise ConfigError(f"sync_rules[{i}]: missing field mapping")
        direction = rule.get("direction", "source_to_target")
        if direction not in VALID_DIRECTIONS:
            raise ConfigError(f"sync_rules[{i}]: invalid direction '{direction}'")
        conflict = rule.get("conflict_resolution", "source_wins")
        if conflict not in VALID_CONFLICT_MODES:
            raise ConfigError(f"sync_rules[{i}]: invalid conflict_resolution '{conflict}'")


def get_gcm_config(config):
    """Extract Global Configuration Management settings."""
    gcm = config.get("gcm", {})
    if not gcm.get("enabled", False):
        return None
    return {
        "server_url": gcm["server_url"],
        "stream": gcm.get("default_stream", "main"),
    }
