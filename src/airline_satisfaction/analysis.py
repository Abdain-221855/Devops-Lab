"""Reproducible exploratory analysis and leakage-safe model evaluation."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import scipy
from scipy import stats
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[2]
SEED = 42
TARGET = "satisfaction"
POSITIVE_LABEL = "satisfied"
INDEX_COLUMN = "Unnamed: 0"

ORDINAL_FEATURES = [
    "Inflight wifi service",
    "Departure/Arrival time convenient",
    "Ease of Online booking",
    "Gate location",
    "Food and drink",
    "Online boarding",
    "Seat comfort",
    "Inflight entertainment",
    "On-board service",
    "Leg room service",
    "Baggage handling",
    "Checkin service",
    "Inflight service",
    "Cleanliness",
]
CATEGORICAL_FEATURES = ["Gender", "Customer Type", "Type of Travel", "Class"]
CONTINUOUS_FEATURES = [
    "Age",
    "Flight Distance",
    "Departure Delay in Minutes",
    "Arrival Delay in Minutes",
]
PREDICTOR_FEATURES = CATEGORICAL_FEATURES + CONTINUOUS_FEATURES + ORDINAL_FEATURES
TOTAL_FEATURE = "TOTAL"
PAPER_TABLE_FEATURES = (
    CATEGORICAL_FEATURES
    + ["Age", "Departure Delay in Minutes", "Arrival Delay in Minutes"]
    + [
        feature
        for feature in ORDINAL_FEATURES
        if feature not in {"Seat comfort", "Inflight entertainment"}
    ]
    + [TOTAL_FEATURE]
)
GROUP_FEATURES = ["Gender", "Customer Type", "Type of Travel", "Class"]
PAPER_ACCURACY = {"original_variables": 0.875, "ten_factors": 0.85}


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if pd.isna(value):
        return None
    return value


def _save_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_safe(value), indent=2, allow_nan=False) + "\n", encoding="utf-8")


def _read_data(path: Path) -> tuple[pd.DataFrame, dict[str, str]]:
    frame = pd.read_csv(path)
    if "Unnamed: 0" not in frame.columns and frame.columns[0] == "Unnamed: 0.1":
        frame = frame.rename(columns={"Unnamed: 0.1": INDEX_COLUMN})
    if INDEX_COLUMN not in frame.columns and frame.columns[0] == "":
        frame = frame.rename(columns={"": INDEX_COLUMN})
    if TARGET not in frame.columns:
        raise ValueError(f"Expected target column {TARGET!r} in {path}")
    expected_labels = {"neutral or dissatisfied", POSITIVE_LABEL}
    observed_labels = set(frame[TARGET].dropna().unique())
    if frame[TARGET].isna().any() or observed_labels != expected_labels:
        raise ValueError(
            f"Expected non-missing target labels {sorted(expected_labels)}, "
            f"found {sorted(observed_labels)}"
        )
    original_columns = {str(column): str(column) for column in frame.columns}
    frame = frame.drop(columns=[column for column in (INDEX_COLUMN, "id") if column in frame])
    expected = set(PREDICTOR_FEATURES + [TARGET])
    missing = expected.difference(frame.columns)
    if missing:
        raise ValueError(f"Required columns missing from {path}: {sorted(missing)}")
    return frame, original_columns


def _profile(frame: pd.DataFrame, source_path: Path, original_columns: dict[str, str]) -> dict[str, Any]:
    targets = frame[TARGET].value_counts().reindex(["neutral or dissatisfied", POSITIVE_LABEL], fill_value=0)
    missing = frame.isna().sum()
    return {
        "source_file": source_path.name,
        "rows": int(len(frame)),
        "columns_in_source": int(len(original_columns)),
        "predictor_count": len(PREDICTOR_FEATURES),
        "target": TARGET,
        "positive_label": POSITIVE_LABEL,
        "class_counts": targets.astype(int).to_dict(),
        "class_percentages": (targets / len(frame) * 100).round(4).to_dict(),
        "missing_values": {str(key): int(value) for key, value in missing[missing > 0].items()},
        "duplicate_rows_after_id_columns_removed": int(frame.duplicated().sum()),
        "excluded_identifier_columns": [column for column in (INDEX_COLUMN, "id") if column in original_columns],
        "data_types": {str(key): str(value) for key, value in frame.dtypes.items()},
        "split": {
            "method": "stratified holdout from the supplied training CSV",
            "test_size": 0.2,
            "random_state": SEED,
            "official_test_file_used": False,
        },
        "versions": {
            "python": __import__("sys").version.split()[0],
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "scikit_learn": sklearn.__version__,
        },
    }


def _plot_eda(frame: pd.DataFrame, figures_dir: Path, tables_dir: Path) -> None:
    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", palette="colorblind")
    class_order = ["neutral or dissatisfied", POSITIVE_LABEL]
    colors = ["#5277a3", "#d1794f"]

    counts = frame[TARGET].value_counts().reindex(class_order)
    counts.rename_axis(TARGET).reset_index(name="passengers").to_csv(
        tables_dir / "class_balance.csv", index=False
    )
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(x=counts.index, y=counts.values, hue=counts.index, palette=colors, legend=False, ax=ax)
    ax.set(title="Satisfaction labels in the supplied training file", xlabel="", ylabel="Passengers")
    ax.tick_params(axis="x", rotation=10)
    fig.tight_layout()
    fig.savefig(figures_dir / "class_balance.png", dpi=160)
    plt.close(fig)

    missing = frame.isna().sum().sort_values(ascending=False)
    missing = missing[missing > 0]
    missing_table = pd.DataFrame(
        {"column": missing.index, "missing_values": missing.values, "percent": (missing / len(frame) * 100).values}
    )
    missing_table.to_csv(tables_dir / "missing_values.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 3.5))
    if missing.empty:
        ax.text(0.5, 0.5, "No missing values detected", ha="center", va="center")
        ax.set_axis_off()
    else:
        sns.barplot(data=missing_table, x="missing_values", y="column", color="#d1794f", ax=ax)
        ax.set(title="Missing values in supplied training data", xlabel="Missing rows", ylabel="")
    fig.tight_layout()
    fig.savefig(figures_dir / "missing_values.png", dpi=160)
    plt.close(fig)

    for column, label, filename in (
        ("Age", "Passenger age (years)", "age_distribution.png"),
        ("Flight Distance", "Flight distance", "flight_distance_distribution.png"),
    ):
        frame[column].plot.hist(bins=40, color="#5277a3", edgecolor="white", figsize=(7, 4))
        plt.title(f"Distribution of {label.lower()}")
        plt.xlabel(label)
        plt.ylabel("Passengers")
        plt.tight_layout()
        plt.savefig(figures_dir / filename, dpi=160)
        plt.close()

    grouped = (
        frame.groupby(GROUP_FEATURES + [TARGET], observed=False)
        .size()
        .rename("passengers")
        .reset_index()
    )
    for feature in GROUP_FEATURES:
        table = pd.crosstab(frame[feature], frame[TARGET], normalize="index").reindex(
            columns=class_order, fill_value=0
        )
        filename = re.sub(r"[^a-z0-9]+", "_", feature.lower()).strip("_")
        table.rename_axis(feature).to_csv(tables_dir / f"satisfaction_by_{filename}.csv")
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, feature in zip(axes.flat, GROUP_FEATURES):
        table = pd.crosstab(frame[feature], frame[TARGET], normalize="index").reindex(
            columns=class_order, fill_value=0
        )
        table.plot(kind="bar", stacked=True, ax=ax, color=colors)
        ax.set(title=f"Satisfaction by {feature.lower()}", xlabel="", ylabel="Share within group", ylim=(0, 1))
        ax.tick_params(axis="x", rotation=15)
        ax.legend(title="", fontsize=8)
    fig.suptitle("Satisfaction composition across passenger groups", y=1.01)
    fig.tight_layout()
    fig.savefig(figures_dir / "satisfaction_by_groups.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    grouped.to_csv(tables_dir / "group_counts.csv", index=False)

    correlation_columns = CONTINUOUS_FEATURES + ORDINAL_FEATURES
    corr = frame[correlation_columns].corr(method="spearman")
    corr.to_csv(tables_dir / "feature_correlations.csv")
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(corr, cmap="vlag", center=0, square=True, linewidths=0.25, cbar_kws={"shrink": 0.75}, ax=ax)
    ax.set(title="Spearman correlations: ratings, passenger and delay measures")
    ax.tick_params(axis="x", rotation=55, labelsize=8)
    ax.tick_params(axis="y", labelsize=8)
    fig.tight_layout()
    fig.savefig(figures_dir / "feature_correlation_matrix.png", dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, column, title in (
        (axes[0, 0], "Departure Delay in Minutes", "Departure delay (log scale)"),
        (axes[0, 1], "Arrival Delay in Minutes", "Arrival delay (log scale)"),
    ):
        sns.histplot(data=frame, x=column, hue=TARGET, bins=45, stat="density", common_norm=False, ax=ax)
        ax.set(title=title, xlabel="Minutes (log1p display)", ylabel="Density")
        ax.set_xscale("symlog", linthresh=1)
    for ax, column, title in (
        (axes[1, 0], "Departure Delay in Minutes", "Departure delay by satisfaction"),
        (axes[1, 1], "Arrival Delay in Minutes", "Arrival delay by satisfaction"),
    ):
        sns.boxplot(data=frame, x=TARGET, y=column, showfliers=False, ax=ax)
        ax.set(title=title, xlabel="", ylabel="Minutes (outliers hidden)")
        ax.tick_params(axis="x", rotation=10)
    fig.tight_layout()
    fig.savefig(figures_dir / "delay_distributions_and_satisfaction.png", dpi=160)
    plt.close(fig)

    rating_corr = frame[ORDINAL_FEATURES].corr(method="spearman")
    rating_corr.to_csv(tables_dir / "service_rating_correlations.csv")
    fig, ax = plt.subplots(figsize=(11, 9))
    sns.heatmap(rating_corr, cmap="vlag", center=0, square=True, linewidths=0.25, ax=ax)
    ax.set(title="Spearman relationships among service ratings")
    ax.tick_params(axis="x", rotation=55, labelsize=8)
    ax.tick_params(axis="y", labelsize=8)
    fig.tight_layout()
    fig.savefig(figures_dir / "service_rating_correlations.png", dpi=160)
    plt.close(fig)


def _statistical_analysis(frame: pd.DataFrame, tables_dir: Path) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    group_values = {
        label: frame.loc[frame[TARGET] == label] for label in ("neutral or dissatisfied", POSITIVE_LABEL)
    }
    for feature in ("Age", "Flight Distance", "Departure Delay in Minutes", "Arrival Delay in Minutes"):
        left = group_values["neutral or dissatisfied"][feature].dropna()
        right = group_values[POSITIVE_LABEL][feature].dropna()
        test = stats.ttest_ind(left, right, equal_var=False, nan_policy="omit")
        mw = stats.mannwhitneyu(left, right, alternative="two-sided")
        results.append(
            {
                "feature": feature,
                "test": "Welch independent-samples t-test",
                "statistic": float(test.statistic),
                "p_value": float(test.pvalue),
                "neutral_or_dissatisfied_mean": float(left.mean()),
                "satisfied_mean": float(right.mean()),
                "neutral_or_dissatisfied_n": len(left),
                "satisfied_n": len(right),
                "sensitivity_test": "Mann-Whitney U (two-sided)",
                "mann_whitney_u": float(mw.statistic),
                "mann_whitney_p_value": float(mw.pvalue),
            }
        )
    pd.DataFrame(results).to_csv(tables_dir / "group_comparisons.csv", index=False)
    crosstabs = {}
    for feature in GROUP_FEATURES:
        counts = pd.crosstab(frame[feature], frame[TARGET])
        row_percent = counts.div(counts.sum(axis=1), axis=0) * 100
        chi_square, p_value, degrees_of_freedom, _ = stats.chi2_contingency(counts)
        crosstabs[feature] = {
            "counts": counts.to_dict(orient="index"),
            "row_percent": row_percent.round(3).to_dict(orient="index"),
            "chi_square_test": {
                "statistic": float(chi_square),
                "degrees_of_freedom": int(degrees_of_freedom),
                "p_value": float(p_value),
            },
        }
    return {
        "group_comparisons": results,
        "categorical_cross_tabs": crosstabs,
        "interpretation_note": "Associations and unadjusted group differences do not establish causation; large samples can make small differences statistically significant.",
    }


def _kmo_diagnostics(training: pd.DataFrame) -> dict[str, Any]:
    ratings = training[ORDINAL_FEATURES].copy()
    ratings = ratings.fillna(ratings.median())
    corr = ratings.corr().to_numpy()
    inverse = np.linalg.pinv(corr)
    partial = -inverse / np.sqrt(np.outer(np.diag(inverse), np.diag(inverse)))
    np.fill_diagonal(partial, 0)
    corr_no_diag = corr.copy()
    np.fill_diagonal(corr_no_diag, 0)
    r2 = corr_no_diag**2
    p2 = partial**2
    denominator = r2 + p2
    overall_kmo = float(r2.sum() / denominator.sum())
    per_item = (r2.sum(axis=0) / denominator.sum(axis=0)).tolist()
    n, p = ratings.shape
    determinant = max(float(np.linalg.det(corr)), np.finfo(float).tiny)
    bartlett_chi2 = -(n - 1 - (2 * p + 5) / 6) * np.log(determinant)
    bartlett_p = float(stats.chi2.sf(bartlett_chi2, p * (p - 1) / 2))
    standardized = StandardScaler().fit_transform(ratings)
    pca = PCA().fit(standardized)
    cumulative = np.cumsum(pca.explained_variance_ratio_)
    return {
        "features": ORDINAL_FEATURES,
        "n_features": p,
        "training_rows": n,
        "overall_kmo": overall_kmo,
        "per_item_kmo": dict(zip(ORDINAL_FEATURES, per_item)),
        "bartlett_sphericity_chi_square": float(bartlett_chi2),
        "bartlett_degrees_of_freedom": int(p * (p - 1) / 2),
        "bartlett_p_value": bartlett_p,
        "pca_cumulative_variance_first_10": float(cumulative[min(9, p - 1)]),
        "pca_components_for_at_least_80_percent_variance": int(np.searchsorted(cumulative, 0.8) + 1),
        "caveat": "KMO and Bartlett diagnostics are calculated on the training partition and service-rating items only. PCA is not common-factor analysis and is not asserted to reproduce the paper's procedure.",
    }


def _make_preprocessor(feature_columns: list[str] | tuple[str, ...] = PREDICTOR_FEATURES) -> ColumnTransformer:
    numeric_columns = [
        column
        for column in CONTINUOUS_FEATURES + ORDINAL_FEATURES + [TOTAL_FEATURE]
        if column in feature_columns
    ]
    categorical_columns = [column for column in CATEGORICAL_FEATURES if column in feature_columns]
    numeric_pipeline = Pipeline(
        [("imputer", SimpleImputer(strategy="mean")), ("scaler", StandardScaler())]
    )
    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        [
            ("numeric", numeric_pipeline, numeric_columns),
            ("categorical", categorical_pipeline, categorical_columns),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def _evaluate_model(name: str, pipeline: Pipeline, x_train: pd.DataFrame, x_test: pd.DataFrame, y_train: pd.Series, y_test: pd.Series) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)
    probabilities = pipeline.predict_proba(x_test)[:, 1]
    matrix = confusion_matrix(y_test, predictions, labels=[0, 1])
    result = {
        "name": name,
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision_macro": float(precision_score(y_test, predictions, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_test, predictions, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_test, predictions, average="macro", zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
        "confusion_matrix_labels": ["neutral or dissatisfied", POSITIVE_LABEL],
        "confusion_matrix": matrix.tolist(),
        "class_report": classification_report(
            y_test,
            predictions,
            labels=[0, 1],
            target_names=["neutral or dissatisfied", POSITIVE_LABEL],
            output_dict=True,
            zero_division=0,
        ),
        "positive_class": {
            "label": POSITIVE_LABEL,
            "precision": float(precision_score(y_test, predictions, pos_label=1, zero_division=0)),
            "recall": float(recall_score(y_test, predictions, pos_label=1, zero_division=0)),
            "f1": float(f1_score(y_test, predictions, pos_label=1, zero_division=0)),
        },
    }
    return result, predictions, probabilities


def _model_analysis(frame: pd.DataFrame, figures_dir: Path, tables_dir: Path) -> dict[str, Any]:
    y = (frame[TARGET] == POSITIVE_LABEL).astype(int)
    x = frame[PREDICTOR_FEATURES]
    paper_frame = frame[PREDICTOR_FEATURES].copy()
    paper_frame[TOTAL_FEATURE] = frame[ORDINAL_FEATURES].sum(axis=1, min_count=len(ORDINAL_FEATURES))
    paper_x = paper_frame.loc[:, PAPER_TABLE_FEATURES]
    train_indices, test_indices = train_test_split(
        frame.index.to_numpy(), test_size=0.2, stratify=y, random_state=SEED
    )
    y_train, y_test = y.loc[train_indices], y.loc[test_indices]
    baseline = Pipeline(
        [("preprocessor", _make_preprocessor()), ("model", LogisticRegression(max_iter=1000, random_state=SEED))]
    )
    reduced = Pipeline(
        [
            ("preprocessor", _make_preprocessor()),
            ("pca", PCA(n_components=10)),
            ("model", LogisticRegression(max_iter=1000, random_state=SEED)),
        ]
    )
    paper_table_sensitivity = Pipeline(
        [
            ("preprocessor", _make_preprocessor(PAPER_TABLE_FEATURES)),
            ("model", LogisticRegression(max_iter=1000, random_state=SEED)),
        ]
    )
    results = []
    fitted: dict[str, Pipeline] = {}
    scores: dict[str, np.ndarray] = {}
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=SEED)
    cv_scoring = ["accuracy", "precision_macro", "recall_macro", "f1_macro", "roc_auc"]
    model_specs = (
        ("original_features_logistic_regression", baseline, x),
        ("pca_10_logistic_regression", reduced, x),
        ("paper_table_feature_sensitivity_with_TOTAL", paper_table_sensitivity, paper_x),
    )
    for name, model, model_x in model_specs:
        result, _, probabilities = _evaluate_model(
            name,
            model,
            model_x.loc[train_indices],
            model_x.loc[test_indices],
            y_train,
            y_test,
        )
        cv_scores = cross_validate(
            model,
            model_x,
            y,
            cv=cv,
            scoring=cv_scoring,
            return_train_score=False,
            n_jobs=1,
        )
        result["cross_validation"] = {
            "folds": 3,
            "random_state": SEED,
            "metrics": {
                metric: {
                    "mean": float(np.mean(cv_scores[f"test_{metric}"])),
                    "std": float(np.std(cv_scores[f"test_{metric}"], ddof=1)),
                }
                for metric in cv_scoring
            },
        }
        results.append(result)
        fitted[name] = model
        scores[name] = probabilities

    fig, axes = plt.subplots(1, len(results), figsize=(6 * len(results), 4.5))
    for ax, result in zip(axes, results):
        sns.heatmap(
            np.asarray(result["confusion_matrix"]),
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=["Neutral / dissatisfied", "Satisfied"],
            yticklabels=["Neutral / dissatisfied", "Satisfied"],
            ax=ax,
        )
        ax.set(title=result["name"].replace("_", " ").title(), xlabel="Predicted", ylabel="Actual")
    fig.tight_layout()
    fig.savefig(figures_dir / "confusion_matrices.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    for result in results:
        fpr, tpr, _ = roc_curve(y_test, scores[result["name"]])
        ax.plot(fpr, tpr, label=f"{result['name'].replace('_', ' ')} (AUC={result['roc_auc']:.3f})")
    ax.plot([0, 1], [0, 1], "--", color="#666666", linewidth=1, label="Chance")
    ax.set(title="ROC curves on stratified holdout", xlabel="False positive rate", ylabel="True positive rate")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(figures_dir / "roc_curves.png", dpi=160)
    plt.close(fig)

    model = fitted["original_features_logistic_regression"]
    feature_names = model.named_steps["preprocessor"].get_feature_names_out()
    coefficients = model.named_steps["model"].coef_[0]
    coefficient_table = pd.DataFrame(
        {"feature": feature_names, "coefficient": coefficients, "absolute_coefficient": np.abs(coefficients)}
    ).sort_values("absolute_coefficient", ascending=False)
    coefficient_table.head(20).to_csv(tables_dir / "top_logistic_coefficients.csv", index=False)

    pca = fitted["pca_10_logistic_regression"].named_steps["pca"]
    pca_summary = {
        "components": int(pca.n_components_),
        "cumulative_variance_explained": float(pca.explained_variance_ratio_.sum()),
        "label": "PCA-based logistic model (not common-factor analysis)",
    }
    return {
        "evaluation_protocol": {
            "dataset": "supplied train.csv only",
            "holdout": "20% stratified random holdout",
            "random_state": SEED,
            "training_rows": int(len(train_indices)),
            "holdout_rows": int(len(test_indices)),
            "positive_label": POSITIVE_LABEL,
            "official_test_set": False,
        },
        "models": results,
        "pca_summary": pca_summary,
        "common_factor_model_status": {
            "generated": False,
            "reason": "A training-only 10-factor scikit-learn FactorAnalysis fit on the 14 rating items did not converge after 100 iterations at tolerance 0.1 on the full 83,123-row training partition. No factor-model prediction metrics are reported; PCA is used for the reduced-model comparison.",
        },
        "paper_reported_accuracy": PAPER_ACCURACY,
        "paper_table_sensitivity_features": list(PAPER_TABLE_FEATURES),
        "total_definition": {
            "feature": TOTAL_FEATURE,
            "items_summed": ORDINAL_FEATURES,
            "interpretation": "Deterministic sum of the 14 supplied ordinal service-rating items; satisfaction target is not included.",
            "leakage_assessment": "No direct target leakage because the target label is not an input to the sum. It is redundant with its component ratings, so the primary leakage-safe baseline excludes it; a separate paper-table feature sensitivity model includes it.",
        },
        "paper_comparison_note": "The paper's table includes TOTAL and uses a conditional-forward logistic regression; the sensitivity model uses the table-listed covariates with a stratified holdout and regularized scikit-learn logistic regression, so its performance is not an exact replication.",
        "top_coefficients": coefficient_table.head(12)[["feature", "coefficient"]].to_dict(orient="records"),
        "coefficient_caveat": "Coefficients describe conditional associations in the primary original-feature model, not causal effects; standardized inputs and one-hot reference categories affect their scale and interpretation.",
    }


def _site_export(
    profile: dict[str, Any],
    statistics: dict[str, Any],
    factor: dict[str, Any],
    modeling: dict[str, Any],
) -> dict[str, Any]:
    export = {
        "generated": True,
        "data_scope": "Aggregate analysis of supplied training CSV; no passenger-level records exported.",
        "profile": profile,
        "statistics": statistics,
        "factor_analysis": factor,
        "modeling": modeling,
        "figures": [
            {"file": "class_balance.png", "caption": "Satisfaction class counts in the supplied training file."},
            {"file": "missing_values.png", "caption": "Missing-value counts in the supplied training file."},
            {"file": "age_distribution.png", "caption": "Passenger age distribution."},
            {"file": "flight_distance_distribution.png", "caption": "Flight-distance distribution."},
            {"file": "satisfaction_by_groups.png", "caption": "Within-group satisfaction composition by passenger category."},
            {"file": "feature_correlation_matrix.png", "caption": "Spearman correlation matrix for numeric passenger, service-rating, and delay variables."},
            {"file": "service_rating_correlations.png", "caption": "Spearman correlations among service-rating items."},
            {"file": "delay_distributions_and_satisfaction.png", "caption": "Delay distributions and delay values by observed satisfaction label."},
            {"file": "confusion_matrices.png", "caption": "Holdout confusion matrices for all three fitted models."},
            {"file": "roc_curves.png", "caption": "Holdout ROC curves for all three fitted models."},
        ],
    }
    return export


def run(input_path: Path, output_root: Path) -> dict[str, Any]:
    input_path = input_path.resolve()
    output_root = output_root.resolve()
    figures_dir = output_root / "figures"
    tables_dir = output_root / "tables"
    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    frame, original_columns = _read_data(input_path)
    profile = _profile(frame, input_path, original_columns)
    profile["source_shape_including_identifier_columns"] = [profile["rows"], profile["columns_in_source"]]
    _save_json(tables_dir / "data_profile.json", profile)
    statistics = _statistical_analysis(frame, tables_dir)
    _plot_eda(frame, figures_dir, tables_dir)

    x_train, _, = train_test_split(
        frame[PREDICTOR_FEATURES],
        test_size=0.2,
        stratify=(frame[TARGET] == POSITIVE_LABEL).astype(int),
        random_state=SEED,
    )
    factor = _kmo_diagnostics(x_train)
    _save_json(tables_dir / "factor_diagnostics.json", factor)
    modeling = _model_analysis(frame, figures_dir, tables_dir)
    _save_json(tables_dir / "model_metrics.json", modeling)
    _save_json(tables_dir / "statistical_results.json", statistics)
    site_data = _site_export(profile, statistics, factor, modeling)
    _save_json(tables_dir / "site_data.json", site_data)

    site_assets = ROOT / "web-showcase" / "src" / "assets"
    site_figures = site_assets / "figures"
    if site_figures.exists():
        for image in figures_dir.glob("*.png"):
            shutil.copy2(image, site_figures / image.name)
    site_data_dir = site_assets / "data"
    if site_data_dir.exists():
        shutil.copy2(tables_dir / "site_data.json", site_data_dir / "analysis.json")
    return site_data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "raw" / "train.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "reports")
    args = parser.parse_args()
    results = run(args.input, args.output)
    print(
        json.dumps(
            {
                "profile": results["profile"],
                "models": [
                    {key: model[key] for key in ("name", "accuracy", "precision_macro", "recall_macro", "f1_macro", "roc_auc")}
                    for model in results["modeling"]["models"]
                ],
                "factor_diagnostics": results["factor_analysis"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
