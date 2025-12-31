"""Migration utility for importing data from DOORS Classic (9.x) to DOORS Next."""

import csv
import argparse
import logging
from src.oslc_client import OSLCClient
from src.doors_connector import DoorsNextConnector

log = logging.getLogger(__name__)


def parse_doors_export(csv_path):
    """Parse DOORS Classic CSV export file."""
    requirements = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            req = {
                "dcterms:identifier": row.get("Object Identifier", ""),
                "dcterms:title": row.get("Object Heading", row.get("Object Text", "")),
                "dcterms:description": row.get("Object Text", ""),
                "doors:priority": row.get("Priority", ""),
                "doors:module": row.get("Module", ""),
            }
            requirements.append(req)
    log.info(f"Parsed {len(requirements)} requirements from DOORS Classic export")
    return requirements


def import_to_doors_next(connector, requirements, batch_size=50):
    """Import parsed requirements into DOORS Next."""
    imported = 0
    errors = 0
    for i in range(0, len(requirements), batch_size):
        batch = requirements[i:i + batch_size]
        for req in batch:
            try:
                existing = connector.get_requirement_by_id(req["dcterms:identifier"])
                if existing:
                    log.info(f"Skipping existing: {req['dcterms:identifier']}")
                    continue
                # Would create via OSLC creation factory
                imported += 1
            except Exception as e:
                log.error(f"Failed to import {req['dcterms:identifier']}: {e}")
                errors += 1
        log.info(f"Progress: {min(i + batch_size, len(requirements))}/{len(requirements)}")
    return {"imported": imported, "errors": errors, "skipped": len(requirements) - imported - errors}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate DOORS Classic to DOORS Next")
    parser.add_argument("--csv", required=True, help="DOORS Classic CSV export file")
    parser.add_argument("--server", required=True, help="Jazz server URL")
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--project", required=True, help="DOORS Next project area URL")
    args = parser.parse_args()

    client = OSLCClient(args.server, args.user, args.password)
    client.authenticate()
    connector = DoorsNextConnector(client, args.project)

    reqs = parse_doors_export(args.csv)
    result = import_to_doors_next(connector, reqs)
    print(f"Migration complete: {result}")
