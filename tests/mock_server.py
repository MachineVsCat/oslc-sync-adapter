"""Mock OSLC server for integration testing."""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

MOCK_CATALOG = """<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:oslc="http://open-services.net/ns/core#"
         xmlns:dcterms="http://purl.org/dc/terms/">
  <oslc:ServiceProviderCatalog>
    <oslc:serviceProvider>
      <oslc:ServiceProvider rdf:about="http://localhost:9800/rm/project1">
        <dcterms:title>Test Project</dcterms:title>
      </oslc:ServiceProvider>
    </oslc:serviceProvider>
  </oslc:ServiceProviderCatalog>
</rdf:RDF>"""

MOCK_REQUIREMENTS = {
    "oslc:results": [
        {
            "dcterms:identifier": "REQ-001",
            "dcterms:title": "System shall support thermal printing",
            "dcterms:description": "The system shall support ZPL and TSPL output.",
        },
        {
            "dcterms:identifier": "REQ-002",
            "dcterms:title": "System shall validate input data",
            "dcterms:description": "All input data shall be validated before processing.",
        },
    ]
}


class MockOSLCHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if "/j_security_check" in self.path:
            self.send_response(200)
            self.end_headers()
        elif "/catalog" in self.path:
            self.send_response(200)
            self.send_header("Content-Type", "application/rdf+xml")
            self.end_headers()
            self.wfile.write(MOCK_CATALOG.encode())
        elif "/query" in self.path or "/resources" in self.path:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(MOCK_REQUIREMENTS).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if "j_security_check" in self.path:
            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(201)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress server logs during tests


class MockOSLCServer:
    def __init__(self, port=9800):
        self.port = port
        self.server = HTTPServer(("localhost", port), MockOSLCHandler)
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.server.shutdown()
        if self.thread:
            self.thread.join()
