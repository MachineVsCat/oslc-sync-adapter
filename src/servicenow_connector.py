"""ServiceNow REST API connector for incident and change request sync."""

import logging
import requests

log = logging.getLogger(__name__)


class ServiceNowConnector:
    def __init__(self, instance_url, username, password):
        self.instance_url = instance_url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def get_incidents(self, query=None, limit=100):
        """Fetch incidents from ServiceNow."""
        params = {"sysparm_limit": limit}
        if query:
            params["sysparm_query"] = query
        resp = self.session.get(
            f"{self.instance_url}/api/now/table/incident",
            params=params,
        )
        resp.raise_for_status()
        return resp.json().get("result", [])

    def create_incident(self, fields):
        """Create a new ServiceNow incident."""
        resp = self.session.post(
            f"{self.instance_url}/api/now/table/incident",
            json=fields,
        )
        resp.raise_for_status()
        result = resp.json().get("result", {})
        log.info(f"Created incident: {result.get('number')}")
        return result.get("sys_id")

    def update_incident(self, sys_id, fields):
        """Update an existing ServiceNow incident."""
        resp = self.session.patch(
            f"{self.instance_url}/api/now/table/incident/{sys_id}",
            json=fields,
        )
        resp.raise_for_status()
        return resp.json().get("result", {})

    def find_by_correlation_id(self, correlation_id):
        """Find incident by ELM correlation ID."""
        query = f"correlation_id={correlation_id}"
        incidents = self.get_incidents(query=query, limit=1)
        return incidents[0] if incidents else None

    def get_change_requests(self, query=None, limit=100):
        """Fetch change requests from ServiceNow."""
        params = {"sysparm_limit": limit}
        if query:
            params["sysparm_query"] = query
        resp = self.session.get(
            f"{self.instance_url}/api/now/table/change_request",
            params=params,
        )
        resp.raise_for_status()
        return resp.json().get("result", [])

    def create_change_request(self, fields):
        """Create a new change request linked to an ELM change set."""
        resp = self.session.post(
            f"{self.instance_url}/api/now/table/change_request",
            json=fields,
        )
        resp.raise_for_status()
        result = resp.json().get("result", {})
        log.info(f"Created change request: {result.get('number')}")
        return result.get("sys_id")

    def link_to_ewm_changeset(self, cr_sys_id, ewm_url):
        """Associate a ServiceNow change request with an EWM change set."""
        return self.update_incident(cr_sys_id, {
            "correlation_id": ewm_url,
            "work_notes": f"Linked to EWM change set: {ewm_url}",
        })
