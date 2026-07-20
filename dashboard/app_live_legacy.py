from pathlib import Path
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
import html as html_lib

import pandas as pd
import streamlit as st
import plotly.express as px
import streamlit.components.v1 as components


APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
REPORTS_DIR = PROJECT_ROOT / "reports"

ADJUSTED_FILE = REPORTS_DIR / "worldcup_adjusted_match_probabilities.csv"
SCORE_FILE = REPORTS_DIR / "worldcup_predictions.csv"
GROUP_FILE = REPORTS_DIR / "group_stage_probabilities.csv"
CHAMPION_FILE = REPORTS_DIR / "champion_probabilities.csv"
MARKET_FILE = REPORTS_DIR / "model_vs_market.csv"
SCORES_FILE = REPORTS_DIR / "worldcup_live_scores.csv"
ACCURACY_FILE = REPORTS_DIR / "prediction_accuracy.csv"


st.set_page_config(
    page_title="World Cup Forecast Dashboard",
    page_icon="🏆",
    layout="wide",
)


FLAG = {
    "Argentina": "🇦🇷", "France": "🇫🇷", "Brazil": "🇧🇷", "England": "🏴",
    "Spain": "🇪🇸", "Germany": "🇩🇪", "Netherlands": "🇳🇱", "Portugal": "🇵🇹",
    "Belgium": "🇧🇪", "Uruguay": "🇺🇾", "Mexico": "🇲🇽", "South Africa": "🇿🇦",
    "South Korea": "🇰🇷", "Czechia": "🇨🇿", "Czech Republic": "🇨🇿",
    "Canada": "🇨🇦", "Qatar": "🇶🇦", "Switzerland": "🇨🇭",
    "Bosnia and Herzegovina": "🇧🇦", "Bosnia & Herzegovina": "🇧🇦",
    "Morocco": "🇲🇦", "Scotland": "🏴", "Haiti": "🇭🇹",
    "Australia": "🇦🇺", "Turkey": "🇹🇷", "USA": "🇺🇸",
    "United States": "🇺🇸", "Paraguay": "🇵🇾", "Curacao": "🇨🇼",
    "Curaçao": "🇨🇼", "Japan": "🇯🇵", "Ivory Coast": "🇨🇮",
    "Ecuador": "🇪🇨", "Sweden": "🇸🇪", "Tunisia": "🇹🇳",
    "Cape Verde": "🇨🇻", "Egypt": "🇪🇬", "Saudi Arabia": "🇸🇦",
    "Iran": "🇮🇷", "New Zealand": "🇳🇿", "Senegal": "🇸🇳",
    "Norway": "🇳🇴", "Algeria": "🇩🇿", "Austria": "🇦🇹",
    "Jordan": "🇯🇴", "DR Congo": "🇨🇩", "Croatia": "🇭🇷",
    "Ghana": "🇬🇭", "Panama": "🇵🇦", "Uzbekistan": "🇺🇿",
    "Colombia": "🇨🇴",
}

FLAG_CODE = {
    "Argentina": "ar",
    "France": "fr",
    "Brazil": "br",
    "England": "gb-eng",
    "Spain": "es",
    "Germany": "de",
    "Netherlands": "nl",
    "Portugal": "pt",
    "Belgium": "be",
    "Uruguay": "uy",
    "Mexico": "mx",
    "South Africa": "za",
    "South Korea": "kr",
    "Czechia": "cz",
    "Czech Republic": "cz",
    "Canada": "ca",
    "Qatar": "qa",
    "Switzerland": "ch",
    "Bosnia and Herzegovina": "ba",
    "Bosnia & Herzegovina": "ba",
    "Morocco": "ma",
    "Scotland": "gb-sct",
    "Haiti": "ht",
    "Australia": "au",
    "Turkey": "tr",
    "USA": "us",
    "United States": "us",
    "Paraguay": "py",
    "Curacao": "cw",
    "Curaçao": "cw",
    "Japan": "jp",
    "Ivory Coast": "ci",
    "Ecuador": "ec",
    "Sweden": "se",
    "Tunisia": "tn",
    "Cape Verde": "cv",
    "Egypt": "eg",
    "Saudi Arabia": "sa",
    "Iran": "ir",
    "New Zealand": "nz",
    "Senegal": "sn",
    "Norway": "no",
    "Algeria": "dz",
    "Austria": "at",
    "Jordan": "jo",
    "DR Congo": "cd",
    "Croatia": "hr",
    "Ghana": "gh",
    "Panama": "pa",
    "Uzbekistan": "uz",
    "Colombia": "co",
}


def flag_img(team, size=24):
    code = FLAG_CODE.get(str(team))
    if not code:
        return '<span class="flag-emoji">🏳️</span>'

    return (
        f'<img class="flag-img" '
        f'src="https://flagcdn.com/w40/{code}.png" '
        f'width="{size}" />'
    )


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def esc(x):
    return html_lib.escape(str(x))


def pct(x):
    try:
        return f"{float(x):.1%}"
    except Exception:
        return "-"


def width(x):
    try:
        return max(0, min(100, float(x) * 100))
    except Exception:
        return 0


def flag(team):
    return FLAG.get(str(team), "🏳️")


def result_label(row):
    probs = {
        "HOME": row["home_prob"],
        "DRAW": row["draw_prob"],
        "AWAY": row["away_prob"],
    }
    return max(probs, key=probs.get)


def kickoff(row):
    raw = row.get("commence_time", None)
    if pd.notna(raw):
        try:
            dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
            la = dt.astimezone(ZoneInfo("America/Los_Angeles"))
            return la.strftime("%b %d, %Y"), la.strftime("%I:%M %p PDT")
        except Exception:
            pass

    raw = row.get("date", None)
    if pd.notna(raw):
        return str(raw), "Kickoff time unavailable"

    return "TBD", "Time unavailable"


def run_pipeline():
    return subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "main_run_worldcup_pipeline.py")],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )


adjusted_df = load_csv(ADJUSTED_FILE)
score_df = load_csv(SCORE_FILE)
group_df = load_csv(GROUP_FILE)
champion_df = load_csv(CHAMPION_FILE)
market_df = load_csv(MARKET_FILE)
scores_df = load_csv(SCORES_FILE)
accuracy_df = load_csv(ACCURACY_FILE)

if not accuracy_df.empty:
    bool_cols = [
        "matched",
        "result_hit",
        "top1_hit",
        "top3_hit",
        "top5_hit",
        "top8_hit",
    ]

    for col in bool_cols:
        if col in accuracy_df.columns:
            accuracy_df[col] = (
                accuracy_df[col]
                .astype(str)
                .str.lower()
                .map({"true": True, "false": False})
                .fillna(False)
            )

