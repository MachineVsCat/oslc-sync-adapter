"""Core synchronization engine for OSLC resource sync."""

import logging
from datetime import datetime

log = logging.getLogger(__name__)


class SyncConflict(Exception):
    def __init__(self, source_id, target_id, field):
        self.source_id = source_id
        self.target_id = target_id
        self.field = field
        super().__init__(f"Conflict on {field}: {source_id} <-> {target_id}")


class SyncEngine:
    def __init__(self, config):
        self.config = config
        self.sync_log = []

    def run_sync(self, source_connector, target_connector, rule):
        """Execute sync based on a mapping rule."""
        mapping = rule["mapping"]
        direction = rule.get("direction", "source_to_target")
        source_items = source_connector.get_requirements()
        log.info(f"Fetched {len(source_items)} items from source")

        for item in source_items:
            mapped = self._apply_mapping(item, mapping)
            target_id = self._find_target(target_connector, mapped)

            if target_id:
                target_connector.update_item(target_id, mapped)
                self.sync_log.append({
                    "action": "update",
                    "source": item.get("dcterms:identifier"),
                    "target": target_id,
                    "timestamp": datetime.utcnow().isoformat(),
                })
            else:
                new_id = target_connector.create_item(mapped)
                self.sync_log.append({
                    "action": "create",
                    "source": item.get("dcterms:identifier"),
                    "target": new_id,
                    "timestamp": datetime.utcnow().isoformat(),
                })

        log.info(f"Sync complete: {len(self.sync_log)} operations")
        return self.sync_log

    def _apply_mapping(self, item, mapping):
        """Map source fields to target fields."""
        result = {}
        for src_field, tgt_field in mapping.items():
            if src_field in item:
                result[tgt_field] = item[src_field]
        return result

    def _find_target(self, connector, mapped_item):
        """Look up existing target item by mapped identifier."""
        return None
