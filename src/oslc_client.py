"""Base OSLC client for IBM Jazz platform authentication and resource queries."""

import time
import logging
import requests
from urllib.parse import urljoin, urlencode
from lxml import etree

OSLC_CORE_NS = "http://open-services.net/ns/core#"
DCTERMS_NS = "http://purl.org/dc/terms/"
OSLC_RM_NS = "http://open-services.net/ns/rm#"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

log = logging.getLogger(__name__)

DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_DELAY = 2


class JazzAuthError(Exception):
    pass


class OSLCClient:
    def __init__(self, server_url, username, password, verify_ssl=True,
                 max_retries=DEFAULT_RETRY_COUNT, retry_delay=DEFAULT_RETRY_DELAY):
        self.server_url = server_url.rstrip("/")
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.username = username
        self.password = password
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._authenticated = False
        self._auth_time = 0
        self._token_ttl = 3600  # 1 hour default

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
        self._auth_time = time.time()
        return True

    def _request_with_retry(self, method, url, **kwargs):
        """Execute HTTP request with retry on timeout/5xx errors."""
        last_error = None
        for attempt in range(self.max_retries):
            try:
                resp = getattr(self.session, method)(url, **kwargs)
                if resp.status_code >= 500:
                    log.warning(f"Server error {resp.status_code} on attempt {attempt + 1}")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                return resp
            except (requests.Timeout, requests.ConnectionError) as e:
                last_error = e
                log.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                time.sleep(self.retry_delay * (attempt + 1))
        raise last_error or requests.ConnectionError("Max retries exceeded")

    def get_service_providers(self, catalog_url):
        """Discover OSLC service providers from catalog."""
        resp = self._request_with_retry("get", catalog_url, headers={
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
        resp = self._request_with_retry("get", query_url, params=params, headers={
            "Accept": "application/json",
            "OSLC-Core-Version": "2.0",
        })
        resp.raise_for_status()
        return resp.json()

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
            resp = self._request_with_retry("get", next_url, params=params, headers={
                "Accept": "application/json",
                "OSLC-Core-Version": "2.0",
            })
            resp.raise_for_status()
            data = resp.json()
            results = data.get("oslc:results", data.get("results", []))
            all_results.extend(results)
            next_url = data.get("oslc:nextPage", data.get("nextPage"))
            params = {}
            log.info(f"Fetched page: {len(results)} items, total: {len(all_results)}")
        return all_results

    def get_resource(self, resource_url):
        """Fetch a single OSLC resource by URL."""
        resp = self._request_with_retry("get", resource_url, headers={
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
        resp = self._request_with_retry("put", resource_url, data=payload, headers=headers)
        resp.raise_for_status()
        return resp

    def _ensure_authenticated(self):
        """Re-authenticate if session token has expired."""
        if not self._authenticated or (time.time() - self._auth_time) > self._token_ttl:
            log.info("Session expired, re-authenticating with Jazz server")
            self.authenticate()
