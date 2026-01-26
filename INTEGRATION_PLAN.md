# SessionDocGen Integration Plan

**How SessionDocGen Integrates with Team Brain Agents and Tools**

---

## Overview

SessionDocGen automatically generates session documentation from tool usage, decisions, and outcomes. This document outlines how each Team Brain agent can integrate and benefit from SessionDocGen.

---

## Integration Goals

1. **Reduce Documentation Burden** - Automate 90% of session documentation
2. **Standardize Reports** - Consistent format across all agents and sessions
3. **Enable Analysis** - JSON output for pattern detection and metrics tracking
4. **Support Handoffs** - Clear session summaries for agent transitions
5. **Archive Knowledge** - Preserve session learnings in Memory Core

---

## Agent-Specific Integration

### ATLAS (Tool Builder)

**Primary Use:** Document tool development sessions

```python
from sessiondocgen import SessionDocGen

# After completing a tool build
gen = SessionDocGen()
gen.session_name = "ToolName Development"
gen.load_log_file("cursor_session.log")

# Add milestones
gen.add_milestone("Core Complete", "Main functionality working", "major")
gen.add_milestone("Tests Passing", f"{test_count} tests pass", "major")
gen.add_milestone("Docs Complete", "README, EXAMPLES ready", "minor")

# Generate for Memory Core
gen.save_report(
    "D:/BEACON_HQ/MEMORY_CORE_V2/02_SESSION_LOGS/toolbuild_session.md",
    format="markdown"
)
```

**Integration Points:**
- Post-build documentation generation
- Quality checklist verification
- Memory Core archival

---

### FORGE (Coordinator)

**Primary Use:** Track coordination sessions, aggregate team metrics

```python
from sessiondocgen import SessionDocGen
import json

# Combine all agent session reports for daily summary
gen = SessionDocGen()
gen.session_name = "Daily Team Summary"

# Load each agent's session
for agent_log in ["atlas.log", "iris.log", "nexus.log", "bolt.log"]:
    gen.load_log_file(f"sessions/{agent_log}")

# Generate team metrics
summary = gen.get_summary()
daily_report = {
    "date": "2026-01-25",
    "total_tool_calls": summary["tool_calls"],
    "files_modified": summary["files_touched"],
    "errors_total": summary["errors"],
    "errors_resolved": summary["errors_resolved"]
}

# Save for analysis
gen.save_report("daily_summary.json", format="json")
```

**Integration Points:**
- Daily/weekly team summaries
- Coordination metrics tracking
- Resource allocation insights

---

### IRIS (Frontend/Implementation)

**Primary Use:** Document development sessions, track error patterns

```python
from sessiondocgen import SessionDocGen

# After implementation session
gen = SessionDocGen()
gen.session_name = "BCH Desktop Implementation"
gen.load_log_file("session.log")

# Add implementation decisions
gen.add_decision(
    "Use Tauri over Electron",
    "architecture",
    "Smaller binary, better performance"
)
gen.add_decision(
    "WebSocket for real-time",
    "architecture", 
    "Native browser support, simple protocol"
)

# Track build errors
for error in build_errors:
    gen.add_error_solution(
        error["message"],
        error["type"],
        error["solution"],
        error["resolved"]
    )

# Save session summary
gen.save_report("implementation_session.md")
```

**Integration Points:**
- Implementation documentation
- Error->Solution pattern building
- Architecture decision records

---

### NEXUS (Backend/API)

**Primary Use:** Document API development, track test results

```python
from sessiondocgen import SessionDocGen

gen = SessionDocGen()
gen.session_name = "API Endpoint Development"
gen.load_log_file("backend_session.log")

# Document API decisions
gen.add_decision("REST over GraphQL", "architecture", "Simpler for current needs")
gen.add_decision("JWT auth", "security", "Stateless, scalable")

# Add test milestones
gen.add_milestone("Unit Tests", "45/45 passing", "major")
gen.add_milestone("Integration Tests", "12/12 passing", "major")
gen.add_milestone("Load Test", "1000 req/s achieved", "major")

gen.save_report("api_session.md")
```

