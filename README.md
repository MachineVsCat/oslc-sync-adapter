# oslc-sync-adapter

OSLC-based synchronization adapter for IBM ELM toolchain integration.
Connects DOORS Next, EWM, ETM with external systems (Jira, ServiceNow)
using Open Services for Lifecycle Collaboration protocols.

## Features

- Bidirectional sync between DOORS Next and Jira
- EWM work item synchronization
- ETM test case linking and execution tracking
- ServiceNow incident correlation
- SPARQL reporting via LQE for traceability matrices
- DO-178C and ISO 26262 compliance reporting
- Suspect link detection and resolution
- GCM (Global Configuration Management) support
- DOORS Classic to DOORS Next migration utility
- Health monitoring for all connected systems

## Setup

```bash
pip install -r requirements.txt
cp config.yaml config.local.yaml
# Edit config.local.yaml with your Jazz server details
export ELM_USER=your_username
export ELM_PASS=your_password
```

## Usage

```bash
# Run synchronization
python cli.py --config config.yaml sync

# Run health checks
python cli.py --config config.yaml health

# Run with verbose logging
python cli.py -v --config config.yaml sync

# Migrate from DOORS Classic
python scripts/migrate_doors_classic.py \
    --csv export.csv \
    --server https://elm.example.com/jts \
    --user admin --password pass \
    --project https://elm.example.com/rm/process/project-areas/MyProject

# Validate process templates
python scripts/validate_process_template.py \
    --server https://elm.example.com/jts \
    --user admin --password pass \
    --project https://elm.example.com/ccm/process/project-areas/MyProject
```

## Configuration

See `config.yaml` for full configuration reference. Key sections:

- `jazz_server` - JTS connection settings
- `doors_next` - DOORS Next project area and catalog
- `ewm` - EWM project area and work item types
- `etm` - ETM project area
- `jira` - Jira Cloud/Server connection
- `sync_rules` - Field mappings, direction, and conflict resolution
- `gcm` - Global Configuration Management settings

Environment variables are supported using `${VAR}` syntax.

## Testing

```bash
python -m pytest tests/
```

## License

MIT
