#!/usr/bin/env python3
"""
Comprehensive test suite for SessionDocGen v1.0

Tests cover:
- Tool usage parsing
- File modification tracking
- Decision parsing
- Error/solution extraction
- Metrics calculation
- Report generation (markdown, JSON, text)
- CLI functionality
- Edge cases and integration

Target: 50+ tests, 100% pass rate

Built by ATLAS (Team Brain) for IRIS
"""

import os
import sys
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from io import StringIO
from unittest.mock import patch, MagicMock

# Import the module under test
from sessiondocgen import (
    ToolUsage,
    FileModification,
    Decision,
    ErrorSolution,
    Milestone,
    SessionMetrics,
    ToolUsageParser,
    FileModificationParser,
    DecisionParser,
    MetricsCalculator,
    ReportGenerator,
    SessionDocGen,
    TOOL_CATEGORIES,
    create_parser,
    main
)


# ============================================================================
# TEST DATA CLASSES
# ============================================================================

class TestToolUsage(unittest.TestCase):
    """Test ToolUsage dataclass."""
    
    def test_create_basic(self):
        """Test basic ToolUsage creation."""
        usage = ToolUsage(
            tool_name="read_file",
            timestamp=datetime.now()
        )
        self.assertEqual(usage.tool_name, "read_file")
        self.assertTrue(usage.success)
        self.assertEqual(usage.duration_ms, 0)
    
    def test_create_with_all_fields(self):
        """Test ToolUsage with all fields."""
        now = datetime.now()
        usage = ToolUsage(
            tool_name="write",
            timestamp=now,
            arguments={"file_path": "test.py"},
            result="Success",
            success=True,
            duration_ms=150,
            category="write"
        )
        self.assertEqual(usage.tool_name, "write")
        self.assertEqual(usage.arguments["file_path"], "test.py")
        self.assertEqual(usage.duration_ms, 150)
    
    def test_to_dict(self):
        """Test ToolUsage.to_dict()."""
        usage = ToolUsage(
            tool_name="grep",
            timestamp=datetime(2026, 1, 25, 10, 30, 0),
            category="search"
        )
        d = usage.to_dict()
        self.assertEqual(d["tool_name"], "grep")
        self.assertEqual(d["category"], "search")
        self.assertIn("timestamp", d)
    
    def test_to_dict_truncates_result(self):
        """Test that to_dict truncates long results."""
        long_result = "x" * 500
        usage = ToolUsage(
            tool_name="read_file",
            timestamp=datetime.now(),
            result=long_result
        )
        d = usage.to_dict()
        self.assertLessEqual(len(d["result"]), 200)


class TestFileModification(unittest.TestCase):
    """Test FileModification dataclass."""
    
    def test_create_basic(self):
        """Test basic FileModification creation."""
        mod = FileModification(
            file_path="test.py",
            modification_type="created",
            timestamp=datetime.now()
        )
        self.assertEqual(mod.file_path, "test.py")
        self.assertEqual(mod.modification_type, "created")
    
    def test_to_dict(self):
        """Test FileModification.to_dict()."""
        mod = FileModification(
            file_path="src/main.py",
            modification_type="edited",
            timestamp=datetime(2026, 1, 25, 10, 30, 0),
            lines_added=50,
            lines_removed=10
        )
        d = mod.to_dict()
        self.assertEqual(d["file_path"], "src/main.py")
        self.assertEqual(d["lines_added"], 50)
        self.assertEqual(d["lines_removed"], 10)


class TestDecision(unittest.TestCase):
    """Test Decision dataclass."""
    
    def test_create_basic(self):
        """Test basic Decision creation."""
        dec = Decision(
            decision_id="DEC_0001",
            description="Chose Python over JavaScript",
            timestamp=datetime.now()
        )
        self.assertEqual(dec.decision_id, "DEC_0001")
        self.assertEqual(dec.category, "")
    
    def test_to_dict(self):
        """Test Decision.to_dict()."""
        dec = Decision(
            decision_id="DEC_0002",
            description="Use SQLite for storage",
            timestamp=datetime(2026, 1, 25, 10, 30, 0),
            category="architecture",
            rationale="Zero dependencies"
        )
        d = dec.to_dict()
        self.assertEqual(d["category"], "architecture")
        self.assertEqual(d["rationale"], "Zero dependencies")