if not score_df.empty:
    score_df["match_label"] = score_df["home_team"] + " vs " + score_df["away_team"]

    if not scores_df.empty:
        time_df = scores_df[["home_team", "away_team", "commence_time", "completed"]].copy()
        score_df = score_df.merge(
            time_df,
            on=["home_team", "away_team"],
            how="left",
        )

    if "commence_time" in score_df.columns:
        score_df["commence_dt"] = pd.to_datetime(
            score_df["commence_time"],
            errors="coerce",
            utc=True,
        )

    if "completed" in score_df.columns:
        score_df["completed"] = score_df["completed"].fillna(False)

if not adjusted_df.empty and not scores_df.empty:
    time_df = scores_df[["home_team", "away_team", "commence_time", "completed"]].copy()
    adjusted_df = adjusted_df.merge(
        time_df,
        on=["home_team", "away_team"],
        how="left",
    )

if not adjusted_df.empty and "commence_time" in adjusted_df.columns:
    adjusted_df["commence_dt"] = pd.to_datetime(
        adjusted_df["commence_time"],
        errors="coerce",
        utc=True,
    )

    adjusted_df["completed"] = adjusted_df["completed"].fillna(False)

    adjusted_df = adjusted_df.sort_values(
        ["completed", "commence_dt"],
        ascending=[True, True],
    )

with st.sidebar:
    st.markdown("## 🏆 World Cup")
    st.markdown("### Forecast System")
    st.divider()

    st.info("Forecast data updates automatically via GitHub Actions.")

    st.divider()
    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "Match Predictions",
            "Score Forecast",
            "Group Stage",
            "Knockout Preview",
            "Champion Race",
            "Recent Results",
            "Model Accuracy",
            "Model vs Market",
        ],
    )

    st.divider()
    st.markdown("### MODEL APPROACH")
    st.markdown(
        """
        ✅ ELO Ratings  
        ✅ Expected Goals xG  
        ✅ Poisson Score Model  
        ✅ Market Odds Adjustment  
        ✅ Monte Carlo Simulation  
        """
    )
    st.divider()
    st.caption("Public analytics dashboard. No betting recommendations.")


def score_list(home, away, n=3):
    if score_df.empty:
        return ""
    df = score_df[
        (score_df["home_team"] == home)
        & (score_df["away_team"] == away)
    ].sort_values("rank").head(n)

    return " · ".join(
        f"{esc(r['score'])} <span>{pct(r['score_probability'])}</span>"
        for _, r in df.iterrows()
    )


def match_card(row):
    home = row["home_team"]
    away = row["away_team"]
    label = result_label(row)
    date, time = kickoff(row)
    badge_class = {"HOME": "green", "DRAW": "gray", "AWAY": "red"}[label]
    top_scores = score_list(home, away, 3)

    return f"""
    <div class="match-card">
        <div class="match-top">
            <div class="date-box">
                <div class="date-month">{esc(date.split()[0] if date != 'TBD' else 'TBD')}</div>
                <div class="date-day">{esc(date.split()[1].replace(',', '') if len(date.split()) > 1 else '--')}</div>
            </div>
            <div class="teams">
                <div class="teams-line">
                    <span>{flag_img(home, 28)}</span>
                    <span>{esc(home)}</span>
                    <span class="vs">vs</span>
                    <span>{flag_img(away, 28)}</span>
                    <span>{esc(away)}</span>
                </div>
                <div class="meta">Group {esc(row.get('group', '-'))} · {esc(time)}</div>
            </div>
            <div class="badge {badge_class}">{label} WIN</div>
        </div>

        <div class="prob-grid">
            <div>
                <div class="prob-label home">HOME</div>
                <div class="prob-value home">{pct(row['home_prob'])}</div>
                <div class="bar"><div class="fill home-fill" style="width:{width(row['home_prob'])}%"></div></div>
            </div>
            <div>
                <div class="prob-label draw">DRAW</div>
                <div class="prob-value draw">{pct(row['draw_prob'])}</div>
                <div class="bar"><div class="fill draw-fill" style="width:{width(row['draw_prob'])}%"></div></div>
            </div>
            <div>
                <div class="prob-label away">AWAY</div>
                <div class="prob-value away">{pct(row['away_prob'])}</div>
                <div class="bar"><div class="fill away-fill" style="width:{width(row['away_prob'])}%"></div></div>
            </div>
        </div>

        <div class="top-scores">Top scores: {top_scores}</div>
    </div>
    """


def render_next_matches(limit=4):
    if adjusted_df.empty:
        return "<div class='panel'>Missing match probability file.</div>"

    df = adjusted_df.copy()
    if "completed" in df.columns:
        df = df[df["completed"] != True]

    if df.empty:
        df = adjusted_df.copy()

    if "commence_dt" in df.columns:
        now_utc = pd.Timestamp.utcnow()
        df = df[
            (df["commence_dt"].isna()) |
            (df["commence_dt"] >= now_utc)
        ]
        df = df.sort_values("commence_dt")

    cards = "".join(match_card(row) for _, row in df.head(limit).iterrows())

    return f"""
    <div class="panel wide">
        <div class="panel-title">
            <span>NEXT MATCH PREDICTIONS</span>
            <span class="link">View all →</span>
        </div>
        <div class="carousel-wrap">
            <div class="match-grid" id="nextMatchCarousel">{cards}</div>
                <button class="carousel-arrow" onclick="document.getElementById('nextMatchCarousel').scrollBy({{left: 340, behavior: 'smooth'}})">›</button>
            </div>
    </div>
    """

