"""SPARQL queries for Lifecycle Query Engine (LQE) and Jazz Reporting Service."""

import logging
from src.oslc_client import OSLCClient

log = logging.getLogger(__name__)

TRACEABILITY_QUERY = """
PREFIX oslc_rm: <http://open-services.net/ns/rm#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX oslc: <http://open-services.net/ns/core#>

SELECT ?req ?title ?satisfiedBy ?implementedBy ?validatedBy
WHERE {
    ?req a oslc_rm:Requirement .
    ?req dcterms:title ?title .
    OPTIONAL { ?req oslc_rm:satisfiedBy ?satisfiedBy }
    OPTIONAL { ?req oslc_rm:implementedBy ?implementedBy }
    OPTIONAL { ?req oslc_rm:validatedBy ?validatedBy }
}
ORDER BY ?title
"""

COVERAGE_QUERY = """
PREFIX oslc_rm: <http://open-services.net/ns/rm#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?req ?title (COUNT(?validatedBy) AS ?testCount)
WHERE {
    ?req a oslc_rm:Requirement .
    ?req dcterms:title ?title .
    OPTIONAL { ?req oslc_rm:validatedBy ?validatedBy }
}
GROUP BY ?req ?title
HAVING (?testCount = 0)
"""


class LQEReporter:
    def __init__(self, client: OSLCClient, lqe_url: str):
        self.client = client
        self.lqe_url = lqe_url.rstrip("/")

    def execute_sparql(self, query):
        """Execute a SPARQL query against LQE."""
        resp = self.client._request_with_retry(
            "post",
            f"{self.lqe_url}/sparql",
            data=query,
            headers={
                "Content-Type": "application/sparql-query",
                "Accept": "application/json",
            },
        )
        resp.raise_for_status()
        return resp.json()

    def get_traceability_matrix(self, project_area=None):
        """Generate requirements traceability matrix."""
        query = TRACEABILITY_QUERY
        if project_area:
            query += f'\nFILTER(STRSTARTS(STR(?req), "{project_area}"))'
        results = self.execute_sparql(query)
        return self._format_matrix(results)

    def get_untested_requirements(self):
        """Find requirements with no linked test cases."""
        results = self.execute_sparql(COVERAGE_QUERY)
        return results.get("results", {}).get("bindings", [])

    def _format_matrix(self, sparql_results):
        """Format SPARQL results into a traceability matrix."""
        bindings = sparql_results.get("results", {}).get("bindings", [])
        matrix = []
        for row in bindings:
            matrix.append({
                "requirement": row.get("req", {}).get("value", ""),
                "title": row.get("title", {}).get("value", ""),
                "satisfied_by": row.get("satisfiedBy", {}).get("value", ""),
                "implemented_by": row.get("implementedBy", {}).get("value", ""),
                "validated_by": row.get("validatedBy", {}).get("value", ""),
            })
        return matrix
