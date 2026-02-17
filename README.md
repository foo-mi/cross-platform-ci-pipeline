# Multi-Platform CI Pipeline

A demonstration of a production-style CI/CD pipeline using **GitHub Actions**, featuring multi-version matrix builds, staged gating, artifact packaging, and automated metrics reporting.

Built to demonstrate DevOps engineering skills for multi-platform developer toolchain environments.
<img width="754" height="477" alt="pipeline" src="https://github.com/user-attachments/assets/95ce809e-1be0-4aef-8727-8a8afb9fa65e" />

---

## Pipeline Architecture

```
Push / PR
    │
    ▼
┌─────────────────────────────────────┐
│  Stage 1: Lint                      │  Matrix: Python 3.10, 3.11, 3.12
│  flake8 style & quality checks      │  fail-fast: false (collect all results)
└──────────────┬──────────────────────┘
               │ needs: lint
               ▼
┌─────────────────────────────────────┐
│  Stage 2: Unit Tests                │  Matrix: Python 3.10, 3.11, 3.12
│  pytest + coverage reporting        │  Uploads per-version coverage artifacts
└──────────────┬──────────────────────┘
               │ needs: test
               ▼
┌─────────────────────────────────────┐
│  Stage 3: Build & Metrics Report    │  Packages artifact
│  run_pipeline.py → job summary      │  Writes metrics to GitHub step summary
└──────────────┬──────────────────────┘
               │ needs: build-and-report
               ▼
┌─────────────────────────────────────┐
│  Stage 4: Regression Gate           │  Verifies artifact integrity
│  Artifact validation + final report │  Writes pass/fail summary table
└─────────────────────────────────────┘
```

## Key Features

- **Matrix builds** across Python 3.10, 3.11, 3.12 — catches version-specific regressions
- **Staged gating** — each stage only runs if the previous passes (`needs:`)
- **`fail-fast: false`** — collects results from all matrix jobs before failing, giving full visibility
- **Metrics reporting** — `run_pipeline.py` times each stage and writes a structured report to the GitHub Actions job summary
- **Artifact packaging** — builds a distributable zip and validates its integrity downstream

## Running Locally

```bash
# Install deps
pip install pytest pytest-cov flake8

# Run the full pipeline locally
python run_pipeline.py

# Run tests only
pytest tests/ -v --cov=src
```

## Project Structure

```
├── .github/
│   └── workflows/
│       └── ci.yml          # Full pipeline definition
├── src/
│   └── pipeline_utils.py   # Core pipeline metrics library
├── tests/
│   └── test_pipeline_utils.py  # Unit tests (15 cases)
├── run_pipeline.py         # Local + CI pipeline runner
└── README.md
```

## Skills Demonstrated

| Skill | Where |
|-------|-------|
| GitHub Actions CI/CD | `.github/workflows/ci.yml` |
| Multi-platform matrix builds | `strategy.matrix` across Python versions |
| Pipeline stage dependency (`needs`) | Lint → Test → Build → Gate |
| Artifact creation & validation | `upload-artifact`, `download-artifact` |
| Python scripting & test automation | `pipeline_utils.py`, `run_pipeline.py` |
| Metrics tracking & reporting | `PipelineReport`, `GITHUB_STEP_SUMMARY` |
| Regression gating | Stage 4 integrity check |