def render_score_forecast():
    if score_df.empty:
        return "<div class='panel'>Missing score forecast.</div>"

    df = score_df.copy()

    if "completed" in df.columns:
        df = df[df["completed"] != True]

    if "commence_dt" in df.columns:
        df = df.sort_values(["commence_dt", "match_id", "rank"])
    else:
        df = df.sort_values(["match_id", "rank"])

    if df.empty:
        return "<div class='panel'>No active score forecast available.</div>"

    first_match = df["match_label"].iloc[0]
    m = df[df["match_label"] == first_match].sort_values("rank").head(5)
    first = m.iloc[0]

    rows = ""
    for _, r in m.iterrows():
        rows += f"""
        <div class="score-row">
            <div class="rank">{int(r['rank'])}</div>
            <div class="score-text">{esc(r['score'])}</div>
            <div class="bar">
                <div class="fill home-fill" style="width:{width(r['score_probability'])}%"></div>
            </div>
            <div class="score-pct">{pct(r['score_probability'])}</div>
        </div>
        """

    return f"""
    <div class="panel score-panel">
        <div class="panel-title">
            <span>SCORE FORECAST</span>
            <span class="link">View full →</span>
        </div>

        <div class="score-layout">
            <div class="score-left">
                <div class="score-teams">
                    <div class="team-block">
                        <div>{flag_img(first['home_team'], 38)}</div>
                        <div class="score-title">{esc(first['home_team'])}</div>
                    </div>

                    <div class="vs-center">VS</div>

                    <div class="team-block">
                        <div>{flag_img(first['away_team'], 38)}</div>
                        <div class="score-title">{esc(first['away_team'])}</div>
                    </div>
                </div>

                <div class="score-meta">
                    {esc(first.get('date', ''))} · Group {esc(first.get('group', '-'))}
                </div>

                <div class="xg-row">
                    <div class="xg-box">
                        <div>xG Home</div>
                        <b>{float(first['home_xg']):.2f}</b>
                    </div>
                    <div class="xg-box">
                        <div>xG Away</div>
                        <b>{float(first['away_xg']):.2f}</b>
                    </div>
                </div>
            </div>

            <div class="score-right">
                <div class="subhead">Top 5 Most Likely Scores</div>
                {rows}
            </div>
        </div>
    </div>
    """

def render_all_score_forecasts():
    if score_df.empty:
        return "<div class='panel'>Missing score forecast.</div>"

    df = score_df.copy()

    if "completed" in df.columns:
        df = df[df["completed"] != True]

    if "commence_dt" in df.columns:
        now_utc = pd.Timestamp.utcnow()
        df = df[
            (df["commence_dt"].isna()) |
            (df["commence_dt"] >= now_utc)
        ]
        df = df.sort_values(["commence_dt", "match_id", "rank"])
    else:
        df = df.sort_values(["match_id", "rank"])

    match_labels = df["match_label"].drop_duplicates().tolist()

    cards = ""

    for match_label in match_labels:
        m = df[df["match_label"] == match_label].sort_values("rank").head(5)
        if m.empty:
            continue

        first = m.iloc[0]

        rows = ""
        for _, r in m.iterrows():
            rows += f"""
            <div class="score-row">
                <div class="rank">{int(r['rank'])}</div>
                <div class="score-text">{esc(r['score'])}</div>
                <div class="bar">
                    <div class="fill home-fill" style="width:{width(r['score_probability'])}%"></div>
                </div>
                <div class="score-pct">{pct(r['score_probability'])}</div>
            </div>
            """

        cards += f"""
        <div class="panel score-panel">
            <div class="panel-title">
                <span>{esc(first['home_team'])} vs {esc(first['away_team'])}</span>
            </div>

            <div class="score-layout">
                <div class="score-left">
                    <div class="score-teams">
                        <div class="team-block">
                            <div>{flag_img(first['home_team'], 34)}</div>
                            <div class="score-title">{esc(first['home_team'])}</div>
                        </div>

                        <div class="vs-center">VS</div>

                        <div class="team-block">
                            <div>{flag_img(first['away_team'], 34)}</div>
                            <div class="score-title">{esc(first['away_team'])}</div>
                        </div>
                    </div>

                    <div class="score-meta">
                        {esc(first.get('date', ''))} · Group {esc(first.get('group', '-'))}
                    </div>

                    <div class="xg-row">
                        <div class="xg-box">
                            <div>xG Home</div>
                            <b>{float(first['home_xg']):.2f}</b>
                        </div>
                        <div class="xg-box">
                            <div>xG Away</div>
                            <b>{float(first['away_xg']):.2f}</b>
                        </div>
                    </div>
                </div>

                <div class="score-right">
                    <div class="subhead">Top 5 Most Likely Scores</div>
                    {rows}
                </div>
            </div>
        </div>
        """

    return f"""
    <div class="score-list-page">
        {cards}
    </div>
    """


def render_all_groups():
    if group_df.empty:
        return "<div class='panel'>Missing group stage file.</div>"

    groups = sorted(group_df["group"].unique().tolist())
    group_cards = ""

    for g in groups:
        df = group_df[group_df["group"] == g].sort_values("qualified_prob", ascending=False)

        rows = ""
        for i, (_, r) in enumerate(df.iterrows(), start=1):
            rows += f"""
            <div class="group-row">
                <div class="group-team"><span>{i}</span> {flag_img(r['team'], 20)} {esc(r['team'])}</div>
                <div class="bar"><div class="fill home-fill" style="width:{width(r['qualified_prob'])}%"></div></div>
                <div class="group-pct">{pct(r['qualified_prob'])}</div>
            </div>
            """

        group_cards += f"""
        <div class="group-card">
            <div class="group-title">GROUP {esc(g)}</div>
            {rows}
        </div>
        """

    return f"""
    <div class="panel">
        <div class="panel-title">
            <span>ALL GROUPS</span>
        </div>
        <div class="groups-grid">{group_cards}</div>
    </div>
    """


def render_group_overview():
    if group_df.empty:
        return "<div class='panel'>Missing group stage file.</div>"

    groups = sorted(group_df["group"].unique().tolist())[:3]
    group_cards = ""

    for g in groups:
        df = group_df[group_df["group"] == g].sort_values("qualified_prob", ascending=False)
        rows = ""
        for i, (_, r) in enumerate(df.iterrows(), start=1):
            rows += f"""
            <div class="group-row">
                <div class="group-team"><span>{i}</span> {flag_img(r['team'], 20)} {esc(r['team'])}</div>
                <div class="bar"><div class="fill home-fill" style="width:{width(r['qualified_prob'])}%"></div></div>
                <div class="group-pct">{pct(r['qualified_prob'])}</div>
            </div>
            """

        group_cards += f"""
        <div class="group-card">
            <div class="group-title">GROUP {esc(g)}</div>
            {rows}
        </div>
        """

    return f"""
    <div class="panel">
        <div class="panel-title">
            <span>GROUP STAGE OVERVIEW</span>
            <span class="link">View all groups →</span>
        </div>
        <div class="groups-grid">{group_cards}</div>
    </div>
    """


