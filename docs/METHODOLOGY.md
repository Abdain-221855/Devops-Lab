# Methodology

## Data and target

The workflow reads `data/raw/train.csv` and does not alter the source file. The blank first CSV header is read by pandas as `Unnamed: 0`; both that row index and passenger `id` are excluded from predictors. `satisfaction` is encoded explicitly as `1 = satisfied` (positive class) and `0 = neutral or dissatisfied`.

The supplied CSV contains 103,904 records. The official `test.csv` is absent, so every reported predictive metric uses a reproducible 20% stratified holdout sampled from this supplied training file (`random_state=42`). It is not the original test set and is not a replication of the paper's evaluation split.

## Preprocessing and feature treatment

All transformations used for predictive evaluation are inside scikit-learn pipelines and are fit on the 80% training partition only:

- Numeric measures (age, flight distance, and departure/arrival delay) and service-rating items are mean-imputed and standardized.
- `Arrival Delay in Minutes` is missing for 310 training-file records. Mean imputation is performed by the training-partition imputer for modeling; the imputed value is not calculated from holdout observations. EDA and group summaries use available values without filling them.
- The service ratings are discrete ordered 0–5 responses (Baggage handling is 1–5 in this file). They are modeled as standardized numeric features, which assumes a linear, equally spaced trend across rating levels. This is a modeling simplification; it is not a claim that the response scale is truly interval-valued.
- Gender, customer type, travel type, and cabin class are treated as nominal categories, most-frequent imputed if needed, and one-hot encoded with unknown-category handling.
- The paper states that `TOTAL` is the sum of all five-point satisfaction-rating variables and includes it as a covariate in its original-variable regression table. For this file, the corresponding 14 items are the service-rating columns listed in [DATA_DICTIONARY.md](./DATA_DICTIONARY.md). `satisfaction` is not included in the sum.
- The primary model excludes `TOTAL` because it is algebraically redundant with those rating predictors and because contemporaneous satisfaction ratings can be target-adjacent. The workflow separately evaluates a sensitivity model using the paper's table-listed covariates, including `TOTAL`, while excluding Flight Distance, Seat comfort, and Inflight entertainment as the paper's original-variable regression table does. This does not use the target label to construct a feature; it is not direct target-column leakage, but its timing/construct validity remains a limitation.

## Exploratory and statistical analyses

The workflow exports class counts, missingness, distributions of age and flight distance, cross-tabulations by gender/customer type/travel type/class, rating and numeric-feature Spearman correlations, and delay distributions/group plots. These are descriptive analyses of the supplied CSV.

Welch independent-samples t-tests compare mean age, distance, and delays between the two observed satisfaction groups. Two-sided Mann–Whitney U tests are included as rank-based sensitivity comparisons, especially relevant to skewed delay data. Pearson chi-square tests examine association between satisfaction and gender, customer type, travel type, and class; categorical summaries include counts and within-group row percentages. Statistical significance does not imply practical importance or causality.

KMO and Bartlett sphericity diagnostics and a PCA variance summary are calculated on the 14 service-rating items in the training partition. The diagnostics support exploring common structure in those ratings. However, a training-only 10-factor scikit-learn `FactorAnalysis` fit did not converge after 100 iterations at tolerance 0.1 on the full 83,123-row training partition, so no common-factor predictive metrics are reported. Instead, a 10-component PCA model is evaluated on the full preprocessed predictor matrix. PCA is not common-factor analysis and is not asserted to reproduce the paper's extraction procedure.

## Models and evaluation

Three logistic-regression models are compared:

1. A logistic-regression baseline on the original predictor set after the preprocessing above.
2. A 10-component PCA + logistic-regression model using the same leakage-safe preprocessing pipeline.
3. A `TOTAL` sensitivity model using the covariates in the paper's original-variable regression table, including the 14-item summed score. It approximates the paper's feature set but uses regularized scikit-learn logistic regression rather than the paper's conditional-forward procedure.

Metrics are calculated once on the stratified holdout: accuracy; macro precision, recall, and F1; ROC-AUC; a confusion matrix; and per-class precision, recall, F1, and support. A default 0.5 decision threshold is used. Three-fold stratified cross-validation (seed 42) additionally reports mean and sample standard deviation for accuracy, macro precision/recall/F1, and ROC-AUC for all three model pipelines. Every fold fits its own imputer, encoder, scaler, and PCA transformation on that fold's training partition.

The largest absolute standardized/one-hot baseline coefficients are exported for interpretation. Coefficients are conditional associations, depend on scaling and categorical reference levels, and must not be interpreted causally.

## Paper comparison and deviations

The PDF reports 87.5% accuracy for the original-variable model, 85.0% for the 10-factor model, KMO = 0.274, and 81.268% cumulative variance for 10 components. It says 393 missing arrival-delay values were mean-replaced, defines `TOTAL` as the sum of five-point satisfaction-rating variables, and lists `TOTAL` in the original-variable logistic regression with conditional-forward selection. The paper's classification tables contain 129,880 observations, matching the combined split size in the project context; the examined regression discussion does not establish a held-out evaluation protocol. The reproduction's holdout and cross-validation results are therefore contextual only, not directly comparable.

## Reproducibility and outputs

Run from the repository root:

```powershell
python -m pip install -r requirements.txt
python src/airline_satisfaction/analysis.py
```

`--input` and `--output` can override the defaults. Figures are saved in `reports/figures/`; aggregate CSV and JSON tables are saved in `reports/tables/`. The workflow records the random seed, data split, package versions, and input filename in the output JSON. It emits aggregate values only; do not publish passenger-level records.
