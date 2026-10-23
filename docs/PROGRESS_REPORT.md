# Project progress report

**Updated:** 2026-10-23
**Overall status:** Planned implementation phases are complete for the files currently available. The Angular showcase is live; remaining items depend on optional inputs or further research replication.

## Live deployment

- **Website:** [https://abdain-221855.github.io/Devops-Lab/](https://abdain-221855.github.io/Devops-Lab/)
- **Repository:** [Abdain-221855/Devops-Lab](https://github.com/Abdain-221855/Devops-Lab)
- **Latest verified Pages run:** [Workflow run #4 — build and deploy succeeded](https://github.com/Abdain-221855/Devops-Lab/actions/runs/39912297817)

The production workflow successfully installed dependencies, built the Angular app, uploaded the Pages artifact, and deployed it. The live page was opened and rendered. A browser check confirmed the Models in-page navigation works and the 390px mobile viewport does not have horizontal overflow. This was a focused responsive/navigation check, not a complete cross-browser accessibility audit.

## Plan checklist

- [x] **Phase A — Audit:** inspected the repository, paper, CSV schema and quality, notebook availability, and frontend availability; recorded evidence in [PROJECT_AUDIT.md](./PROJECT_AUDIT.md).
- [x] **Phase B — Exploratory analysis:** generated reproducible aggregate EDA figures, tables, cross-tabs, and group comparisons from the supplied training CSV.
- [x] **Phase C — Modeling:** evaluated leakage-safe logistic regression and PCA pipelines, plus a separately labeled paper-table `TOTAL` sensitivity model, using a stratified holdout and cross-validation.
- [x] **Phase D — Research documentation:** documented methods, computed results, paper-reported results, data dictionary, and limitations.
- [x] **Phase E — Static showcase:** implemented the Angular showcase, supplied it aggregate data and charts, and deployed it to GitHub Pages.
- [x] **Phase F — Verification:** Python compilation and all 4 unit tests passed; the workflow and notebook executed; generated website JSON matches the analysis output; the GitHub Actions production build and deployment passed; live page, navigation, and a mobile viewport were checked.

## Remaining work and dependencies

- [ ] **Official test-set evaluation (requires the actual `data/raw/test.csv`).** The available CSV is only the 103,904-row training split. Current model scores use a stratified holdout from that file and are not official test-set metrics. Do not use a printed notebook preview as a substitute.
- [ ] **Original-notebook comparison (requires the original `.ipynb`).** The original notebook was not supplied; `notebooks/reproduction_analysis.ipynb` is a new, reproducible workflow, not a reconstruction of the absent notebook.
- [ ] **Exact factor-analysis reproduction (requires methodological clarification and a convergent, paper-compatible fit).** The tested ten-factor `FactorAnalysis` estimator did not converge on the training partition, so no common-factor predictive score is reported. The PCA result is a separate dimensionality-reduction comparison, not a replacement claim.
- [ ] **Optional broader browser/accessibility testing.** The live page and a mobile viewport/navigation path were smoke-tested; additional browsers, device sizes, keyboard-only flows, and assistive-technology testing remain useful before treating the site as comprehensively accessibility-verified.

No additional project phase is blocked for the currently supplied inputs. The first two items can only be completed if the missing source files become available; the remaining items are optional follow-up validation/research.
