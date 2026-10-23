# Project audit

**Audit scope:** repository contents, supplied CSV, project documentation, and the supplied research-paper PDF.
**Status:** Phase A audit completed before implementation. Inventory statements below record the repository as first inspected.

## Repository inventory

| Path | Present state |
|---|---|
| `data/raw/train.csv` | Supplied training CSV; profiled below. |
| `data/raw/test.csv` | Not present. |
| `docs/Factors_Affect_Airline_Customers_Satisfaction_Data_Mining.pdf` | Supplied 2.16 MB paper PDF. Its cover and abstract identify the cited work; the article abstract is also available on the publisher page. |
| `notebooks/` | Contains only `README.md`; no `.ipynb` file or captured notebook cells/outputs are present. |
| `src/airline_satisfaction/` | Contains only `__init__.py`; no analysis workflow exists yet. |
| `web-showcase/` | Contains only a placeholder `README.md`; no Angular project or `package.json` exists. |
| `requirements.txt` | Lists pandas, NumPy, Matplotlib, Seaborn, scikit-learn, SciPy, statsmodels, and Jupyter. |
| `README.md` | Describes the project and correctly cautions that the original test CSV and complete notebook are not supplied. |
| `docs/` | Also contains an initial data dictionary and methodology plan; these are explicitly preliminary/planning documents. |

The repository also contains `.gitignore` and `CODEX_MASTER_PROMPT.md`. The initial worktree was clean. The Git remote identifies `Abdain-221855/Devops-Lab`; no deployment URL or custom domain has been assumed.

## Supplied training-data profile

The CSV was parsed from its header and all records using Python's standard-library CSV reader. The source file was not modified.

| Check | Observed result |
|---|---|
| Rows × columns | 103,904 × 25 |
| Exact duplicate rows | 0 |
| Missing values | 310, all in `Arrival Delay in Minutes` (about 0.30% of rows) |
| Target counts | `neutral or dissatisfied`: 58,879 (56.67%); `satisfied`: 45,025 (43.33%) |
| Categorical columns | `Gender`, `Customer Type`, `Type of Travel`, `Class`, `satisfaction` |
| Numeric-looking columns | 20, including the index-like first column, `id`, ratings, age, distance, and delays |
| Index-like first column | CSV header is blank; values are unique and contiguous from 0 to 103,903. This corresponds to the `Unnamed: 0` name used in the project brief. |
| Passenger `id` | 103,904 unique values, from 1 to 129,880; identifier, not an appropriate model feature without a specific research justification. |
| Age / flight distance | Age range 7–85; flight distance range 31–4,983. |
| Delays | Departure delay range 0–1,592 minutes; observed arrival delay range 0–1,584 minutes. |
| Service-rating fields | Integer values generally span 0–5; `Baggage handling` spans 1–5. Their ordinal interpretation must be made explicit in analysis. |

Observed categories:

- `Gender`: Male, Female.
- `Customer Type`: Loyal Customer, disloyal Customer.
- `Type of Travel`: Personal Travel, Business travel.
- `Class`: Eco, Eco Plus, Business.
- `satisfaction`: neutral or dissatisfied, satisfied.

`Arrival Delay in Minutes` has a mean of approximately 15.18 among its 103,594 observed training values. This is a descriptive statistic from the supplied training file, not an imputation or model result.

## Paper-reported information (not reproduced)

The supplied PDF is titled “Factors Affect Airline Customers’ Satisfaction: Data Mining,” by Yifei Wang (2023), ECIT 2023 / *Atlantis Highlights in Engineering*, pp. 344–362, DOI [10.2991/978-94-6463-210-1_43](https://doi.org/10.2991/978-94-6463-210-1_43). Its abstract describes exploratory analysis, comparative statistical approaches, and logistic-regression prediction. Full-text extraction of the supplied PDF confirmed that the paper:

- mean-replaced 393 missing `arrival_delay_in_minutes` values in the full data and defined `TOTAL` as the sum of the variables on the five-point satisfaction scale;
- included `TOTAL` as a covariate in the original-variable logistic regression and used conditional-forward variable selection;
- reported KMO = 0.274 and Bartlett sphericity chi-square = 1,777,150.592 (df = 231, p < .001), then extracted 10 common factors explaining 81.268% cumulative variance;
- reported 87.5% classification accuracy for the original-variable model and 85.0% for the factor model.

The original-variable regression table lists `TOTAL` and does not list `Flight Distance`, `Seat comfort`, or `Inflight entertainment`; the prose describes conditional-forward variable selection. Its reported classification table totals 129,880 records. The `TOTAL` wording does not enumerate its items, so this project interprets it as the 14 five-point service-rating columns available in the supplied schema. The paper's regression discussion does not establish a separate held-out test protocol; treat its classification accuracy as paper-reported rather than a directly comparable test-set score.

## Reproduction status and limitations

- Only the training CSV is available. The original notebook's reported 25,976-row test file is not in the repository; its preview or printed shape cannot substitute for the real file.
- There is no standalone original `.ipynb` to inspect, preserve, or reproduce. The notebook README says the complete original notebook was not supplied.
- At initial inspection, no computed EDA outputs, statistical test results, PCA/factor analysis, model metrics, or figures existed.
- At initial inspection, no Angular version could be inferred because no frontend package manifest or application source existed.
- At initial inspection, the available Python 3.13 interpreter did not have pandas, NumPy, or PDF-extraction packages installed. The analysis dependencies are now installed to run the new workflow.
- Detailed performance comparability remains limited because the paper does not establish a held-out evaluation protocol in the regression section inspected.
- The supplied CSV is one 103,904-row split, not the 129,880-row combined dataset described in the project context. No test-set result may be claimed unless the actual test data are supplied.
- No passenger-level data should be published through the static showcase; any published output must be aggregate.

## Phase A checklist

- [x] Inventory repository files and frontend/notebook presence.
- [x] Read the README, preliminary methodology, data dictionary, and notebook/showcase notes.
- [x] Inspect the supplied PDF's full text, methods, factor diagnostics, and reported classification tables.
- [x] Parse the supplied CSV and inspect its dimensions, header, missingness, duplicate rows, target balance, categories, identifiers, and numeric ranges.
- [x] Record absent test/notebook/frontend assets and environment limitations.
- [x] Phase B: implement reproducible data-quality inspection and exploratory analysis.
- [x] Phase C: implement and evaluate leakage-safe models using only available data.
- [x] Phase D: document computed findings and verify paper comparisons.
- [x] Phase E: implement and deploy the Angular static showcase from generated aggregate outputs; the production build passed in GitHub Actions and the live GitHub Pages site was verified.
- [x] Phase F: compile the Python workflow, run unit tests, regenerate the analysis outputs, execute the notebook, verify the aggregate website payload, and confirm the Pages deployment.
- [x] Verify the live site renders, the Models navigation anchor works, and a 390px mobile viewport has no horizontal overflow.

The initial npm registry issue is resolved for CI: GitHub Actions successfully installed dependencies, built the Angular site, and deployed the Pages artifact. See [PROGRESS_REPORT.md](./PROGRESS_REPORT.md) for current status and remaining optional work.
