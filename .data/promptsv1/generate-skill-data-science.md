# Data Science Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are data-science-specific overrides.

```
ROLE:     Senior data scientist/ML engineer analyzing a data-focused codebase
GOAL:     Generate a production-grade data science skill directory
SCOPE:    Data processing, ML pipelines, notebooks, experiment tracking only — ignore web app code, API layer, infrastructure
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Data Science Only

Ignore web application code, API layers, and infrastructure. Scan for:

**Language & Environment**

- Primary language (Python, R, Julia, Scala)
- Python version and virtual environment tool (venv, conda, poetry, uv, pyenv)
- Package manager + dependency file (requirements.txt, pyproject.toml, environment.yml, setup.cfg)
- Jupyter environment (JupyterLab, VS Code notebooks, Google Colab, Databricks)
- Key dependencies and version pinning strategy

**Data Processing**

- DataFrame library (pandas, polars, dask, vaex, modin, PySpark)
- Data loading patterns (CSV, Parquet, Arrow, HDF5, database connectors)
- Data validation framework (Great Expectations, Pandera, pydantic, cerberus)
- ETL/ELT pipeline tools (Airflow, Prefect, Dagster, Luigi, dbt)
- Data versioning (DVC, LakeFS, Delta Lake, none)
- Data storage (local files, S3, GCS, HDFS, data warehouse)

**ML Frameworks & Patterns**

- ML framework (scikit-learn, PyTorch, TensorFlow, JAX, XGBoost, LightGBM)
- Pipeline abstraction (sklearn Pipeline, PyTorch Lightning, Keras Sequential, custom)
- Model serialization (pickle, joblib, ONNX, TorchScript, SavedModel)
- Hyperparameter tuning (Optuna, Ray Tune, GridSearchCV, Hyperopt)
- AutoML usage (auto-sklearn, FLAML, H2O, none)
- Deep learning patterns (custom training loops, callbacks, mixed precision)

**Experiment Tracking & Reproducibility**

- Experiment tracker (MLflow, Weights & Biases, Neptune, DVC, Comet, none)
- Metric logging conventions (what is tracked, naming patterns)
- Random seed management (global seeds, per-experiment seeds, none)
- Reproducibility practices (pinned deps, versioned data, deterministic training)
- Model registry (MLflow Model Registry, SageMaker, Vertex AI, custom)

**Notebook Patterns**

- Notebook organization (exploratory vs production, naming conventions)
- Notebook execution (papermill, nbconvert, Ploomber, manual)
- Notebook-to-script conversion patterns (nbdev, jupytext, manual refactor)
- Cell organization (imports, config, data load, processing, modeling, evaluation)
- Output management (cleared outputs, stored outputs, widget state)

**Feature Engineering**

- Feature store (Feast, Tecton, Hopsworks, custom, none)
- Feature engineering patterns (sklearn transformers, custom functions, SQL-based)
- Encoding strategies (one-hot, target, ordinal, embeddings)
- Scaling/normalization patterns
- Feature selection methods (statistical, model-based, domain-driven)

**Visualization**

- Plotting libraries (matplotlib, seaborn, plotly, altair, bokeh)
- Style/theme conventions (custom stylesheets, corporate palette)
- Dashboard tools (Streamlit, Gradio, Dash, Panel, none)
- Report generation (nbconvert, Quarto, Jupyter Book, none)

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_data_science.md`:

1. **Data Architecture** — how this project structures data pipelines, storage, and processing
2. **Coding Conventions** — style, naming, notebook structure conventions
3. **Package Patterns** — key packages and idiomatic usage (pandas vs polars, sklearn vs PyTorch)
4. **Things to ALWAYS do** — non-negotiable patterns observed (e.g., seed everything, validate inputs, log experiments)
5. **Things to NEVER do** — anti-patterns explicitly avoided (e.g., hardcoded paths, unversioned data, training without validation)
6. **ML Pipeline Wisdom** — patterns unique to the detected framework and pipeline design
7. **Reproducibility Conventions** — how this project ensures reproducible results

---

## PHASE 3: BEST PRACTICES

Integrate for the detected framework/tooling:

