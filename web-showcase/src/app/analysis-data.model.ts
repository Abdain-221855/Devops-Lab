export interface ModelMetrics {
  name: string;
  accuracy: number;
  precision_macro: number;
  recall_macro: number;
  f1_macro: number;
  roc_auc: number;
  positive_class: {
    label: string;
    precision: number;
    recall: number;
    f1: number;
  };
  confusion_matrix: number[][];
  cross_validation: {
    folds: number;
    metrics: Record<string, { mean: number; std: number }>;
  };
}

export interface GroupComparison {
  feature: string;
  test: string;
  statistic: number;
  p_value: number;
  neutral_or_dissatisfied_mean: number;
  satisfied_mean: number;
  neutral_or_dissatisfied_n: number;
  satisfied_n: number;
  sensitivity_test: string;
  mann_whitney_u: number;
  mann_whitney_p_value: number;
}

export interface FigureAsset {
  file: string;
  caption: string;
}

export interface AnalysisPayload {
  generated: boolean;
  data_scope: string;
  profile: {
    rows: number;
    columns_in_source: number;
    predictor_count: number;
    class_counts: Record<string, number>;
    class_percentages: Record<string, number>;
    missing_values: Record<string, number>;
    positive_label: string;
    split: {
      method: string;
      test_size: number;
      random_state: number;
      official_test_file_used: boolean;
    };
    versions: Record<string, string>;
  };
  statistics: {
    group_comparisons: GroupComparison[];
    categorical_cross_tabs: Record<
      string,
      {
        chi_square_test: {
          statistic: number;
          degrees_of_freedom: number;
          p_value: number;
        };
      }
    >;
    interpretation_note: string;
  };
  factor_analysis: {
    n_features: number;
    training_rows: number;
    overall_kmo: number;
    bartlett_p_value: number;
    pca_cumulative_variance_first_10: number;
    pca_components_for_at_least_80_percent_variance: number;
    caveat: string;
  };
  modeling: {
    evaluation_protocol: {
      dataset: string;
      holdout: string;
      random_state: number;
      training_rows: number;
      holdout_rows: number;
      positive_label: string;
      official_test_set: boolean;
    };
    models: ModelMetrics[];
    pca_summary: {
      components: number;
      cumulative_variance_explained: number;
      label: string;
    };
    common_factor_model_status: {
      generated: boolean;
      reason: string;
    };
    paper_reported_accuracy: Record<string, number>;
    paper_comparison_note: string;
  };
  figures: FigureAsset[];
}
