# 2026 World Cup Forecast Platform

### Final Tournament Analytics & Model Evaluation

An end-to-end quantitative football forecasting project built with **ELO team-strength modeling**, **Expected Goals (xG)**, **Poisson score forecasting**, **market probability calibration**, and **Monte Carlo tournament simulation**.

The platform operated as a live forecasting system during the tournament. With the tournament complete, it now serves as a permanent research archive containing the original pre-match forecasts, final results, tournament progression, and post-tournament model evaluation.

> **Tournament completed.** Live forecasting and scheduled automation have been retired. The public application now presents the final historical archive.

## Public Dashboard

**Streamlit application:**

https://world-cup-forecast-platform.streamlit.app/

The final dashboard contains nine research and archive views:

- Final tournament dashboard
- Historical forecast archive
- Exact-score forecast archive
- Group-stage qualification archive
- Complete knockout results
- Pre-tournament champion forecast
- Complete tournament results
- Final model evaluation
- Archived model-versus-market analysis

## Final Dashboard

<img src="screenshoots/final_dashboard.png" alt="Final World Cup Forecast Dashboard" width="1000">

## Tournament Archive

The permanent archive preserves the earliest committed pre-match probabilities recovered for all 104 matchups and pairs them with the completed tournament results.

<img src="screenshoots/final_forecast_archive.png" alt="Historical Forecast Archive" width="1000">

## Final Model Evaluation

The archived forecasts were evaluated against all 104 final results. The dashboard reports three-way outcome performance, ranked exact-score hit rates, and probabilistic scoring metrics.

| Evaluation metric | Final result |
| --- | ---: |
| Evaluated matches | 104 |
| Three-way outcome hit rate | 64.4% |
| Top-1 exact-score hit rate | 12.5% |
| Top-3 exact-score hit rate | 35.6% |
| Top-5 exact-score hit rate | 51.9% |
| Top-8 exact-score hit rate | 71.2% |
| Brier score | 0.481 |
| Log loss | 0.822 |

<img src="screenshoots/final_model_accuracy.png" alt="Final Model Accuracy Evaluation" width="1000">

## Complete Knockout Results

<img src="screenshoots/final_knockout_results.png" alt="Complete Knockout Results" width="1000">

## Project Lifecycle

### 1. Model development

The forecasting system combined relative team strength, expected scoring rates, score-distribution modeling, market information, and tournament simulation.

### 2. Live tournament operation

An automated GitHub Actions pipeline collected data, generated reports, refreshed forecasts, and supplied the public Streamlit dashboard during the tournament.

### 3. Historical recovery

When the live APIs no longer returned the complete tournament dataset, the final archive was reconstructed from committed pre-match snapshots preserved in the repository history. Forecasts shown in the archive were not regenerated after the results were known.

### 4. Final evaluation

All recovered forecasts were matched with the completed tournament results to produce the permanent model evaluation and research archive. Live forecasting and scheduled updates are now retired.

## Quantitative Methodology

### ELO team-strength modeling

ELO ratings quantify relative national-team strength and provide the foundation for matchup-level expectations.

### Expected Goals estimation

Offensive and defensive strength are translated into expected home and away scoring rates.

### Poisson score forecasting

Poisson distributions convert expected goals into ranked exact-score probabilities and home/draw/away outcome probabilities.

### Market probability calibration

Market-implied information is incorporated when available to calibrate the model probabilities and support model-versus-market research.

### Monte Carlo tournament simulation

The platform ran 10,000+ tournament simulations to estimate group qualification, knockout advancement, and championship probabilities.

## Final Tournament Coverage

| Item | Coverage |
| --- | ---: |
| National teams | 48 |
| Groups | 12 |
| Group-stage matches | 72 |
| Round of 32 | 16 |
| Round of 16 | 8 |
| Quarterfinals | 4 |
| Semifinals | 2 |
| Third-place match | 1 |
| Final | 1 |
| Total archived forecasts and results | 104 |
| Tournament simulations | 10,000+ |

## Technology Stack

- **Programming:** Python
- **Data processing:** pandas, NumPy
- **Statistical modeling:** SciPy, scikit-learn
- **Visualization:** Streamlit, Plotly
- **Automation:** GitHub Actions
- **Deployment:** Streamlit Community Cloud

## Repository Structure

```text
World-Cup-Forecast-Platform/
├── api/                    # Historical data-acquisition clients
├── dashboard/              # Final Streamlit archive and preserved live-era app
│   ├── app.py              # Public final archive
│   ├── app_live_legacy.py  # Preserved tournament-period dashboard
│   └── archive_data/       # Materialized final archive datasets
├── data/                   # Raw and processed project data
├── models/                 # Forecasting models
├── reports/                # Forecast reports and historical outputs
├── screenshoots/           # Dashboard documentation images
├── scripts/                # Original pipeline scripts
├── simulation/             # Monte Carlo simulation engine
└── validation/             # Model evaluation framework
```

## Run the Final Dashboard Locally

Install the existing project dependencies:

```bash
pip install -r requirements.txt
```

Launch the archived dashboard:

```bash
streamlit run dashboard/app.py --server.port 8503
```

The final application reads only the repository's archived dashboard datasets. It does not call live APIs, run the forecast pipeline, or execute subprocesses.

## Archive Status

| Component | Status |
| --- | --- |
| Live forecasting | Retired |
| Scheduled automation | Retired |
| Historical forecast recovery | Complete |
| Final model evaluation | Complete |
| Public Streamlit archive | Deployed |

## Author

### Fenglei Wu

**M.S. Financial Engineering**

Claremont Graduate University

Areas of focus:

- Quantitative Research
- Forecasting Models
- Risk Analytics
- Data Science
- Sports Analytics

GitHub: https://github.com/kevinwu1994

## Disclaimer

This project is intended for quantitative research, analytics, education, and portfolio demonstration only. It does not provide betting recommendations, financial advice, wagering guidance, or commercial forecasting services.