def render_champion_race(n=10):
    if champion_df.empty:
        return "<div class='panel'>Missing champion probabilities.</div>"

    df = champion_df.sort_values("champion_prob", ascending=False).head(n)
    rows = ""

    for i, (_, r) in enumerate(df.iterrows(), start=1):
        rows += f"""
        <div class="champ-row">
            <div class="rank">{i}</div>
            <div class="champ-team">{flag_img(r['team'], 20)} {esc(r['team'])}</div>
            <div class="bar"><div class="fill blue-fill" style="width:{width(r['champion_prob'])}%"></div></div>
            <div class="champ-pct">{pct(r['champion_prob'])}</div>
        </div>
        """

    return f"""
    <div class="panel">
        <div class="panel-title">
            <span>CHAMPION RACE — TOP {n}</span>
            <span class="link">View full ranking →</span>
        </div>
        {rows}
    </div>
    """


def render_bracket():

    if champion_df.empty:
        return "<div class='panel'>Missing champion probabilities.</div>"

    df = champion_df.sort_values(
        "champion_prob",
        ascending=False
    ).head(8)

    teams = df["team"].tolist()

    return f"""
    <div class="panel">

        <div class="panel-title">
            <span>KNOCKOUT PROGRESSION PREVIEW</span>
            <span class="link">View full bracket →</span>
        </div>

        <div class="fake-bracket">

            <div class="round">
                <div class="round-title">ROUND OF 16</div>

                <div class="team-box">{teams[0]}</div>
                <div class="team-box">{teams[1]}</div>

                <div class="team-box">{teams[2]}</div>
                <div class="team-box">{teams[3]}</div>

                <div class="team-box">{teams[4]}</div>
                <div class="team-box">{teams[5]}</div>

                <div class="team-box">{teams[6]}</div>
                <div class="team-box">{teams[7]}</div>
            </div>

            <div class="round">
                <div class="round-title">QUARTER FINAL</div>

                <div class="team-box">
                    {teams[0]}
                    <span>68%</span>
                </div>

                <div class="team-box">
                    {teams[2]}
                    <span>61%</span>
                </div>

                <div class="team-box">
                    {teams[4]}
                    <span>57%</span>
                </div>

                <div class="team-box">
                    {teams[6]}
                    <span>54%</span>
                </div>
            </div>

            <div class="round">
                <div class="round-title">SEMI FINAL</div>

                <div class="team-box">{teams[0]}</div>

                <div class="team-box">{teams[4]}</div>
            </div>

            <div class="round">
                <div class="round-title">FINAL</div>

                <div class="team-box">{teams[0]}</div>
            </div>

            <div class="round champion">

                <div class="round-title">
                    CHAMPION
                </div>

                <div class="champion-box">

                    🏆 {teams[0]}

                    <br>

                    {pct(df.iloc[0]["champion_prob"])}

                </div>

            </div>

        </div>

    </div>
    """


def render_recent_results(limit=4):
    if accuracy_df.empty:
        return "<div class='panel'>Missing prediction_accuracy.csv.</div>"

    df = accuracy_df.copy()
    if "matched" in df.columns:
        df = df[df["matched"] == True]

    df = df.tail(limit).iloc[::-1]

    cards = ""
    for _, r in df.iterrows():
        hit = "hit" if bool(r["result_hit"]) else "miss"
        hit_text = "✅ Hit" if bool(r["result_hit"]) else "❌ Miss"
        top8 = "hit" if bool(r["top8_hit"]) else "miss"
        top8_text = "✅ Top8" if bool(r["top8_hit"]) else "❌ Top8"

        cards += f"""
        <div class="result-card">
            <div class="result-title">
                {flag_img(r['home_team'], 22)}
                {esc(r['home_team'])}

            <span style="color:#ffffff;font-weight:950;margin:0 10px;">
                {esc(r['actual_score'])}
            </span>

                {flag_img(r['away_team'], 22)}
                {esc(r['away_team'])}
        </div>
            <div class="result-meta">
                Predicted: <b>{esc(r['predicted_result'])}</b> · Actual: <b>{esc(r['actual_result'])}</b>
            </div>
            <div class="result-badges">
                <span class="{hit}">{hit_text}</span>
                <span class="{top8}">{top8_text}</span>
            </div>
            <div class="top-scores">
                Top scores: {esc(r.get('top1_score',''))} · {esc(r.get('top2_score',''))} · {esc(r.get('top3_score',''))}
            </div>
        </div>
        """

    return f"""
    <div class="panel">
        <div class="panel-title">RECENT RESULTS</div>
        {cards}
    </div>
    """


def render_explainer():
    return """
    <div class="panel explain-panel">
        <div class="panel-title">HOW TO READ PROBABILITIES</div>
        <div class="explain-row"><div>🏠</div><div><b>Home Win</b><br><span>Probability that the home team wins in 90 minutes.</span></div></div>
        <div class="explain-row"><div>➖</div><div><b>Draw</b><br><span>Probability that the match ends tied in 90 minutes.</span></div></div>
        <div class="explain-row"><div>✈️</div><div><b>Away Win</b><br><span>Probability that the away team wins in 90 minutes.</span></div></div>
        <div class="explain-row"><div>📈</div><div><b>Market Adjustment</b><br><span>Probabilities combine model forecast with market odds when available.</span></div></div>
    </div>
    """


