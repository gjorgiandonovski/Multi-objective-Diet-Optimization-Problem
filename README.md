# Multi-objective Diet Optimization

Project for the Bioinspired Algorithms for Optimization (BAO) course.

A weekly meal plan (7 days x 5 meals x structured slots) is built from a real food database to simultaneously minimise:

- **f1**: per-day calorie deviation from the user's target.
- **f2**: per-day macronutrient deviation from the assignment-specified split (50% carbohydrates, 27.5% fat, 22.5% protein).

## Coverage of the assignment requirements

| Requirement | Implementation |
|---|---|
| At least 1 evolutionary algorithm | `diet_bao/ea/nsga2_diet.py`, `diet_bao/ea/paes_diet.py` |
| At least 1 swarm intelligence algorithm | `diet_bao/si/pso_diet.py` (scalarised) |
| Different representations compared | `diet_bao/representations/{direct_index,random_key}.py` |
| Different constraint handlers compared | `diet_bao/constraints/{repair,penalty,death_penalty}.py` |
| Multi-objective metrics | `diet_bao/metrics/{hypervolume,igd,spread}.py` |
| 30+ replicates per configuration | `BenchmarkPlan(n_runs=30)` in `experiment_loader.py` |
| Quality + runtime comparison | `summarize_results()` plus boxplots in `main.ipynb` |
| Convergence + diversity plots | `diet_bao/experiment/visualization.py` |
| Statistical significance tests | `stac/stat_tests.py` (Wilcoxon signed-ranks, Friedman aligned ranks, Shaffer + Holm corrections) |
| inspyred library | NSGA-II and PAES wrap `inspyred.ec.emo`. PSO wraps `inspyred.swarm.PSO`. |

Optional advanced techniques (allowed by the assignment) are implemented:

- **Parallel experiment execution** via `BenchmarkPlan(n_jobs>1)` in `diet_bao/experiment/experiment_loader.py`.
- **Memetic NSGA-II variant** via `memetic_rate>0` in `diet_bao/ea/nsga2_diet.py`.

## Project structure

```
diet_bao/
  data.py                  MySQL loaders
  encoding.py              food-group filtering (mirrors funciones_auxiliares.py)
  fitness.py               f1 (per-day calorie dev) + f2 (per-day macro dev)
  representations/         direct_index | random_key
  constraints/             repair | penalty | death_penalty
  metrics/                 hypervolume, IGD, Schott spacing
  ea/
    nsga2_diet.py          NSGA-II via inspyred
    paes_diet.py           PAES via inspyred
  si/
    pso_diet.py            scalarised PSO via inspyred
  experiment/
    experiment_loader.py   AlgorithmConfig, BenchmarkPlan, run_all_subjects
    visualization.py       convergence, Pareto, diversity plots
stac/
  stat_tests.py            Wilcoxon, Friedman aligned ranks, Shaffer + Holm, average ranks
tests/                     unit and integration tests
main.ipynb                 experiment notebook
verify_db.py               database connection check
smoke_test.py              short end-to-end pipeline check
```

## Setup

1. Restore `food_database_dump.sql` (from the NutritionPlanning repository) into MySQL or MariaDB.
2. Copy `.env.example` to `.env` and set the MySQL credentials.
3. Create a virtual environment and install the package.

   macOS/Linux:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -e .
   ```

   Windows PowerShell:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   pip install -e .
   ```
4. Check that the `.env` credentials work against MySQL before running the full smoke test:
   ```bash
   set -a
   source .env
   set +a
   mysql -u "$DB_USER" -p -h "$DB_HOST" -P "${DB_PORT:-3306}" "$DB_NAME"
   ```
5. Run the sanity checks:
   ```bash
   python verify_db.py
   python smoke_test.py
   pytest tests/ -q
   ```
6. Open `main.ipynb` and run all cells. Outputs (CSVs and PNGs) are written to `experiments/`.

## Algorithms and their mapping to the course syllabus

- **NSGA-II** — Topic 2 (genetic algorithms) and Topic 4 (multi-objective). Dominance + crowding-distance selection.
- **PAES** — Topic 4 (multi-objective). (1+1)-ES with adaptive grid archive (Knowles and Corne, 2000). Contrasts with NSGA-II by using archive-based selection instead of population-dominance selection.
- **Scalarised PSO** — Topic 3.1 (PSO) used as a single-objective baseline via weighted sum.

ACO (Topic 3.2) is not included. A simple memetic NSGA-II variant (Topic 7.1) is implemented as an optional extension.
