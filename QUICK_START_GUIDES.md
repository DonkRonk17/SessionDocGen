# SessionDocGen Quick Start Guides

**Agent-Specific 5-Minute Setup Guides**

---

## Table of Contents

1. [ATLAS Quick Start](#atlas-quick-start-tool-builder)
2. [FORGE Quick Start](#forge-quick-start-coordinator)
3. [IRIS Quick Start](#iris-quick-start-frontend)
4. [NEXUS Quick Start](#nexus-quick-start-backend)
5. [BOLT Quick Start](#bolt-quick-start-mobile)
6. [CLIO Quick Start](#clio-quick-start-documentation)

---

## ATLAS Quick Start (Tool Builder)

### Installation (30 seconds)

```bash
cd /path/to/tools
git clone https://github.com/DonkRonk17/SessionDocGen.git
cd SessionDocGen
python sessiondocgen.py --help  # Verify installation
```

### First Use (2 minutes)

After completing a tool build:

```bash
# Generate session report
python sessiondocgen.py parse cursor_session.log \
    -n "ToolName v1.0 Build" \
    -o DEVELOPMENT_TRANSCRIPT.md
```

### Integration (2 minutes)

Add to your post-build workflow:

```python
from sessiondocgen import SessionDocGen

def document_tool_build(log_path, tool_name, test_count):
    gen = SessionDocGen()
    gen.session_name = f"{tool_name} Development"
    gen.load_log_file(log_path)
    
    # Add standard milestones
    gen.add_milestone("Core Complete", "Main script working", "major")
    gen.add_milestone("Tests Passing", f"{test_count} tests pass", "major")
    gen.add_milestone("Docs Complete", "All documentation ready", "minor")
    
    # Save to project folder
    gen.save_report(f"{tool_name}/DEVELOPMENT_TRANSCRIPT.md")
    
    return gen.get_summary()
```

### Key Commands for ATLAS

```bash
# Quick summary
python sessiondocgen.py summary session.log

# Full report
python sessiondocgen.py parse session.log -o report.md

# Tool stats
python sessiondocgen.py stats session.log
```

---

## FORGE Quick Start (Coordinator)

### Installation (30 seconds)

```bash
cd /path/to/tools
git clone https://github.com/DonkRonk17/SessionDocGen.git
```

### First Use (2 minutes)

Aggregate team sessions:

```bash
# Combine multiple agent logs
python sessiondocgen.py parse \
    atlas.log iris.log nexus.log bolt.log \
    -n "Daily Team Summary" \
    -o daily_summary.md
```

### Integration (2 minutes)

Daily team metrics collection:

```python
from sessiondocgen import SessionDocGen
import glob

def generate_daily_summary():
    gen = SessionDocGen()
    gen.session_name = f"Daily Summary - {date_str}"
    
    # Load all agent sessions
    for log in glob.glob("sessions/*.log"):
        gen.load_log_file(log)
    
    # Generate reports
    gen.save_report("daily_summary.md")
    gen.save_report("daily_data.json", format="json")
    
    return gen.get_summary()
```

### Key Commands for FORGE

```bash
# Team aggregate
python sessiondocgen.py parse sessions/*.log -n "Team Summary"

# JSON for analysis
python sessiondocgen.py parse *.log -f json -o team_data.json

# Quick team stats
python sessiondocgen.py stats sessions/*.log
```

---

## IRIS Quick Start (Frontend)

### Installation (30 seconds)

```bash
cd /path/to/tools
git clone https://github.com/DonkRonk17/SessionDocGen.git
```

### First Use (2 minutes)

Document an implementation session:

```bash
# With git diff for file changes
git diff HEAD~10 > changes.diff
python sessiondocgen.py parse session.log \
    --git-diff changes.diff \
    -n "Feature Implementation" \
    -o implementation_report.md
```

### Integration (2 minutes)

Track UI/UX decisions:

```python
from sessiondocgen import SessionDocGen

def document_implementation(log_path, feature_name):
    gen = SessionDocGen()
    gen.session_name = f"{feature_name} Implementation"
    gen.load_log_file(log_path)
    
    # Document architecture decisions
    gen.add_decision("Component structure", "architecture", "Reason...")
    gen.add_decision("State management", "architecture", "Reason...")
    
    # Save with timestamp
    gen.save_report(f"docs/{feature_name}_{date_str}.md")
    
    return gen.get_summary()
```

### Key Commands for IRIS

```bash
# With file changes
python sessiondocgen.py parse session.log --git-diff changes.diff

# Quick check during dev
python sessiondocgen.py summary session.log

# Track what changed
python sessiondocgen.py stats session.log
```

---

## NEXUS Quick Start (Backend)

### Installation (30 seconds)

```bash
cd /path/to/tools
git clone https://github.com/DonkRonk17/SessionDocGen.git
```

### First Use (2 minutes)

Document API development:

```bash
# Generate API session report
python sessiondocgen.py parse backend_session.log \
    -n "API v2 Development" \
    -o api_development.md
```

### Integration (2 minutes)

Track API decisions and test results:

```python
from sessiondocgen import SessionDocGen

def document_api_session(log_path, api_version, test_results):
    gen = SessionDocGen()
    gen.session_name = f"API v{api_version} Development"
    gen.load_log_file(log_path)
    
    # Document decisions
    gen.add_decision("REST endpoints", "architecture", "...")
    gen.add_decision("Auth strategy", "security", "...")
    
    # Test milestones
    gen.add_milestone("Unit Tests", f"{test_results['unit']} passing", "major")
    gen.add_milestone("Integration", f"{test_results['integration']} passing", "major")
    
    gen.save_report(f"api_v{api_version}_session.md")
    return gen.get_summary()
```

### Key Commands for NEXUS

```bash
# API session report
python sessiondocgen.py parse backend.log -n "API Session"

# JSON for CI/CD
python sessiondocgen.py parse backend.log -f json -o api_data.json

# Error analysis
python sessiondocgen.py stats backend.log
```

---

## BOLT Quick Start (Mobile)

### Installation (30 seconds)

```bash
cd /path/to/tools
git clone https://github.com/DonkRonk17/SessionDocGen.git
```

### First Use (2 minutes)

Document a build session:

```bash
# Generate build report
python sessiondocgen.py parse build_session.log \
    -n "Mobile Build v1.2.0" \
    -o build_report.md
```

### Integration (2 minutes)

Track builds and deployments:

```python
from sessiondocgen import SessionDocGen

def document_build(log_path, version, platforms):
    gen = SessionDocGen()
    gen.session_name = f"Mobile v{version} Build"
    gen.load_log_file(log_path)
    
    # Build milestones
    for platform in platforms:
        status = "complete" if platform['success'] else "failed"
        gen.add_milestone(
            f"{platform['name']} Build",
            status,
            "major" if platform['success'] else "critical"
        )
    
    gen.save_report(f"builds/v{version}_report.md")
    return gen.get_summary()
```

### Key Commands for BOLT

```bash
# Build session report
python sessiondocgen.py parse build.log -n "Build Session"

# Quick status check
python sessiondocgen.py summary build.log

# Error tracking
python sessiondocgen.py stats build.log
```

---

## CLIO Quick Start (Documentation)

### Installation (30 seconds)

```bash
cd /path/to/tools
git clone https://github.com/DonkRonk17/SessionDocGen.git
```

### First Use (2 minutes)

Extract knowledge from sessions:

```bash
# Generate JSON for analysis
python sessiondocgen.py parse any_session.log \
    -f json \
    -o session_data.json
```

### Integration (2 minutes)

Knowledge extraction pipeline:

```python
from sessiondocgen import SessionDocGen
import json

def extract_knowledge(log_path):
    gen = SessionDocGen()
    gen.load_log_file(log_path)
    
    report = json.loads(gen.generate_report("json"))
    
    # Extract learnings
    learnings = []
    
    # From decisions
    for dec in report["decisions"]:
        learnings.append({
            "type": "decision",
            "category": dec["category"],
            "content": dec["description"],
            "rationale": dec["rationale"]
        })
    
    # From solved errors
    for err in report["errors"]:
        if err["effective"]:
            learnings.append({
                "type": "solution",
                "category": err["error_type"],
                "problem": err["error_message"],
                "solution": err["solution"]
            })
    
    return learnings
```

### Key Commands for CLIO

```bash
# JSON for knowledge extraction
python sessiondocgen.py parse session.log -f json -o data.json

# Multiple sessions for pattern finding
python sessiondocgen.py parse sessions/*.log -f json -o all_data.json

# Stats for overview
python sessiondocgen.py stats sessions/*.log
```

---

## Universal Commands

Every agent should know these:

```bash
# Help
python sessiondocgen.py --help
python sessiondocgen.py parse --help

# Quick summary (no file output)
python sessiondocgen.py summary session.log

# Full markdown report
python sessiondocgen.py parse session.log -o report.md

# JSON for automation
python sessiondocgen.py parse session.log -f json -o data.json

# Tool statistics
python sessiondocgen.py stats session.log

# Multiple logs combined
python sessiondocgen.py parse *.log -n "Combined" -o combined.md

# Named session
python sessiondocgen.py parse session.log -n "Feature X" -o report.md
```

---

## Common Patterns

### Post-Session Documentation

```bash
# Standard post-session workflow
python sessiondocgen.py parse session.log -n "$(date +%Y-%m-%d) Session" -o "sessions/$(date +%Y-%m-%d).md"
```

### CI/CD Integration

```bash
# In CI pipeline
python sessiondocgen.py parse "$LOG_FILE" -f json -o "artifacts/session_$BUILD_NUMBER.json"
```

### Memory Core Archival

```bash
# Archive to Memory Core
python sessiondocgen.py parse session.log -o "D:/BEACON_HQ/MEMORY_CORE_V2/02_SESSION_LOGS/session_$(date +%Y-%m-%d).md"
```

---

*SessionDocGen Quick Start Guides v1.0*
*Built by ATLAS | Requested by IRIS*