def simple_page(title, content):
    return f"""
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            font-family: Inter, Segoe UI, Arial, sans-serif;
            color: #f7fbff;
            background: #020711;
        }}

        .page {{
            padding: 30px;
        }}

        .page-title {{
            font-size: 32px;
            font-weight: 900;
            margin-bottom: 22px;
        }}

        .match-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
        }}

        .match-card {{
            background: linear-gradient(145deg, rgba(13,39,70,.82), rgba(7,20,38,.92));
            border: 1px solid rgba(92,174,255,.20);
            border-radius: 18px;
            padding: 18px;
            min-height: 190px;
            width: 300px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,.03), 0 6px 18px rgba(0,0,0,.25);
        }}

        .match-top {{
            text-align: center;
            margin-bottom: 12px;
        }}

        .teams-line {{
            display: grid;
            grid-template-columns: 32px 1fr 28px 32px 1fr;
            align-items: center;
            gap: 8px;
            font-size: 16px;
            font-weight: 900;
            margin-bottom: 12px;
        }}

        .flag-img {{
            border-radius: 4px;
            vertical-align: middle;
        }}

        .vs {{
            color: #48617d;
            font-weight: 800;
        }}

        .meta {{
            color: #9db5d0;
            font-size: 13px;
            margin-bottom: 8px;
        }}

        .badge {{
            display: inline-block;
            border-radius: 999px;
            padding: 6px 12px;
            font-size: 11px;
            font-weight: 950;
        }}

        .green {{ color: #67ff9d; background: rgba(63,220,120,.16); border: 1px solid rgba(100,255,150,.4); }}
        .gray {{ color: #d5deea; background: rgba(210,220,235,.10); border: 1px solid rgba(210,220,235,.3); }}
        .red {{ color: #ff7777; background: rgba(255,80,90,.12); border: 1px solid rgba(255,100,100,.4); }}

        .prob-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 11px;
            margin-top: 12px;
        }}

        .prob-label {{
            color: #9bb3cc;
            font-size: 11px;
            font-weight: 800;
        }}

        .prob-value {{
            font-size: 20px;
            font-weight: 950;
            margin: 4px 0 7px;
        }}

        .bar {{
            height: 10px;
            background: rgba(255,255,255,.075);
            border-radius: 999px;
            overflow: hidden;
        }}

        .fill {{
            height: 100%;
            border-radius: 999px;
        }}

        .home-fill {{ background: linear-gradient(90deg, #20c36d, #68ff9e); }}
        .draw-fill {{ background: linear-gradient(90deg, #73849a, #cbd5e5); }}
        .away-fill {{ background: linear-gradient(90deg, #d74751, #ff7777); }}

        .top-scores {{
            color: #9fc2e8;
            font-size: 14px;
            font-weight: 750;
            margin-top: 12px;
        }}

        .score-list-page {{
            display: flex;
            flex-direction: column;
            gap: 18px;
    }}

    </style>
    </head>

    <body>
        <div class="page">
            <div class="page-title">{title}</div>
            {content}
        </div>
    </body>
    </html>
    """




