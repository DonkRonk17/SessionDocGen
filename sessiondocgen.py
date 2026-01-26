#!/usr/bin/env python3
"""
SessionDocGen v1.0 - Auto-Generate Session Summaries from Tool Usage

Automatically generates comprehensive session summaries from tool usage,
decisions, and outcomes. Reduces manual documentation burden significantly.

REQUESTED BY: IRIS (Tool Request #21)
BUILT BY: ATLAS (Team Brain)

USE CASES:
- Extract tool usage statistics (tool type, count, percentage)
- Identify error->solution patterns
- Track file modifications (created, edited, deleted with diffs)
- Capture key decisions and their rationale
- Generate timeline of milestones
- Summarize outcomes (working features, bugs found, pending items)
- Calculate metrics (duration, LOC written, files touched)

Zero dependencies - Python standard library only.
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
import hashlib


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ToolUsage:
    """Represents a single tool call/usage."""
    tool_name: str
    timestamp: datetime
    arguments: Dict[str, Any] = field(default_factory=dict)
    result: str = ""
    success: bool = True
    duration_ms: int = 0
    category: str = ""  # read, write, search, terminal, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "timestamp": self.timestamp.isoformat(),
            "arguments": self.arguments,
            "result": self.result[:200] if self.result else "",  # Truncate
            "success": self.success,
            "duration_ms": self.duration_ms,
            "category": self.category
        }


@dataclass
class FileModification:
    """Represents a file modification event."""
    file_path: str
    modification_type: str  # created, edited, deleted
    timestamp: datetime
    before_snippet: str = ""
    after_snippet: str = ""
    lines_added: int = 0
    lines_removed: int = 0
    tool_used: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "modification_type": self.modification_type,
            "timestamp": self.timestamp.isoformat(),
            "before_snippet": self.before_snippet[:500] if self.before_snippet else "",
            "after_snippet": self.after_snippet[:500] if self.after_snippet else "",
            "lines_added": self.lines_added,
            "lines_removed": self.lines_removed,
            "tool_used": self.tool_used
        }


@dataclass
class Decision:
    """Represents a key decision made during session."""
    decision_id: str
    description: str
    timestamp: datetime
    category: str = ""  # architecture, bug_fix, optimization, handoff, config
    rationale: str = ""
    alternatives_considered: List[str] = field(default_factory=list)
    related_files: List[str] = field(default_factory=list)
    outcome: str = ""  # success, partial, reverted
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "category": self.category,
            "rationale": self.rationale,
            "alternatives_considered": self.alternatives_considered,
            "related_files": self.related_files,
            "outcome": self.outcome
        }


@dataclass
class ErrorSolution:
    """Represents an error and its solution."""
    error_id: str
    error_type: str  # build, network, dependency, syntax, runtime
    error_message: str
    timestamp: datetime
    solution: str = ""
    solution_steps: List[str] = field(default_factory=list)
    effective: bool = True
    recurred: bool = False
    related_tools: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_id": self.error_id,
            "error_type": self.error_type,
            "error_message": self.error_message[:500] if self.error_message else "",
            "timestamp": self.timestamp.isoformat(),
            "solution": self.solution,
            "solution_steps": self.solution_steps,
            "effective": self.effective,
            "recurred": self.recurred,
            "related_tools": self.related_tools
        }


@dataclass
class Milestone:
    """Represents a session milestone."""
    milestone_id: str
    title: str
    timestamp: datetime
    description: str = ""
    impact: str = ""  # major, minor, critical
    related_decisions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "milestone_id": self.milestone_id,
            "title": self.title,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "impact": self.impact,
            "related_decisions": self.related_decisions
        }


@dataclass
class SessionMetrics:
    """Aggregated session metrics."""
    duration_minutes: float = 0.0
    total_tool_calls: int = 0
    successful_tool_calls: int = 0
    files_created: int = 0
    files_edited: int = 0
    files_deleted: int = 0
    total_lines_added: int = 0
    total_lines_removed: int = 0
    errors_encountered: int = 0
    errors_resolved: int = 0
    decisions_made: int = 0
    milestones_achieved: int = 0
    unique_files_touched: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# TOOL CATEGORY MAPPING
# ============================================================================

TOOL_CATEGORIES = {
    # Read operations
    "read_file": "read",
    "list_dir": "read",
    "glob_file_search": "search",
    "grep": "search",
    "codebase_search": "search",
    
    # Write operations
    "write": "write",
    "search_replace": "write",
    "edit_notebook": "write",
    "delete_file": "write",
    
    # Terminal operations
    "run_terminal_cmd": "terminal",
    
    # Browser operations
    "mcp_cursor-ide-browser_browser_navigate": "browser",
    "mcp_cursor-ide-browser_browser_snapshot": "browser",
    "mcp_cursor-ide-browser_browser_click": "browser",
    "mcp_cursor-ide-browser_browser_type": "browser",
    
    # Other
    "web_search": "web",
    "todo_write": "planning",
    "update_memory": "memory",
}


# ============================================================================
# PARSERS
# ============================================================================

class ToolUsageParser:
    """Parses tool usage from various log formats."""
    
    # Pattern for common tool call formats
    TOOL_CALL_PATTERNS = [
        # JSON-style: {"tool": "read_file", "args": {...}}
        r'\{["\']tool["\']\s*:\s*["\'](\w+)["\'].*?["\']args["\']\s*:\s*(\{[^}]+\})',
        # XML-style: <tool name="read_file">...</tool>
        r'<tool\s+name=["\'](\w+)["\']>(.*?)</tool>',
        # Function-style: read_file(file="path")
        r'(\w+)\s*\(\s*([^)]+)\)',
        # antml invoke style
        r'<invoke\s+name=["\']([^"\']+)["\']',
    ]
    
    ERROR_PATTERNS = [
        # Python errors
        r'((?:Traceback|Error|Exception|Failed)[^\n]*(?:\n[^\n]+){0,10})',
        # Build errors
        r'((?:error|FAILED|ERROR):\s*[^\n]+)',
        # Exit codes
        r'Exit code:\s*([1-9]\d*)',
    ]
    
    def __init__(self):
        self.tool_usages: List[ToolUsage] = []
        self.errors: List[ErrorSolution] = []
        self._error_counter = 0
    
    def parse_log_file(self, log_path: str) -> Tuple[List[ToolUsage], List[ErrorSolution]]:
        """Parse a log file for tool usages and errors."""
        if not os.path.exists(log_path):
            raise FileNotFoundError(f"Log file not found: {log_path}")
        
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> Tuple[List[ToolUsage], List[ErrorSolution]]:
        """Parse content string for tool usages and errors."""
        self.tool_usages = []
        self.errors = []
        
        # Extract tool calls
        self._extract_tool_calls(content)
        
        # Extract errors
        self._extract_errors(content)
        
        return self.tool_usages, self.errors
    
    def _extract_tool_calls(self, content: str) -> None:
        """Extract tool calls from content."""
        base_time = datetime.now()
        call_index = 0
        
        # Try antml invoke pattern (most common in our system)
        invoke_pattern = r'<invoke\s+name=["\']([^"\']+)["\']'
        for match in re.finditer(invoke_pattern, content):
            tool_name = match.group(1)
            category = TOOL_CATEGORIES.get(tool_name, "other")
            
            usage = ToolUsage(
                tool_name=tool_name,
                timestamp=base_time + timedelta(seconds=call_index),
                category=category,
                success=True
            )
            self.tool_usages.append(usage)
            call_index += 1
        
        # Try other patterns if no antml found
        if not self.tool_usages:
            for pattern in self.TOOL_CALL_PATTERNS:
                for match in re.finditer(pattern, content, re.DOTALL):
                    tool_name = match.group(1)
                    if tool_name in TOOL_CATEGORIES or not tool_name.startswith('_'):
                        category = TOOL_CATEGORIES.get(tool_name, "other")
                        usage = ToolUsage(
                            tool_name=tool_name,
                            timestamp=base_time + timedelta(seconds=call_index),
                            category=category,
                            success=True
                        )
                        self.tool_usages.append(usage)
                        call_index += 1
    
    def _extract_errors(self, content: str) -> None:
        """Extract errors from content."""
        for pattern in self.ERROR_PATTERNS:
            for match in re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE):
                error_text = match.group(1) if match.lastindex else match.group(0)
                
                # Categorize error
                error_type = self._categorize_error(error_text)
                
                self._error_counter += 1
                error = ErrorSolution(
                    error_id=f"ERR_{self._error_counter:04d}",
                    error_type=error_type,
                    error_message=error_text.strip()[:500],
                    timestamp=datetime.now()
                )
                self.errors.append(error)
    
    def _categorize_error(self, error_text: str) -> str:
        """Categorize error type."""
        error_lower = error_text.lower()
        
        if any(k in error_lower for k in ['import', 'module', 'package', 'dependency', 'pip']):
            return "dependency"
        elif any(k in error_lower for k in ['syntax', 'parse', 'unexpected token', 'indent']):
            return "syntax"
        elif any(k in error_lower for k in ['build', 'compile', 'gradle', 'npm run', 'webpack']):
            return "build"
        elif any(k in error_lower for k in ['network', 'connection', 'timeout', 'socket', 'http']):
            return "network"
        elif any(k in error_lower for k in ['permission', 'access denied', 'unauthorized']):
            return "permission"
        else:
            return "runtime"


class FileModificationParser:
    """Parses file modifications from logs or file system."""
    
    def __init__(self):
        self.modifications: List[FileModification] = []
    
    def parse_from_tool_usages(self, tool_usages: List[ToolUsage]) -> List[FileModification]:
        """Extract file modifications from tool usages."""
        self.modifications = []
        
        for usage in tool_usages:
            if usage.tool_name == "write":
                file_path = usage.arguments.get("file_path", "unknown")
                mod = FileModification(
                    file_path=file_path,
                    modification_type="created" if not os.path.exists(file_path) else "edited",
                    timestamp=usage.timestamp,
                    tool_used="write"
                )
                self.modifications.append(mod)
            
            elif usage.tool_name == "search_replace":
                file_path = usage.arguments.get("file_path", "unknown")
                mod = FileModification(
                    file_path=file_path,
                    modification_type="edited",
                    timestamp=usage.timestamp,
                    tool_used="search_replace"
                )
                self.modifications.append(mod)
            
            elif usage.tool_name == "delete_file":
                file_path = usage.arguments.get("target_file", "unknown")
                mod = FileModification(
                    file_path=file_path,
                    modification_type="deleted",
                    timestamp=usage.timestamp,
                    tool_used="delete_file"
                )
                self.modifications.append(mod)
        
        return self.modifications
    
    def parse_from_git_diff(self, diff_content: str) -> List[FileModification]:
        """Parse file modifications from git diff output."""
        self.modifications = []
        
        # Pattern for diff headers - match "diff --git a/file b/file"
        diff_pattern = r'^diff --git a/(.+?) b/(.+?)$'
        add_pattern = r'^\+(?!\+\+)(.*)$'
        remove_pattern = r'^-(?!--)(.*)$'
        
        current_file = None
        lines_added = 0
        lines_removed = 0
        
        for line in diff_content.split('\n'):
            diff_match = re.match(diff_pattern, line)
            if diff_match:
                # Save previous file if exists
                if current_file:
                    mod = FileModification(
                        file_path=current_file,
                        modification_type="edited",
                        timestamp=datetime.now(),
                        lines_added=lines_added,
                        lines_removed=lines_removed,
                        tool_used="git"
                    )
                    self.modifications.append(mod)
                
                current_file = diff_match.group(2)
                lines_added = 0
                lines_removed = 0
            elif current_file:
                if re.match(add_pattern, line):
                    lines_added += 1
                elif re.match(remove_pattern, line):
                    lines_removed += 1
        
        # Don't forget last file
        if current_file:
            mod = FileModification(
                file_path=current_file,
                modification_type="edited",
                timestamp=datetime.now(),
                lines_added=lines_added,
                lines_removed=lines_removed,
                tool_used="git"
            )
            self.modifications.append(mod)
        
        return self.modifications


class DecisionParser:
    """Parses decisions from conversation/log content."""
    
    DECISION_KEYWORDS = [
        r'\b(?:decided|decision|chose|choosing|selected|opted|went with)\b',
        r'\b(?:will use|using|implemented|implementing)\b',
        r'\b(?:approach|strategy|solution|fix)\b.*\b(?:is|was|will be)\b',
    ]
    
    CATEGORY_KEYWORDS = {
        "architecture": ["architecture", "design", "structure", "pattern", "module"],
        "bug_fix": ["fix", "bug", "error", "issue", "problem", "resolve"],
        "optimization": ["optimize", "performance", "speed", "efficient", "cache"],
        "handoff": ["handoff", "hand-off", "transition", "switch", "pass to"],
        "config": ["config", "configuration", "setting", "environment", "variable"],
    }
    
    def __init__(self):
        self.decisions: List[Decision] = []
        self._decision_counter = 0
    
    def parse_content(self, content: str) -> List[Decision]:
        """Parse decisions from content."""
        self.decisions = []
        
        # Split into sentences/paragraphs
        sentences = re.split(r'[.!?\n]', content)
        
        for sentence in sentences:
            if self._is_decision(sentence):
                self._decision_counter += 1
                category = self._categorize_decision(sentence)
                
                decision = Decision(
                    decision_id=f"DEC_{self._decision_counter:04d}",
                    description=sentence.strip()[:200],
                    timestamp=datetime.now(),
                    category=category
                )
                self.decisions.append(decision)
        
        return self.decisions
    
    def _is_decision(self, text: str) -> bool:
        """Check if text contains a decision."""
        text_lower = text.lower()
        for pattern in self.DECISION_KEYWORDS:
            if re.search(pattern, text_lower):
                return True
        return False
    
    def _categorize_decision(self, text: str) -> str:
        """Categorize a decision."""
        text_lower = text.lower()
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return category
        return "general"


# ============================================================================
# METRICS CALCULATOR
# ============================================================================

class MetricsCalculator:
    """Calculate session metrics from parsed data."""
    
    def calculate(
        self,
        tool_usages: List[ToolUsage],
        file_modifications: List[FileModification],
        errors: List[ErrorSolution],
        decisions: List[Decision],
        milestones: List[Milestone],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> SessionMetrics:
        """Calculate comprehensive session metrics."""
        metrics = SessionMetrics()
        
        # Duration
        if start_time and end_time:
            duration = (end_time - start_time).total_seconds() / 60
            metrics.duration_minutes = round(duration, 2)
        elif tool_usages:
            first = min(u.timestamp for u in tool_usages)
            last = max(u.timestamp for u in tool_usages)
            metrics.duration_minutes = round((last - first).total_seconds() / 60, 2)
        
        # Tool calls
        metrics.total_tool_calls = len(tool_usages)
        metrics.successful_tool_calls = sum(1 for u in tool_usages if u.success)
        
        # File modifications
        metrics.files_created = sum(1 for m in file_modifications if m.modification_type == "created")
        metrics.files_edited = sum(1 for m in file_modifications if m.modification_type == "edited")
        metrics.files_deleted = sum(1 for m in file_modifications if m.modification_type == "deleted")
        metrics.total_lines_added = sum(m.lines_added for m in file_modifications)
        metrics.total_lines_removed = sum(m.lines_removed for m in file_modifications)
        
        # Unique files
        unique_files: Set[str] = set()
        for m in file_modifications:
            unique_files.add(m.file_path)
        metrics.unique_files_touched = len(unique_files)
        
        # Errors
        metrics.errors_encountered = len(errors)
        metrics.errors_resolved = sum(1 for e in errors if e.effective)
        
        # Decisions and milestones
        metrics.decisions_made = len(decisions)
        metrics.milestones_achieved = len(milestones)
        
        return metrics


# ============================================================================
# REPORT GENERATOR
# ============================================================================

class ReportGenerator:
    """Generate session summary reports in various formats."""
    
    def __init__(self):
        self.tool_usages: List[ToolUsage] = []
        self.file_modifications: List[FileModification] = []
        self.errors: List[ErrorSolution] = []
        self.decisions: List[Decision] = []
        self.milestones: List[Milestone] = []
        self.metrics: SessionMetrics = SessionMetrics()
    
    def set_data(
        self,
        tool_usages: List[ToolUsage],
        file_modifications: List[FileModification],
        errors: List[ErrorSolution],
        decisions: List[Decision],
        milestones: List[Milestone],
        metrics: SessionMetrics
    ) -> None:
        """Set the data for report generation."""
        self.tool_usages = tool_usages
        self.file_modifications = file_modifications
        self.errors = errors
        self.decisions = decisions
        self.milestones = milestones
        self.metrics = metrics
    
    def generate_markdown(self, session_name: str = "Session") -> str:
        """Generate markdown report."""
        lines = []
        now = datetime.now()
        
        # Header
        lines.append(f"# {session_name} Summary")
        lines.append(f"\n**Generated:** {now.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Duration:** {self.metrics.duration_minutes:.1f} minutes")
        lines.append("")
        
        # Quick Stats
        lines.append("## Quick Stats")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Tool Calls | {self.metrics.total_tool_calls} |")
        lines.append(f"| Successful | {self.metrics.successful_tool_calls} |")
        lines.append(f"| Files Created | {self.metrics.files_created} |")
        lines.append(f"| Files Edited | {self.metrics.files_edited} |")
        lines.append(f"| Files Deleted | {self.metrics.files_deleted} |")
        lines.append(f"| Lines Added | {self.metrics.total_lines_added} |")
        lines.append(f"| Lines Removed | {self.metrics.total_lines_removed} |")
        lines.append(f"| Errors Encountered | {self.metrics.errors_encountered} |")
        lines.append(f"| Errors Resolved | {self.metrics.errors_resolved} |")
        lines.append(f"| Decisions Made | {self.metrics.decisions_made} |")
        lines.append(f"| Milestones | {self.metrics.milestones_achieved} |")
        lines.append("")
        
        # Tool Usage Breakdown
        lines.append("## Tool Usage Breakdown")
        lines.append("")
        tool_counts = self._count_by_category(self.tool_usages, "category")
        if tool_counts:
            lines.append("| Category | Count | Percentage |")
            lines.append("|----------|-------|------------|")
            total = sum(tool_counts.values())
            for cat, count in sorted(tool_counts.items(), key=lambda x: -x[1]):
                pct = (count / total * 100) if total > 0 else 0
                lines.append(f"| {cat} | {count} | {pct:.1f}% |")
            lines.append("")
        
        # Top Tools
        lines.append("### Top Tools Used")
        lines.append("")
        tool_names = self._count_by_field(self.tool_usages, "tool_name")
        for name, count in sorted(tool_names.items(), key=lambda x: -x[1])[:10]:
            lines.append(f"- `{name}`: {count}")
        lines.append("")
        
        # File Modifications
        lines.append("## File Modifications")
        lines.append("")
        if self.file_modifications:
            lines.append("| File | Type | Lines +/- |")
            lines.append("|------|------|-----------|")
            for mod in self.file_modifications[:20]:  # Limit to 20
                file_name = Path(mod.file_path).name
                lines.append(f"| {file_name} | {mod.modification_type} | +{mod.lines_added}/-{mod.lines_removed} |")
            if len(self.file_modifications) > 20:
                lines.append(f"| ... | ... | ({len(self.file_modifications) - 20} more) |")
        else:
            lines.append("*No file modifications tracked*")
        lines.append("")
        
        # Errors & Solutions
        lines.append("## Errors & Solutions")
        lines.append("")
        if self.errors:
            for error in self.errors[:10]:  # Limit to 10
                status = "[OK]" if error.effective else "[x]"
                lines.append(f"### {status} {error.error_id}: {error.error_type.upper()}")
                lines.append(f"**Error:** {error.error_message[:200]}...")
                if error.solution:
                    lines.append(f"**Solution:** {error.solution}")
                lines.append("")
        else:
            lines.append("*No errors encountered*")
        lines.append("")
        
        # Decisions
        lines.append("## Key Decisions")
        lines.append("")
        if self.decisions:
            for dec in self.decisions[:15]:  # Limit to 15
                lines.append(f"- **[{dec.category.upper()}]** {dec.description}")
        else:
            lines.append("*No decisions tracked*")
        lines.append("")
        
        # Milestones
        lines.append("## Milestones")
        lines.append("")
        if self.milestones:
            for ms in self.milestones:
                impact_emoji = {"critical": "[!]", "major": "[*]", "minor": "[-]"}.get(ms.impact, "[-]")
                lines.append(f"- {impact_emoji} **{ms.title}**: {ms.description}")
        else:
            lines.append("*No milestones defined*")
        lines.append("")
        
        # Timeline
        lines.append("## Timeline")
        lines.append("")
        lines.append("```")
        lines.append(self._generate_ascii_timeline())
        lines.append("```")
        lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("*Generated by SessionDocGen v1.0*")
        
        return "\n".join(lines)
    
    def generate_json(self, session_name: str = "Session") -> str:
        """Generate JSON report."""
        report = {
            "session_name": session_name,
            "generated_at": datetime.now().isoformat(),
            "metrics": self.metrics.to_dict(),
            "tool_usages": [u.to_dict() for u in self.tool_usages],
            "file_modifications": [m.to_dict() for m in self.file_modifications],
            "errors": [e.to_dict() for e in self.errors],
            "decisions": [d.to_dict() for d in self.decisions],
            "milestones": [m.to_dict() for m in self.milestones]
        }
        return json.dumps(report, indent=2)
    
    def generate_text(self, session_name: str = "Session") -> str:
        """Generate plain text report."""
        lines = []
        sep = "=" * 60
        
        lines.append(sep)
        lines.append(f"  {session_name.upper()} SUMMARY")
        lines.append(sep)
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Duration:  {self.metrics.duration_minutes:.1f} minutes")
        lines.append("")
        lines.append("-" * 60)
        lines.append("METRICS")
        lines.append("-" * 60)
        lines.append(f"  Tool Calls:     {self.metrics.total_tool_calls} ({self.metrics.successful_tool_calls} successful)")
        lines.append(f"  Files Created:  {self.metrics.files_created}")
        lines.append(f"  Files Edited:   {self.metrics.files_edited}")
        lines.append(f"  Files Deleted:  {self.metrics.files_deleted}")
        lines.append(f"  Lines Added:    {self.metrics.total_lines_added}")
        lines.append(f"  Lines Removed:  {self.metrics.total_lines_removed}")
        lines.append(f"  Errors:         {self.metrics.errors_encountered} ({self.metrics.errors_resolved} resolved)")
        lines.append(f"  Decisions:      {self.metrics.decisions_made}")
        lines.append(f"  Milestones:     {self.metrics.milestones_achieved}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("TOP TOOLS")
        lines.append("-" * 60)
        tool_names = self._count_by_field(self.tool_usages, "tool_name")
        for i, (name, count) in enumerate(sorted(tool_names.items(), key=lambda x: -x[1])[:5], 1):
            lines.append(f"  {i}. {name}: {count}")
        lines.append("")
        lines.append(sep)
        lines.append("END OF SUMMARY")
        lines.append(sep)
        
        return "\n".join(lines)
    
    def _count_by_category(self, items: List[Any], field: str) -> Dict[str, int]:
        """Count items by a category field."""
        counts: Dict[str, int] = defaultdict(int)
        for item in items:
            value = getattr(item, field, "unknown")
            counts[value] += 1
        return dict(counts)
    
    def _count_by_field(self, items: List[Any], field: str) -> Dict[str, int]:
        """Count items by a field."""
        counts: Dict[str, int] = defaultdict(int)
        for item in items:
            value = getattr(item, field, "unknown")
            counts[value] += 1
        return dict(counts)
    
    def _generate_ascii_timeline(self) -> str:
        """Generate an ASCII timeline of events."""
        events = []
        
        # Collect all timestamped events
        for usage in self.tool_usages:
            events.append((usage.timestamp, "tool", usage.tool_name))
        for mod in self.file_modifications:
            events.append((mod.timestamp, "file", f"{mod.modification_type}: {Path(mod.file_path).name}"))
        for error in self.errors:
            events.append((error.timestamp, "error", error.error_type))
        for ms in self.milestones:
            events.append((ms.timestamp, "milestone", ms.title))
        
        if not events:
            return "No events recorded"
        
        # Sort by timestamp
        events.sort(key=lambda x: x[0])
        
        # Generate timeline (show key events)
        lines = []
        shown = 0
        prev_type = None
        
        for ts, event_type, desc in events:
            # Show milestones and errors always, compress sequential same-type events
            if event_type in ("milestone", "error") or event_type != prev_type or shown < 10:
                icon = {"tool": "[T]", "file": "[F]", "error": "[!]", "milestone": "[*]"}.get(event_type, "[-]")
                time_str = ts.strftime("%H:%M:%S")
                lines.append(f"{time_str} {icon} {desc[:40]}")
                shown += 1
            prev_type = event_type
            
            if shown >= 20:
                lines.append(f"... ({len(events) - shown} more events)")
                break
        
        return "\n".join(lines)


# ============================================================================
# MAIN SESSION DOC GENERATOR
# ============================================================================

class SessionDocGen:
    """Main class for generating session documentation."""
    
    def __init__(self):
        self.tool_parser = ToolUsageParser()
        self.file_parser = FileModificationParser()
        self.decision_parser = DecisionParser()
        self.metrics_calculator = MetricsCalculator()
        self.report_generator = ReportGenerator()
        
        # Data storage
        self.tool_usages: List[ToolUsage] = []
        self.file_modifications: List[FileModification] = []
        self.errors: List[ErrorSolution] = []
        self.decisions: List[Decision] = []
        self.milestones: List[Milestone] = []
        self.metrics: SessionMetrics = SessionMetrics()
        
        # Session info
        self.session_name: str = "Session"
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    def load_log_file(self, log_path: str) -> None:
        """Load and parse a log file."""
        tool_usages, errors = self.tool_parser.parse_log_file(log_path)
        self.tool_usages.extend(tool_usages)
        self.errors.extend(errors)
        
        # Extract file modifications from tool usages
        file_mods = self.file_parser.parse_from_tool_usages(tool_usages)
        self.file_modifications.extend(file_mods)
        
        # Read file content for decision parsing
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        decisions = self.decision_parser.parse_content(content)
        self.decisions.extend(decisions)
    
    def load_content(self, content: str) -> None:
        """Load and parse content string."""
        tool_usages, errors = self.tool_parser.parse_content(content)
        self.tool_usages.extend(tool_usages)
        self.errors.extend(errors)
        
        # Extract file modifications from tool usages
        file_mods = self.file_parser.parse_from_tool_usages(tool_usages)
        self.file_modifications.extend(file_mods)
        
        decisions = self.decision_parser.parse_content(content)
        self.decisions.extend(decisions)
    
    def load_git_diff(self, diff_content: str) -> None:
        """Load file modifications from git diff."""
        file_mods = self.file_parser.parse_from_git_diff(diff_content)
        self.file_modifications.extend(file_mods)
    
    def add_milestone(
        self,
        title: str,
        description: str = "",
        impact: str = "minor",
        timestamp: Optional[datetime] = None
    ) -> str:
        """Add a milestone manually."""
        milestone_id = f"MS_{len(self.milestones) + 1:04d}"
        milestone = Milestone(
            milestone_id=milestone_id,
            title=title,
            description=description,
            impact=impact,
            timestamp=timestamp or datetime.now()
        )
        self.milestones.append(milestone)
        return milestone_id
    
    def add_decision(
        self,
        description: str,
        category: str = "general",
        rationale: str = "",
        timestamp: Optional[datetime] = None
    ) -> str:
        """Add a decision manually."""
        decision_id = f"DEC_{len(self.decisions) + 1:04d}"
        decision = Decision(
            decision_id=decision_id,
            description=description,
            category=category,
            rationale=rationale,
            timestamp=timestamp or datetime.now()
        )
        self.decisions.append(decision)
        return decision_id
    
    def add_error_solution(
        self,
        error_message: str,
        error_type: str,
        solution: str,
        effective: bool = True
    ) -> str:
        """Add an error-solution pair manually."""
        error_id = f"ERR_{len(self.errors) + 1:04d}"
        error = ErrorSolution(
            error_id=error_id,
            error_type=error_type,
            error_message=error_message,
            timestamp=datetime.now(),
            solution=solution,
            effective=effective
        )
        self.errors.append(error)
        return error_id
    
    def calculate_metrics(self) -> SessionMetrics:
        """Calculate session metrics."""
        self.metrics = self.metrics_calculator.calculate(
            self.tool_usages,
            self.file_modifications,
            self.errors,
            self.decisions,
            self.milestones,
            self.start_time,
            self.end_time
        )
        return self.metrics
    
    def generate_report(
        self,
        format: str = "markdown",
        session_name: Optional[str] = None
    ) -> str:
        """Generate session report."""
        # Calculate metrics if not done
        if self.metrics.total_tool_calls == 0 and self.tool_usages:
            self.calculate_metrics()
        
        # Set report data
        self.report_generator.set_data(
            self.tool_usages,
            self.file_modifications,
            self.errors,
            self.decisions,
            self.milestones,
            self.metrics
        )
        
        name = session_name or self.session_name
        
        if format == "markdown" or format == "md":
            return self.report_generator.generate_markdown(name)
        elif format == "json":
            return self.report_generator.generate_json(name)
        elif format == "text" or format == "txt":
            return self.report_generator.generate_text(name)
        else:
            raise ValueError(f"Unknown format: {format}. Use 'markdown', 'json', or 'text'")
    
    def save_report(
        self,
        output_path: str,
        format: str = "markdown",
        session_name: Optional[str] = None
    ) -> str:
        """Generate and save report to file."""
        report = self.generate_report(format, session_name)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return output_path
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a quick summary of the session."""
        if self.metrics.total_tool_calls == 0 and self.tool_usages:
            self.calculate_metrics()
        
        return {
            "session_name": self.session_name,
            "duration_minutes": self.metrics.duration_minutes,
            "tool_calls": self.metrics.total_tool_calls,
            "files_touched": self.metrics.unique_files_touched,
            "errors": self.metrics.errors_encountered,
            "errors_resolved": self.metrics.errors_resolved,
            "decisions": self.metrics.decisions_made,
            "milestones": self.metrics.milestones_achieved
        }
    
    def reset(self) -> None:
        """Reset all data for a new session."""
        self.tool_usages = []
        self.file_modifications = []
        self.errors = []
        self.decisions = []
        self.milestones = []
        self.metrics = SessionMetrics()
        self.session_name = "Session"
        self.start_time = None
        self.end_time = None


