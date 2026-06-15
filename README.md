# ⚽ World Cup Forecast Platform

### AI-Powered Football Forecasting & Tournament Analytics System

A production-style football forecasting platform that combines **ELO Ratings**, **Expected Goals (xG)**, **Poisson Score Modeling**, **Market Odds Calibration**, and **Monte Carlo Simulation** to generate match forecasts, exact-score probabilities, tournament projections, and model performance analytics.

Built as an end-to-end quantitative modeling project with automated data pipelines, simulation engines, and interactive dashboard visualization.

---

## 🌐 Live Dashboard

**Dashboard URL**

https://world-cup-forecast-platform.streamlit.app/

---

# Dashboard Preview

## Dashboard Overview

<img src="https://raw.githubusercontent.com/kevinwu1994/World-Cup-Forecast-Platform/main/screenshots/dashboard_home.png" width="1000">

---

## Score Forecast Engine

<img src="https://raw.githubusercontent.com/kevinwu1994/World-Cup-Forecast-Platform/main/screenshots/score_forecast.png" width="1000">

---

## Model Validation & Accuracy Tracking

<img src="https://raw.githubusercontent.com/kevinwu1994/World-Cup-Forecast-Platform/main/screenshots/model_accuracy_1.png" width="1000">

---

# Project Motivation

Forecasting international football tournaments is a challenging quantitative problem involving:

* Team strength estimation
* Goal-scoring distributions
* Tournament structure uncertainty
* Market sentiment and bookmaker expectations
* Dynamic progression through knockout stages

This project was designed to build a fully automated forecasting framework capable of generating:

* Match outcome probabilities
* Exact-score forecasts
* Group-stage qualification probabilities
* Knockout-stage projections
* Championship probabilities
* Historical prediction validation

The objective is to demonstrate practical applications of statistical modeling, simulation methods, probability theory, and data visualization in a real-world forecasting environment.

---

# Forecasting Architecture

```text
Football Data Sources
            │
            ▼
      ELO Rating Engine
            │
            ▼
   Expected Goals (xG)
            │
            ▼
  Poisson Score Modeling
            │
            ▼
 Market Odds Adjustment
            │
            ▼
Monte Carlo Simulation
            │
            ▼
 Forecast Report Engine
            │
            ▼
 Streamlit Dashboard
```

---

# Quantitative Methodology

## 1. ELO Rating Framework

Team strength is estimated using ELO ratings to quantify relative performance differences between national teams.

The model continuously updates strength estimates using historical match performance and competitive context.

---

## 2. Expected Goals (xG) Engine

Expected goals are generated from offensive and defensive ratings.

The xG framework transforms team strength metrics into expected scoring outputs that drive score forecasting.

Example:

```text
France xG: 1.92
Senegal xG: 0.78
```

---

## 3. Poisson Score Modeling

Match scores are modeled using Poisson distributions.

The score engine estimates probabilities for:

* 0–0
* 1–0
* 2–1
* 3–0
* etc.

and generates ranked exact-score forecasts.

---

## 4. Market Odds Calibration

Bookmaker probabilities are incorporated as an additional information source.

This calibration layer helps reduce model bias and improve probability realism.

---

## 5. Monte Carlo Tournament Simulation

The platform executes 10,000+ tournament simulations to estimate:

* Group-stage qualification probability
* Knockout-stage advancement probability
* Championship probability

This allows the model to forecast tournament progression beyond individual matches.

---

# Platform Features

### Match Prediction Engine

Forecasts:

* Home Win Probability
* Draw Probability
* Away Win Probability

---

### Exact Score Forecasting

Generates ranked score probabilities using Poisson distributions.

Example:

```text
Belgium 1–0 Egypt
Probability: 13.4%

Belgium 2–0 Egypt
Probability: 13.3%
```

---

### Group Stage Simulation

Projects qualification probabilities for all teams within each group.

---

### Knockout Bracket Projection

Simulates likely progression paths through:

* Round of 16
* Quarter Finals
* Semi Finals
* Final

---

### Champion Probability Ranking

Produces dynamic championship probability rankings based on simulation outcomes.

---

### Model Accuracy Tracking

Evaluates historical performance using:

* Winner Prediction Accuracy
* Top-3 Score Hit Rate
* Top-5 Score Hit Rate
* Top-8 Score Hit Rate

This enables ongoing model validation and performance monitoring.

---

### Model vs Market Analysis

Compares internal model probabilities against market-implied probabilities to identify forecasting differences.

---

# Current Coverage

| Metric                 | Coverage                              |
| ---------------------- | ------------------------------------- |
| Teams                  | 48                                    |
| Group Stage Matches    | 72                                    |
| Tournament Simulations | 10,000+                               |
| Forecast Types         | Match, Score, Qualification, Champion |
| Dashboard Pages        | 9                                     |
| Validation Module      | Included                              |

---

# Technology Stack

## Programming

* Python

## Data Processing

* Pandas
* NumPy

## Statistical Modeling

* SciPy
* scikit-learn

## Visualization

* Streamlit
* Plotly

## Forecasting Methods

* ELO Ratings
* Expected Goals (xG)
* Poisson Probability Models
* Monte Carlo Simulation

## External Integrations

* Football Data APIs
* Odds APIs

---

# Repository Structure

```text
World-Cup-Forecast-Platform/
│
├── api/                 # Data acquisition clients
├── dashboard/           # Streamlit dashboard application
├── data/                # Raw and processed datasets
├── models/              # Forecasting models
├── reports/             # Generated forecasting outputs
├── screenshots/         # Dashboard screenshots
├── scripts/             # Pipeline execution scripts
├── simulation/          # Monte Carlo simulation engine
├── validation/          # Accuracy tracking framework
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

# Running Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run dashboard/app.py
```

Run the forecasting pipeline:

```bash
python scripts/main_run_worldcup_pipeline.py
```

---

# Deployment

The platform is deployed using:

```text
GitHub Repository
        │
        ▼
Streamlit Community Cloud
        │
        ▼
Public Forecast Dashboard
```

Application entry point:

```text
dashboard/app.py
```

---

# Future Development

Planned enhancements include:

* Probability Calibration Curves
* Brier Score Evaluation
* Log-Loss Tracking
* Historical Backtesting Framework
* Automated Daily Forecast Updates
* Team-Level Analytics Pages
* Advanced Tournament Bracket Visualization

---

# About the Author

## Fenglei Wu

**M.S. Financial Engineering**
Claremont Graduate University

Areas of Interest:

* Quantitative Research
* Forecasting Models
* Risk Analytics
* Data Science
* Machine Learning
* Sports Analytics

GitHub:
https://github.com/kevinwu1994

---

### Disclaimer

This project is intended for research, analytics, and educational purposes only.

It does not provide betting recommendations, financial advice, or wagering guidance.
