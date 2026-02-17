"""
tests/test_pipeline_utils.py
Unit tests for the pipeline_utils module.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from pipeline_utils import BuildMetric, PipelineReport, timed_step


# ── BuildMetric ──────────────────────────────────────────────────────────

class TestBuildMetric:
    def test_fields_set_correctly(self):
        m = BuildMetric(name="lint", status="pass", duration_ms=42.5, details="clean")
        assert m.name == "lint"
        assert m.status == "pass"
        assert m.duration_ms == 42.5
        assert m.details == "clean"

    def test_details_optional(self):
        m = BuildMetric(name="build", status="fail", duration_ms=10.0)
        assert m.details is None


# ── PipelineReport ────────────────────────────────────────────────────────

class TestPipelineReport:
    def _report_with_metrics(self):
        r = PipelineReport()
        r.add_metric(BuildMetric("lint",  "pass", 10.0))
        r.add_metric(BuildMetric("test",  "fail", 20.0))
        r.add_metric(BuildMetric("build", "skip",  0.0))
        return r

    def test_passed_count(self):
        r = self._report_with_metrics()
        assert r.passed == 1

    def test_failed_count(self):
        r = self._report_with_metrics()
        assert r.failed == 1

    def test_skipped_count(self):
        r = self._report_with_metrics()
        assert r.skipped == 1

    def test_summary_contains_stage_names(self):
        r = self._report_with_metrics()
        s = r.summary()
        assert "lint" in s
        assert "test" in s
        assert "build" in s

    def test_summary_contains_pass_fail(self):
        r = self._report_with_metrics()
        s = r.summary()
        assert "PASS" in s
        assert "FAIL" in s

    def test_total_duration_positive(self):
        r = PipelineReport()
        time.sleep(0.01)
        assert r.total_duration_ms > 0

    def test_python_version_populated(self):
        r = PipelineReport()
        assert len(r.python_version) > 0

    def test_platform_populated(self):
        r = PipelineReport()
        assert len(r.platform) > 0


# ── timed_step ────────────────────────────────────────────────────────────

class TestTimedStep:
    def test_successful_step_returns_true(self):
        r = PipelineReport()
        result = timed_step("ok", lambda: "done", r)
        assert result is True
        assert r.metrics[0].status == "pass"

    def test_failing_step_returns_false(self):
        r = PipelineReport()
        def boom():
            raise ValueError("something broke")
        result = timed_step("bad", boom, r)
        assert result is False
        assert r.metrics[0].status == "fail"
        assert "something broke" in r.metrics[0].details

    def test_skip_records_skip_status(self):
        r = PipelineReport()
        result = timed_step("skipped_step", lambda: "x", r, skip=True)
        assert result is True
        assert r.metrics[0].status == "skip"
        assert r.metrics[0].duration_ms == 0

    def test_step_detail_captured(self):
        r = PipelineReport()
        timed_step("detail_test", lambda: "my detail", r)
        assert r.metrics[0].details == "my detail"

    def test_duration_recorded(self):
        r = PipelineReport()
        def slow():
            time.sleep(0.05)
        timed_step("slow_step", slow, r)
        assert r.metrics[0].duration_ms >= 40  # at least 40ms
