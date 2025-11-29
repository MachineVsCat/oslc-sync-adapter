"""DOORS Next Generation (DNG) connector for requirements management."""

from src.oslc_client import OSLCClient, OSLC_RM_NS, DCTERMS_NS


class DoorsNextConnector:
    def __init__(self, client: OSLCClient, project_area_url: str):
        self.client = client
        self.project_area_url = project_area_url
        self._query_base = None

    def _discover_query_base(self):
        """Find the OSLC query capability for requirements."""
        if self._query_base:
            return self._query_base
        providers = self.client.get_service_providers(
            f"{self.client.server_url}/rm/oslc_rm/catalog"
        )
        for sp in providers:
            if sp["url"] == self.project_area_url:
                self._query_base = f"{sp['url']}/query"
                break
        return self._query_base

    def get_requirements(self, module_url=None, filter_attr=None):
        """Fetch requirements from a DOORS Next project area."""
        query_url = self._discover_query_base()
        where = None
        if filter_attr:
            where = f"dcterms:identifier={filter_attr}"
        result = self.client.query_resources(
            query_url,
            select="dcterms:title,dcterms:identifier,dcterms:description",
            where=where,
        )
        return result.get("oslc:results", result.get("results", []))

    def get_requirement_by_id(self, req_id):
        """Fetch a single requirement by its identifier."""
        reqs = self.get_requirements(filter_attr=req_id)
        return reqs[0] if reqs else None

    def get_module_structure(self, module_url):
        """Retrieve module hierarchy and artifact bindings."""
        resource = self.client.get_resource(module_url)
        artifacts = resource.findall(f".//{{{OSLC_RM_NS}}}Requirement")
        structure = []
        for art in artifacts:
            title = art.find(f"{{{DCTERMS_NS}}}title")
            structure.append({
                "uri": art.get("rdf:about", ""),
                "title": title.text if title is not None else "",
            })
        return structure

    def get_links(self, requirement_url):
        """Get all OSLC links for a requirement."""
        resource = self.client.get_resource(requirement_url)
        links = []
        for link_type in ["satisfiedBy", "implementedBy", "validatedBy", "trackedBy"]:
            found = resource.findall(f".//{{{OSLC_RM_NS}}}{link_type}")
            for lnk in found:
                links.append({
                    "type": link_type,
                    "target": lnk.get("rdf:resource", ""),
                })
        return links
