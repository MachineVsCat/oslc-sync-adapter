"""Integration health check and monitoring."""

import logging
import time
from datetime import datetime

log = logging.getLogger(__name__)


class HealthCheck:
    def __init__(self, client, connectors=None):
        self.client = client
        self.connectors = connectors or {}
        self.results = []

    def check_jazz_server(self):
        """Verify Jazz Team Server is reachable and authenticated."""
        try:
            start = time.time()
            self.client.authenticate()
            elapsed = time.time() - start
            self.results.append({
                "check": "jazz_server",
                "status": "ok",
                "response_time_ms": round(elapsed * 1000),
                "timestamp": datetime.utcnow().isoformat(),
            })
            return True
        except Exception as e:
            self.results.append({
                "check": "jazz_server",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            })
            return False

    def check_connector(self, name, connector):
        """Test connectivity for a specific connector."""
        try:
            start = time.time()
            if hasattr(connector, "get_requirements"):
                connector.get_requirements()
            elif hasattr(connector, "get_work_items"):
                connector.get_work_items()
            elif hasattr(connector, "get_issues"):
                connector.get_issues(max_results=1)
            elapsed = time.time() - start
            self.results.append({
                "check": name,
                "status": "ok",
                "response_time_ms": round(elapsed * 1000),
                "timestamp": datetime.utcnow().isoformat(),
            })
            return True
        except Exception as e:
            self.results.append({
                "check": name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            })
            return False

    def run_all_checks(self):
        """Execute all health checks and return summary."""
        self.results = []
        self.check_jazz_server()
        for name, conn in self.connectors.items():
            self.check_connector(name, conn)

        failed = [r for r in self.results if r["status"] != "ok"]
        log.info(f"Health check: {len(self.results)} checks, {len(failed)} failed")
        return {
            "overall": "healthy" if not failed else "degraded",
            "checks": self.results,
            "timestamp": datetime.utcnow().isoformat(),
        }