class TestErrorSolution(unittest.TestCase):
    """Test ErrorSolution dataclass."""
    
    def test_create_basic(self):
        """Test basic ErrorSolution creation."""
        err = ErrorSolution(
            error_id="ERR_0001",
            error_type="syntax",
            error_message="Unexpected token",
            timestamp=datetime.now()
        )
        self.assertEqual(err.error_type, "syntax")
        self.assertTrue(err.effective)
    
    def test_to_dict_truncates_message(self):
        """Test that to_dict truncates long error messages."""
        long_msg = "Error: " + "x" * 1000
        err = ErrorSolution(
            error_id="ERR_0002",
            error_type="runtime",
            error_message=long_msg,
            timestamp=datetime.now()
        )
        d = err.to_dict()
        self.assertLessEqual(len(d["error_message"]), 500)


class TestMilestone(unittest.TestCase):
    """Test Milestone dataclass."""
    
    def test_create_basic(self):
        """Test basic Milestone creation."""
        ms = Milestone(
            milestone_id="MS_0001",
            title="MVP Complete",
            timestamp=datetime.now()
        )
        self.assertEqual(ms.title, "MVP Complete")
    
    def test_to_dict(self):
        """Test Milestone.to_dict()."""
        ms = Milestone(
            milestone_id="MS_0002",
            title="All Tests Passing",
            timestamp=datetime(2026, 1, 25, 10, 30, 0),
            impact="major"
        )
        d = ms.to_dict()
        self.assertEqual(d["impact"], "major")


class TestSessionMetrics(unittest.TestCase):
    """Test SessionMetrics dataclass."""
    
    def test_defaults(self):
        """Test default values."""
        metrics = SessionMetrics()
        self.assertEqual(metrics.total_tool_calls, 0)
        self.assertEqual(metrics.duration_minutes, 0.0)
    
    def test_to_dict(self):
        """Test SessionMetrics.to_dict()."""
        metrics = SessionMetrics(
            duration_minutes=45.5,
            total_tool_calls=100,
            successful_tool_calls=98
        )
        d = metrics.to_dict()
        self.assertEqual(d["duration_minutes"], 45.5)
        self.assertEqual(d["total_tool_calls"], 100)


# ============================================================================
# TEST PARSERS
# ============================================================================

