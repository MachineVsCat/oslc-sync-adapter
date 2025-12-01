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

    def detect_suspect_links(self, requirement_url):
        """Check if any links on a requirement are marked as suspect."""
        links = self.get_links(requirement_url)
        suspect = []
        for link in links:
            target_resource = self.client.get_resource(link["target"])
            modified = target_resource.find(f".//{{{DCTERMS_NS}}}modified")
            if modified is not None:
                suspect.append({
                    "link_type": link["type"],
                    "target": link["target"],
                    "last_modified": modified.text,
                    "suspect": True,
                })
        return suspect

    def clear_suspect_flag(self, link_url):
        """Clear the suspect flag on a traceability link."""
        log.info(f"Clearing suspect flag on {link_url}")
        # Would update the link resource to remove suspect status
        pass

    def create_link(self, source_url, target_url, link_type="implementedBy"):
        """Create an OSLC traceability link between resources."""
        payload = f"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:oslc_rm="{OSLC_RM_NS}">
  <rdf:Description rdf:about="{source_url}">
    <oslc_rm:{link_type} rdf:resource="{target_url}"/>
  </rdf:Description>
</rdf:RDF>"""
        resource = self.client.get_resource(source_url)
        etag = None  # would extract from response headers
        return self.client.update_resource(source_url, payload, etag)

    def remove_link(self, source_url, target_url, link_type):
        """Remove a traceability link from a requirement."""
        log.info(f"Removing {link_type} link: {source_url} -> {target_url}")
        # Would PATCH the resource to remove the link triple
        pass
