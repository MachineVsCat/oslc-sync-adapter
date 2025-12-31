"""Core synchronization engine for OSLC resource sync."""

import logging
from datetime import datetime
from abc import ABC, abstractmethod

log = logging.getLogger(__name__)


class SyncConflict(Exception):
    def __init__(self, source_id, target_id, field):
        self.source_id = source_id
        self.target_id = target_id
        self.field = field
        super().__init__(f"Conflict on {field}: {source_id} <-> {target_id}")


class BaseConnectorAdapter(ABC):
    """Abstract adapter interface for sync connectors."""

    @abstractmethod
    def fetch_items(self, since=None):
        pass

    @abstractmethod
    def find_item(self, identifier):
        pass

    @abstractmethod
    def create_item(self, fields):
        pass

    @abstractmethod
    def update_item(self, item_id, fields):
        pass


class DoorsAdapter(BaseConnectorAdapter):
    def __init__(self, connector):
        self.connector = connector

    def fetch_items(self, since=None):
        return self.connector.get_requirements()

    def find_item(self, identifier):
        return self.connector.get_requirement_by_id(identifier)

    def create_item(self, fields):
        log.info(f"Creating DOORS Next requirement: {fields}")
        return None

    def update_item(self, item_id, fields):
        log.info(f"Updating DOORS Next requirement: {item_id}")


class JiraAdapter(BaseConnectorAdapter):
    def __init__(self, connector):
        self.connector = connector

    def fetch_items(self, since=None):
        return self.connector.get_issues()

    def find_item(self, identifier):
        return self.connector.find_by_custom_field("ELM Requirement ID", identifier)

    def create_item(self, fields):
        return self.connector.create_item(fields)

    def update_item(self, item_id, fields):
        self.connector.update_item(item_id, fields)


class SyncEngine:
    def __init__(self, config):
        self.config = config
        self.sync_log = []
        self.conflicts = []

    def run_sync(self, source_adapter, target_adapter, rule):
        """Execute sync between two adapter-wrapped connectors."""
        mapping = rule["mapping"]
        direction = rule.get("direction", "source_to_target")
        conflict_mode = rule.get("conflict_resolution", "source_wins")

        try:
            source_items = source_adapter.fetch_items()
        except Exception as e:
            log.error(f"Failed to fetch source items: {e}")
            return self.sync_log

        log.info(f"Fetched {len(source_items)} items from source")

        for item in source_items:
            mapped = self._apply_mapping(item, mapping)
            identifier = item.get("dcterms:identifier")
            target_item = target_adapter.find_item(identifier) if identifier else None

            if target_item:
                if direction == "bidirectional":
                    conflicts = self._detect_conflicts(mapped, target_item, mapping)
                    if conflicts:
                        mapped = self._resolve_conflicts(
                            conflicts, mapped, target_item, conflict_mode
                        )
                        self.conflicts.extend(conflicts)

                target_adapter.update_item(target_item, mapped)
                self.sync_log.append({
                    "action": "update",
                    "source": identifier,
                    "target": target_item,
                    "timestamp": datetime.utcnow().isoformat(),
                })
            else:
                new_id = target_adapter.create_item(mapped)
                self.sync_log.append({
                    "action": "create",
                    "source": identifier,
                    "target": new_id,
                    "timestamp": datetime.utcnow().isoformat(),
                })

        log.info(f"Sync complete: {len(self.sync_log)} ops, {len(self.conflicts)} conflicts")
        return self.sync_log

    def _apply_mapping(self, item, mapping):
        result = {}
        for src_field, tgt_field in mapping.items():
            if src_field in item:
                result[tgt_field] = item[src_field]
        return result

    def _detect_conflicts(self, source_data, target_data, mapping):
        conflicts = []
        target_fields = target_data if isinstance(target_data, dict) else {}
        for src_field, tgt_field in mapping.items():
            src_val = source_data.get(tgt_field)
            tgt_val = target_fields.get(tgt_field)
            if src_val and tgt_val and src_val != tgt_val:
                conflicts.append({
                    "field": tgt_field,
                    "source_value": src_val,
                    "target_value": tgt_val,
                })
        return conflicts

    def _resolve_conflicts(self, conflicts, source_data, target_data, mode):
        resolved = dict(source_data)
        if mode == "target_wins":
            target_fields = target_data if isinstance(target_data, dict) else {}
            for conflict in conflicts:
                resolved[conflict["field"]] = conflict["target_value"]
        elif mode == "newest_wins":
            log.warning("newest_wins not fully implemented, falling back to source_wins")
        return resolved
