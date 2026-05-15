# Multi-objective Diet Optimization

Project for the Bioinspired Algorithms for Optimization (BAO) course.

This repository is organised around one reproducible pipeline:

1. Run `main.ipynb` to generate tuning results, benchmark runs, statistical summaries and figures.
2. Use those artifacts in `report.tex`.
3. Optionally run `python experiments/emit_latex.py` to print LaTeX-ready table rows from generated CSVs.

## Core objective

A weekly meal plan (7 days x 5 meals x structured slots) is optimized with two minimization objectives:

- **f1**: per-day calorie deviation from the subject target.
- **f2**: per-day macronutrient deviation from the split 50% carbohydrates, 27.5% fat, 22.5% protein.

## Precise repository structure

Only the files and directories involved in `main.ipynb` and/or `report.tex` are listed below.

```
main.ipynb                 End-to-end experiment pipeline.
report.tex                 Technical report (Beamer slides).
presentation.tex           10-minute academic presentation (Beamer slides).

requirements.txt           Python dependencies.
pyproject.toml             Package metadata for editable install.
.env.example               Database environment variable template.

diet_bao/
  __init__.py
  data.py                  Loads foods and subject profiles from MySQL.
  types.py                 Typed structures for foods and subjects.
  encoding.py              Slot/domain construction for 77-gene plans.
  fitness.py               f1/f2 fitness definitions.

  representations/
    base.py
    direct_index.py
    random_key.py

  metrics/
    hypervolume.py
    igd.py
    spread.py

  ea/
    nsga2_diet.py          NSGA-II (inspyred-based).
    paes_diet.py           PAES (inspyred-based).

  si/
    pareto_archive.py
    mopso_diet.py          Native Pareto MOPSO.
    paco_diet.py           Native Pareto ACO.

  experiment/
    __init__.py            Exposes notebook-used API.
    experiment_loader.py   AlgorithmConfig, BenchmarkPlan, run_all_subjects.
    tuning.py              Hyperparameter grid search and winner selection.
    stats.py               Summary/statistical artifact generation.
    visualization.py       Plot helpers used by the notebook.

stac/
  stat_tests.py            Wilcoxon, Friedman aligned ranks, Shaffer/Holm.

experiments/
  all_runs.csv             Full benchmark results (750 runs).
  tuning_results.csv       Hyperparameter tuning sweep results.
  tuning_best.csv          Best hyperparameters per algorithm.
  summary.csv              Aggregated metrics by configuration.
  friedman_aligned.csv     Friedman aligned ranks test output.
  pairwise_hv.csv          Wilcoxon pairwise HV comparisons.
  pairwise_hv_shaffer.csv  Wilcoxon results with Shaffer correction.
  demo_overview.png        Convergence and diversity visualization.
  boxplots.png             Hypervolume distribution across configurations.
  best_pts_subject_1.png   Pareto front example for subject 1.
```

## Setup and execution

1. Restore `food_database_dump.sql` (NutritionPlanning) in MySQL or MariaDB.
2. Copy `.env.example` to `.env` and set DB credentials.
3. Install dependencies:

   Windows PowerShell:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   pip install -e .
   ```

   macOS/Linux:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -e .
   ```

4. Run all cells in `main.ipynb`.
5. Compile `report.tex`.
6. Optional: `python experiments/emit_latex.py` to refresh table rows.

## Algorithms in this repository

- **NSGA-II** and **PAES**: implemented through `inspyred.ec.emo` wrappers.
- **MOPSO** and **P-ACO**: native project implementations with Pareto archives.
