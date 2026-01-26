# SessionDocGen Examples

**10 Working Examples with Expected Output**

This document provides practical examples of SessionDocGen usage, from basic parsing to advanced integration patterns.

---

## Table of Contents

1. [Basic Log Parsing](#example-1-basic-log-parsing)
2. [Quick Summary](#example-2-quick-summary)
3. [JSON Report Generation](#example-3-json-report-generation)
4. [Multiple Log Files](#example-4-multiple-log-files)
5. [Git Diff Integration](#example-5-git-diff-integration)
6. [Adding Manual Annotations](#example-6-adding-manual-annotations)
7. [Tool Statistics Analysis](#example-7-tool-statistics-analysis)
8. [Programmatic Report Generation](#example-8-programmatic-report-generation)
9. [Error Pattern Analysis](#example-9-error-pattern-analysis)
10. [Full Workflow Integration](#example-10-full-workflow-integration)

---

## Example 1: Basic Log Parsing

Parse a session log and generate a markdown report.

### Input Log File (`session.log`)

```
Starting coding session...

<invoke name="read_file">
<parameter name="target_file">main.py</parameter>
</invoke>

File contents loaded.

<invoke name="write">
<parameter name="file_path">output.py</parameter>
<parameter name="contents">print("Hello World")</parameter>
</invoke>

File written successfully.

<invoke name="run_terminal_cmd">
<parameter name="command">python output.py</parameter>
</invoke>

Output: Hello World
Session complete.
```

### Command

```bash
python sessiondocgen.py parse session.log -n "Hello World Session" -o report.md
```

### Expected Output (`report.md`)

```markdown
# Hello World Session Summary

**Generated:** 2026-01-25 14:30:00
**Duration:** 0.0 minutes

## Quick Stats

| Metric | Value |
|--------|-------|
| Total Tool Calls | 3 |
| Successful | 3 |
| Files Created | 1 |
| Files Edited | 0 |
| Files Deleted | 0 |
| Lines Added | 0 |
| Lines Removed | 0 |
| Errors Encountered | 0 |
| Errors Resolved | 0 |
| Decisions Made | 0 |
| Milestones | 0 |

## Tool Usage Breakdown

| Category | Count | Percentage |
|----------|-------|------------|
| read | 1 | 33.3% |
| write | 1 | 33.3% |
| terminal | 1 | 33.3% |

### Top Tools Used

- `read_file`: 1
- `write`: 1
- `run_terminal_cmd`: 1

## File Modifications

| File | Type | Lines +/- |
|------|------|-----------|
| output.py | created | +0/-0 |

...
```

---

## Example 2: Quick Summary

Get a quick summary without generating a full report.

### Command

```bash
python sessiondocgen.py summary session.log -n "Quick Check"
```

### Expected Output

```
=== Quick Check Summary ===
Duration:       0.0 minutes
Tool Calls:     3
Files Touched:  1
Errors:         0 (0 resolved)
Decisions:      0
Milestones:     0
```

---

## Example 3: JSON Report Generation

Generate machine-readable JSON output.

### Command

```bash
python sessiondocgen.py parse session.log -f json -o report.json
```

### Expected Output (`report.json`)

```json
{
  "session_name": "Session",
  "generated_at": "2026-01-25T14:30:00.000000",
  "metrics": {
    "duration_minutes": 0.0,
    "total_tool_calls": 3,
    "successful_tool_calls": 3,
    "files_created": 1,
    "files_edited": 0,
    "files_deleted": 0,
    "total_lines_added": 0,
    "total_lines_removed": 0,
    "errors_encountered": 0,
    "errors_resolved": 0,
    "decisions_made": 0,
    "milestones_achieved": 0,
    "unique_files_touched": 1
  },
  "tool_usages": [
    {
      "tool_name": "read_file",
      "timestamp": "2026-01-25T14:30:00.000000",
      "arguments": {},
      "result": "",
      "success": true,
      "duration_ms": 0,
      "category": "read"
    },
    {
      "tool_name": "write",
      "timestamp": "2026-01-25T14:30:01.000000",
      "arguments": {},
      "result": "",
      "success": true,
      "duration_ms": 0,
      "category": "write"
    },
    {
      "tool_name": "run_terminal_cmd",
      "timestamp": "2026-01-25T14:30:02.000000",
      "arguments": {},
      "result": "",
      "success": true,
      "duration_ms": 0,
      "category": "terminal"
    }
  ],
  "file_modifications": [
    {
      "file_path": "output.py",
      "modification_type": "created",
      "timestamp": "2026-01-25T14:30:01.000000",
      "before_snippet": "",
      "after_snippet": "",
      "lines_added": 0,
      "lines_removed": 0,
      "tool_used": "write"
    }
  ],
  "errors": [],
  "decisions": [],
  "milestones": []
}
```

---

## Example 4: Multiple Log Files

Combine multiple session logs into one report.

### Input Files

**day1.log:**
```
<invoke name="read_file"></invoke>
<invoke name="write"></invoke>
```

**day2.log:**
```
<invoke name="grep"></invoke>
<invoke name="write"></invoke>
<invoke name="write"></invoke>
```

**day3.log:**
```
<invoke name="run_terminal_cmd"></invoke>
```

### Command

```bash
python sessiondocgen.py parse day1.log day2.log day3.log -n "Week Summary" -o weekly.md
```

### Expected Output

```markdown
# Week Summary Summary

**Generated:** 2026-01-25 14:30:00
**Duration:** 0.0 minutes

## Quick Stats

| Metric | Value |
|--------|-------|
| Total Tool Calls | 6 |
| Successful | 6 |
...
```

---

## Example 5: Git Diff Integration

Include detailed file modification stats from git diff.

### Input Git Diff (`changes.diff`)

```diff
diff --git a/main.py b/main.py
index abc123..def456 100644
--- a/main.py
+++ b/main.py
@@ -1,3 +1,10 @@
 import os
+import sys
+import json
+
+def new_function():
+    """New function added."""
+    return True
 
 def main():
-    pass
+    print("Hello")
+    new_function()
```

### Command

```bash
python sessiondocgen.py parse session.log --git-diff changes.diff -o report.md
```

### Expected Output (File Modifications Section)

```markdown
## File Modifications

| File | Type | Lines +/- |
|------|------|-----------|
| main.py | edited | +9/-1 |
```

---

## Example 6: Adding Manual Annotations

Add milestones, decisions, and error solutions programmatically.

### Python Code

```python
from sessiondocgen import SessionDocGen
from datetime import datetime

# Initialize
gen = SessionDocGen()
gen.session_name = "Feature Development"
gen.start_time = datetime(2026, 1, 25, 10, 0, 0)
gen.end_time = datetime(2026, 1, 25, 14, 30, 0)

# Load log
gen.load_content("""
<invoke name="read_file"></invoke>
<invoke name="write"></invoke>
<invoke name="grep"></invoke>
""")

# Add milestones
gen.add_milestone("Setup Complete", "Environment configured", "minor")
gen.add_milestone("Core Logic Done", "Main algorithm implemented", "major")
gen.add_milestone("Tests Passing", "All 50 tests pass", "major")

# Add decisions
gen.add_decision(
    "Use SQLite for storage",
    category="architecture",
    rationale="Zero dependencies, embedded database"
)
gen.add_decision(
    "Async/await for I/O",
    category="optimization",
    rationale="Better performance for file operations"
)

# Add error solutions
gen.add_error_solution(
    "ImportError: No module named 'requests'",
    "dependency",
    "pip install requests",
    effective=True
)

# Generate report
report = gen.generate_report("markdown")
print(report)
```

### Expected Output

```markdown
# Feature Development Summary

**Generated:** 2026-01-25 14:35:00
**Duration:** 270.0 minutes

...

## Key Decisions

- **[ARCHITECTURE]** Use SQLite for storage
- **[OPTIMIZATION]** Async/await for I/O

## Milestones

- [-] **Setup Complete**: Environment configured
- [*] **Core Logic Done**: Main algorithm implemented
- [*] **Tests Passing**: All 50 tests pass

## Errors & Solutions

### [OK] ERR_0001: DEPENDENCY
**Error:** ImportError: No module named 'requests'...
**Solution:** pip install requests
```

---

## Example 7: Tool Statistics Analysis

Analyze tool usage patterns across sessions.

### Command

```bash
python sessiondocgen.py stats complex_session.log
```

### Expected Output

```
=== Tool Usage Statistics ===

By Category:
----------------------------------------
  write          45 ( 35.4%) ###########
  read           38 ( 29.9%) #########
  search         22 ( 17.3%) #####
  terminal       15 ( 11.8%) ###
  other           7 (  5.5%) #

Top 10 Tools:
----------------------------------------
  write                               45 ( 35.4%)
  read_file                           28 ( 22.0%)
  grep                                15 ( 11.8%)
  search_replace                      12 (  9.4%)
  run_terminal_cmd                    10 (  7.9%)
  list_dir                             8 (  6.3%)
  codebase_search                      5 (  3.9%)
  delete_file                          3 (  2.4%)
  todo_write                           1 (  0.8%)

Total Tool Calls: 127
```

---

## Example 8: Programmatic Report Generation

Generate reports programmatically for automation.

### Python Code

```python
from sessiondocgen import SessionDocGen
import json

def generate_session_report(log_path: str, output_dir: str, session_name: str):
    """Generate all report formats for a session."""
    gen = SessionDocGen()
    gen.session_name = session_name
    gen.load_log_file(log_path)
    
    # Generate all formats
    gen.save_report(f"{output_dir}/{session_name}_report.md", format="markdown")
    gen.save_report(f"{output_dir}/{session_name}_data.json", format="json")
    gen.save_report(f"{output_dir}/{session_name}_summary.txt", format="text")
    
    # Return summary for further processing
    return gen.get_summary()

# Use it
summary = generate_session_report(
    "session.log",
    "reports",
    "FeatureX"
)

print(f"Session {summary['session_name']} complete:")
print(f"  - {summary['tool_calls']} tool calls")
print(f"  - {summary['files_touched']} files modified")
print(f"  - {summary['errors']} errors ({summary['errors_resolved']} resolved)")
```

### Expected Output

```
Session FeatureX complete:
  - 45 tool calls
  - 12 files modified
  - 3 errors (3 resolved)
```

---

## Example 9: Error Pattern Analysis

Analyze error patterns across multiple sessions.

### Python Code

```python
from sessiondocgen import SessionDocGen
from collections import Counter
import glob
import json

def analyze_error_patterns(log_pattern: str):
    """Analyze error patterns across sessions."""
    gen = SessionDocGen()
    
    # Load all matching logs
    for log_path in glob.glob(log_pattern):
        gen.load_log_file(log_path)
    
    # Generate JSON report for analysis
    report = json.loads(gen.generate_report("json"))
    
    # Analyze errors
    error_types = Counter(e["error_type"] for e in report["errors"])
    effective_count = sum(1 for e in report["errors"] if e["effective"])
    
    print("=== Error Pattern Analysis ===\n")
    print(f"Total Errors: {len(report['errors'])}")
    print(f"Resolved: {effective_count}")
    print(f"Resolution Rate: {effective_count/len(report['errors'])*100:.1f}%\n")
    
    print("Error Types:")
    for error_type, count in error_types.most_common():
        print(f"  {error_type}: {count}")
    
    return report["errors"]

# Analyze all session logs
errors = analyze_error_patterns("sessions/*.log")
```

### Expected Output

```
=== Error Pattern Analysis ===

Total Errors: 24
Resolved: 22
Resolution Rate: 91.7%

Error Types:
  dependency: 8
  syntax: 6
  build: 5
  network: 3
  runtime: 2
```

---

## Example 10: Full Workflow Integration

Complete workflow from session start to Team Brain notification.

### Python Code

```python
from sessiondocgen import SessionDocGen
from datetime import datetime
import json
import os

def complete_session_workflow(
    log_path: str,
    session_name: str,
    milestones: list,
    decisions: list,
    output_dir: str = "reports"
):
    """
    Complete session documentation workflow:
    1. Parse log
    2. Add annotations
    3. Generate reports
    4. Create summary for team notification
    """
    
    # Initialize
    gen = SessionDocGen()
    gen.session_name = session_name
    gen.start_time = datetime.now().replace(hour=10, minute=0)
    gen.end_time = datetime.now()
    
    # Parse log
    print(f"[1/4] Parsing log: {log_path}")
    gen.load_log_file(log_path)
    
    # Add milestones
    print(f"[2/4] Adding {len(milestones)} milestones")
    for ms in milestones:
        gen.add_milestone(ms["title"], ms.get("description", ""), ms.get("impact", "minor"))
    
    # Add decisions
    print(f"[2/4] Adding {len(decisions)} decisions")
    for dec in decisions:
        gen.add_decision(
            dec["description"],
            dec.get("category", "general"),
            dec.get("rationale", "")
        )
    
    # Generate reports
    print("[3/4] Generating reports...")
    os.makedirs(output_dir, exist_ok=True)
    
    gen.save_report(f"{output_dir}/{session_name}.md", format="markdown")
    gen.save_report(f"{output_dir}/{session_name}.json", format="json")
    
    # Get summary for team notification
    summary = gen.get_summary()
    
    # Create Synapse notification message
    notification = {
        "type": "SESSION_COMPLETE",
        "session_name": session_name,
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "duration_minutes": summary["duration_minutes"],
            "tool_calls": summary["tool_calls"],
            "files_touched": summary["files_touched"],
            "errors": summary["errors"],
            "errors_resolved": summary["errors_resolved"],
            "milestones": summary["milestones"]
        },
        "reports": {
            "markdown": f"{output_dir}/{session_name}.md",
            "json": f"{output_dir}/{session_name}.json"
        }
    }
    
    # Save notification
    with open(f"{output_dir}/{session_name}_notification.json", "w") as f:
        json.dump(notification, f, indent=2)
    
    print("[4/4] Complete!")
    print(f"\nSession Summary:")
    print(f"  Duration: {summary['duration_minutes']:.1f} minutes")
    print(f"  Tool Calls: {summary['tool_calls']}")
    print(f"  Files: {summary['files_touched']}")
    print(f"  Errors: {summary['errors']} ({summary['errors_resolved']} resolved)")
    print(f"  Milestones: {summary['milestones']}")
    print(f"\nReports saved to: {output_dir}/")
    
    return notification

# Example usage
notification = complete_session_workflow(
    log_path="feature_session.log",
    session_name="UserAuth_Implementation",
    milestones=[
        {"title": "Database Schema", "description": "User tables created", "impact": "major"},
        {"title": "Login API", "description": "POST /login working", "impact": "major"},
        {"title": "Tests Complete", "description": "All 25 tests passing", "impact": "major"}
    ],
    decisions=[
        {
            "description": "Use bcrypt for password hashing",
            "category": "architecture",
            "rationale": "Industry standard, proven security"
        },
        {
            "description": "JWT for session tokens",
            "category": "architecture",
            "rationale": "Stateless, scalable"
        }
    ],
    output_dir="reports/auth"
)
```

### Expected Output

```
[1/4] Parsing log: feature_session.log
[2/4] Adding 3 milestones
[2/4] Adding 2 decisions
[3/4] Generating reports...
[4/4] Complete!

Session Summary:
  Duration: 180.5 minutes
  Tool Calls: 89
  Files: 15
  Errors: 4 (4 resolved)
  Milestones: 3

Reports saved to: reports/auth/
```

---

## Quick Reference

```bash
# Basic parsing
python sessiondocgen.py parse session.log -o report.md

# Quick summary
python sessiondocgen.py summary session.log

# JSON output
python sessiondocgen.py parse session.log -f json -o data.json

# Multiple logs
python sessiondocgen.py parse *.log -o combined.md

# With git diff
python sessiondocgen.py parse session.log --git-diff changes.diff

# Stats only
python sessiondocgen.py stats session.log

# Named session
python sessiondocgen.py parse session.log -n "Feature X" -o report.md
```

---

**SessionDocGen** - Examples that work.