# ============================================================================
# CLI
# ============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="sessiondocgen",
        description="Auto-generate session summaries from tool usage, decisions, and outcomes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse a log file and generate markdown report
  python sessiondocgen.py parse session.log -o summary.md

  # Parse multiple log files
  python sessiondocgen.py parse log1.txt log2.txt -o combined.md

  # Generate JSON report
  python sessiondocgen.py parse session.log -f json -o summary.json

  # Parse with git diff for file modifications
  python sessiondocgen.py parse session.log --git-diff changes.diff

  # Quick summary to stdout
  python sessiondocgen.py summary session.log

Built by ATLAS (Team Brain) for IRIS
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Parse command
    parse_parser = subparsers.add_parser("parse", help="Parse log files and generate report")
    parse_parser.add_argument("logs", nargs="+", help="Log files to parse")
    parse_parser.add_argument("-o", "--output", help="Output file path")
    parse_parser.add_argument("-f", "--format", choices=["markdown", "md", "json", "text", "txt"],
                              default="markdown", help="Output format (default: markdown)")
    parse_parser.add_argument("-n", "--name", default="Session", help="Session name")
    parse_parser.add_argument("--git-diff", help="Git diff file for file modifications")
    parse_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Quick summary to stdout")
    summary_parser.add_argument("logs", nargs="+", help="Log files to parse")
    summary_parser.add_argument("-n", "--name", default="Session", help="Session name")
    
    # Milestone command
    milestone_parser = subparsers.add_parser("milestone", help="Add milestone to existing report")
    milestone_parser.add_argument("title", help="Milestone title")
    milestone_parser.add_argument("-d", "--description", default="", help="Description")
    milestone_parser.add_argument("-i", "--impact", choices=["minor", "major", "critical"],
                                   default="minor", help="Impact level")
    milestone_parser.add_argument("-r", "--report", required=True, help="Report JSON file to update")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show tool usage statistics")
    stats_parser.add_argument("logs", nargs="+", help="Log files to analyze")
    
    return parser


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    generator = SessionDocGen()
    
    if args.command == "parse":
        # Parse all log files
        for log_path in args.logs:
            if os.path.exists(log_path):
                generator.load_log_file(log_path)
                if args.verbose:
                    print(f"Parsed: {log_path}")
            else:
                print(f"Warning: File not found: {log_path}", file=sys.stderr)
        
        # Load git diff if provided
        if args.git_diff and os.path.exists(args.git_diff):
            with open(args.git_diff, 'r', encoding='utf-8') as f:
                generator.load_git_diff(f.read())
            if args.verbose:
                print(f"Loaded git diff: {args.git_diff}")
        
        generator.session_name = args.name
        
        # Generate report
        report = generator.generate_report(format=args.format, session_name=args.name)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to: {args.output}")
        else:
            print(report)
        
        return 0
    
    elif args.command == "summary":
        # Parse and show quick summary
        for log_path in args.logs:
            if os.path.exists(log_path):
                generator.load_log_file(log_path)
        
        generator.session_name = args.name
        summary = generator.get_summary()
        
        print(f"\n=== {summary['session_name']} Summary ===")
        print(f"Duration:       {summary['duration_minutes']:.1f} minutes")
        print(f"Tool Calls:     {summary['tool_calls']}")
        print(f"Files Touched:  {summary['files_touched']}")
        print(f"Errors:         {summary['errors']} ({summary['errors_resolved']} resolved)")
        print(f"Decisions:      {summary['decisions']}")
        print(f"Milestones:     {summary['milestones']}")
        print()
        
        return 0
    
    elif args.command == "milestone":
        # Load existing report and add milestone
        if not os.path.exists(args.report):
            print(f"Error: Report file not found: {args.report}", file=sys.stderr)
            return 1
        
        with open(args.report, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add milestone
        new_milestone = {
            "milestone_id": f"MS_{len(data.get('milestones', [])) + 1:04d}",
            "title": args.title,
            "timestamp": datetime.now().isoformat(),
            "description": args.description,
            "impact": args.impact,
            "related_decisions": []
        }
        
        if "milestones" not in data:
            data["milestones"] = []
        data["milestones"].append(new_milestone)
        
        # Save updated report
        with open(args.report, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"Added milestone: {args.title}")
        return 0
    
    elif args.command == "stats":
        # Show statistics
        for log_path in args.logs:
            if os.path.exists(log_path):
                generator.load_log_file(log_path)
        
        generator.calculate_metrics()
        
        print("\n=== Tool Usage Statistics ===\n")
        
        # Category breakdown
        category_counts: Dict[str, int] = defaultdict(int)
        tool_counts: Dict[str, int] = defaultdict(int)
        
        for usage in generator.tool_usages:
            category_counts[usage.category] += 1
            tool_counts[usage.tool_name] += 1
        
        total = len(generator.tool_usages)
        
        print("By Category:")
        print("-" * 40)
        for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            pct = (count / total * 100) if total > 0 else 0
            bar = "#" * int(pct / 5)
            print(f"  {cat:12s} {count:4d} ({pct:5.1f}%) {bar}")
        
        print("\nTop 10 Tools:")
        print("-" * 40)
        for name, count in sorted(tool_counts.items(), key=lambda x: -x[1])[:10]:
            pct = (count / total * 100) if total > 0 else 0
            print(f"  {name:30s} {count:4d} ({pct:5.1f}%)")
        
        print(f"\nTotal Tool Calls: {total}")
        print()
        
        return 0
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