**Integration Points:**
- API development tracking
- Test result documentation
- Performance metrics logging

---

### BOLT (Mobile/Execution)

**Primary Use:** Document mobile builds, track deployment steps

```python
from sessiondocgen import SessionDocGen

gen = SessionDocGen()
gen.session_name = "Mobile Build Session"
gen.load_log_file("mobile_build.log")

# Add build milestones
gen.add_milestone("iOS Build", "Archive created", "major")
gen.add_milestone("Android Build", "APK signed", "major")
gen.add_milestone("Store Upload", "Both platforms submitted", "critical")

# Document build issues
for issue in build_issues:
    gen.add_error_solution(
        issue["error"],
        "build",
        issue["fix"],
        True
    )

gen.save_report("mobile_build_report.md")
```

**Integration Points:**
- Build process documentation
- Deployment checklists
- Release notes generation

---

### CLIO (Documentation/Knowledge)

**Primary Use:** Generate and maintain documentation, knowledge extraction

```python
from sessiondocgen import SessionDocGen
import json

# Analyze session for knowledge extraction
gen = SessionDocGen()
gen.load_log_file("any_session.log")

report = json.loads(gen.generate_report("json"))

# Extract learnings
learnings = []
for decision in report["decisions"]:
    learnings.append({
        "topic": decision["category"],
        "decision": decision["description"],
        "rationale": decision["rationale"]
    })

for error in report["errors"]:
    if error["effective"]:
        learnings.append({
            "topic": error["error_type"],
            "problem": error["error_message"][:100],
            "solution": error["solution"]
        })

# Store in knowledge base
save_to_memory_core(learnings)
```

**Integration Points:**
- Knowledge extraction from sessions
- Documentation generation
- Pattern learning and sharing

---

## Tool Integration

### With ContextPreserver

```python
from sessiondocgen import SessionDocGen
from contextpreserver import ContextPreserver

# Generate session summary
gen = SessionDocGen()
gen.load_log_file("session.log")
summary = gen.get_summary()

# Preserve key context
preserver = ContextPreserver()
preserver.add_event(
    event_type="SESSION_COMPLETE",
    description=f"Session '{gen.session_name}' completed",
    metadata=summary,
    priority="MEDIUM"
)
```

### With PostMortem

```python
from sessiondocgen import SessionDocGen

# SessionDocGen generates the data
gen = SessionDocGen()
gen.load_log_file("session.log")
gen.save_report("session_data.json", format="json")

# PostMortem analyzes it
from postmortem import PostMortem
pm = PostMortem()
pm.load_session_data("session_data.json")
analysis = pm.analyze()
```

### With SynapseLink

```python
from sessiondocgen import SessionDocGen
from synapselink import quick_send

gen = SessionDocGen()
gen.load_log_file("session.log")
summary = gen.get_summary()

# Notify team
quick_send(
    "FORGE,CLIO,NEXUS,BOLT",
    "Session Complete",
    f"Session: {gen.session_name}\n"
    f"Tools: {summary['tool_calls']}\n"
    f"Files: {summary['files_touched']}\n"
    f"Errors: {summary['errors']} ({summary['errors_resolved']} resolved)\n"
    f"Milestones: {summary['milestones']}"
)
```

### With TeamCoherenceMonitor

```python
from sessiondocgen import SessionDocGen

gen = SessionDocGen()
gen.load_log_file("session.log")
metrics = gen.calculate_metrics()

# Feed into coherence monitoring
coherence_data = {
    "session_duration": metrics.duration_minutes,
    "tool_success_rate": metrics.successful_tool_calls / metrics.total_tool_calls,
    "error_resolution_rate": metrics.errors_resolved / max(metrics.errors_encountered, 1)
}
```

