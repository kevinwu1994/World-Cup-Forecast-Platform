from html import escape
from math import log
from pathlib import Path

import pandas as pd
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
ARCHIVE_DIR = APP_DIR / "archive_data"

st.set_page_config(
    page_title="2026 World Cup Forecast Platform",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

GLOBAL_CSS = """
<style>
:root { color-scheme: dark; }
.stApp, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 88% 2%, rgba(32, 101, 158, .16), transparent 34rem),
        radial-gradient(circle at 22% 100%, rgba(151, 113, 24, .07), transparent 30rem),
        #0c1119 !important;
    color: #f4f7fb !important;
}
[data-testid="stHeader"] {
    background: #0e1117 !important;
}
[data-testid="stSidebar"] {
    background: #262730 !important;
    border-right: 1px solid rgba(255,255,255,.08);
}
[data-testid="stSidebar"] * {
    color: #f2f5f9;
}
[data-testid="stSidebar"] [data-testid="stAlert"] {
    background: rgba(24, 104, 70, .22);
    border-color: rgba(72, 202, 137, .35);
}
.block-container {
    max-width: 1780px !important;
    padding: 3.6rem 2.25rem 3rem !important;
}
[data-testid="stSelectbox"] label,
[data-testid="stRadio"] label,
[data-testid="stWidgetLabel"] {
    color: #e9eef5 !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #17212f;
    color: #f4f7fb;
    border-color: #344c66;
    border-radius: 9px;
}
[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 8px;
    margin: 1px 0;
    padding: 2px 5px;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(255,255,255,.05);
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
    letter-spacing: -.015em;
}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #aab5c2;
}
@media (max-width: 800px) {
    .block-container { padding: 1.25rem .8rem 2rem !important; }
}
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def load_csv(name: str) -> pd.DataFrame:
    path = ARCHIVE_DIR / name
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


matches = load_csv("tournament_matches.csv")
scores = load_csv("score_forecasts.csv")
groups = load_csv("group_stage_probabilities.csv")
champions = load_csv("champion_probabilities.csv")
market = load_csv("model_vs_market.csv")

for column in ("completed", "result_hit", "top1_hit", "top3_hit", "top5_hit", "top8_hit"):
    if column in matches:
        matches[column] = matches[column].astype(str).str.lower().eq("true")

if "commence_time" in matches:
    matches["commence_dt"] = pd.to_datetime(matches["commence_time"], utc=True)
    matches = matches.sort_values("commence_dt").reset_index(drop=True)


FLAGS = {
    "Algeria": "🇩🇿", "Argentina": "🇦🇷", "Australia": "🇦🇺", "Austria": "🇦🇹",
    "Belgium": "🇧🇪", "Bosnia and Herzegovina": "🇧🇦", "Brazil": "🇧🇷",
    "Canada": "🇨🇦", "Cape Verde": "🇨🇻", "Colombia": "🇨🇴", "Croatia": "🇭🇷",
    "Curacao": "🇨🇼", "Curaçao": "🇨🇼", "Czechia": "🇨🇿", "DR Congo": "🇨🇩",
    "Ecuador": "🇪🇨", "Egypt": "🇪🇬", "England": "🏴", "France": "🇫🇷",
    "Germany": "🇩🇪", "Ghana": "🇬🇭", "Haiti": "🇭🇹", "Iran": "🇮🇷",
    "Iraq": "🇮🇶", "Ivory Coast": "🇨🇮", "Japan": "🇯🇵", "Jordan": "🇯🇴",
    "Mexico": "🇲🇽", "Morocco": "🇲🇦", "Netherlands": "🇳🇱", "New Zealand": "🇳🇿",
    "Norway": "🇳🇴", "Panama": "🇵🇦", "Paraguay": "🇵🇾", "Portugal": "🇵🇹",
    "Qatar": "🇶🇦", "Saudi Arabia": "🇸🇦", "Scotland": "🏴", "Senegal": "🇸🇳",
    "South Africa": "🇿🇦", "South Korea": "🇰🇷", "Spain": "🇪🇸", "Sweden": "🇸🇪",
    "Switzerland": "🇨🇭", "Tunisia": "🇹🇳", "Turkey": "🇹🇷", "Uruguay": "🇺🇾",
    "USA": "🇺🇸", "United States": "🇺🇸", "Uzbekistan": "🇺🇿",
}

STAGE_ORDER = [
    "Group Stage", "Round of 32", "Round of 16", "Quarterfinal",
    "Semifinal", "Third Place", "Final",
]


def esc(value) -> str:
    return escape(str(value))


def flag(team) -> str:
    symbol = FLAGS.get(str(team), "")
    code = "".join(
        chr(ord(character) - 127397)
        for character in symbol
        if 127462 <= ord(character) <= 127487
    )
    if not code:
        words = str(team).replace("&", " ").split()
        code = "".join(word[0] for word in words[:2]).upper() or "—"
    return f'<span class="flag">{esc(code)}</span>'


def pct(value) -> str:
    try:
        return f"{float(value):.1%}"
    except (TypeError, ValueError):
        return "—"


def bar(value, color="green") -> str:
    width = max(0, min(100, float(value) * 100))
    return f'<div class="bar"><div class="fill {color}" style="width:{width:.1f}%"></div></div>'


def date_label(value) -> str:
    try:
        return pd.to_datetime(value, utc=True).strftime("%b %d, 2026")
    except Exception:
        return "2026"


def actual_score(row) -> str:
    return f"{int(row.home_score)}–{int(row.away_score)}" if bool(row.completed) else "—"


def brier_score(frame: pd.DataFrame) -> float:
    total = 0.0
    for _, row in frame.iterrows():
        actual = row.actual_result
        total += sum(
            (float(row[column]) - (1.0 if actual == label else 0.0)) ** 2
            for column, label in (("home_prob", "HOME"), ("draw_prob", "DRAW"), ("away_prob", "AWAY"))
        )
    return total / len(frame) if len(frame) else 0.0


def log_loss(frame: pd.DataFrame) -> float:
    values = []
    columns = {"HOME": "home_prob", "DRAW": "draw_prob", "AWAY": "away_prob"}
    for _, row in frame.iterrows():
        probability = max(1e-12, min(1 - 1e-12, float(row[columns[row.actual_result]])))
        values.append(-log(probability))
    return sum(values) / len(values) if values else 0.0


completed = matches[matches["completed"]].copy() if not matches.empty else matches.copy()
winner_accuracy = completed["result_hit"].mean() if len(completed) else 0
top3_accuracy = completed["top3_hit"].mean() if len(completed) else 0
top5_accuracy = completed["top5_hit"].mean() if len(completed) else 0
top8_accuracy = completed["top8_hit"].mean() if len(completed) else 0


with st.sidebar:
    st.markdown("## 🏆 World Cup")
    st.markdown("### Final Forecast Archive")
    st.divider()
    st.success("Tournament complete · Archive edition")
    st.divider()
    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "Forecast Archive",
            "Score Forecast",
            "Group Stage",
            "Knockout Results",
            "Champion Forecast",
            "Tournament Results",
            "Model Accuracy",
            "Model vs Market",
        ],
    )
    st.divider()
    st.markdown("### MODEL APPROACH")
    st.markdown(
        "✅ ELO Ratings  \n"
        "✅ Expected Goals xG  \n"
        "✅ Poisson Score Model  \n"
        "✅ Market Calibration  \n"
        "✅ Monte Carlo Simulation"
    )
    st.divider()
    st.caption("Final historical archive. No live forecasts or betting recommendations.")


CSS = """
<style>
*{box-sizing:border-box}.page{margin:0;padding:28px;background:radial-gradient(circle at 88% 0,rgba(27,94,151,.21),transparent 36rem),radial-gradient(circle at 5% 85%,rgba(178,132,27,.055),transparent 28rem),linear-gradient(150deg,#031225,#071a2d);border:1px solid rgba(45,102,148,.42);border-radius:5px;min-height:100vh;color:#eaf1f8;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI Variable","Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:15px;-webkit-font-smoothing:antialiased}.flag{display:inline-flex;align-items:center;justify-content:center;min-width:29px;height:20px;padding:0 6px;margin-right:6px;border:1px solid #326384;border-radius:5px;background:linear-gradient(145deg,#143651,#102b43);color:#b8ddff;font-size:10px;font-weight:750;letter-spacing:.05em;vertical-align:2px}.header{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:24px}
.title{color:#fff;font-size:31px;font-weight:780;letter-spacing:-.035em;text-shadow:0 1px 2px rgba(0,0,0,.2)}.subtitle,.updated,.muted{color:#94bddf}.subtitle{font-size:14px;margin-top:8px}.updated{font-size:11px;font-weight:650;letter-spacing:.06em;text-align:right}
.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:16px 0}.kpi,.panel,.match-card,.group-card,.result-card{background:linear-gradient(145deg,rgba(11,39,65,.96),rgba(7,29,50,.96));border:1px solid #1b4a70;border-radius:13px;box-shadow:0 8px 24px rgba(0,0,0,.10)}
.kpi{padding:16px 18px;min-height:102px}.kpi-label,.section-label{color:#7db8e9;font-size:11px;font-weight:720;text-transform:uppercase;letter-spacing:.09em}.kpi-value{color:#fff;font-size:24px;font-weight:760;letter-spacing:-.025em;margin:8px 0 4px}.kpi-note{font-size:12px;color:#91aec7}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px}.panel{padding:16px}.panel-title{color:#f3f7fb;font-size:13px;font-weight:760;letter-spacing:.01em;margin-bottom:15px;display:flex;justify-content:space-between}.panel-title span:last-child{color:#4eb4ff;font-size:10px;font-weight:700}
.stage-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.stage-card{background:linear-gradient(145deg,#112c45,#10263a);border:1px solid #214864;border-radius:10px;padding:13px}.stage-name{font-size:11px;color:#a2c1dc;font-weight:650}.stage-count{color:#fff;font-size:21px;font-weight:740;margin-top:6px}
.final-card{background:linear-gradient(135deg,rgba(154,119,18,.25),rgba(22,63,94,.92));border:1px solid #806817;border-radius:13px;padding:22px;text-align:center}.final-label{color:#f1d365;font-size:10px;font-weight:750;letter-spacing:.1em}.final-teams{color:#fff;font-size:22px;font-weight:740;margin:15px 0}.final-score{font-size:40px;font-weight:780;letter-spacing:-.04em;color:#fff}.final-note{color:#c0d2e2;font-size:11px;margin-top:9px}
.match-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:13px}.match-card{padding:18px;transition:border-color .15s ease,transform .15s ease}.match-card:hover{border-color:#2b6d9e;transform:translateY(-1px)}.match-meta{display:flex;justify-content:space-between;color:#94bbdc;font-size:11px;margin-bottom:15px}.teams{color:#f4f8fc;display:grid;grid-template-columns:1fr 62px 1fr;align-items:center;text-align:center;font-size:16px;font-weight:690}.vs{color:#8eafca;font-size:12px;font-weight:650}.score{color:#fff;font-size:25px;font-weight:760;margin-top:7px}.prob-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:11px;margin-top:17px}.prob-label{font-size:10px;color:#95b7d3;letter-spacing:.06em}.prob-value{color:#fff;font-size:16px;font-weight:720;margin:6px 0}.bar{height:8px;background:#173149;border-radius:99px;overflow:hidden}.fill{height:100%;border-radius:99px}.green{background:linear-gradient(90deg,#25c96d,#65f49a)}.gray{background:#9aaabd}.red{background:#f05b67}.blue{background:linear-gradient(90deg,#1489f5,#3ab6ff)}
.group-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:13px}.group-card{padding:17px}.group-title{font-size:16px;font-weight:760;margin-bottom:15px}.group-row{display:grid;grid-template-columns:1.45fr 1fr 58px;gap:9px;align-items:center;margin:12px 0;font-size:13px}.right{text-align:right;font-weight:720}
.group-title,.group-row,.right{color:#f4f8fc}.ranking-row{color:#eaf1f8;display:grid;grid-template-columns:34px 190px 1fr 68px;gap:11px;align-items:center;margin:13px 0;font-size:13px}.rank{color:#88bce7;font-weight:720}.team{color:#fff;font-weight:680}
.result-card{color:#eaf1f8;padding:16px;margin-bottom:11px}.result-title{color:#fff;font-size:15px;font-weight:720}.result-meta{font-size:12px;color:#92b5d2;margin-top:7px}.badges{display:flex;gap:13px;margin-top:10px;font-size:12px;font-weight:720}.hit{color:#5cf090}.miss{color:#ff617a}
.score-layout{display:grid;grid-template-columns:.85fr 1.15fr;gap:26px}.score-team{text-align:center;padding:22px}.score-team-name{color:#fff;font-size:24px;font-weight:740}.xg-grid{display:grid;grid-template-columns:1fr 1fr;gap:11px;margin-top:19px}.xg{background:#10283e;border:1px solid #1b405d;border-radius:9px;padding:14px;color:#94b7d3}.xg b{display:block;color:#fff;font-size:23px;font-weight:730;margin-top:5px}.score-row{color:#eaf1f8;display:grid;grid-template-columns:32px 64px 1fr 62px;gap:10px;align-items:center;margin:12px 0;font-size:13px}.score-text{color:#fff;font-weight:720;font-size:16px}
.metric-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:13px}.metric{color:#eaf1f8;background:linear-gradient(145deg,#122f48,#10283e);border:1px solid #24506f;border-radius:10px;padding:13px}.metric b{color:#fff;display:block;font-size:20px;font-weight:740;margin-top:6px}.note{background:#0d2d49;border-left:3px solid #3bafff;border-radius:8px;padding:13px;color:#bdd2e4;font-size:11px;line-height:1.55}
@media(max-width:1000px){.kpis{grid-template-columns:repeat(2,1fr)}.grid-2,.score-layout{grid-template-columns:1fr}.group-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:650px){.page{padding:12px}.match-grid,.group-grid,.stage-grid,.metric-grid{grid-template-columns:1fr}.kpis{grid-template-columns:1fr}.header{display:block}.updated{text-align:left;margin-top:8px}}
</style>
"""


def page_shell(title: str, body: str, subtitle: str = "Final Tournament Analytics & Model Evaluation") -> str:
    return f"""<!doctype html><html><head>{CSS}</head><body><div class="page">
    <div class="header"><div><div class="title">🏆 {esc(title)}</div><div class="subtitle">{esc(subtitle)}</div></div>
    <div class="updated">2026 WORLD CUP · FINAL ARCHIVE</div></div>{body}</div></body></html>"""


def render(html: str, height: int = 1100):
    st.html(html)


def match_card(row, show_prediction=True) -> str:
    prediction = ""
    if show_prediction:
        prediction = f"""<div class="prob-grid">
        <div><div class="prob-label">HOME</div><div class="prob-value">{pct(row.home_prob)}</div>{bar(row.home_prob)}</div>
        <div><div class="prob-label">DRAW</div><div class="prob-value">{pct(row.draw_prob)}</div>{bar(row.draw_prob,'gray')}</div>
        <div><div class="prob-label">AWAY</div><div class="prob-value">{pct(row.away_prob)}</div>{bar(row.away_prob,'red')}</div></div>"""
    return f"""<div class="match-card"><div class="match-meta"><span>{esc(row.stage)}</span><span>{date_label(row.commence_time)}</span></div>
    <div class="teams"><div>{flag(row.home_team)}<br>{esc(row.home_team)}</div><div class="vs">FINAL<div class="score">{actual_score(row)}</div></div><div>{flag(row.away_team)}<br>{esc(row.away_team)}</div></div>{prediction}</div>"""


def result_card(row) -> str:
    badges = "".join(
        f'<span class="{"hit" if bool(row[col]) else "miss"}">{"✓" if bool(row[col]) else "✕"} {label}</span>'
        for col, label in (("result_hit", "Winner"), ("top3_hit", "Top3"), ("top5_hit", "Top5"), ("top8_hit", "Top8"))
    )
    return f"""<div class="result-card"><div class="result-title">{flag(row.home_team)} {esc(row.home_team)} &nbsp; {actual_score(row)} &nbsp; {flag(row.away_team)} {esc(row.away_team)}</div>
    <div class="result-meta">{esc(row.stage)} · Predicted: {esc(row.predicted_result)} · Actual: {esc(row.actual_result)}</div><div class="badges">{badges}</div></div>"""


def group_cards(frame: pd.DataFrame) -> str:
    cards = []
    for group_name in sorted(frame["group"].dropna().unique()):
        rows = []
        group = frame[frame["group"] == group_name].sort_values("qualified_prob", ascending=False)
        for index, (_, row) in enumerate(group.iterrows(), 1):
            rows.append(f'<div class="group-row"><div>{index} &nbsp; {flag(row.team)} <b>{esc(row.team)}</b></div>{bar(row.qualified_prob)}<div class="right">{pct(row.qualified_prob)}</div></div>')
        cards.append(f'<div class="group-card"><div class="group-title">GROUP {esc(group_name)}</div>{"".join(rows)}</div>')
    return f'<div class="group-grid">{"".join(cards)}</div>'


def stage_summary() -> str:
    cards = []
    for stage in STAGE_ORDER:
        count = int((matches["stage"] == stage).sum())
        cards.append(f'<div class="stage-card"><div class="stage-name">{esc(stage)}</div><div class="stage-count">{count}</div></div>')
    return f'<div class="stage-grid">{"".join(cards)}</div>'


def champion_ranking(limit=10) -> str:
    rows = []
    for index, (_, row) in enumerate(champions.sort_values("champion_prob", ascending=False).head(limit).iterrows(), 1):
        rows.append(f'<div class="ranking-row"><div class="rank">{index}</div><div class="team">{flag(row.team)} {esc(row.team)}</div>{bar(row.champion_prob,"blue")}<div class="right">{pct(row.champion_prob)}</div></div>')
    return "".join(rows)


def dashboard_page() -> str:
    final = matches[matches["stage"] == "Final"].iloc[-1]
    kpis = f"""<div class="kpis">
    <div class="kpi"><div class="kpi-label">Matches</div><div class="kpi-value">{len(matches)}</div><div class="kpi-note">Complete tournament</div></div>
    <div class="kpi"><div class="kpi-label">Teams</div><div class="kpi-value">48</div><div class="kpi-note">12 groups</div></div>
    <div class="kpi"><div class="kpi-label">Champion</div><div class="kpi-value"><span class="flag">ES</span> Spain</div><div class="kpi-note">2026 World Cup winner</div></div>
    <div class="kpi"><div class="kpi-label">Winner Accuracy</div><div class="kpi-value">{pct(winner_accuracy)}</div><div class="kpi-note">104 archived forecasts</div></div>
    <div class="kpi"><div class="kpi-label">Top-3 Score Hit</div><div class="kpi-value">{pct(top3_accuracy)}</div><div class="kpi-note">Exact score evaluation</div></div></div>"""
    final_card = f"""<div class="final-card"><div class="final-label">2026 FIFA WORLD CUP FINAL</div><div class="final-teams"><span class="flag">ES</span> Spain &nbsp; vs &nbsp; <span class="flag">AR</span> Argentina</div><div class="final-score">{actual_score(final)}</div><div class="final-note">Spain crowned world champions after extra time</div></div>"""
    body = kpis + f'<div class="grid-2"><div class="panel"><div class="panel-title"><span>TOURNAMENT COMPLETE</span><span>104 MATCHES</span></div>{final_card}</div><div class="panel"><div class="panel-title"><span>TOURNAMENT STAGES</span><span>FULL ARCHIVE</span></div>{stage_summary()}</div></div>'
    body += f'<div class="grid-2"><div class="panel"><div class="panel-title"><span>PRE-TOURNAMENT CHAMPION FORECAST</span><span>ARCHIVED MODEL OUTPUT</span></div>{champion_ranking()}</div><div class="panel"><div class="panel-title"><span>FINAL MODEL EVALUATION</span><span>ALL MATCHES</span></div><div class="metric-grid"><div class="metric"><div class="section-label">Top 5</div><b>{pct(top5_accuracy)}</b></div><div class="metric"><div class="section-label">Top 8</div><b>{pct(top8_accuracy)}</b></div><div class="metric"><div class="section-label">Brier</div><b>{brier_score(completed):.3f}</b></div><div class="metric"><div class="section-label">Log Loss</div><b>{log_loss(completed):.3f}</b></div></div><div class="note">Forecasts shown here were recovered from the project’s committed pre-match snapshots and evaluated against all 104 final results. Live forecasting and scheduled updates are retired.</div></div></div>'
    body += f'<div class="panel" style="margin-top:12px"><div class="panel-title"><span>FINAL MATCHES</span><span>ARCHIVED FORECASTS + RESULTS</span></div><div class="match-grid">{"".join(match_card(row) for _,row in matches.tail(6).iterrows())}</div></div>'
    return page_shell("WORLD CUP FORECAST DASHBOARD", body, "Final edition · Historical forecasts · Actual results · Model evaluation")


if page == "Dashboard":
    render(dashboard_page(), 1400)

elif page == "Forecast Archive":
    stage = st.selectbox("Tournament stage", STAGE_ORDER)
    frame = matches[matches["stage"] == stage]
    body = f'<div class="note">These are the earliest committed model probabilities recovered for each matchup—not forecasts regenerated after the results.</div><div class="match-grid" style="margin-top:12px">{"".join(match_card(row) for _,row in frame.iterrows())}</div>'
    render(page_shell("Forecast Archive", body, f"{stage} · {len(frame)} archived pre-match forecasts"), max(850, 330 * ((len(frame) + 2) // 3)))

elif page == "Score Forecast":
    stage = st.selectbox("Tournament stage", STAGE_ORDER, key="score_stage")
    options = matches[matches["stage"] == stage][["matchup_key", "home_team", "away_team"]].copy()
    labels = {row.matchup_key: f"{row.home_team} vs {row.away_team}" for _, row in options.iterrows()}
    key = st.selectbox("Match", list(labels), format_func=labels.get)
    match = matches[matches["matchup_key"] == key].iloc[0]
    ranked = scores[scores["matchup_key"] == key].sort_values("rank").head(10)
    rows = "".join(f'<div class="score-row"><div class="rank">{int(row["rank"])}</div><div class="score-text">{esc(row["score"])}</div>{bar(row["score_probability"])}<div class="right">{pct(row["score_probability"])}</div></div>' for _, row in ranked.iterrows())
    body = f'<div class="panel"><div class="score-layout"><div class="score-team"><div class="score-team-name">{flag(match.home_team)} {esc(match.home_team)} &nbsp; {actual_score(match)} &nbsp; {flag(match.away_team)} {esc(match.away_team)}</div><div class="muted" style="margin-top:8px">{esc(stage)} · Archived pre-match forecast</div><div class="xg-grid"><div class="xg">xG Home<b>{float(match.home_xg):.2f}</b></div><div class="xg">xG Away<b>{float(match.away_xg):.2f}</b></div></div></div><div><div class="panel-title"><span>TOP 10 MOST LIKELY SCORES</span><span>ACTUAL: {actual_score(match)}</span></div>{rows}</div></div></div>'
    render(page_shell("Score Forecast Archive", body, labels[key]), 760)

elif page == "Group Stage":
    body = '<div class="note">All 12 groups and 48 teams are restored from the complete pre-tournament group-stage simulation snapshot.</div><div style="margin-top:12px">' + group_cards(groups) + '</div>'
    render(page_shell("Group Stage Archive", body, "12 groups · 48 teams · Archived qualification probabilities"), 1500)

elif page == "Knockout Results":
    knockout = matches[matches["stage"] != "Group Stage"]
    sections = []
    for stage in STAGE_ORDER[1:]:
        frame = knockout[knockout["stage"] == stage]
        sections.append(f'<div class="panel" style="margin-bottom:12px"><div class="panel-title"><span>{esc(stage).upper()}</span><span>{len(frame)} MATCHES</span></div><div class="match-grid">{"".join(match_card(row,False) for _,row in frame.iterrows())}</div></div>')
    render(page_shell("Knockout Results", "".join(sections), "Complete path from the Round of 32 to Spain’s title"), 2200)

elif page == "Champion Forecast":
    body = '<div class="final-card"><div class="final-label">ACTUAL 2026 WORLD CHAMPION</div><div class="final-teams"><span class="flag">ES</span> SPAIN</div><div class="final-note">The ranking below preserves the model’s pre-tournament probabilities for comparison with the final outcome.</div></div><div class="panel" style="margin-top:12px"><div class="panel-title"><span>PRE-TOURNAMENT CHAMPION PROBABILITY</span><span>48 TEAMS</span></div>' + champion_ranking(48) + '</div>'
    render(page_shell("Champion Forecast", body, "Archived Monte Carlo probabilities versus the final champion"), 2100)

elif page == "Tournament Results":
    stage = st.selectbox("Tournament stage", STAGE_ORDER, key="results_stage")
    frame = matches[matches["stage"] == stage]
    body = f'<div class="match-grid">{"".join(match_card(row,False) for _,row in frame.iterrows())}</div>'
    render(page_shell("Tournament Results", body, f"{stage} · {len(frame)} completed matches"), max(800, 245 * ((len(frame) + 2) // 3)))

elif page == "Model Accuracy":
    stage = st.selectbox("Evaluation scope", ["All Matches"] + STAGE_ORDER, key="accuracy_stage")
    frame = completed if stage == "All Matches" else completed[completed["stage"] == stage]
    body = f'<div class="kpis"><div class="kpi"><div class="kpi-label">Evaluated Matches</div><div class="kpi-value">{len(frame)}</div></div><div class="kpi"><div class="kpi-label">Winner Accuracy</div><div class="kpi-value">{pct(frame.result_hit.mean())}</div></div><div class="kpi"><div class="kpi-label">Top-3 Hit</div><div class="kpi-value">{pct(frame.top3_hit.mean())}</div></div><div class="kpi"><div class="kpi-label">Top-5 Hit</div><div class="kpi-value">{pct(frame.top5_hit.mean())}</div></div><div class="kpi"><div class="kpi-label">Top-8 Hit</div><div class="kpi-value">{pct(frame.top8_hit.mean())}</div></div></div><div class="metric-grid"><div class="metric"><div class="section-label">Brier Score</div><b>{brier_score(frame):.3f}</b></div><div class="metric"><div class="section-label">Log Loss</div><b>{log_loss(frame):.3f}</b></div><div class="metric"><div class="section-label">Top-1 Score</div><b>{pct(frame.top1_hit.mean())}</b></div><div class="metric"><div class="section-label">Coverage</div><b>{len(frame)}/104</b></div></div><div class="panel"><div class="panel-title"><span>MATCH-BY-MATCH EVALUATION</span><span>{esc(stage).upper()}</span></div>{"".join(result_card(row) for _,row in frame.iloc[::-1].iterrows())}</div>'
    render(page_shell("Model Accuracy", body, "Final evaluation of archived pre-match forecasts"), max(1100, 125 * len(frame)))

elif page == "Model vs Market":
    if market.empty:
        render(page_shell("Model vs Market", '<div class="note">No archived market comparison is available.</div>'), 600)
    else:
        avg_diff = market["abs_diff"].mean()
        rows = []
        for _, row in market.sort_values("abs_diff", ascending=False).iterrows():
            rows.append(f'<div class="result-card"><div class="result-title">{flag(row.home_team)} {esc(row.home_team)} vs {flag(row.away_team)} {esc(row.away_team)}</div><div class="result-meta">Average absolute difference: {float(row.abs_diff):.3f}</div><div class="prob-grid"><div><div class="prob-label">MODEL HOME</div><div class="prob-value">{pct(row.model_home_prob)}</div></div><div><div class="prob-label">MODEL DRAW</div><div class="prob-value">{pct(row.model_draw_prob)}</div></div><div><div class="prob-label">MODEL AWAY</div><div class="prob-value">{pct(row.model_away_prob)}</div></div></div></div>')
        body = f'<div class="metric-grid"><div class="metric"><div class="section-label">Archived Matches</div><b>{len(market)}</b></div><div class="metric"><div class="section-label">Mean Difference</div><b>{avg_diff:.3f}</b></div></div><div class="note">Historical model-versus-market analysis is presented for research evaluation only. It is not a betting recommendation.</div><div class="panel" style="margin-top:12px">{"".join(rows)}</div>'
        render(page_shell("Model vs Market", body, "Archived calibration comparison · Research use only"), max(1000, 145 * len(market)))
