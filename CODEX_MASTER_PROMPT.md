# Codex Master Prompt — Airline Customer Satisfaction Research Project

You are the lead data-science engineer and frontend engineer for a research-replication project. Work inside this repository. Your job is to understand the actual supplied paper, dataset, and original Jupyter notebook first, then create a reproducible analysis and a polished Angular static website that explains the work. Do not start by blindly rewriting everything.

## 1. Project context
Research paper:
- Yifei Wang (2023), “Factors Affect Airline Customers’ Satisfaction: Data Mining”
- ECIT 2023, AHE 18, pp. 344–362
- DOI: https://doi.org/10.2991/978-94-6463-210-1_43
- The paper describes EDA, missing-value handling, a summed `TOTAL` score, PCA/factor analysis, group comparisons (t-tests/ANOVA/crosstabs), delay-time analysis, and binary logistic regression.

Dataset currently available:
- `data/raw/train.csv` — 103,904 rows and 25 columns.
- Columns include an index-like `Unnamed: 0`, `id`, demographics, customer/travel/class fields, service ratings, flight distance, departure/arrival delay, and `satisfaction`.
- Target classes in this file: `neutral or dissatisfied` and `satisfied`.
- `Arrival Delay in Minutes` has missing values.
- The notebook pasted by the user loads `/content/train.csv` and `/content/test.csv`, and its captured output reports 103,904 training rows and 25,976 test rows. **The actual `test.csv` is not currently in the repository. Do not invent it, infer test predictions from its printed preview, or claim test-set metrics until the real file is supplied.**
- The full original notebook file may not yet be present. Search `notebooks/` and inspect any `.ipynb` there. If it is absent or incomplete, clearly report this and create a clean, reproducible notebook without pretending it is the original.

## 2. First action: audit before changing
1. Inspect the entire repository tree, README, research PDF, CSV schemas, and all notebook cells/outputs.
2. Record what is present and missing. Check dataset dimensions, duplicate rows, missingness, target balance, data types, category values, and suspicious index/ID columns.
3. Extract the paper's stated methods and reported metrics. Clearly distinguish:
   - facts explicitly reported in the paper,
   - outputs independently reproduced from the available data,
   - methodological choices made for this implementation.
4. Make a short `docs/PROJECT_AUDIT.md` before implementing. Include limitations and a task checklist.
5. Preserve source data and any original notebook. Never overwrite the only copy.

## 3. Research implementation
Create a clear, runnable Python workflow using sensible modules under `src/airline_satisfaction/` and/or a notebook under `notebooks/`. Use common, maintained packages (pandas, numpy, matplotlib/seaborn if useful, scikit-learn, scipy, statsmodels if justified). Keep dependencies listed in `requirements.txt`.

### Data quality and preprocessing
- Normalize column handling carefully; preserve a mapping to original names where useful.
- Drop `Unnamed: 0` and passenger `id` from model features unless a documented research reason says otherwise.
- Treat `satisfaction` as the target and encode it explicitly and consistently. Document which label maps to positive class.
- Inspect missingness. For `Arrival Delay in Minutes`, compare with the paper's stated mean-imputation approach, but fit the imputer on training data only for predictive evaluation.
- Avoid leakage: every imputer, encoder, scaler, PCA/factor step, feature selector, and model must be fit only on training data.
- Use a scikit-learn `Pipeline` and `ColumnTransformer` where appropriate.
- Keep categorical and ordinal variables' treatment explicit. Do not silently assume all integer-looking service ratings are continuous without explaining it.
- If a `TOTAL` feature is added, define exactly which satisfaction-rating columns are summed. Check whether the paper includes it as a covariate and whether that creates target leakage or a methodological inconsistency. Explain the decision and report a leakage-safe model separately if needed.

### Exploratory data analysis
Generate reproducible plots/tables for:
- class balance,
- missing values,
- passenger age and flight-distance distributions,
- satisfaction by gender, customer type, travel type, and cabin class,
- service-rating relationships/correlation,
- departure and arrival delay distributions and their relationship with satisfaction,
- feature correlation matrix (with a readable layout).
Save plots under `reports/figures/` and tabular summaries under `reports/tables/`. Use meaningful filenames and captions. Don't fabricate findings; compute them from the data.

