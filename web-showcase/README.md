# Angular research showcase

This is a static, single-page Angular application. It reads aggregate analysis JSON and generated figures from `src/assets/`; it does not call a backend or include passenger-level rows. If generated assets are absent, the app presents a clear not-generated state.

## Local setup and build

From the repository root, first generate outputs:

```powershell
python -m pip install -r requirements.txt
python src/airline_satisfaction/analysis.py
```

Then install and build the site:

```powershell
Set-Location web-showcase
npm install
npm run build
```

The first `npm install` creates the dependency lockfile; commit it and use `npm ci` for subsequent clean/reproducible installs.

For a local development server, run `npm start` from `web-showcase`. Production output is `web-showcase/dist/airline-satisfaction/browser/`.

## GitHub Pages

The Angular build sets a relative base URL (`./`) and uses in-page anchor navigation rather than client-side routes. This avoids assuming a repository slug or custom domain and supports publishing the static output from a project subpath.

The repository's deployment workflow builds the site and publishes `dist/airline-satisfaction/browser/` on pushes to `main`. Enable it in **Repository Settings → Pages → Build and deployment → Source → GitHub Actions**. The configured project URL is [https://abdain-221855.github.io/Devops-Lab/](https://abdain-221855.github.io/Devops-Lab/); it becomes available after Pages is enabled and the first workflow run succeeds.

Before publishing, run the Python workflow and verify the generated data and figures are aggregate-only. No raw CSV is copied into the web application.

## Output provenance

`src/assets/data/analysis.json` is produced from `reports/tables/site_data.json`; `src/assets/figures/` receives the generated plots. Both are generated when the analysis script runs. Paper numbers are labeled as paper-reported in the UI and remain separate from computed metrics. The missing official test CSV is not reconstructed or substituted.