- Reproducibility: pin all dependencies, version data, set random seeds everywhere (Priority 1)
- Data validation at pipeline boundaries — never trust upstream data (Priority 1)
- Train/validation/test split integrity — no data leakage across splits (Priority 1)
- Experiment tracking for every training run — log params, metrics, artifacts (Priority 1)
- Feature engineering in reusable transformers, not ad-hoc notebook cells (Priority 2)
- Notebook hygiene: restart-and-run-all must succeed, no hidden state (Priority 2)
- Memory management: chunked processing, lazy evaluation, dtype optimization (Priority 2)
- Model evaluation beyond accuracy — fairness, calibration, confidence intervals (Priority 2)
- Pipeline idempotency — re-running produces identical results (Priority 2)
- Visualization: label axes, title plots, use colorblind-safe palettes (Priority 3)
- Model serving: separate training and inference code, version endpoints (Priority 3)
- Security: no credentials in notebooks, sanitize PII in datasets (Priority 1)
- Cost awareness: GPU utilization, spot instances, data transfer costs (Priority 3)
- Documentation: docstrings on all transforms, README per experiment (Priority 3)
- Testing: unit test transforms, integration test pipelines, validate model outputs (Priority 2)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY data science task — data loading, cleaning, feature engineering, model training, evaluation, experiment tracking, notebook creation, visualization, pipeline design, hyperparameter tuning, model deployment, data validation, ML debugging.

**`allowed-tools`**: `Read Edit Write Bash(python:*) Bash(jupyter:*) Bash(pip:*) Bash(uv:*) Glob Grep`

**Body sections** (all required in SKILL.md):

| # | Section | Content |
| -- | ------- | ------- |
| 1 | **When to Use** | 4-6 trigger conditions (data processing, model training, notebook work, experiment tracking, feature engineering, ML pipeline design) |
| 2 | **Do NOT Use** | Cross-references to sibling skills (backend for API code, frontend for dashboards, infra for cluster provisioning) |
| 3 | **Data Architecture** | Data flow diagram, storage locations, pipeline stages, key directories |
| 4 | **ML Pipeline Patterns** | Summary table only (pattern name, approach, key rule). Full code examples in references/ only |
| 5 | **Notebook Standards** | Rules table only. Cell ordering, naming, output management, execution rules in references/notebook-standards.md |
| 6 | **Common Recipes** | Numbered step lists only, no code blocks (data loading, feature engineering, training, evaluation) |
| 7 | **Experiment Tracking** | Rules list + link to references/experiment-tracking.md |
| 8 | **Reproducibility Rules** | Bullet list, no code examples (seeds, versioning, determinism) |
| 9 | **Data Quality** | Summary + link to references/data-validation-checklist.md for per-dataset verification |
| 10 | **Anti-Patterns** | What NOT to do (with why) — data leakage, unversioned models, notebook hidden state |
| 11 | **References** | Key files, docs, resources |
| 12 | **Adaptive Interaction Protocols** | Interaction modes with data-science-specific detection signals (e.g., "model accuracy dropped" for Diagnostic, "train another model" for Efficient, "what is cross-validation" for Teaching), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md |

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/notebook-standards.md` — cell ordering, naming conventions, execution rules with full examples
- `references/experiment-tracking.md` — logging conventions, metric naming, artifact management
- `references/data-validation-checklist.md` — per-dataset, per-pipeline validation checklists
- `references/ml-pipeline-patterns.md` — pipeline design patterns with full code examples
- `references/feature-engineering.md` — transformer patterns, encoding strategies, feature store usage
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `references/visualization-guide.md` — plotting conventions, style templates, accessibility rules
- `references/common-issues.md` — troubleshooting common data science pitfalls
- `assets/notebook-template.ipynb` — starter notebook with standard cell structure
- `scripts/validate-data-science.sh` — reproducibility + notebook hygiene checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent                | Role                                                        | Tools                | Spawn When                                                        |
| -------------------- | ----------------------------------------------------------- | -------------------- | ----------------------------------------------------------------- |
| data-quality-checker | Data validation, profiling, and schema verification         | Read Glob Grep Bash  | New data source, pipeline change, data drift suspected            |
| notebook-reviewer    | Notebook best practices audit and hygiene check             | Read Glob Grep       | PR with notebooks, notebook cleanup, pre-publication review       |
| pipeline-auditor     | ML pipeline reproducibility and correctness check           | Read Glob Grep       | Pipeline change, experiment reproducibility failure, model review |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/data-quality-checker.md` — data validation and profiling agent
- `agents/notebook-reviewer.md` — notebook best practices audit agent
- `agents/pipeline-auditor.md` — ML pipeline reproducibility verification agent
