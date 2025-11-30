"""IBM Engineering Workflow Management (EWM/RTC) connector."""

import logging
from src.oslc_client import OSLCClient, DCTERMS_NS

OSLC_CM_NS = "http://open-services.net/ns/cm#"

log = logging.getLogger(__name__)


class EWMConnector:
    def __init__(self, client: OSLCClient, project_area_url: str):
        self.client = client
        self.project_area_url = project_area_url

    def get_work_items(self, work_item_type=None, state=None):
        """Query EWM work items with optional filters."""
        query_url = f"{self.project_area_url}/oslc/contexts/_default/workitems"
        where_parts = []
        if work_item_type:
            where_parts.append(f'dcterms:type="{work_item_type}"')
        if state:
            where_parts.append(f'oslc_cm:state="{state}"')
        where = " and ".join(where_parts) if where_parts else None
        result = self.client.query_resources(
            query_url,
            select="dcterms:title,dcterms:identifier,oslc_cm:state",
            where=where,
        )
        return result.get("oslc:results", [])

    def get_work_item(self, work_item_url):
        """Fetch a single work item resource."""
        return self.client.get_resource(work_item_url)

    def create_work_item(self, fields):
        """Create a new EWM work item."""
        log.info(f"Creating work item: {fields.get('dcterms:title', 'untitled')}")
        # Would POST to the work item creation factory
        return None

    def update_work_item(self, work_item_url, fields, etag=None):
        """Update an existing EWM work item."""
        payload = self._build_rdf_payload(fields)
        return self.client.update_resource(work_item_url, payload, etag)

    def get_change_requests(self, since=None):
        """Fetch change requests, optionally filtered by date."""
        where = None
        if since:
            where = f'dcterms:modified>="{since}"'
        query_url = f"{self.project_area_url}/oslc/contexts/_default/workitems"
        return self.client.query_resources(query_url, where=where)

    def _build_rdf_payload(self, fields):
        """Build RDF/XML payload from field dictionary."""
        parts = ['<?xml version="1.0"?>\n<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"'
                 f' xmlns:dcterms="{DCTERMS_NS}">']
        for key, val in fields.items():
            parts.append(f"  <{key}>{val}</{key}>")
        parts.append("</rdf:RDF>")
        return "\n".join(parts)
