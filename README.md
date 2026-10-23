# Airline customer satisfaction research replication

This project analyzes the supplied airline satisfaction training CSV alongside Yifei Wang's 2023 paper, “Factors Affect Airline Customers’ Satisfaction: Data Mining” ([DOI](https://doi.org/10.2991/978-94-6463-210-1_43)). Paper-reported results are distinguished from independently computed results throughout.

## Available inputs and caveats

- `data/raw/train.csv`: 103,904 rows × 25 columns; contains 310 missing values in `Arrival Delay in Minutes`.
- `data/raw/test.csv`: not supplied. The reported 25,976-row test preview is not a substitute for the actual file.
- Original `.ipynb`: not supplied. [`notebooks/reproduction_analysis.ipynb`](notebooks/reproduction_analysis.ipynb) is a new, reproducible workflow and is not represented as the original.
- The detailed paper-reported metrics are not exact replication targets until its feature definitions and evaluation protocol are matched. See [`docs/PROJECT_AUDIT.md`](docs/PROJECT_AUDIT.md) and [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md).

## Run the Python workflow

Requires Python 3.10+:

```powershell
python -m pip install -r requirements.txt
python src/airline_satisfaction/analysis.py
```

The same workflow can be explored in Jupyter:

```powershell
jupyter notebook notebooks/reproduction_analysis.ipynb
```

Optional command-line inputs:

```powershell
python src/airline_satisfaction/analysis.py --input data/raw/train.csv --output reports
```

All modeling uses a fixed-seed, stratified 20% holdout sampled from the supplied training CSV because the official test file is absent. Positive target is `satisfied`. Imputation, scaling, one-hot encoding, PCA, and model fitting are kept in pipelines fit on the training partition only. See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for assumptions.

Outputs are generated in:

- `reports/figures/` — EDA, confusion-matrix, and ROC plots.
- `reports/tables/` — aggregate CSV/JSON summaries, factor diagnostics, statistical tests, and model metrics.

Run the analysis before building the website so its charts and aggregate data are available. The site does not publish passenger-level rows.

## Static showcase

The Angular application lives in [`web-showcase/`](web-showcase/README.md). GitHub Pages deployment is configured through the Actions workflow; the project URL is [https://abdain-221855.github.io/Devops-Lab/](https://abdain-221855.github.io/Devops-Lab/). The URL will serve the site after Pages is enabled in repository settings and the deployment workflow succeeds. The site was not yet deployed when this README was updated.

## Documentation

- [Project audit](docs/PROJECT_AUDIT.md)
- [Methodology](docs/METHODOLOGY.md)
- [Computed and paper-reported findings](docs/FINDINGS.md)
- [Data dictionary](docs/DATA_DICTIONARY.md)

Raw input data are preserved. Review licensing and privacy before publishing derived outputs.
