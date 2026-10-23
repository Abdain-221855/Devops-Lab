import { DecimalPipe, KeyValuePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { AnalysisPayload } from './analysis-data.model';

@Component({
  selector: 'airline-root',
  standalone: true,
  imports: [DecimalPipe, KeyValuePipe],
  templateUrl: './app.component.html',
})
export class AppComponent implements OnInit {
  private readonly http = inject(HttpClient);

  data: AnalysisPayload | null = null;
  loading = true;
  errorMessage: string | null = null;

  ngOnInit(): void {
    this.http.get<AnalysisPayload>('assets/data/analysis.json').subscribe({
      next: (data) => {
        this.data = data;
        this.loading = false;
      },
      error: () => {
        this.errorMessage =
          'Analysis results are not available yet. Run the Python workflow from the repository root, then rebuild the showcase.';
        this.loading = false;
      },
    });
  }

  formatPercent(value: number): string {
    return `${(value * 100).toFixed(1)}%`;
  }

  formatPValue(value: number): string {
    return value < 0.001 ? '<0.001' : value.toFixed(3);
  }

  modelTitle(name: string): string {
    if (name === 'pca_10_logistic_regression') {
      return '10-component PCA + logistic regression';
    }
    if (name === 'paper_table_feature_sensitivity_with_TOTAL') {
      return 'Paper-table covariates + TOTAL (sensitivity)';
    }
    return 'Original-feature logistic regression';
  }
}
