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
        self.conflicts = []

    def run_sync(self, source_connector, target_connector, rule):
        """Execute sync based on a mapping rule."""
        mapping = rule["mapping"]
        direction = rule.get("direction", "source_to_target")
        conflict_mode = rule.get("conflict_resolution", "source_wins")
        try:
            source_items = source_connector.get_requirements()
        except Exception as e:
            log.error(f"Failed to fetch source items: {e}")
            return self.sync_log
        log.info(f"Fetched {len(source_items)} items from source")

        for item in source_items:
            mapped = self._apply_mapping(item, mapping)
            target_id = self._find_target(target_connector, mapped)

            if target_id:
                if direction == "bidirectional":
                    target_data = target_connector.get_issue(target_id)
                    conflicts = self._detect_conflicts(mapped, target_data, mapping)
                    if conflicts:
                        resolved = self._resolve_conflicts(
                            conflicts, mapped, target_data, conflict_mode
                        )
                        mapped = resolved
                        self.conflicts.extend(conflicts)

                target_connector.update_item(target_id, mapped)
                self.sync_log.append({
                    "action": "update",
                    "source": item.get("dcterms:identifier"),
                    "target": target_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "conflicts": len([c for c in self.conflicts if c["target"] == target_id]),
                })
            else:
                new_id = target_connector.create_item(mapped)
                self.sync_log.append({
                    "action": "create",
                    "source": item.get("dcterms:identifier"),
                    "target": new_id,
                    "timestamp": datetime.utcnow().isoformat(),
                })

        log.info(f"Sync complete: {len(self.sync_log)} ops, {len(self.conflicts)} conflicts")
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
        if hasattr(connector, "find_by_custom_field"):
            identifier = mapped_item.get("customfield_10001")
            if identifier:
                return connector.find_by_custom_field("ELM Requirement ID", identifier)
        return None

    def _detect_conflicts(self, source_data, target_data, mapping):
        """Detect field-level conflicts between source and target."""
        conflicts = []
        target_fields = target_data.get("fields", target_data)
        for src_field, tgt_field in mapping.items():
            src_val = source_data.get(tgt_field)
            tgt_val = target_fields.get(tgt_field)
            if src_val and tgt_val and src_val != tgt_val:
                conflicts.append({
                    "field": tgt_field,
                    "source_value": src_val,
                    "target_value": tgt_val,
                    "target": target_data.get("key", ""),
                })
        return conflicts

    def _resolve_conflicts(self, conflicts, source_data, target_data, mode):
        """Resolve conflicts based on configured strategy."""
        resolved = dict(source_data)
        if mode == "target_wins":
            target_fields = target_data.get("fields", target_data)
            for conflict in conflicts:
                resolved[conflict["field"]] = conflict["target_value"]
        elif mode == "newest_wins":
            log.warning("newest_wins not fully implemented, falling back to source_wins")
        return resolved