def dashboard_html():
    matches = len(adjusted_df)

    teams = 0
    if not adjusted_df.empty:
        teams = len(set(adjusted_df["home_team"]) | set(adjusted_df["away_team"]))

    top_team = "-"
    top_prob = "-"
    if not champion_df.empty:
        top = champion_df.sort_values("champion_prob", ascending=False).iloc[0]
        top_team = top["team"]
        top_prob = pct(top["champion_prob"])

    avg_diff = "-"
    if not market_df.empty and "abs_diff" in market_df.columns:
        avg_diff = f"{market_df['abs_diff'].mean():.3f}"

    accuracy = "-"
    if not accuracy_df.empty and "matched" in accuracy_df.columns:
        matched = accuracy_df[accuracy_df["matched"] == True]
        if len(matched) > 0:
            accuracy = pct(matched["result_hit"].mean())

    try:
        ts = SCORES_FILE.stat().st_mtime

        last_updated = datetime.fromtimestamp(
            ts,
            ZoneInfo("America/Los_Angeles")
        ).strftime("%Y-%m-%d %H:%M:%S PDT")

    except Exception:
        last_updated = "-"

    return f"""

    <html>
    <head>
    <style>
    body {{
        margin: 0;
        font-family: Inter, Segoe UI, Arial, sans-serif;
        color: #f7fbff;
        background: radial-gradient(circle at top left, rgba(18, 81, 146, .28), transparent 34%),
                    linear-gradient(135deg, #020711, #071528 48%, #02050b);
    }}

    .page {{
        padding: 26px 28px 34px 28px;
    }}

    .header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 22px;
    }}

    .title {{
        font-size: 32px;
        font-weight: 950;
        line-height: 1.1;
    }}

    .subtitle {{
        color: #a9bdd6;
        font-size: 14px;
        margin-top: 8px;
    }}

    .updated {{
        color: #9fb4ce;
        font-size: 13px;
    }}

    .kpis {{
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 16px;
        margin-bottom: 20px;
    }}

    .kpi {{
        background: linear-gradient(135deg, rgba(9, 31, 55, .98), rgba(5, 16, 31, .98));
        border: 1px solid rgba(80, 165, 255, .28);
        border-radius: 17px;
        padding: 16px 18px;
        min-height: 92px;
        box-shadow: 0 16px 36px rgba(0,0,0,.34);
    }}

    .kpi-icon {{
        font-size: 26px;
        float: left;
        margin-right: 12px;
    }}

    .kpi-label {{
        color: #91a9c7;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 800;
    }}

    .kpi-value {{
        font-size: 25px;
        font-weight: 950;
        margin-top: 5px;
    }}

    .kpi-note {{
        color: #91a9c7;
        font-size: 12px;
        margin-top: 4px;
    }}

    .layout-top {{
        display: grid;
        grid-template-columns: 2.2fr .8fr;
        gap: 16px;
        margin-bottom: 16px;
    }}

    .layout-mid {{
        display: grid;
        grid-template-columns: .9fr 1.4fr;
        gap: 16px;
        margin-bottom: 16px;
    }}

    .layout-bottom {{
        display: grid;
        grid-template-columns: .9fr 1.4fr;
        gap: 16px;
    }}

    .panel {{
        background: linear-gradient(135deg, rgba(8, 28, 50, .96), rgba(5, 17, 32, .97));
        border: 1px solid rgba(85, 168, 255, .24);
        border-radius: 20px;
        padding: 17px;
        box-shadow: 0 15px 34px rgba(0,0,0,.34);
        overflow: hidden;
    }}

    .panel-title {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 17px;
        font-weight: 950;
        margin-bottom: 14px;
    }}

    .link {{
        color: #25a7ff;
        font-size: 13px;
        font-weight: 700;
    }}

    .carousel-wrap {{
        position: relative;
        width: 100%;
        overflow: hidden;
    }}

    .carousel-arrow {{
        position: absolute;
        right: -18px;
        top: 50%;
        transform: translateY(-50%);
        width: 42px;
        height: 42px;
        border-radius: 999px;
        border: 1px solid rgba(80,165,255,.45);
        background: linear-gradient(135deg, #0b5fbd, #063b78);
        color: white;
        font-size: 30px;
        font-weight: 900;
        cursor: pointer;
        box-shadow: 0 8px 24px rgba(0,0,0,.45);
        z-index: 20;
    }}

    .carousel-arrow:hover {{
        background: linear-gradient(135deg, #1588ff, #0754a8);
    }}


    .match-grid{{
        display:flex;
        gap:16px;
        overflow-x:auto;
        overflow-y:hidden;
        padding-bottom:8px;
        scroll-behavior:smooth;
        width:100%;
        max-width:100%;
    }}

    .match-grid::-webkit-scrollbar{{
        height:8px;
    }}

    .match-grid::-webkit-scrollbar-thumb{{
        background:#1b4d82;
        border-radius:10px;
    }}

    .match-card{{
        background:linear-gradient(
            145deg,
            rgba(13,39,70,.82),
            rgba(7,20,38,.92)
        );

        border:1px solid rgba(92,174,255,.20);

        border-radius:18px;

        padding:18px;

        min-height:190px;

        width:300px;

        flex:0 0 300px;

        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.03),
            0 6px 18px rgba(0,0,0,.25);
    }}

    .match-top {{
        text-align: center;
        margin-bottom: 12px;
    }}

    .date {{
        color: #9db5d0;
        font-size: 13px;
        margin-bottom: 8px;
    }}

    .teams-line {{
        display: grid;
        grid-template-columns: 32px 1fr 28px 32px 1fr;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: 900;
        margin-bottom: 12px;
    }}

    .flag-img {{
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,.35);
        vertical-align: middle;
    }}

    .flag-emoji {{
        font-size: 24px;
    }}


    .vs {{
        color: #48617d;
        font-weight: 800;
    }}

    .badge {{
        display: inline-block;
        border-radius: 999px;
        padding: 6px 12px;
        font-size: 11px;
        font-weight: 950;
    }}

    .green {{ color: #67ff9d; background: rgba(63, 220, 120, .16); border: 1px solid rgba(100,255,150,.4); }}
    .gray {{ color: #d5deea; background: rgba(210,220,235,.10); border: 1px solid rgba(210,220,235,.3); }}
    .red {{ color: #ff7777; background: rgba(255,80,90,.12); border: 1px solid rgba(255,100,100,.4); }}

    .prob-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 11px;
        margin-top: 12px;
    }}

    .prob-label {{
        color: #9bb3cc;
        font-size: 11px;
        font-weight: 800;
    }}

    .prob-value {{
        font-size: 20px;
        font-weight: 950;
        margin: 4px 0 7px;
    }}

    .bar {{
        height: 10px;
        background: rgba(255,255,255,.075);
        border-radius: 999px;
        overflow: hidden;
    }}

    .fill {{
        height: 100%;
        border-radius: 999px;
    }}

    .home-fill {{ background: linear-gradient(90deg, #20c36d, #68ff9e); }}
    .draw-fill {{ background: linear-gradient(90deg, #73849a, #cbd5e5); }}
    .away-fill {{ background: linear-gradient(90deg, #d74751, #ff7777); }}
    .blue-fill {{ background: linear-gradient(90deg, #006dff, #2aa8ff); }}

    .top-scores {{
        color: #90a8c4;
        font-size: 12px;
        margin-top: 12px;
    }}

    .score-panel {{
        min-height: 250px;
    }}

    .score-layout {{
        display: grid;
        grid-template-columns: 0.85fr 1.15fr;
        gap: 24px;
        align-items: center;
    }}

    .score-left {{
        border-right: 1px solid rgba(255,255,255,.08);
        padding-right: 20px;
    }}

    .score-teams {{
        display: grid;
        grid-template-columns: 1fr 50px 1fr;
        gap: 12px;
        align-items: center;
    }}

    .team-block {{
        text-align: center;
    }}

    .vs-center {{
        color: #7f96b3;
        font-weight: 900;
        text-align: center;
    }}

    .score-meta {{
        color: #9db5d0;
        font-size: 13px;
        text-align: center;
        margin: 14px 0;
    }}

    .xg-box {{
        background: rgba(255,255,255,.04);
        border: 1px solid rgba(255,255,255,.075);
        border-radius: 12px;
        padding: 11px;
        text-align: center;
        color: #8fb0d0;
        font-size: 12px;
    }}

    .xg-box b {{
        display: block;
        color: white;
        font-size: 22px;
        margin-top: 5px;
    }}

    .subhead {{
        color: #dcecff;
        font-size: 14px;
        font-weight: 900;
        margin-bottom: 16px;
    }}

    .score-pct {{
        font-weight: 900;
        text-align: right;
    }}
    
    .score-head {{
        display:flex;
        justify-content:space-between;
        align-items:center;
    }}

    .flag-big {{
        font-size: 32px;
    }}

    .score-title {{
        font-size: 21px;
        font-weight: 950;
    }}

    .xg-row {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
        margin-bottom: 14px;
    }}

    .xg {{
        background: rgba(255,255,255,.04);
        border: 1px solid rgba(255,255,255,.075);
        border-radius: 12px;
        padding: 10px;
        text-align: center;
        color: #8fb0d0;
        font-size: 12px;
    }}

    .xg b {{
        display: block;
        color: white;
        font-size: 22px;
        margin-top: 5px;
    }}

    .score-row, .champ-row, .group-row {{
        display: grid;
        grid-template-columns: 32px 70px 1fr 58px;
        gap: 10px;
        align-items: center;
        margin-bottom: 11px;
    }}

    .rank {{
        color: #8fb0d0;
        font-weight: 900;
    }}

    .score-text {{
        font-weight: 950;
        font-size: 17px;
    }}

    .groups-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
    }}

    .group-card {{
        background: rgba(255,255,255,.03);
        border: 1px solid rgba(255,255,255,.07);
        border-radius: 14px;
        padding: 12px;
    }}

    .group-title {{
        font-size: 14px;
        font-weight: 950;
        margin-bottom: 12px;
    }}

    .group-row {{
        grid-template-columns: 1.4fr 1fr 52px;
    }}

    .group-team, .champ-team {{
        font-weight: 850;
    }}

    .group-pct, .champ-pct {{
        font-weight: 950;
        text-align: right;
    }}

    .champ-row {{
        grid-template-columns: 30px 140px 1fr 58px;
    }}

    .result-card {{
        background: rgba(255,255,255,.035);
        border: 1px solid rgba(255,255,255,.07);
        border-radius: 14px;
        padding: 12px;
        margin-bottom: 10px;
    }}

    .result-title {{
        font-size: 16px;
        font-weight: 950;
        margin-bottom: 8px;
    }}

    .result-meta {{
        color: #99b3d0;
        font-size: 12px;
    }}

    .result-badges {{
        margin-top: 8px;
        display: flex;
        gap: 8px;
        font-weight: 900;
    }}

    .hit {{ color: #67ff9d; }}
    .miss {{ color: #ff6e86; }}

    .bracket-grid {{
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 13px;
    }}

    .bracket-col {{
        background: rgba(255,255,255,.03);
        border: 1px solid rgba(255,255,255,.07);
        border-radius: 14px;
        padding: 12px;
    }}

    .bracket-stage {{
        color: #a9bdd6;
        font-size: 12px;
        font-weight: 950;
        text-transform: uppercase;
        margin-bottom: 10px;
    }}

    .bracket-team {{
        background: rgba(255,255,255,.04);
        border-radius: 10px;
        padding: 8px;
        margin-bottom: 8px;
        font-size: 13px;
    }}

    .bracket-team b {{
        float: right;
        color: #67ff9d;
    }}

    .explain-row {{
        display: grid;
        grid-template-columns: 30px 1fr;
        gap: 10px;
        margin-bottom: 14px;
        font-size: 14px;
    }}

    .explain-row span {{
        color: #9db5d0;
        font-size: 13px;
    }}


    .fake-bracket{{
        display:flex;
        gap:24px;
        align-items:center;
    }}

    .fake-bracket{{
        display:flex;
        gap:24px;
        align-items:center;
    }}

    .round{{
        flex:1;
    }}

    .round-title{{
        font-size:12px;
        font-weight:900;
        color:#8fb0d0;
        margin-bottom:12px;
    }}

    .team-box{{
        background:rgba(255,255,255,.05);
        border:1px solid rgba(255,255,255,.08);
        border-radius:10px;
        padding:10px;
        margin-bottom:16px;
        font-size:13px;
        font-weight:700;
    }}

    .team-box span{{
        float:right;
        color:#67ff9d;
    }}

    .champion-box{{
        background:linear-gradient(
            135deg,
            rgba(255,196,0,.18),
            rgba(255,128,0,.12)
        );
        border:1px solid rgba(255,196,0,.45);
        border-radius:16px;
        padding:20px;
        text-align:center;
        font-size:18px;
        font-weight:900;
    }}

    

    </style>
    </head>
    <body>
    <div class="page">
        <div class="header">
            <div>
                <div class="title">🏆 WORLD CUP FORECAST DASHBOARD</div>
                <div class="subtitle">ELO + xG + Poisson + Market Odds + Monte Carlo Simulation</div>
            </div>
            <div class="updated">Last updated: {esc(last_updated)}</div>
        </div>

        <div class="kpis">
            <div class="kpi"><div class="kpi-icon">📅</div><div class="kpi-label">Matches</div><div class="kpi-value">{matches}</div><div class="kpi-note">Group Stage</div></div>
            <div class="kpi"><div class="kpi-icon">🎲</div><div class="kpi-label">Simulations</div><div class="kpi-value">10,000+</div><div class="kpi-note">Monte Carlo</div></div>
            <div class="kpi"><div class="kpi-icon">👥</div><div class="kpi-label">Teams</div><div class="kpi-value">{teams}</div><div class="kpi-note">Nations</div></div>
            <div class="kpi"><div class="kpi-icon">👑</div><div class="kpi-label">Top Champion</div><div class="kpi-value">{esc(top_team)}</div><div class="kpi-note">{top_prob}</div></div>
            <div class="kpi"><div class="kpi-icon">📈</div><div class="kpi-label">Model vs Market</div><div class="kpi-value">{avg_diff}</div><div class="kpi-note">Avg Difference</div></div>
        </div>

        <div class="layout-top">
            {render_next_matches(12)}
            {render_explainer()}
        </div>

        <div class="layout-mid">
            {render_score_forecast()}
            {render_group_overview()}
        </div>

        <div class="layout-bottom">
            {render_champion_race(10)}
            {render_bracket()}
        </div>

        {render_recent_results(20)}
    </div>
    </body>
    </html>
    """


