"""IBM Engineering Test Management (ETM/RQM) connector."""

import logging
from src.oslc_client import OSLCClient, DCTERMS_NS

OSLC_QM_NS = "http://open-services.net/ns/qm#"

log = logging.getLogger(__name__)


class ETMConnector:
    def __init__(self, client: OSLCClient, project_area_url: str):
        self.client = client
        self.project_area_url = project_area_url

    def get_test_cases(self, category=None):
        """Query ETM test cases with optional category filter."""
        query_url = f"{self.project_area_url}/oslc_qm/contexts/_default/resources"
        where = None
        if category:
            where = f'oslc_qm:category="{category}"'
        result = self.client.query_resources(
            query_url,
            select="dcterms:title,dcterms:identifier,oslc_qm:status",
            where=where,
        )
        return result.get("oslc:results", [])

    def get_test_case(self, test_case_url):
        """Fetch a single test case resource."""
        return self.client.get_resource(test_case_url)

    def get_execution_results(self, test_case_url):
        """Get execution results linked to a test case."""
        resource = self.client.get_resource(test_case_url)
        results = resource.findall(f".//{{{OSLC_QM_NS}}}executionResult")
        return [{"url": r.get("rdf:resource", "")} for r in results]

    def get_test_plan(self, test_plan_url):
        """Fetch test plan with linked test cases."""
        resource = self.client.get_resource(test_plan_url)
        cases = resource.findall(f".//{{{OSLC_QM_NS}}}usesTestCase")
        return {
            "url": test_plan_url,
            "test_cases": [c.get("rdf:resource", "") for c in cases],
        }

    def link_to_requirement(self, test_case_url, requirement_url):
        """Create a validatesRequirement link from test case to requirement."""
        log.info(f"Linking test case to requirement: {requirement_url}")
        payload = f"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:oslc_qm="{OSLC_QM_NS}">
  <rdf:Description rdf:about="{test_case_url}">
    <oslc_qm:validatesRequirement rdf:resource="{requirement_url}"/>
  </rdf:Description>
</rdf:RDF>"""
        return self.client.update_resource(test_case_url, payload)