### Statistical analyses
Where supported by the dataset and paper, implement:
- group comparisons using suitable tests (e.g., t-test/ANOVA or non-parametric alternatives when assumptions warrant),
- cross-tabulations with percentages,
- PCA/factor-analysis exploration with suitability diagnostics when technically appropriate.
The paper reports a KMO value of .274 after removing one highly correlated variable for a suitability test, extracts 10 components explaining about 81.268% cumulative variance, and uses factors in a reduced logistic-regression model. Treat these as reported paper values to compare against, not values to hardcode into new results. Investigate whether the same procedures and assumptions can be reproduced. If factor analysis is unsuitable, explain why rather than forcing it.

### Modeling and evaluation
- Build a simple, transparent logistic-regression baseline.
- If feasible, compare original-feature logistic regression against a factor/PCA-reduced logistic model.
- Use the provided official train/test split only if the actual test CSV is present and labels are available. Otherwise, use a clearly documented stratified holdout from the training file for exploratory validation and do not call it the original test set.
- Report accuracy, precision, recall, F1, confusion matrix, ROC-AUC, and class-wise metrics. Include cross-validation if practical.
- Compare model performance to the paper's reported 87.5% overall classification accuracy, while emphasizing that scores are comparable only if preprocessing, feature set, and split/evaluation protocol match.
- Save machine-readable metrics (for example `reports/tables/model_metrics.json`) for the website. Save confusion-matrix and ROC plots where supported.
- Set random seeds for reproducibility and record versions/configuration.
- Include a short interpretation of coefficients or feature importance with caveats about association versus causation.

## 4. Documentation and deliverables
Create or maintain:
- `docs/PROJECT_AUDIT.md`
- `docs/METHODOLOGY.md` describing preprocessing, split, models, metrics, and deviations from the paper
- `docs/FINDINGS.md` containing only computed findings, plus a clearly separated “paper-reported findings” section
- `docs/DATA_DICTIONARY.md`
- `reports/figures/` and `reports/tables/`
- `requirements.txt`
- a reproducible notebook with markdown explanations and outputs where practical
- a README with setup/run instructions
- a complete Angular showcase under `web-showcase/`

Do not include unsupported claims, fake metrics, mock chart values presented as real, or screenshots that imply analyses ran when they did not. If results are not available, show a transparent “not generated yet” state.

## 5. Angular / GitHub Pages showcase
Build a responsive, professional, research-oriented static Angular site. Inspect existing frontend files first; preserve and extend them if present. Do not assume a framework version before checking `package.json`.

Suggested pages/sections:
1. Overview / research question
2. Dataset profile and data-quality summary
3. Exploratory insights with generated chart assets
4. Statistical findings and factor-analysis summary
5. Model comparison and evaluation metrics
6. Methodology and reproducibility
7. Paper-vs-reproduction comparison and limitations
8. References / citation

Design requirements:
- High-quality, clean visual hierarchy; responsive desktop/mobile layout; accessible color contrast; semantic headings; useful loading/empty/error states.
- Use real generated JSON/CSV/chart outputs from the Python workflow. If charts are rendered in the browser, use actual exported values.
- No backend is required for the GitHub Pages deployment. The website should work as a static site.
- Make base-path and router behavior compatible with GitHub Pages. Prefer a build/deploy strategy compatible with the repository's actual name and Angular version; document the exact commands.
- Do not assume repository name, GitHub username, deployment URL, or custom domain. Ask only if required to configure the final deployment; otherwise leave clearly documented placeholders.
- Ensure the production build succeeds and test mobile layout and navigation.
- Do not upload raw passenger-level data to a public site. Only publish aggregate statistics and approved charts.

## 6. Engineering standards
- Make small, coherent changes and explain what each stage does.
- Do not ask repeated questions if repository evidence can answer them.
- If a required file is missing, continue with safe work and clearly list the blocker instead of stopping the entire project.
- Do not claim tests, notebook execution, metrics generation, or deployment succeeded unless you actually ran and verified them.
- Keep code typed, modular, documented, and maintainable.
- Check for data leakage, misleading comparisons, and reproducibility problems.
- Before finishing, run the available tests, lint/build commands, and Python workflow. Fix failures where possible and provide exact commands/results.
- Final response must include: implemented work, files created/modified, verified results, limitations, and the next concrete action required from the user.

## 7. Execution order
Phase A: audit all files and write `docs/PROJECT_AUDIT.md`.
Phase B: reproduce data inspection and exploratory analysis.
Phase C: implement and evaluate models; save real metrics and figures.
Phase D: document findings and compare to the paper without overstating equivalence.
Phase E: build Angular showcase from real outputs.
Phase F: run checks/build, update README, and summarize verified status.

Begin with Phase A now. Do not skip the audit.
