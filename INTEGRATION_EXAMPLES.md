# SessionDocGen Integration Examples

**Copy-Paste Ready Code Examples for Tool Integration**

---

## Table of Contents

1. [Basic Integration](#1-basic-integration)
2. [With ContextPreserver](#2-with-contextpreserver)
3. [With PostMortem](#3-with-postmortem)
4. [With SynapseLink](#4-with-synapselink)
5. [With TeamCoherenceMonitor](#5-with-teamcoherencemonitor)
6. [With ContextDecayMeter](#6-with-contextdecaymeter)
7. [CI/CD Pipeline](#7-cicd-pipeline)
8. [Memory Core Archival](#8-memory-core-archival)
9. [Error Pattern Database](#9-error-pattern-database)
10. [Team Dashboard](#10-team-dashboard)

---

## 1. Basic Integration

### Simple Report Generation

```python
from sessiondocgen import SessionDocGen

# Initialize and configure
gen = SessionDocGen()
gen.session_name = "Feature Implementation"

# Load log file
gen.load_log_file("session.log")

# Generate markdown report
report = gen.generate_report("markdown")
print(report)

# Or save directly
gen.save_report("report.md")
```

### With Manual Annotations

```python
from sessiondocgen import SessionDocGen
from datetime import datetime

gen = SessionDocGen()
gen.session_name = "API Development"
gen.start_time = datetime(2026, 1, 25, 10, 0, 0)
gen.end_time = datetime(2026, 1, 25, 14, 30, 0)

# Load log
gen.load_log_file("session.log")

# Add milestones
gen.add_milestone("Setup Complete", "Environment ready", "minor")
gen.add_milestone("Core API Done", "All endpoints working", "major")
gen.add_milestone("Tests Passing", "100% coverage", "major")

# Add decisions
gen.add_decision(
    "Use FastAPI over Flask",
    category="architecture",
    rationale="Better async support, auto docs"
)

# Generate report
gen.save_report("api_session.md")
```

---

## 2. With ContextPreserver

### Store Session Summary in Context

```python
from sessiondocgen import SessionDocGen
from contextpreserver import ContextPreserver

def document_and_preserve(log_path: str, session_name: str):
    # Generate session documentation
    gen = SessionDocGen()
    gen.session_name = session_name
    gen.load_log_file(log_path)
    
    summary = gen.get_summary()
    
    # Preserve in context
    preserver = ContextPreserver()
    
    # Add session completion event
    preserver.add_event(
        event_type="SESSION_COMPLETE",
        description=f"Session '{session_name}' completed successfully",
        metadata={
            "tool_calls": summary["tool_calls"],
            "files_touched": summary["files_touched"],
            "errors_resolved": f"{summary['errors_resolved']}/{summary['errors']}",
            "milestones": summary["milestones"]
        },
        priority="MEDIUM"
    )
    
    # Add key decisions
    for decision in gen.decisions:
        preserver.add_event(
            event_type="DECISION",
            description=f"[{decision.category.upper()}] {decision.description}",
            metadata={"rationale": decision.rationale},
            priority="HIGH"
        )
    
    # Save both reports
    gen.save_report(f"{session_name}_report.md")
    preserver.checkpoint()
    
    return summary

# Usage
summary = document_and_preserve("session.log", "Feature X")
print(f"Documented {summary['tool_calls']} tool calls")
```

---

## 3. With PostMortem

### Feed Session Data to PostMortem Analysis

```python
from sessiondocgen import SessionDocGen
import json

def session_to_postmortem(log_path: str, session_name: str):
    # Generate session data
    gen = SessionDocGen()
    gen.session_name = session_name
    gen.load_log_file(log_path)
    
    # Export JSON for PostMortem
    json_report = gen.generate_report("json")
    
    # Save for PostMortem consumption
    with open("session_data.json", "w") as f:
        f.write(json_report)
    
    # PostMortem can now analyze
    from postmortem import PostMortem
    
    pm = PostMortem()
    pm.load_session_data("session_data.json")
    
    analysis = pm.analyze()
    
    return {
        "session_summary": gen.get_summary(),
        "postmortem_analysis": analysis
    }

# Usage
results = session_to_postmortem("session.log", "Feature Development")
print(f"Errors analyzed: {results['session_summary']['errors']}")
```

---

## 4. With SynapseLink

### Notify Team of Session Completion

```python
from sessiondocgen import SessionDocGen
from synapselink import quick_send

def document_and_notify(log_path: str, session_name: str, recipients: str = "FORGE,CLIO"):
    # Generate documentation
    gen = SessionDocGen()
    gen.session_name = session_name
    gen.load_log_file(log_path)
    
    summary = gen.get_summary()
    
    # Save reports
    gen.save_report(f"{session_name}.md")
    gen.save_report(f"{session_name}.json", format="json")
    
    # Notify via Synapse
    message = f"""Session Complete: {session_name}

METRICS:
- Duration: {summary['duration_minutes']:.1f} minutes
- Tool Calls: {summary['tool_calls']}
- Files Modified: {summary['files_touched']}
- Errors: {summary['errors']} ({summary['errors_resolved']} resolved)
- Milestones: {summary['milestones']}

Reports saved to:
- {session_name}.md
- {session_name}.json

Ready for review."""

    quick_send(recipients, f"Session Complete: {session_name}", message)
    
    return summary

# Usage
summary = document_and_notify("session.log", "ToolName_v1.0", "FORGE,CLIO,NEXUS,BOLT")
```

---

## 5. With TeamCoherenceMonitor

### Feed Session Metrics to Coherence Tracking

```python
from sessiondocgen import SessionDocGen
from teamcoherencemonitor import TeamCoherenceMonitor

def session_coherence_metrics(log_path: str, agent_id: str):
    # Generate session metrics
    gen = SessionDocGen()
    gen.load_log_file(log_path)
    metrics = gen.calculate_metrics()
    
    # Calculate coherence indicators
    tool_success_rate = (
        metrics.successful_tool_calls / max(metrics.total_tool_calls, 1)
    )
    error_resolution_rate = (
        metrics.errors_resolved / max(metrics.errors_encountered, 1)
    )
    
    # Feed to coherence monitor
    monitor = TeamCoherenceMonitor()
    
    monitor.record_agent_metrics(
        agent_id=agent_id,
        metrics={
            "session_duration": metrics.duration_minutes,
            "tool_success_rate": tool_success_rate,
            "error_resolution_rate": error_resolution_rate,
            "files_touched": metrics.unique_files_touched,
            "decisions_made": metrics.decisions_made
        }
    )
    
    # Get coherence score
    coherence = monitor.get_coherence_score()
    
    return {
        "session_metrics": metrics.to_dict(),
        "coherence_score": coherence
    }

# Usage
results = session_coherence_metrics("session.log", "ATLAS")
print(f"Coherence Score: {results['coherence_score']}")
```

---

## 6. With ContextDecayMeter

### Correlate Session Complexity with Context Decay

```python
from sessiondocgen import SessionDocGen
from contextdecaymeter import ContextDecayMeter

def analyze_session_context_decay(log_path: str):
    # Generate session metrics
    gen = SessionDocGen()
    gen.load_log_file(log_path)
    metrics = gen.calculate_metrics()
    
    # Analyze context decay
    decay_meter = ContextDecayMeter()
    decay_meter.load_conversation_log(log_path)
    decay_analysis = decay_meter.analyze()
    
    # Correlate findings
    correlation = {
        "session_duration": metrics.duration_minutes,
        "tool_call_count": metrics.total_tool_calls,
        "decay_rate": decay_analysis["decay_rate"],
        "checkpoint_recommendations": decay_analysis["checkpoints"],
        "correlation": {
            "high_velocity_decay": (
                metrics.total_tool_calls > 50 and 
                decay_analysis["decay_rate"] > 0.3
            ),
            "recommended_breaks": len(decay_analysis["checkpoints"])
        }
    }
    
    return correlation

# Usage
analysis = analyze_session_context_decay("long_session.log")
if analysis["correlation"]["high_velocity_decay"]:
    print("Warning: High tool velocity correlates with context decay")
```

---

## 7. CI/CD Pipeline

### GitHub Actions Integration

```yaml
# .github/workflows/document-session.yml
name: Document Session

on:
  workflow_dispatch:
    inputs:
      session_log:
        description: 'Path to session log'
        required: true
      session_name:
        description: 'Session name'
        required: true

jobs:
  document:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Generate Session Report
        run: |
          python sessiondocgen.py parse "${{ inputs.session_log }}" \
            -n "${{ inputs.session_name }}" \
            -f markdown \
            -o "reports/${{ inputs.session_name }}.md"
          
          python sessiondocgen.py parse "${{ inputs.session_log }}" \
            -f json \
            -o "reports/${{ inputs.session_name }}.json"
      
      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: session-reports
          path: reports/
```

### Python CI Script

```python
#!/usr/bin/env python3
"""CI/CD session documentation script."""

import os
import sys
from sessiondocgen import SessionDocGen

def ci_document_session():
    log_path = os.environ.get("SESSION_LOG", "session.log")
    session_name = os.environ.get("SESSION_NAME", f"Build_{os.environ.get('BUILD_NUMBER', 'unknown')}")
    output_dir = os.environ.get("OUTPUT_DIR", "artifacts")
    
    os.makedirs(output_dir, exist_ok=True)
    
    gen = SessionDocGen()
    gen.session_name = session_name
    gen.load_log_file(log_path)
    
    # Generate reports
    gen.save_report(f"{output_dir}/{session_name}.md", format="markdown")
    gen.save_report(f"{output_dir}/{session_name}.json", format="json")
    
    # Output summary for CI
    summary = gen.get_summary()
    print(f"::set-output name=tool_calls::{summary['tool_calls']}")
    print(f"::set-output name=errors::{summary['errors']}")
    print(f"::set-output name=errors_resolved::{summary['errors_resolved']}")
    
    # Fail if unresolved errors
    unresolved = summary['errors'] - summary['errors_resolved']
    if unresolved > 0:
        print(f"::warning::Session has {unresolved} unresolved errors")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(ci_document_session())
```

---

## 8. Memory Core Archival

### Auto-Archive to Memory Core

```python
from sessiondocgen import SessionDocGen
from datetime import datetime
import os
import shutil

MEMORY_CORE_PATH = "D:/BEACON_HQ/MEMORY_CORE_V2/02_SESSION_LOGS"

def archive_to_memory_core(log_path: str, session_name: str):
    gen = SessionDocGen()
    gen.session_name = session_name
    gen.load_log_file(log_path)
    
    # Create dated filename
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_name = session_name.replace(" ", "_").replace("/", "-")
    
    # Generate reports
    md_path = f"{MEMORY_CORE_PATH}/{safe_name}_{date_str}.md"
    json_path = f"{MEMORY_CORE_PATH}/{safe_name}_{date_str}.json"
    
    gen.save_report(md_path, format="markdown")
    gen.save_report(json_path, format="json")
    
    # Create session bookmark
    bookmark_content = f"""# Session Bookmark: {session_name}

**Date:** {date_str}
**Archived:** {datetime.now().isoformat()}

## Summary
{gen.get_summary()}

## Reports
- Markdown: {md_path}
- JSON: {json_path}

## Quick Stats
- Tool Calls: {gen.metrics.total_tool_calls}
- Files Modified: {gen.metrics.unique_files_touched}
- Errors: {gen.metrics.errors_encountered} ({gen.metrics.errors_resolved} resolved)
"""
    
    bookmark_path = f"{MEMORY_CORE_PATH}/BOOKMARK_{safe_name}_{date_str}.md"
    with open(bookmark_path, 'w') as f:
        f.write(bookmark_content)
    
    return {
        "markdown": md_path,
        "json": json_path,
        "bookmark": bookmark_path
    }

# Usage
paths = archive_to_memory_core("session.log", "ToolName Development")
print(f"Archived to: {paths['bookmark']}")
```

---

## 9. Error Pattern Database

### Build Searchable Error Database

```python
from sessiondocgen import SessionDocGen
import json
import sqlite3
from datetime import datetime
import glob

def build_error_database(log_pattern: str, db_path: str = "errors.db"):
    # Initialize database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS errors (
            id INTEGER PRIMARY KEY,
            session_name TEXT,
            timestamp TEXT,
            error_type TEXT,
            error_message TEXT,
            solution TEXT,
            effective BOOLEAN,
            created_at TEXT
        )
    """)
    
    # Process all logs
    for log_path in glob.glob(log_pattern):
        gen = SessionDocGen()
        gen.load_log_file(log_path)
        
        session_name = os.path.basename(log_path).replace(".log", "")
        
        for error in gen.errors:
            cursor.execute("""
                INSERT INTO errors (
                    session_name, timestamp, error_type, 
                    error_message, solution, effective, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_name,
                error.timestamp.isoformat(),
                error.error_type,
                error.error_message,
                error.solution,
                error.effective,
                datetime.now().isoformat()
            ))
    
    conn.commit()
    
    # Query statistics
    cursor.execute("""
        SELECT error_type, COUNT(*) as count, 
               SUM(CASE WHEN effective THEN 1 ELSE 0 END) as resolved
        FROM errors
        GROUP BY error_type
        ORDER BY count DESC
    """)
    
    stats = cursor.fetchall()
    conn.close()
    
    return stats

# Usage
stats = build_error_database("sessions/*.log")
for error_type, count, resolved in stats:
    print(f"{error_type}: {count} total, {resolved} resolved")
```

---

## 10. Team Dashboard

### Generate Dashboard Data

```python
from sessiondocgen import SessionDocGen
import json
import glob
from datetime import datetime, timedelta
from collections import defaultdict

def generate_dashboard_data(log_dir: str, days: int = 7):
    dashboard = {
        "generated_at": datetime.now().isoformat(),
        "period_days": days,
        "totals": {
            "sessions": 0,
            "tool_calls": 0,
            "files_modified": 0,
            "errors": 0,
            "errors_resolved": 0
        },
        "by_day": defaultdict(lambda: {
            "sessions": 0,
            "tool_calls": 0,
            "files_modified": 0
        }),
        "by_tool": defaultdict(int),
        "by_error_type": defaultdict(int),
        "recent_milestones": []
    }
    
    cutoff = datetime.now() - timedelta(days=days)
    
    for log_path in glob.glob(f"{log_dir}/*.log"):
        gen = SessionDocGen()
        gen.load_log_file(log_path)
        
        # Skip if outside date range
        if gen.tool_usages and gen.tool_usages[0].timestamp < cutoff:
            continue
        
        summary = gen.get_summary()
        date_str = gen.tool_usages[0].timestamp.strftime("%Y-%m-%d") if gen.tool_usages else "unknown"
        
        # Update totals
        dashboard["totals"]["sessions"] += 1
        dashboard["totals"]["tool_calls"] += summary["tool_calls"]
        dashboard["totals"]["files_modified"] += summary["files_touched"]
        dashboard["totals"]["errors"] += summary["errors"]
        dashboard["totals"]["errors_resolved"] += summary["errors_resolved"]
        
        # Update by day
        dashboard["by_day"][date_str]["sessions"] += 1
        dashboard["by_day"][date_str]["tool_calls"] += summary["tool_calls"]
        dashboard["by_day"][date_str]["files_modified"] += summary["files_touched"]
        
        # Update by tool
        for usage in gen.tool_usages:
            dashboard["by_tool"][usage.tool_name] += 1
        
        # Update by error type
        for error in gen.errors:
            dashboard["by_error_type"][error.error_type] += 1
        
        # Collect milestones
        for ms in gen.milestones:
            dashboard["recent_milestones"].append({
                "title": ms.title,
                "timestamp": ms.timestamp.isoformat(),
                "impact": ms.impact
            })
    
    # Convert defaultdicts
    dashboard["by_day"] = dict(dashboard["by_day"])
    dashboard["by_tool"] = dict(dashboard["by_tool"])
    dashboard["by_error_type"] = dict(dashboard["by_error_type"])
    
    # Sort milestones by time
    dashboard["recent_milestones"].sort(key=lambda x: x["timestamp"], reverse=True)
    dashboard["recent_milestones"] = dashboard["recent_milestones"][:10]
    
    return dashboard

# Usage
dashboard = generate_dashboard_data("sessions", days=7)

# Save as JSON for web dashboard
with open("dashboard_data.json", "w") as f:
    json.dump(dashboard, f, indent=2)

print(f"Sessions: {dashboard['totals']['sessions']}")
print(f"Tool Calls: {dashboard['totals']['tool_calls']}")
print(f"Error Rate: {dashboard['totals']['errors'] - dashboard['totals']['errors_resolved']} unresolved")
```

---

## Quick Copy-Paste Templates

### Minimal Integration

```python
from sessiondocgen import SessionDocGen
gen = SessionDocGen()
gen.load_log_file("session.log")
gen.save_report("report.md")
```

### With Summary

```python
from sessiondocgen import SessionDocGen
gen = SessionDocGen()
gen.load_log_file("session.log")
summary = gen.get_summary()
print(f"Tools: {summary['tool_calls']}, Errors: {summary['errors']}")
gen.save_report("report.md")
```

### Full Workflow

```python
from sessiondocgen import SessionDocGen
from datetime import datetime

gen = SessionDocGen()
gen.session_name = "Feature X"
gen.load_log_file("session.log")
gen.add_milestone("Complete", "All done", "major")
gen.save_report("report.md")
gen.save_report("data.json", format="json")
print(gen.get_summary())
```

---

*SessionDocGen Integration Examples v1.0*
*Built by ATLAS | Requested by IRIS*
