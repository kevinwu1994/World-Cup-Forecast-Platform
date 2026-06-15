# ⚽ World Cup Forecast Platform

AI-Powered Football Analytics & Forecasting System

ELO Ratings • Expected Goals (xG) • Poisson Modeling • Market Odds Adjustment • Monte Carlo Simulation

---

## Live Dashboard

🌐 https://world-cup-forecast-platform.streamlit.app/

---

## Dashboard Preview

### Dashboard Overview

![Dashboard](screenshots/dashboard_home.png)

### Score Forecast

![Score Forecast](screenshots/score_forecast.png)

### Model Accuracy

![Model Accuracy](screenshots/model_accuracy.png)

---

## Project Motivation

Forecasting international football tournaments is a challenging quantitative problem. Team strength, expected goals, tournament structure, and market sentiment all influence match outcomes.

This project was built to create a fully automated forecasting platform capable of generating:

* Match outcome probabilities
* Exact-score forecasts
* Group-stage qualification probabilities
* Knockout-stage projections
* Championship probabilities
* Historical model validation

The goal is to combine quantitative modeling, simulation techniques, and interactive analytics into a production-style forecasting dashboard.

> This project is intended for analytics, research, and educational purposes only. It does not provide betting recommendations.

---

## Forecasting Pipeline

```text
Football Data
      ↓
ELO Rating Engine
      ↓
Expected Goals (xG) Model
      ↓
Poisson Score Distribution
      ↓
Market Odds Adjustment
      ↓
Monte Carlo Tournament Simulation
      ↓
Forecast Reports
      ↓
Streamlit Dashboard
```

---

## Methodology

### 1. ELO Rating Framework

Team strength is estimated using ELO ratings to quantify relative performance differences between national teams.

### 2. Expected Goals (xG) Engine

Expected goals are generated from offensive and defensive team ratings and used as scoring expectations.

### 3. Poisson Score Modeling

Goal distributions are modeled using Poisson probabilities to estimate exact-score outcomes.

### 4. Market Adjustment Layer

Bookmaker odds are incorporated as an additional information source to improve calibration.

### 5. Monte Carlo Simulation

10,000+ tournament simulations are executed to estimate:

* Group qualification probability
* Knockout progression probability
* Championship probability

---

## Current Capabilities

✅ Match outcome forecasting

✅ Exact-score probability forecasting

✅ Expected goals estimation

✅ Group-stage qualification simulation

✅ Knockout bracket projection

✅ Championship probability ranking

✅ Model vs Market comparison

✅ Historical forecast validation

✅ Interactive Streamlit dashboard

---

## Dashboard Features

### Match Predictions

Forecasts home win, draw, and away win probabilities.

### Score Forecast

Generates exact-score probability rankings using Poisson distributions.

### Group Stage Overview

Simulates qualification probabilities for all teams.

### Knockout Preview

Projects likely tournament progression paths.

### Champion Race

Ranks teams by championship probability.

### Model Accuracy

Tracks historical forecasting performance and prediction hit rates.

### Model vs Market

Compares model probabilities against market-implied probabilities.

---

## Technical Stack

### Data & Modeling

* Python
* Pandas
* NumPy
* SciPy
* scikit-learn

### Visualization

* Streamlit
* Plotly

### Data Sources

* Football Data APIs
* Market Odds APIs

### Simulation

* Monte Carlo Simulation
* Poisson Probability Models
* ELO Rating Systems

---

## Repository Structure

```text
World Cup Forecast Platform/
├── api/                 # Data acquisition clients
├── dashboard/           # Streamlit dashboard
├── data/                # Raw and processed input data
├── models/              # Forecasting and score probability models
├── reports/             # Dashboard output reports
├── screenshots/         # Dashboard screenshots
├── scripts/             # Pipeline entry points
├── simulation/          # Monte Carlo simulation logic
├── validation/          # Model validation and accuracy tracking
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Running Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Launch the dashboard:

```bash
streamlit run dashboard/app.py
```

Run the full forecasting pipeline:

```bash
python scripts/main_run_worldcup_pipeline.py
```

---

## Deployment

```text
GitHub Repository
        ↓
Streamlit Community Cloud
        ↓
Public Dashboard
```

Dashboard entry point:

```text
dashboard/app.py
```

---

## Future Enhancements

* Probability calibration analysis
* Brier Score evaluation
* Log-loss tracking
* Automated daily updates
* Historical backtesting framework
* Interactive tournament bracket visualization
* Team-level analytics pages

---

## Author

### Fenglei Wu

M.S. Financial Engineering
Claremont Graduate University

Areas of Interest:

* Quantitative Research
* Forecasting Models
* Risk Analytics
* Data Science
* Machine Learning

GitHub: https://github.com/kevinwu1994