def styled_page(title, content):
    css = dashboard_html().split("<style>", 1)[1].split("</style>", 1)[0]

    return f"""
    <html>
    <head>
    <style>
    {css}

    .page-title {{
        font-size: 32px;
        font-weight: 900;
        margin-bottom: 22px;
    }}
    </style>
    </head>

    <body>
        <div class="page">
            <div class="page-title">{esc(title)}</div>
            {content}
        </div>
    </body>
    </html>
    """



if page == "Dashboard":
    components.html(
        dashboard_html(),
        height=1700,
        scrolling=True,
    )


elif page == "Match Predictions":

    if not adjusted_df.empty:

        df = adjusted_df.copy()

        if "completed" in df.columns:
            df = df[df["completed"] != True]

        if "commence_dt" in df.columns:
            
            df = df.sort_values("commence_dt")

        cards = "".join(
            match_card(r)
            for _, r in df.iterrows()
        )

        components.html(
            styled_page(
                "Match Predictions",
                f"<div class='match-grid'>{cards}</div>"
            ),
            height=1400,
            scrolling=True
        )



elif page == "Score Forecast":
    components.html(
        styled_page(
            "Score Forecast",
            render_all_score_forecasts()
        ),
        height=1800,
        scrolling=True,
    )

elif page == "Group Stage":
    components.html(
        styled_page(
            "Group Stage",
            render_all_groups()
        ),
        height=1400,
        scrolling=True,
    )

elif page == "Knockout Preview":
    components.html(
        styled_page(
            "Knockout Preview",
            render_bracket()
        ),
        height=1000,
        scrolling=True,
    )

elif page == "Champion Race":
    components.html(
        styled_page(
            "Champion Race",
            render_champion_race(20)
        ),
        height=1200,
        scrolling=True,
    )

elif page == "Recent Results":
    components.html(
        styled_page(
            "Recent Results",
            render_recent_results(20)
        ),
        height=1200,
        scrolling=True,
    )

