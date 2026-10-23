# Airline Customer Satisfaction — Research Replication & Showcase

This project studies airline passenger satisfaction using the supplied research paper and dataset.

## Research source
Yifei Wang (2023), **“Factors Affect Airline Customers’ Satisfaction: Data Mining”**, ECIT 2023, pp. 344–362. DOI: https://doi.org/10.2991/978-94-6463-210-1_43

## Current inputs
- `docs/Factors_Affect_Airline_Customers_Satisfaction_Data_Mining.pdf` — supplied paper.
- `data/raw/train.csv` — supplied training CSV (103,904 rows × 25 columns).
- `notebooks/` — put the complete original `.ipynb` here before asking Codex to refactor/extend it.
- The notebook content pasted into the conversation references `train.csv` and `test.csv`; `test.csv` itself has not been included in this ZIP. The notebook output reports a test shape of 25,976 × 25. Add the actual test file if available. Do not manufacture a replacement or claim evaluation on a missing test file.

## Research goals
1. Audit the data and reproduce defensible exploratory data analysis.
2. Investigate satisfaction associations by demographics, travel type/class, service ratings, flight distance, and delays.
3. Implement a transparent logistic-regression baseline and report classification metrics.
4. Where justified, reproduce factor/PCA-based analysis and compare it fairly with the original-variable model.
5. Build a polished Angular static showcase suitable for GitHub Pages, using exported, non-sensitive aggregate results rather than requiring a Python backend at runtime.

## Important reproducibility rules
- Keep the paper's reported results separate from newly computed results.
- Do not promise an exact replication until preprocessing, split, encoding, feature selection, and evaluation details are verified.
- Fit imputers, encoders, scalers, PCA/factor transformations, and feature selection on training data only.
- Avoid leakage: do not use passenger IDs/index columns as predictive features, and do not derive features from the target.
- Report accuracy, precision, recall, F1, confusion matrix, and ROC-AUC where appropriate. Include class balance and explain any threshold choices.
- Document deviations from the paper, especially when the supplied dataset schema or available files differ.
- Keep raw data unchanged. Write derived datasets and outputs to `data/processed/` and `reports/`.
- Do not commit large generated artifacts or the raw dataset to a public GitHub repository unless the owner has explicitly decided it is appropriate.

## Suggested workflow
1. Put the full original notebook at `notebooks/original_notebook.ipynb`.
2. Add the missing test CSV to `data/raw/test.csv` if it is available.
3. Open `CODEX_MASTER_PROMPT.md` in Codex and ask it to inspect the existing materials before editing.
4. Run Python analysis first, save reproducible outputs, then build the Angular showcase from those outputs.
5. Verify the static site locally and deploy to GitHub Pages only after the repository and base path are known.
