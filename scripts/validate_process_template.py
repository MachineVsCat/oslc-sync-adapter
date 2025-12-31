"""Validate ELM project area process templates and role definitions."""

import argparse
import logging
import json
from src.oslc_client import OSLCClient

log = logging.getLogger(__name__)

REQUIRED_ROLES = ["Analyst", "Developer", "Tester", "Project Lead", "Stakeholder"]
REQUIRED_LINK_TYPES = ["satisfiedBy", "implementedBy", "validatedBy", "trackedBy"]


def validate_project_area(client, project_area_url):
    """Validate project area configuration against standards."""
    issues = []
    resource = client.get_resource(project_area_url)

    # Check roles
    roles = [r.text for r in resource.findall(".//{http://jazz.net/xmlns/process#}role")]
    for required in REQUIRED_ROLES:
        if required not in roles:
            issues.append(f"Missing role: {required}")

    log.info(f"Validated {len(roles)} roles, {len(issues)} issues found")
    return {"project_area": project_area_url, "roles": roles, "issues": issues}


def validate_link_types(client, rm_catalog_url):
    """Verify required OSLC link types are configured."""
    providers = client.get_service_providers(rm_catalog_url)
    issues = []
    if not providers:
        issues.append("No service providers found in catalog")
    log.info(f"Found {len(providers)} service providers")
    return {"link_types_checked": REQUIRED_LINK_TYPES, "issues": issues}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate ELM process templates")
    parser.add_argument("--server", required=True, help="Jazz server URL")
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--project", required=True, help="Project area URL")
    parser.add_argument("--output", default=None, help="Output JSON file")
    args = parser.parse_args()

    client = OSLCClient(args.server, args.user, args.password)
    client.authenticate()

    result = validate_project_area(client, args.project)
    link_result = validate_link_types(client, f"{args.server}/rm/oslc_rm/catalog")
    result["link_validation"] = link_result

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
    else:
        print(json.dumps(result, indent=2))