class TestToolUsageParser(unittest.TestCase):
    """Test ToolUsageParser."""
    
    def setUp(self):
        self.parser = ToolUsageParser()
    
    def test_parse_empty_content(self):
        """Test parsing empty content."""
        usages, errors = self.parser.parse_content("")
        self.assertEqual(len(usages), 0)
        self.assertEqual(len(errors), 0)
    
    def test_parse_antml_invoke(self):
        """Test parsing antml invoke format."""
        content = '''
        <invoke name="read_file">
        <parameter name="target_file">test.py</parameter>
        </invoke>
        <invoke name="write">
        <parameter name="file_path">output.py</parameter>
        </invoke>
        '''
        usages, _ = self.parser.parse_content(content)
        self.assertEqual(len(usages), 2)
        self.assertEqual(usages[0].tool_name, "read_file")
        self.assertEqual(usages[1].tool_name, "write")
    
    def test_parse_categorizes_tools(self):
        """Test that tools are categorized correctly."""
        content = '<invoke name="grep"></invoke>'
        usages, _ = self.parser.parse_content(content)
        self.assertEqual(len(usages), 1)
        self.assertEqual(usages[0].category, "search")
    
    def test_extract_python_errors(self):
        """Test extracting Python errors."""
        content = '''
        Running script...
        Traceback (most recent call last):
            File "test.py", line 10
                print(x
        SyntaxError: unexpected EOF
        '''
        _, errors = self.parser.parse_content(content)
        self.assertGreater(len(errors), 0)
    
    def test_extract_exit_code_errors(self):
        """Test extracting exit code errors."""
        content = 'Command failed\nExit code: 1\nDone'
        _, errors = self.parser.parse_content(content)
        self.assertGreater(len(errors), 0)
    
    def test_categorize_dependency_error(self):
        """Test dependency error categorization."""
        error_type = self.parser._categorize_error("ModuleNotFoundError: No module named 'requests'")
        self.assertEqual(error_type, "dependency")
    
    def test_categorize_syntax_error(self):
        """Test syntax error categorization."""
        error_type = self.parser._categorize_error("SyntaxError: invalid syntax")
        self.assertEqual(error_type, "syntax")
    
    def test_categorize_network_error(self):
        """Test network error categorization."""
        error_type = self.parser._categorize_error("Connection timeout after 30s")
        self.assertEqual(error_type, "network")
    
    def test_parse_log_file(self):
        """Test parsing from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write('<invoke name="list_dir"></invoke>')
            temp_path = f.name
        
        try:
            usages, _ = self.parser.parse_log_file(temp_path)
            self.assertEqual(len(usages), 1)
        finally:
            os.unlink(temp_path)
    
    def test_parse_log_file_not_found(self):
        """Test FileNotFoundError for missing log file."""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_log_file("/nonexistent/path/log.txt")


class TestFileModificationParser(unittest.TestCase):
    """Test FileModificationParser."""
    
    def setUp(self):
        self.parser = FileModificationParser()
    
    def test_parse_from_tool_usages_write(self):
        """Test extracting modifications from write tool."""
        usages = [
            ToolUsage(
                tool_name="write",
                timestamp=datetime.now(),
                arguments={"file_path": "new_file.py"}
            )
        ]
        mods = self.parser.parse_from_tool_usages(usages)
        self.assertEqual(len(mods), 1)
        self.assertEqual(mods[0].file_path, "new_file.py")
    
    def test_parse_from_tool_usages_search_replace(self):
        """Test extracting modifications from search_replace tool."""
        usages = [
            ToolUsage(
                tool_name="search_replace",
                timestamp=datetime.now(),
                arguments={"file_path": "existing.py"}
            )
        ]
        mods = self.parser.parse_from_tool_usages(usages)
        self.assertEqual(len(mods), 1)
        self.assertEqual(mods[0].modification_type, "edited")
    
    def test_parse_from_tool_usages_delete(self):
        """Test extracting modifications from delete_file tool."""
        usages = [
            ToolUsage(
                tool_name="delete_file",
                timestamp=datetime.now(),
                arguments={"target_file": "old_file.py"}
            )
        ]
        mods = self.parser.parse_from_tool_usages(usages)
        self.assertEqual(len(mods), 1)
        self.assertEqual(mods[0].modification_type, "deleted")
    
    def test_parse_from_git_diff(self):
        """Test parsing git diff output."""
        diff = '''diff --git a/file1.py b/file1.py
index abc123..def456 100644
--- a/file1.py
+++ b/file1.py
@@ -1,3 +1,5 @@
 import os
+import sys
+import json
 
 def main():
-    pass
+    print("Hello")
'''
        mods = self.parser.parse_from_git_diff(diff)
        self.assertEqual(len(mods), 1)
        self.assertEqual(mods[0].file_path, "file1.py")
        self.assertEqual(mods[0].lines_added, 3)
        self.assertEqual(mods[0].lines_removed, 1)
    
    def test_parse_from_git_diff_multiple_files(self):
        """Test parsing git diff with multiple files."""
        diff = '''diff --git a/file1.py b/file1.py
--- a/file1.py
+++ b/file1.py
+line1
diff --git a/file2.py b/file2.py
--- a/file2.py
+++ b/file2.py
+line2
+line3
'''
        mods = self.parser.parse_from_git_diff(diff)
        self.assertEqual(len(mods), 2)


class TestDecisionParser(unittest.TestCase):
    """Test DecisionParser."""
    
    def setUp(self):
        self.parser = DecisionParser()
    
    def test_parse_empty_content(self):
        """Test parsing empty content."""
        decisions = self.parser.parse_content("")
        self.assertEqual(len(decisions), 0)
    
    def test_detect_decision_keyword_decided(self):
        """Test detecting 'decided' keyword."""
        content = "We decided to use Python for this project."
        decisions = self.parser.parse_content(content)
        self.assertEqual(len(decisions), 1)
    
    def test_detect_decision_keyword_chose(self):
        """Test detecting 'chose' keyword."""
        content = "I chose SQLite over PostgreSQL."
        decisions = self.parser.parse_content(content)
        self.assertEqual(len(decisions), 1)
    
    def test_detect_decision_keyword_will_use(self):
        """Test detecting 'will use' keyword."""
        content = "We will use REST API for communication."
        decisions = self.parser.parse_content(content)
        self.assertEqual(len(decisions), 1)
    
    def test_categorize_architecture_decision(self):
        """Test architecture category detection."""
        content = "Decided on microservices architecture."
        decisions = self.parser.parse_content(content)
        self.assertEqual(decisions[0].category, "architecture")
    
    def test_categorize_bug_fix_decision(self):
        """Test bug fix category detection."""
        content = "Decided to fix the bug by adding null check."
        decisions = self.parser.parse_content(content)
        self.assertEqual(decisions[0].category, "bug_fix")
    
    def test_categorize_optimization_decision(self):
        """Test optimization category detection."""
        content = "Chose to optimize the algorithm for better performance."
        decisions = self.parser.parse_content(content)
        self.assertEqual(decisions[0].category, "optimization")
    
    def test_multiple_decisions(self):
        """Test parsing multiple decisions."""
        content = """
        First, we decided to use Python.
        Then we chose Flask over Django.
        Finally, we implemented caching for optimization.
        """
        decisions = self.parser.parse_content(content)
        self.assertGreaterEqual(len(decisions), 2)


# ============================================================================
# TEST METRICS CALCULATOR
# ============================================================================

class TestMetricsCalculator(unittest.TestCase):
    """Test MetricsCalculator."""
    
    def setUp(self):
        self.calculator = MetricsCalculator()
    
    def test_calculate_empty_data(self):
        """Test calculation with empty data."""
        metrics = self.calculator.calculate([], [], [], [], [])
        self.assertEqual(metrics.total_tool_calls, 0)
        self.assertEqual(metrics.files_created, 0)
    
    def test_calculate_tool_calls(self):
        """Test tool call counting."""
        usages = [
            ToolUsage(tool_name="read_file", timestamp=datetime.now(), success=True),
            ToolUsage(tool_name="write", timestamp=datetime.now(), success=True),
            ToolUsage(tool_name="grep", timestamp=datetime.now(), success=False),
        ]
        metrics = self.calculator.calculate(usages, [], [], [], [])
        self.assertEqual(metrics.total_tool_calls, 3)
        self.assertEqual(metrics.successful_tool_calls, 2)
    
    def test_calculate_file_modifications(self):
        """Test file modification counting."""
        mods = [
            FileModification(file_path="a.py", modification_type="created", timestamp=datetime.now()),
            FileModification(file_path="b.py", modification_type="edited", timestamp=datetime.now()),
            FileModification(file_path="c.py", modification_type="edited", timestamp=datetime.now()),
            FileModification(file_path="d.py", modification_type="deleted", timestamp=datetime.now()),
        ]
        metrics = self.calculator.calculate([], mods, [], [], [])
        self.assertEqual(metrics.files_created, 1)
        self.assertEqual(metrics.files_edited, 2)
        self.assertEqual(metrics.files_deleted, 1)
    
    def test_calculate_lines_added_removed(self):
        """Test lines added/removed calculation."""
        mods = [
            FileModification(file_path="a.py", modification_type="edited", 
                           timestamp=datetime.now(), lines_added=100, lines_removed=20),
            FileModification(file_path="b.py", modification_type="edited",
                           timestamp=datetime.now(), lines_added=50, lines_removed=30),
        ]
        metrics = self.calculator.calculate([], mods, [], [], [])
        self.assertEqual(metrics.total_lines_added, 150)
        self.assertEqual(metrics.total_lines_removed, 50)
    
    def test_calculate_unique_files(self):
        """Test unique files counting."""
        mods = [
            FileModification(file_path="a.py", modification_type="edited", timestamp=datetime.now()),
            FileModification(file_path="a.py", modification_type="edited", timestamp=datetime.now()),
            FileModification(file_path="b.py", modification_type="edited", timestamp=datetime.now()),
        ]
        metrics = self.calculator.calculate([], mods, [], [], [])
        self.assertEqual(metrics.unique_files_touched, 2)
    
    def test_calculate_errors(self):
        """Test error counting."""
        errors = [
            ErrorSolution(error_id="E1", error_type="syntax", error_message="", 
                         timestamp=datetime.now(), effective=True),
            ErrorSolution(error_id="E2", error_type="runtime", error_message="",
                         timestamp=datetime.now(), effective=False),
        ]
        metrics = self.calculator.calculate([], [], errors, [], [])
        self.assertEqual(metrics.errors_encountered, 2)
        self.assertEqual(metrics.errors_resolved, 1)
    
    def test_calculate_duration_from_timestamps(self):
        """Test duration calculation from tool timestamps."""
        start = datetime.now()
        end = start + timedelta(minutes=30)
        usages = [
            ToolUsage(tool_name="read", timestamp=start),
            ToolUsage(tool_name="write", timestamp=end),
        ]
        metrics = self.calculator.calculate(usages, [], [], [], [])
        self.assertAlmostEqual(metrics.duration_minutes, 30.0, places=1)
    
    def test_calculate_duration_with_explicit_times(self):
        """Test duration calculation with explicit start/end times."""
        start = datetime(2026, 1, 25, 10, 0, 0)
        end = datetime(2026, 1, 25, 11, 30, 0)
        metrics = self.calculator.calculate([], [], [], [], [], start, end)
        self.assertEqual(metrics.duration_minutes, 90.0)


# ============================================================================
# TEST REPORT GENERATOR
# ============================================================================

class TestReportGenerator(unittest.TestCase):
    """Test ReportGenerator."""
    
    def setUp(self):
        self.generator = ReportGenerator()
        self.setup_sample_data()
    
    def setup_sample_data(self):
        """Set up sample data for report generation."""
        now = datetime.now()
        
        self.tool_usages = [
            ToolUsage(tool_name="read_file", timestamp=now, category="read"),
            ToolUsage(tool_name="write", timestamp=now, category="write"),
            ToolUsage(tool_name="grep", timestamp=now, category="search"),
        ]
        
        self.file_mods = [
            FileModification(file_path="test.py", modification_type="created",
                           timestamp=now, lines_added=100),
        ]
        
        self.errors = [
            ErrorSolution(error_id="ERR_0001", error_type="syntax",
                        error_message="Invalid syntax", timestamp=now,
                        solution="Fixed indentation", effective=True),
        ]
        
        self.decisions = [
            Decision(decision_id="DEC_0001", description="Use Python",
                    timestamp=now, category="architecture"),
        ]
        
        self.milestones = [
            Milestone(milestone_id="MS_0001", title="MVP Complete",
                     timestamp=now, impact="major"),
        ]
        
        self.metrics = SessionMetrics(
            duration_minutes=45.0,
            total_tool_calls=3,
            successful_tool_calls=3,
            files_created=1
        )
    
    def test_generate_markdown_basic(self):
        """Test basic markdown generation."""
        self.generator.set_data(
            self.tool_usages, self.file_mods, self.errors,
            self.decisions, self.milestones, self.metrics
        )
        report = self.generator.generate_markdown("Test Session")
        
        self.assertIn("# Test Session Summary", report)
        self.assertIn("Quick Stats", report)
        self.assertIn("Tool Usage Breakdown", report)
    
    def test_generate_markdown_has_metrics_table(self):
        """Test that markdown contains metrics table."""
        self.generator.set_data(
            self.tool_usages, self.file_mods, self.errors,
            self.decisions, self.milestones, self.metrics
        )
        report = self.generator.generate_markdown()
        
        self.assertIn("| Metric | Value |", report)
        self.assertIn("Total Tool Calls", report)
    
    def test_generate_json_basic(self):
        """Test basic JSON generation."""
        self.generator.set_data(
            self.tool_usages, self.file_mods, self.errors,
            self.decisions, self.milestones, self.metrics
        )
        report = self.generator.generate_json("Test Session")
        
        data = json.loads(report)
        self.assertEqual(data["session_name"], "Test Session")
        self.assertIn("metrics", data)
        self.assertIn("tool_usages", data)
    
    def test_generate_json_valid_structure(self):
        """Test JSON report has valid structure."""
        self.generator.set_data(
            self.tool_usages, self.file_mods, self.errors,
            self.decisions, self.milestones, self.metrics
        )
        report = self.generator.generate_json()
        
        data = json.loads(report)
        self.assertIsInstance(data["tool_usages"], list)
        self.assertIsInstance(data["metrics"], dict)
    
    def test_generate_text_basic(self):
        """Test basic text generation."""
        self.generator.set_data(
            self.tool_usages, self.file_mods, self.errors,
            self.decisions, self.milestones, self.metrics
        )
        report = self.generator.generate_text("Test Session")
        
        self.assertIn("TEST SESSION SUMMARY", report)
        self.assertIn("METRICS", report)
    
    def test_generate_text_has_stats(self):
        """Test that text report contains stats."""
        self.generator.set_data(
            self.tool_usages, self.file_mods, self.errors,
            self.decisions, self.milestones, self.metrics
        )
        report = self.generator.generate_text()
        
        self.assertIn("Tool Calls:", report)
        self.assertIn("Files Created:", report)


# ============================================================================
# TEST SESSION DOC GEN MAIN CLASS
# ============================================================================

class TestSessionDocGen(unittest.TestCase):
    """Test SessionDocGen main class."""
    
    def setUp(self):
        self.generator = SessionDocGen()
    
    def test_init(self):
        """Test initialization."""
        self.assertIsNotNone(self.generator.tool_parser)
        self.assertEqual(len(self.generator.tool_usages), 0)
    
    def test_load_content(self):
        """Test loading content string."""
        content = '<invoke name="read_file"></invoke>'
        self.generator.load_content(content)
        self.assertGreater(len(self.generator.tool_usages), 0)
    
    def test_load_log_file(self):
        """Test loading from log file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write('<invoke name="grep"></invoke>')
            temp_path = f.name
        
        try:
            self.generator.load_log_file(temp_path)
            self.assertGreater(len(self.generator.tool_usages), 0)
        finally:
            os.unlink(temp_path)
    
    def test_add_milestone(self):
        """Test adding milestone."""
        ms_id = self.generator.add_milestone("Test Complete", "All tests pass", "major")
        self.assertEqual(len(self.generator.milestones), 1)
        self.assertIn("MS_", ms_id)
    
    def test_add_decision(self):
        """Test adding decision."""
        dec_id = self.generator.add_decision("Use REST API", "architecture", "Simple and standard")
        self.assertEqual(len(self.generator.decisions), 1)
        self.assertIn("DEC_", dec_id)
    
    def test_add_error_solution(self):
        """Test adding error-solution pair."""
        err_id = self.generator.add_error_solution(
            "ModuleNotFoundError", "dependency",
            "pip install missing_module", True
        )
        self.assertEqual(len(self.generator.errors), 1)
        self.assertIn("ERR_", err_id)
    
    def test_calculate_metrics(self):
        """Test metrics calculation."""
        self.generator.load_content('<invoke name="read_file"></invoke>')
        metrics = self.generator.calculate_metrics()
        self.assertEqual(metrics.total_tool_calls, 1)
    
    def test_generate_report_markdown(self):
        """Test generating markdown report."""
        self.generator.load_content('<invoke name="write"></invoke>')
        report = self.generator.generate_report("markdown", "Test")
        self.assertIn("Test Summary", report)
    
    def test_generate_report_json(self):
        """Test generating JSON report."""
        self.generator.load_content('<invoke name="grep"></invoke>')
        report = self.generator.generate_report("json", "Test")
        data = json.loads(report)
        self.assertEqual(data["session_name"], "Test")
    
    def test_generate_report_text(self):
        """Test generating text report."""
        self.generator.load_content('<invoke name="list_dir"></invoke>')
        report = self.generator.generate_report("text", "Test")
        self.assertIn("TEST", report)
    
    def test_generate_report_invalid_format(self):
        """Test error on invalid format."""
        with self.assertRaises(ValueError):
            self.generator.generate_report("invalid_format")
    
    def test_save_report(self):
        """Test saving report to file."""
        self.generator.load_content('<invoke name="read_file"></invoke>')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            temp_path = f.name
        
        try:
            self.generator.save_report(temp_path, "markdown", "Test")
            self.assertTrue(os.path.exists(temp_path))
            
            with open(temp_path, 'r') as f:
                content = f.read()
            self.assertIn("Test Summary", content)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_get_summary(self):
        """Test getting quick summary."""
        self.generator.load_content('<invoke name="write"></invoke>')
        summary = self.generator.get_summary()
        self.assertIn("tool_calls", summary)
        self.assertEqual(summary["tool_calls"], 1)
    
    def test_reset(self):
        """Test reset functionality."""
        self.generator.load_content('<invoke name="grep"></invoke>')
        self.generator.add_milestone("Test", "Desc", "minor")
        
        self.generator.reset()
        
        self.assertEqual(len(self.generator.tool_usages), 0)
        self.assertEqual(len(self.generator.milestones), 0)
    
    def test_load_git_diff(self):
        """Test loading git diff."""
        diff = '''diff --git a/test.py b/test.py
+new line
'''
        self.generator.load_git_diff(diff)
        self.assertGreater(len(self.generator.file_modifications), 0)


