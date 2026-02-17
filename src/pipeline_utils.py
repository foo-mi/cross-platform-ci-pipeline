"""
pipeline_utils.py
Utility functions for a DevOps metrics and build pipeline.
Demonstrates Python scripting skills relevant to CI/CD automation.
"""

import time
import platform
import sys
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BuildMetric:
    name: str
    status: str          # "pass" | "fail" | "skip"
    duration_ms: float
    details: Optional[str] = None


@dataclass
class PipelineReport:
    python_version: str = field(default_factory=lambda: sys.version.split()[0])
    platform: str = field(default_factory=platform.system)
    metrics: List[BuildMetric] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)

    def add_metric(self, metric: BuildMetric):
        self.metrics.append(metric)

    @property
    def total_duration_ms(self) -> float:
        return (time.time() - self.start_time) * 1000

    @property
    def passed(self) -> int:
        return sum(1 for m in self.metrics if m.status == "pass")

    @property
    def failed(self) -> int:
        return sum(1 for m in self.metrics if m.status == "fail")

    @property
    def skipped(self) -> int:
        return sum(1 for m in self.metrics if m.status == "skip")

    def summary(self) -> str:
        lines = [
            "=" * 55,
            f"  PIPELINE REPORT — Python {self.python_version} on {self.platform}",
            "=" * 55,
            f"  {'Stage':<25} {'Status':<8} {'Duration':>10}",
            "  " + "-" * 47,
        ]
        for m in self.metrics:
            icon = "✓" if m.status == "pass" else ("✗" if m.status == "fail" else "–")
            lines.append(f"  {icon} {m.name:<24} {m.status.upper():<8} {m.duration_ms:>7.1f} ms")
            if m.details:
                lines.append(f"    ↳ {m.details}")
        lines += [
            "  " + "-" * 47,
            f"  Total: {self.passed} passed, {self.failed} failed, {self.skipped} skipped",
            f"  Pipeline duration: {self.total_duration_ms:.1f} ms",
            "=" * 55,
        ]
        return "\n".join(lines)


def timed_step(name: str, fn, report: PipelineReport, skip=False) -> bool:
    """Run a pipeline step, record its metric, return True if passed."""
    if skip:
        report.add_metric(BuildMetric(name=name, status="skip", duration_ms=0))
        return True
    t0 = time.time()
    try:
        detail = fn()
        duration = (time.time() - t0) * 1000
        report.add_metric(BuildMetric(name=name, status="pass",
                                      duration_ms=duration, details=detail))
        return True
    except Exception as e:
        duration = (time.time() - t0) * 1000
        report.add_metric(BuildMetric(name=name, status="fail",
                                      duration_ms=duration, details=str(e)))
        return False
