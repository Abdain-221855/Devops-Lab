# Findings

## Independently computed results

All figures below were generated from `data/raw/train.csv` by `src/airline_satisfaction/analysis.py`. Model evaluation is from a stratified 20% holdout sampled from that file (20,781 records; seed 42), not the absent official test CSV.

### Data profile

- The supplied file has 103,904 records and 25 source columns. The target is 56.67% `neutral or dissatisfied` and 43.33% `satisfied`.
- 310 records (0.30%) have missing arrival-delay values. Predictive imputation is fitted only on training partitions; descriptive group summaries use observed values.
- No exact duplicate source rows were found in the Phase A audit. The index-like first column and passenger identifier are excluded from the models.

### Group comparisons

Welch tests and two-sided Mann–Whitney sensitivity tests found differences for age, distance, and both delay measures between the two satisfaction groups (all p < 0.001). Mean values were:

| Measure | Neutral or dissatisfied | Satisfied |
|---|---:|---:|
| Age (years) | 37.57 | 41.75 |
| Flight distance | 928.92 | 1,530.14 |
| Departure delay (minutes) | 16.50 | 12.61 |
| Arrival delay (minutes; observed rows only) | 17.13 | 12.63 |

Within-group satisfaction shares were 58.26% satisfied for business travel versus 10.17% for personal travel; 69.43% for Business class versus 18.61% for Eco and 24.61% for Eco Plus; and 47.73% for loyal versus 23.67% for disloyal customers. These are unadjusted associations in this file, not causal effects.

Pearson chi-square tests found association between each of gender, customer type, travel type, and class and satisfaction (all p < 0.001). The gender association is statistically detectable in this large sample, while the observed satisfaction shares differ by only about 1.2 percentage points between males and females; p-values alone do not measure practical importance.

### Predictive evaluation

`satisfied` is the positive class. The default 0.5 threshold is used.

| Model | Holdout accuracy | Macro precision | Macro recall | Macro F1 | ROC-AUC | Satisfied precision / recall / F1 | 3-fold CV accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|
| Original-feature logistic regression | 87.66% | 87.56% | 87.25% | 87.39% | 0.9281 | 86.93% / 84.19% / 85.54% | 87.53% ± 0.09% |
| 10-component PCA + logistic regression | 84.55% | 84.41% | 84.02% | 84.18% | 0.9065 | 83.61% / 80.03% / 81.78% | 84.45% ± 0.14% |
| Paper-table feature sensitivity, including `TOTAL` | 87.71% | 87.61% | 87.30% | 87.44% | 0.9281 | 87.00% / 84.22% / 85.59% | 87.52% ± 0.11% |

Confusion matrices, in label order `[neutral or dissatisfied, satisfied]`:

- Original-feature model: `[[10636, 1140], [1424, 7581]]`.
- PCA model: `[[10363, 1413], [1798, 7207]]`.
- Paper-table sensitivity model with `TOTAL`: `[[10643, 1133], [1421, 7584]]`.

For the baseline, the largest absolute fitted coefficient was for `Type of Travel_Personal Travel` (negative conditional association with the positive class); `Online boarding` had a positive coefficient. These standardized/one-hot coefficients are model associations, not causal effects. The paper-table sensitivity feature set includes `TOTAL` and excludes Flight Distance, Seat comfort, and Inflight entertainment, matching the variables listed in the paper's original-variable regression table. Its holdout accuracy is close to the primary baseline in this implementation.

### Factor/PCA diagnostics

On the 14 service-rating items in the training partition (83,123 rows), overall KMO was 0.7811; Bartlett's sphericity test returned p < 0.001. PCA on these 14 rating items explained 92.42% of variance in the first 10 components, and 7 components reached 80%. In the separately preprocessed, encoded full-predictor model matrix, the model's 10-component PCA retained 81.29% cumulative variance. These are different feature representations; neither is asserted to reproduce the paper's factor analysis.

A training-only 10-factor scikit-learn `FactorAnalysis` fit on the 14 rating items did not converge under the tested 100-iteration, 0.1-tolerance configuration on the 83,123-row training partition. No common-factor predictive score is reported. The PCA model is a separate dimensionality-reduction comparison, not a substitute claim of reproducing common-factor analysis.

## Paper-reported findings (not reproduced)

The PDF reports 87.5% accuracy for its original-variable logistic model and 85.0% for a 10-factor model. Its factor-suitability table reports KMO = 0.274 and Bartlett chi-square = 1,777,150.592 (df = 231, p < .001); its 10 factors explain 81.268% cumulative variance. It reports 393 missing arrival delays mean-replaced in the full dataset and defines `TOTAL` as the sum of variables on the five-point satisfaction scale. Its original-variable regression table includes `TOTAL` and uses conditional-forward variable selection. The abstract describes differences in male/female concerns, older customers using better cabins, greater departure-delay tolerance, and greater delay sensitivity among business travelers.

The paper's classification tables total 129,880 cases, which matches the combined train/test count in the project context. The paper does not document a separate held-out evaluation protocol in the regression discussion examined here. The computed baseline holdout accuracy (87.66%) and three-fold cross-validation accuracy (87.53%) are numerically close to the paper's reported 87.5%; the computed PCA holdout accuracy (84.55%) is close to its reported 85.0%. The model's 10-component PCA explains 81.288% in its encoded full-predictor representation, numerically close to the paper's 81.268%. These similarities are **not evidence of an exact replication**: evaluation protocol, transformations, feature representations, and factor-extraction procedure differ or remain undocumented. The computed KMO (0.781 on 14 service ratings in the training split) differs materially from the paper's reported 0.274 (df = 231) and uses a different, explicitly documented feature set.

## Interpretation limits

The supplied file is only one 103,904-row split; it does not include the paper-context test CSV. A holdout or cross-validation score from this file must not be called a result on the original test set. Group differences and logistic coefficients describe associations and do not establish causality.