elif page == "Model Accuracy":
    if accuracy_df.empty:
        st.warning("Missing prediction_accuracy.csv")
    else:
        matched = accuracy_df[accuracy_df["matched"] == True].copy()
        recent = matched.tail(12).iloc[::-1]

        rows = ""

        for _, r in recent.iterrows():
            result_hit = bool(r["result_hit"])
            top3_hit = bool(r["top3_hit"])
            top5_hit = bool(r["top5_hit"])
            top8_hit = bool(r["top8_hit"])

            if result_hit and top3_hit:
                grade = "A"
                grade_class = "hit"
            elif result_hit and top5_hit:
                grade = "B"
                grade_class = "hit"
            elif result_hit and top8_hit:
                grade = "C"
                grade_class = "hit"
            elif result_hit:
                grade = "D"
                grade_class = "miss"
            else:
                grade = "F"
                grade_class = "miss"

            result_class = "hit" if result_hit else "miss"
            top3_class = "hit" if top3_hit else "miss"
            top5_class = "hit" if top5_hit else "miss"
            top8_class = "hit" if top8_hit else "miss"

            rows += f"""
            <div class="result-card">
                <div class="result-title">
                    {flag_img(r['home_team'])} {esc(r['home_team'])}
                    <span style="color:#ffffff;font-weight:950;margin:0 8px;">
                        {esc(r['actual_score'])}
                    </span>
                    {flag_img(r['away_team'])} {esc(r['away_team'])}
            </div>

                <div class="result-meta">
                    Predicted Winner:
                    <b>{esc(r['predicted_result'])}</b>
                    · Actual:
                    <b>{esc(r['actual_result'])}</b>
                    · Grade:
                    <b class="{grade_class}">{grade}</b>
                </div>

                <div class="result-badges">
                    <span class="{result_class}">
                        {"✅ Winner" if result_hit else "❌ Winner"}
                    </span>
                    <span class="{top3_class}">
                        {"✅ Top3" if top3_hit else "❌ Top3"}
                    </span>
                    <span class="{top5_class}">
                        {"✅ Top5" if top5_hit else "❌ Top5"}
                    </span>
                    <span class="{top8_class}">
                        {"✅ Top8" if top8_hit else "❌ Top8"}
                    </span>
                </div>

                <div class="top-scores">
                    Top Scores:
                    {esc(r.get('top1_score', ''))} ·
                    {esc(r.get('top2_score', ''))} ·
                    {esc(r.get('top3_score', ''))} ·
                    {esc(r.get('top4_score', ''))} ·
                    {esc(r.get('top5_score', ''))}
                </div>
            </div>
            """

        html = f"""
        <div class="kpis">
            <div class="kpi">
                <div class="kpi-label">Evaluated Matches</div>
                <div class="kpi-value">{len(matched)}</div>
                <div class="kpi-note">Historical Results</div>
            </div>

            <div class="kpi">
                <div class="kpi-label">Winner Accuracy</div>
                <div class="kpi-value">{pct(matched["result_hit"].mean())}</div>
                <div class="kpi-note">HOME / DRAW / AWAY</div>
            </div>

            <div class="kpi">
                <div class="kpi-label">Top3 Score Hit</div>
                <div class="kpi-value">{pct(matched["top3_hit"].mean())}</div>
                <div class="kpi-note">Exact score in top 3</div>
            </div>

            <div class="kpi">
                <div class="kpi-label">Top5 Score Hit</div>
                <div class="kpi-value">{pct(matched["top5_hit"].mean())}</div>
                <div class="kpi-note">Exact score in top 5</div>
            </div>

            <div class="kpi">
                <div class="kpi-label">Top8 Score Hit</div>
                <div class="kpi-value">{pct(matched["top8_hit"].mean())}</div>
                <div class="kpi-note">Exact score in top 8</div>
            </div>
        </div>

        <div class="panel">
            <div class="panel-title">
                <span>RECENT MODEL EVALUATIONS</span>
            </div>
            {rows}
        </div>
        """

        components.html(
            styled_page(
                "Model Accuracy",
                html
            ),
            height=1400,
            scrolling=True,
        )

elif page == "Model vs Market":
    if market_df.empty:
        st.warning("Missing model_vs_market.csv")
    else:
        df = market_df.copy()

        edge_rows = []

        for _, r in df.iterrows():
            markets = [
                {
                    "pick": "HOME",
                    "team": r["home_team"],
                    "opponent": r["away_team"],
                    "model_prob": r["model_home_prob"],
                    "market_prob": r["market_home_prob"],
                    "edge": r["home_diff"],
                },
                {
                    "pick": "DRAW",
                    "team": "Draw",
                    "opponent": f"{r['home_team']} vs {r['away_team']}",
                    "model_prob": r["model_draw_prob"],
                    "market_prob": r["market_draw_prob"],
                    "edge": r["draw_diff"],
                },
                {
                    "pick": "AWAY",
                    "team": r["away_team"],
                    "opponent": r["home_team"],
                    "model_prob": r["model_away_prob"],
                    "market_prob": r["market_away_prob"],
                    "edge": r["away_diff"],
                },
            ]

            for m in markets:
                if pd.isna(m["model_prob"]) or pd.isna(m["market_prob"]):
                    continue

                if float(m["edge"]) > 0:
                    edge_rows.append({
                        "home_team": r["home_team"],
                        "away_team": r["away_team"],
                        "pick": m["pick"],
                        "team": m["team"],
                        "opponent": m["opponent"],
                        "model_prob": float(m["model_prob"]),
                        "market_prob": float(m["market_prob"]),
                        "edge": float(m["edge"]),
                    })

        edge_df = pd.DataFrame(edge_rows)

        if edge_df.empty:
            st.warning("No positive model edges found.")
        else:
            edge_df = edge_df.sort_values("edge", ascending=False).head(5)

            rows = ""

            for i, (_, r) in enumerate(edge_df.iterrows(), start=1):
                if r["edge"] >= 0.20:
                    grade = "ELITE EDGE"
                    grade_class = "hit"
                elif r["edge"] >= 0.15:
                    grade = "STRONG EDGE"
                    grade_class = "hit"
                elif r["edge"] >= 0.10:
                    grade = "GOOD EDGE"
                    grade_class = "hit"
                elif r["edge"] >= 0.05:
                    grade = "SMALL EDGE"
                    grade_class = "miss"
                else:
                    grade = "WEAK EDGE"
                    grade_class = "miss"

                if r["pick"] == "DRAW":
                    pick_title = "Draw"
                    match_title = f"{flag_img(r['home_team'], 22)} {esc(r['home_team'])} vs {flag_img(r['away_team'], 22)} {esc(r['away_team'])}"
                else:
                    pick_title = f"{flag_img(r['team'], 22)} {esc(r['team'])} to Win"
                    match_title = f"{flag_img(r['home_team'], 22)} {esc(r['home_team'])} vs {flag_img(r['away_team'], 22)} {esc(r['away_team'])}"

                rows += f"""
                <div class="result-card">
                    <div class="result-title">
                        #{i} {pick_title}
                    </div>

                    <div class="result-meta">
                        Match: {match_title}
                    </div>

                    <div class="result-badges">
                        <span class="{grade_class}">{grade}</span>
                    </div>

                    <div class="top-scores">
                        Model Prob: <b>{pct(r['model_prob'])}</b> ·
                        Market Prob: <b>{pct(r['market_prob'])}</b> ·
                        Edge: <b>+{pct(r['edge'])}</b>
                    </div>
                </div>
                """

            html = f"""
            <div class="panel">
                <div class="panel-title">
                    <span>TOP 5 BETTING EDGES</span>
                </div>
                {rows}
            </div>
            """

            components.html(
                styled_page(
                    "Model vs Market",
                    html
                ),
                height=900,
                scrolling=True,
            )