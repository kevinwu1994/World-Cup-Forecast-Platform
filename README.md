# World Cup Forecast Platform

A Streamlit-based football analytics and forecasting platform for international tournament prediction.

The system combines ELO ratings, expected goals, Poisson score modeling, market-implied probability adjustment, and Monte Carlo simulation to generate match probabilities, score forecasts, group-stage qualification probabilities, knockout previews, champion probabilities, model-vs-market comparisons, and historical accuracy tracking.

> This project is for analytics, research, and educational purposes only. It does not provide betting recommendations.

---

## Live Dashboard

Streamlit Cloud deployment link will be added after deployment.

---

## Project Highlights

- Match outcome forecasting: home win, draw, away win
- Exact-score probability ranking using Poisson modeling
- Expected goals conversion engine
- ELO-based team strength framework
- Market odds adjustment layer
- Monte Carlo group-stage and tournament simulation
- Champion probability ranking
- Model accuracy tracking against completed match results
- Streamlit dashboard with interactive navigation

---

## Technical Stack

- Python
- Pandas / NumPy
- SciPy / scikit-learn
- Plotly
- Streamlit
- Requests
- Football data and odds API clients
- CSV-based reporting pipeline

---

## Repository Structure

```text
World Cup Forecast Platform/
├── api/                 # Data acquisition clients
├── dashboard/           # Streamlit dashboard
├── data/                # Raw and processed input data
├── models/              # Forecasting and score probability models
├── reports/             # Generated CSV outputs used by the dashboard
├── screenshots/         # Dashboard screenshots for documentation
├── scripts/             # Pipeline entry points
├── simulation/          # Monte Carlo simulation logic
├── validation/          # Accuracy tracking and validation utilities
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Dashboard Pages

- Dashboard Overview
- Match Predictions
- Score Forecast
- Group Stage
- Knockout Preview
- Champion Race
- Recent Results
- Model Accuracy
- Model vs Market

---

## How to Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run dashboard/app.py
```

Run the full forecasting pipeline:

```bash
python scripts/main_run_worldcup_pipeline.py
```

---

## Data Pipeline

The dashboard reads generated CSV files from the `reports/` directory, including:

```text
worldcup_adjusted_match_probabilities.csv
worldcup_predictions.csv
group_stage_probabilities.csv
champion_probabilities.csv
model_vs_market.csv
worldcup_live_scores.csv
prediction_accuracy.csv
```

The pipeline updates these reports before the dashboard is refreshed.

---

## Deployment Plan

This project is designed for deployment with:

```text
GitHub Repository
↓
Streamlit Community Cloud
↓
Public dashboard URL
```

Streamlit Cloud should use the following app entry point:

```text
dashboard/app.py
```

---

## Author

Fenglei Wu

M.S. Financial Engineering  
Quantitative Modeling | Forecasting | Risk Analytics | Data Science