# ============================================================================
# TEST CLI
# ============================================================================

class TestCLI(unittest.TestCase):
    """Test CLI functionality."""
    
    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        self.assertIsNotNone(parser)
    
    def test_parse_command(self):
        """Test parse command parsing."""
        parser = create_parser()
        args = parser.parse_args(["parse", "test.log", "-o", "out.md"])
        self.assertEqual(args.command, "parse")
        self.assertEqual(args.logs, ["test.log"])
        self.assertEqual(args.output, "out.md")
    
    def test_parse_command_format(self):
        """Test parse command with format option."""
        parser = create_parser()
        args = parser.parse_args(["parse", "test.log", "-f", "json"])
        self.assertEqual(args.format, "json")
    
    def test_summary_command(self):
        """Test summary command parsing."""
        parser = create_parser()
        args = parser.parse_args(["summary", "log1.txt", "log2.txt"])
        self.assertEqual(args.command, "summary")
        self.assertEqual(len(args.logs), 2)
    
    def test_milestone_command(self):
        """Test milestone command parsing."""
        parser = create_parser()
        args = parser.parse_args(["milestone", "MVP Done", "-r", "report.json"])
        self.assertEqual(args.command, "milestone")
        self.assertEqual(args.title, "MVP Done")
        self.assertEqual(args.report, "report.json")
    
    def test_stats_command(self):
        """Test stats command parsing."""
        parser = create_parser()
        args = parser.parse_args(["stats", "session.log"])
        self.assertEqual(args.command, "stats")
    
    def test_main_no_command(self):
        """Test main with no command shows help."""
        with patch('sys.argv', ['sessiondocgen']):
            result = main()
            self.assertEqual(result, 0)
    
    def test_main_parse_command(self):
        """Test main with parse command."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write('<invoke name="read_file"></invoke>')
            temp_path = f.name
        
        try:
            with patch('sys.argv', ['sessiondocgen', 'parse', temp_path]):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    result = main()
                    self.assertEqual(result, 0)
        finally:
            os.unlink(temp_path)
    
    def test_main_summary_command(self):
        """Test main with summary command."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write('<invoke name="write"></invoke>')
            temp_path = f.name
        
        try:
            with patch('sys.argv', ['sessiondocgen', 'summary', temp_path]):
                with patch('sys.stdout', new_callable=StringIO):
                    result = main()
                    self.assertEqual(result, 0)
        finally:
            os.unlink(temp_path)


