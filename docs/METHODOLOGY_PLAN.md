# Methodology Plan

This document is a plan, not a claim that analyses have already run.

1. Preserve raw files unchanged.
2. Inspect column names, missing values, duplicates, label balance, and index/ID fields.
3. Exclude index and passenger ID from predictive features unless a documented experiment requires them.
4. Fit all preprocessing inside training-only pipelines to prevent leakage.
5. Produce EDA summaries and charts.
6. Evaluate a logistic-regression baseline using the official test file only if it is actually provided. Otherwise use a documented stratified holdout from the available training CSV.
7. Optionally compare a PCA/factor-based model to the original-feature baseline, after checking whether the factor-analysis assumptions and implementation are justified.
8. Compare newly computed results to the paper's reported values only with an explicit caveat about differences in splits and preprocessing.
