"""Base OSLC client for IBM Jazz platform authentication and resource queries."""

import requests
from urllib.parse import urljoin, urlencode
from lxml import etree

OSLC_CORE_NS = "http://open-services.net/ns/core#"
DCTERMS_NS = "http://purl.org/dc/terms/"
OSLC_RM_NS = "http://open-services.net/ns/rm#"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"


class JazzAuthError(Exception):
    pass


class OSLCClient:
    def __init__(self, server_url, username, password, verify_ssl=True):
        self.server_url = server_url.rstrip("/")
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.username = username
        self.password = password
        self._authenticated = False

    def authenticate(self):
        """Perform Jazz Form-based authentication."""
        auth_url = f"{self.server_url}/j_security_check"
        payload = {
            "j_username": self.username,
            "j_password": self.password,
        }
        resp = self.session.post(auth_url, data=payload, allow_redirects=True)
        if "authfailed" in resp.url or resp.status_code == 401:
            raise JazzAuthError(f"Authentication failed for {self.username}")
        self._authenticated = True
        return True

    def get_service_providers(self, catalog_url):
        """Discover OSLC service providers from catalog."""
        resp = self.session.get(catalog_url, headers={
            "Accept": "application/rdf+xml",
            "OSLC-Core-Version": "2.0",
        })
        resp.raise_for_status()
        tree = etree.fromstring(resp.content)
        providers = tree.findall(
            f".//{{{OSLC_CORE_NS}}}ServiceProvider"
        )
        results = []
        for sp in providers:
            title_el = sp.find(f"{{{DCTERMS_NS}}}title")
            about = sp.get(f"{{{RDF_NS}}}about", "")
            if not about:
                about = sp.attrib.get("rdf:about", "")
            results.append({
                "title": title_el.text if title_el is not None else "",
                "url": about,
            })
        return results

    def query_resources(self, query_url, select=None, where=None, page_size=100, fetch_all=False):
        """Execute OSLC query with optional select and where clauses."""
        params = {"oslc.pageSize": str(page_size)}
        if select:
            params["oslc.select"] = select
        if where:
            params["oslc.where"] = where
        resp = self.session.get(query_url, params=params, headers={
            "Accept": "application/json",
            "OSLC-Core-Version": "2.0",
        })
        resp.raise_for_status()
        return resp.json()

    def get_resource(self, resource_url):
        """Fetch a single OSLC resource by URL."""
        resp = self.session.get(resource_url, headers={
            "Accept": "application/rdf+xml",
            "OSLC-Core-Version": "2.0",
        })
        resp.raise_for_status()
        return etree.fromstring(resp.content)

    def update_resource(self, resource_url, payload, etag=None):
        """Update an OSLC resource using PUT with optional ETag."""
        headers = {
            "Content-Type": "application/rdf+xml",
            "OSLC-Core-Version": "2.0",
        }
        if etag:
            headers["If-Match"] = etag
        resp = self.session.put(resource_url, data=payload, headers=headers)
        resp.raise_for_status()
        return resp

    def query_all_pages(self, query_url, select=None, where=None, page_size=100):
        """Fetch all pages of an OSLC query result."""
        all_results = []
        params = {"oslc.pageSize": str(page_size)}
        if select:
            params["oslc.select"] = select
        if where:
            params["oslc.where"] = where

        next_url = query_url
        while next_url:
            resp = self.session.get(next_url, params=params, headers={
                "Accept": "application/json",
                "OSLC-Core-Version": "2.0",
            })
            resp.raise_for_status()
            data = resp.json()
            results = data.get("oslc:results", data.get("results", []))
            all_results.extend(results)
            next_url = data.get("oslc:nextPage", data.get("nextPage"))
            params = {}  # next page URL includes params
            log.info(f"Fetched page: {len(results)} items, total: {len(all_results)}")

        return all_results