# ============================================================================
# TEST EDGE CASES
# ============================================================================

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_parse_malformed_content(self):
        """Test parsing malformed content."""
        parser = ToolUsageParser()
        # Should not raise exception
        usages, errors = parser.parse_content("<<<malformed>>>not valid<<<")
        # May or may not find anything, but shouldn't crash
        self.assertIsInstance(usages, list)
    
    def test_empty_file_modifications(self):
        """Test with no file modifications."""
        generator = SessionDocGen()
        generator.load_content("Just text, no tool calls")
        report = generator.generate_report("markdown")
        self.assertIn("No file modifications tracked", report)
    
    def test_unicode_content(self):
        """Test handling unicode content."""
        parser = ToolUsageParser()
        content = '<invoke name="read_file"></invoke> Unicode: '
        usages, _ = parser.parse_content(content)
        self.assertGreater(len(usages), 0)
    
    def test_very_long_content(self):
        """Test handling very long content."""
        parser = ToolUsageParser()
        content = '<invoke name="read_file"></invoke>\n' * 1000
        usages, _ = parser.parse_content(content)
        self.assertEqual(len(usages), 1000)
    
    def test_mixed_tool_formats(self):
        """Test content with mixed tool call formats."""
        parser = ToolUsageParser()
        content = '''
        <invoke name="read_file"></invoke>
        <invoke name="write"></invoke>
        '''
        usages, _ = parser.parse_content(content)
        self.assertEqual(len(usages), 2)
    
    def test_report_with_no_data(self):
        """Test generating report with no data."""
        generator = SessionDocGen()
        report = generator.generate_report("markdown", "Empty Session")
        self.assertIn("Empty Session Summary", report)


