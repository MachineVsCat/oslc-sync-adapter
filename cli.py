"""Command-line interface for OSLC Sync Adapter."""

import argparse
import logging
import sys
from src.config_loader import load_config, get_gcm_config
from src.oslc_client import OSLCClient
from src.doors_connector import DoorsNextConnector
from src.jira_connector import JiraConnector
from src.sync_engine import SyncEngine, DoorsAdapter, JiraAdapter
from src.health_check import HealthCheck
from src.utils.logging_config import setup_logging

log = logging.getLogger(__name__)


def cmd_sync(args, config):
    """Run synchronization based on config rules."""
    client = OSLCClient(
        config["jazz_server"]["url"],
        config["jazz_server"]["username"],
        config["jazz_server"]["password"],
        verify_ssl=config["jazz_server"].get("verify_ssl", True),
    )
    client.authenticate()

    doors = DoorsNextConnector(client, config["doors_next"]["project_area"])
    jira_cfg = config.get("jira", {})
    jira = JiraConnector(
        jira_cfg["base_url"], jira_cfg["username"],
        jira_cfg["api_token"], jira_cfg["project_key"],
    )

    engine = SyncEngine(config)
    for rule in config["sync_rules"]:
        source_adapter = DoorsAdapter(doors)
        target_adapter = JiraAdapter(jira)
        results = engine.run_sync(source_adapter, target_adapter, rule)
        log.info(f"Rule complete: {len(results)} operations")


def cmd_health(args, config):
    """Run health checks."""
    client = OSLCClient(
        config["jazz_server"]["url"],
        config["jazz_server"]["username"],
        config["jazz_server"]["password"],
    )
    hc = HealthCheck(client)
    report = hc.run_all_checks()
    print(f"Status: {report['overall']}")
    for check in report["checks"]:
        print(f"  {check['check']}: {check['status']}")


def main():
    parser = argparse.ArgumentParser(description="OSLC Sync Adapter")
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    parser.add_argument("--verbose", "-v", action="store_true")

    sub = parser.add_subparsers(dest="command")
    sub.add_parser("sync", help="Run synchronization")
    sub.add_parser("health", help="Run health checks")

    args = parser.parse_args()
    setup_logging(level=logging.DEBUG if args.verbose else logging.INFO)

    config = load_config(args.config)

    if args.command == "sync":
        cmd_sync(args, config)
    elif args.command == "health":
        cmd_health(args, config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