---

## Data Flow Diagram

```
Session Logs ─────────────────────────────────────────┐
                                                      │
Git Diffs ────────────────────────────────────────────┤
                                                      │
Manual Annotations ───────────────────────────────────┤
                                                      ▼
                                            ┌─────────────────┐
                                            │  SessionDocGen  │
                                            └────────┬────────┘
                                                     │
                    ┌────────────┬──────────────────┼──────────────────┬────────────┐
                    ▼            ▼                  ▼                  ▼            ▼
              ┌──────────┐ ┌──────────┐      ┌──────────┐      ┌──────────┐  ┌──────────┐
              │ Markdown │ │   JSON   │      │   Text   │      │ Summary  │  │ Metrics  │
              │  Report  │ │  Report  │      │  Report  │      │   Dict   │  │  Object  │
              └────┬─────┘ └────┬─────┘      └────┬─────┘      └────┬─────┘  └────┬─────┘
                   │            │                 │                 │             │
                   ▼            ▼                 ▼                 ▼             ▼
              ┌──────────┐ ┌──────────┐      ┌──────────┐      ┌──────────┐  ┌──────────┐
              │  GitHub  │ │ Database │      │  Email   │      │ Synapse  │  │ Coherence│
              │  README  │ │ Storage  │      │  Alert   │      │  Notify  │  │ Monitor  │
              └──────────┘ └──────────┘      └──────────┘      └──────────┘  └──────────┘
```

---

## Automation Workflows

### Post-Session Auto-Documentation

```bash
#!/bin/bash
# Run after every session

# Generate report
python sessiondocgen.py parse "$SESSION_LOG" \
    -n "$SESSION_NAME" \
    -f markdown \
    -o "reports/${SESSION_NAME}.md"

# Generate JSON for analysis
python sessiondocgen.py parse "$SESSION_LOG" \
    -f json \
    -o "data/${SESSION_NAME}.json"

# Copy to Memory Core
cp "reports/${SESSION_NAME}.md" \
    "D:/BEACON_HQ/MEMORY_CORE_V2/02_SESSION_LOGS/"
```

### Weekly Team Summary

```python
# Run weekly
from sessiondocgen import SessionDocGen
import glob

gen = SessionDocGen()
gen.session_name = f"Week {week_number} Summary"

for log in glob.glob("sessions/week_*/*.log"):
    gen.load_log_file(log)

gen.save_report(f"weekly/week_{week_number}.md")
gen.save_report(f"weekly/week_{week_number}.json", format="json")
```

---

## Memory Core Integration

### Session Log Storage

```
D:\BEACON_HQ\MEMORY_CORE_V2\
├── 02_SESSION_LOGS\
│   ├── HOLYGRAIL_SessionDocGen_2026-01-25.md  <-- Session bookmark
│   ├── session_summary_2026-01-25.md           <-- Generated report
│   └── session_data_2026-01-25.json            <-- JSON for analysis
```

### Automated Archival

```python
from sessiondocgen import SessionDocGen
from datetime import datetime

def archive_session(log_path, session_name):
    gen = SessionDocGen()
    gen.session_name = session_name
    gen.load_log_file(log_path)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Archive to Memory Core
    gen.save_report(
        f"D:/BEACON_HQ/MEMORY_CORE_V2/02_SESSION_LOGS/{session_name}_{date_str}.md",
        format="markdown"
    )
    
    return gen.get_summary()
```

---

## Best Practices

1. **Run after every session** - Capture context while fresh
2. **Add milestones explicitly** - Auto-detection misses some
3. **Use consistent naming** - Enables trend analysis
4. **Store JSON for analysis** - Markdown for reading, JSON for processing
5. **Integrate with Synapse** - Keep team informed of completions

---

*SessionDocGen Integration Plan v1.0*
*Built by ATLAS | Requested by IRIS*
*January 25, 2026*