# ============================================================================
# TEST INTEGRATION
# ============================================================================

class TestIntegration(unittest.TestCase):
    """Integration tests for full workflow."""
    
    def test_full_workflow(self):
        """Test complete workflow from parse to report."""
        # Create test log content
        log_content = '''
        Starting session...
        <invoke name="read_file">
        <parameter name="target_file">main.py</parameter>
        </invoke>
        Reading file complete.
        
        <invoke name="write">
        <parameter name="file_path">output.py</parameter>
        </invoke>
        File written.
        
        Error: SyntaxError: invalid syntax
        Fixed by correcting indentation.
        
        We decided to use async/await for better performance.
        
        <invoke name="grep">
        <parameter name="pattern">TODO</parameter>
        </invoke>
        '''
        
        # Write to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write(log_content)
            temp_path = f.name
        
        try:
            # Process
            generator = SessionDocGen()
            generator.session_name = "Integration Test"
            generator.load_log_file(temp_path)
            generator.add_milestone("Phase 1 Complete", "Initial setup done", "major")
            
            # Generate all report formats
            md_report = generator.generate_report("markdown")
            json_report = generator.generate_report("json")
            text_report = generator.generate_report("text")
            
            # Verify markdown
            self.assertIn("Integration Test Summary", md_report)
            self.assertIn("Tool Usage Breakdown", md_report)
            
            # Verify JSON
            data = json.loads(json_report)
            self.assertGreater(len(data["tool_usages"]), 0)
            
            # Verify text
            self.assertIn("INTEGRATION TEST", text_report)
            
            # Verify metrics
            summary = generator.get_summary()
            self.assertGreater(summary["tool_calls"], 0)
            
        finally:
            os.unlink(temp_path)
    
    def test_multiple_log_files(self):
        """Test combining multiple log files."""
        # Create two log files
        logs = []
        for i in range(2):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
                f.write(f'<invoke name="read_file{i}"></invoke>')
                logs.append(f.name)
        
        try:
            generator = SessionDocGen()
            for log_path in logs:
                generator.load_log_file(log_path)
            
            metrics = generator.calculate_metrics()
            self.assertEqual(metrics.total_tool_calls, 2)
        finally:
            for log_path in logs:
                os.unlink(log_path)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
