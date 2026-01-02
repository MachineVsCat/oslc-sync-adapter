"""Jira REST API connector for issue synchronization."""

import requests
import logging

log = logging.getLogger(__name__)


class JiraConnector:
    def __init__(self, base_url, username, api_token, project_key):
        self.base_url = base_url.rstrip("/")
        self.project_key = project_key
        self.session = requests.Session()
        self.session.auth = (username, api_token)
        self.session.headers.update({"Content-Type": "application/json"})

    def get_issues(self, jql=None, max_results=100):
        """Fetch issues from Jira using JQL."""
        if not jql:
            jql = f"project = {self.project_key}"
        resp = self.session.get(
            f"{self.base_url}/rest/api/2/search",
            params={"jql": jql, "maxResults": max_results},
        )
        if resp.status_code == 401:
            log.error("Jira authentication failed - check API token")
        resp.raise_for_status()
        return resp.json().get("issues", [])

    def get_issue(self, issue_key):
        """Fetch a single Jira issue."""
        resp = self.session.get(
            f"{self.base_url}/rest/api/2/issue/{issue_key}"
        )
        if resp.status_code == 401:
            log.error("Jira authentication failed - check API token")
        resp.raise_for_status()
        return resp.json()

    def create_item(self, fields):
        """Create a new Jira issue from mapped fields."""
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "issuetype": {"name": "Task"},
                **fields,
            }
        }
        resp = self.session.post(
            f"{self.base_url}/rest/api/2/issue",
            json=payload,
        )
        if resp.status_code == 401:
            log.error("Jira authentication failed - check API token")
        resp.raise_for_status()
        return resp.json()["key"]

    def update_item(self, issue_key, fields):
        """Update an existing Jira issue."""
        resp = self.session.put(
            f"{self.base_url}/rest/api/2/issue/{issue_key}",
            json={"fields": fields},
        )
        if resp.status_code == 401:
            log.error("Jira authentication failed - check API token")
        resp.raise_for_status()
        log.info(f"Updated Jira issue {issue_key}")

    def find_by_custom_field(self, field_name, value):
        """Find Jira issue by custom field value (used for traceability)."""
        jql = f'"{field_name}" ~ "{value}" AND project = {self.project_key}'
        issues = self.get_issues(jql=jql, max_results=1)
        return issues[0]["key"] if issues else None

    def test_connection(self):
        """Test Jira connectivity and permissions."""
        try:
            self.get_issues(max_results=1)
            return True
        except Exception as e:
            log.error(f"Jira connection test failed: {e}")
            return False
