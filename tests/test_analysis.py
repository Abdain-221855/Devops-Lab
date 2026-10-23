import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from airline_satisfaction.analysis import (  # noqa: E402
    CATEGORICAL_FEATURES,
    CONTINUOUS_FEATURES,
    ORDINAL_FEATURES,
    PAPER_TABLE_FEATURES,
    TARGET,
    TOTAL_FEATURE,
    _make_preprocessor,
    _read_data,
)


class AnalysisInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frame, cls.original_columns = _read_data(ROOT / "data" / "raw" / "train.csv")

    def test_source_dimensions_and_identifier_exclusion(self) -> None:
        self.assertEqual(len(self.frame), 103_904)
        self.assertEqual(len(self.original_columns), 25)
        self.assertNotIn("id", self.frame.columns)
        self.assertNotIn("Unnamed: 0", self.frame.columns)
        self.assertEqual(self.frame["Arrival Delay in Minutes"].isna().sum(), 310)

    def test_target_positive_label_encoding_is_explicit(self) -> None:
        encoded = (self.frame[TARGET] == "satisfied").astype(int)
        self.assertEqual(int(encoded.sum()), 45_025)
        self.assertEqual(set(encoded.unique()), {0, 1})

    def test_paper_total_sensitivity_is_not_the_target(self) -> None:
        self.assertEqual(len(PAPER_TABLE_FEATURES), 20)
        self.assertIn(TOTAL_FEATURE, PAPER_TABLE_FEATURES)
        self.assertNotIn(TARGET, PAPER_TABLE_FEATURES)
        self.assertNotIn("Seat comfort", PAPER_TABLE_FEATURES)
        self.assertNotIn("Inflight entertainment", PAPER_TABLE_FEATURES)
        self.assertNotIn("Flight Distance", PAPER_TABLE_FEATURES)

    def test_preprocessor_handles_missing_delay_and_categories(self) -> None:
        features = CATEGORICAL_FEATURES + CONTINUOUS_FEATURES + ORDINAL_FEATURES
        sample = self.frame.loc[:, features].iloc[:2_000].copy()
        transformed = _make_preprocessor().fit_transform(sample)
        self.assertEqual(transformed.shape[0], len(sample))
        self.assertTrue(pd.notna(transformed).all())


if __name__ == "__main__":
    unittest.main()
