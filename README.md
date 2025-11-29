# oslc-sync-adapter

OSLC-based synchronization adapter for IBM ELM toolchain integration.
Connects DOORS Next, EWM, ETM with external systems (Jira, ServiceNow)
using Open Services for Lifecycle Collaboration protocols.

## Setup

```bash
pip install -r requirements.txt
cp config.yaml.example config.yaml
# Edit config.yaml with your Jazz server details
python cli.py --config config.yaml
```

## Components

- `src/oslc_client.py` - Base OSLC/REST client with Jazz authentication
- `src/sync_engine.py` - Bidirectional sync logic and conflict resolution
- `src/doors_connector.py` - DOORS Next requirements connector
- `src/jira_connector.py` - Jira issue sync via REST API

## License

MIT
