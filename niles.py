# proclubs_app.py
# Streamlit app for a FIFA Pro Clubs team with 4 roles + Admin player management
# Manager interactive tactics board with visual formation placement
# + NEW: Training Sessions + Training Attendance (color-coded + stats)
# Run locally: pip install streamlit pandas plotly pillow
# Then: streamlit run proclubs_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import time
from datetime import datetime, date, time as dtime

# -------------------------------
# CONFIG (set once, top-level)
# -------------------------------
st.set_page_config(page_title="Nile Esports ProClubs Hub", page_icon="⚽", layout="wide")

# -------------------------------
# GLOBAL STYLES (including Intro UX)
# -------------------------------
appINTRO_CSS = """
<style>
:root{
  --glass-bg: rgba(255,255,255,0.08);
  --glass-brd: rgba(255,255,255,0.18);
  --accent: #1e3a8a;      /* navy for selectbox/date text */
  --accent-2: #0ea5e9;    /* bright blue */
  --button-accent: #22c55e; /* bright green for buttons */
}

/* Restore your radial gradient background */
html, body, [data-testid="stAppViewContainer"] {
  background: radial-gradient(
    1200px 800px at 10% 10%,
    #0b1220 0%,
    #0b1220 30%,
    #0d1b2a 60%,
    #0a0f1a 100%
  ) !important;
  color: white !important;
}

/* Sidebar keeps solid background */
[data-testid="stSidebar"] {
  background-color: #0b1220 !important;
}
[data-testid="stSidebar"] * {
  color: #ffffff !important;
  font-weight: 500;
}

/* Header transparent gradient */
[data-testid="stHeader"]{
  background: linear-gradient(180deg, rgba(0,0,0,0.35), rgba(0,0,0,0)) !important;
}

/* Links */
a{
  color: var(--accent-2) !important;
  text-decoration: none;
}

/* === SELECTBOX === */
.stSelectbox > div, .stMultiSelect > div {
  background-color: transparent !important;
  border: 1px solid var(--accent-2) !important;
  border-radius: 8px !important;
  backdrop-filter: blur(6px) !important;
}
.stSelectbox div[data-baseweb="select"] > div[role="button"] span {
  color: var(--accent) !important;
  font-weight: 600 !important;
}
.stSelectbox [data-baseweb="select"] span[data-testid="stMarkdownContainer"] p {
  color: var(--accent) !important;
}
/* Dropdown popover */
[data-baseweb="popover"] {
  background-color: #0b1220 !important;
  border: 1px solid var(--accent-2) !important;
  border-radius: 8px !important;
}
[data-baseweb="popover"] [role="option"],
[data-baseweb="popover"] [role="option"] * {
  color: var(--accent) !important;
}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [role="option"]:hover * {
  background-color: var(--accent) !important;
  color: #ffffff !important;
}
[data-baseweb="popover"] [aria-selected="true"],
[data-baseweb="popover"] [aria-selected="true"] * {
  background-color: var(--accent-2) !important;
  color: #ffffff !important;
}

/* === DATE INPUT === */
.stDateInput > div > div input {
  color: var(--accent) !important;
  font-weight: 600 !important;
}
[data-baseweb="calendar"] {
  background-color: #0b1220 !important;
  color: var(--accent) !important;
  border: 1px solid var(--accent-2) !important;
  border-radius: 8px !important;
}
[data-baseweb="calendar"] div[role="row"] div[role="gridcell"] {
  color: var(--accent) !important;
}
[data-baseweb="calendar"] div[role="row"] div[role="gridcell"][aria-selected="true"] {
  background-color: var(--accent-2) !important;
  color: #ffffff !important;
}
[data-baseweb="calendar"] div[role="row"] div[role="gridcell"]:hover {
  background-color: var(--accent) !important;
  color: #ffffff !important;
}

/* === INPUT FIELDS === */
.stTextInput>div>div>input,
.stPasswordInput>div>div>input,
.stTextArea>div>textarea {
  background-color: rgba(15, 23, 42, 0.85) !important;
  color: #ffffff !important;
  border: 1px solid var(--accent-2) !important;
  border-radius: 8px !important;
  backdrop-filter: blur(6px) !important;
}
.stTextInput>div>div>input::placeholder,
.stPasswordInput>div>div>input::placeholder,
.stTextArea>div>textarea::placeholder {
  color: rgba(255, 255, 255, 0.6) !important;
}

/* === BUTTONS === */
.stButton>button {
  background: linear-gradient(90deg, var(--button-accent), var(--accent-2)) !important;
  color: white !important;
  border-radius: 8px !important;
  border: none !important;
  font-weight: bold !important;
}
.stButton>button:hover {
  opacity: 0.9 !important;
}
[data-testid="stSidebar"] .stButton>button {
  background-color: #dc2626 !important;
}
[data-testid="stSidebar"] .stButton>button:hover {
  background-color: #b91c1c !important;
}

/* === GLASS EFFECT === */
.glass{
  background: var(--glass-bg);
  border: 1px solid var(--glass-brd);
  box-shadow: 0 10px 30px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.06);
  backdrop-filter: blur(10px);
  border-radius: 18px;
}

/* === HERO BLOCK === */
.hero{
  position: relative;
  overflow: hidden;
  padding: 28px 26px;
}
.glow{
  position:absolute; inset:-2px;
  background: conic-gradient(from 0deg, #1e3a8a33, #0ea5e933, transparent 30%, transparent 100%);
  filter: blur(18px); animation: spin 7s linear infinite;
  z-index:0; opacity:.7;
}
@keyframes spin{ to{ transform: rotate(360deg); } }
.hero-content{ position:relative; z-index:2; }
.title{
  font-weight: 900; letter-spacing: .6px; font-size: 40px; line-height:1.1;
  text-shadow: 0 6px 30px rgba(34,197,94,.25);
}
.subtitle{
  font-size: 17px; opacity: .92;
}
.card{
  transition: transform .25s ease, box-shadow .25s ease, background .25s ease;
  padding: 18px;
}
.card:hover{
  transform: translateY(-4px) scale(1.01);
  box-shadow: 0 12px 30px rgba(0,0,0,.35);
}
.badge{
  display:inline-block; padding:6px 12px; border-radius:14px;
  background: linear-gradient(90deg, var(--button-accent), var(--accent-2));
  color:white; font-size:12px; font-weight:700;
}
</style>
"""






















st.markdown(appINTRO_CSS, unsafe_allow_html=True)

# -------------------------------
# APP TITLE & PATHS
# -------------------------------
APP_TITLE = "Nile Esports ProClubs Hub"
DATA_DIR = "data"
UPLOADS_DIR = "uploads"

MATCHES_FILE = os.path.join(DATA_DIR, "matches.csv")
PLAYER_STATS_FILE = os.path.join(DATA_DIR, "player_stats.csv")
TACTICS_FILE = os.path.join(DATA_DIR, "tactics.csv")              # high-level tactics text
TACTICS_POS_FILE = os.path.join(DATA_DIR, "tactics_positions.csv") # visual board assignments
AVAIL_FILE = os.path.join(DATA_DIR, "availability.csv")
FANWALL_FILE = os.path.join(DATA_DIR, "fan_wall.csv")
PLAYERS_FILE = os.path.join(DATA_DIR, "players.csv")               # roster

# NEW: training sessions + attendance
TRAINING_SESSIONS_FILE = os.path.join(DATA_DIR, "training_sessions.csv")
TRAINING_ATTEND_FILE   = os.path.join(DATA_DIR, "training_attendance.csv")

# Simple in-code fallback role codes
ROLE_CODES = {
    "admin": {"Admin": "ADMIN-123"},
    "manager": {"Manager": "MGR-456"},
    "player": {"Player1": "PL-001", "Player2": "PL-002", "Player3": "PL-003"},
}

# Backward compatibility for Streamlit rerun
if not hasattr(st, "rerun"):
    st.rerun = st.experimental_rerun  # type: ignore

# -------------------------------
# DATA LAYER HELPERS
# -------------------------------
def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)

def ensure_csvs():
    if not os.path.exists(MATCHES_FILE):
        pd.DataFrame(columns=["match_id","date","opponent","our_score","their_score","result","notes"]).to_csv(MATCHES_FILE, index=False)
    if not os.path.exists(PLAYER_STATS_FILE):
        pd.DataFrame(columns=["match_id","player_name","position","goals","assists","rating","yellow_cards","red_cards"]).to_csv(PLAYER_STATS_FILE, index=False)
    if not os.path.exists(TACTICS_FILE):
        pd.DataFrame(columns=["formation","roles","instructions","notes","image_path","updated_by","updated_at"]).to_csv(TACTICS_FILE, index=False)
    if not os.path.exists(TACTICS_POS_FILE):
        pd.DataFrame(columns=["formation","position","player_name","x","y","updated_by","updated_at"]).to_csv(TACTICS_POS_FILE, index=False)
    if not os.path.exists(AVAIL_FILE):
        pd.DataFrame(columns=["date","player_name","availability"]).to_csv(AVAIL_FILE, index=False)
    if not os.path.exists(FANWALL_FILE):
        pd.DataFrame(columns=["timestamp","user","message","approved"]).to_csv(FANWALL_FILE, index=False)
    if not os.path.exists(PLAYERS_FILE):
        seed = pd.DataFrame([
            {"player_id":1, "name":"Player1", "position":"ST",  "code":"PL-001", "active":True},
            {"player_id":2, "name":"Player2", "position":"CM",  "code":"PL-002", "active":True},
            {"player_id":3, "name":"Player3", "position":"CB",  "code":"PL-003", "active":True},
        ])
        seed.to_csv(PLAYERS_FILE, index=False)
    # NEW: training CSVs
    if not os.path.exists(TRAINING_SESSIONS_FILE):
        pd.DataFrame(columns=["session_id","date","time","title","location","notes","created_by","created_at"]).to_csv(TRAINING_SESSIONS_FILE, index=False)
    if not os.path.exists(TRAINING_ATTEND_FILE):
        pd.DataFrame(columns=["session_id","date","player_name","status","timestamp"]).to_csv(TRAINING_ATTEND_FILE, index=False)

def read_csv_safe(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        ensure_csvs()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

def write_csv_safe(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False)

# -------------------------------
# AUTH & SESSION
# -------------------------------
def init_session():
    if "auth" not in st.session_state:
        st.session_state.auth = {"role": None, "name": None}
    if "page" not in st.session_state:
        st.session_state.page = "intro"   # INTRO -> LOGIN -> APP

def logout():
    st.session_state.auth = {"role": None, "name": None}
    st.session_state.page = "intro"
    st.rerun()

def validate_player_login(name: str, code: str) -> bool:
    players = read_csv_safe(PLAYERS_FILE)
    if not players.empty:
        active_col = "active" in players.columns
        cond = (players["name"].str.lower()==name.lower()) & (players["code"].astype(str)==str(code))
        if active_col:
            cond = cond & (players["active"]==True)
        row = players[cond]
        if not row.empty:
            return True
    valid = ROLE_CODES.get("player", {}).get(name)
    return bool(valid and code == valid)

# -------------------------------
# UTILITIES
# -------------------------------
def calc_result(our_score: int, their_score: int) -> str:
    if our_score > their_score: return "W"
    if our_score < their_score: return "L"
    return "D"


# =============================
# Helper for match labels everywhere ### CHANGE ###
# =============================

def match_label_from_id(mid, matches_df):
    try:
        row = matches_df[matches_df["match_id"] == int(mid)].iloc[0]
        return f"{row['date']} vs {row['opponent']}"
    except Exception:
        return str(mid)


def next_match_info(matches: pd.DataFrame):
    if matches.empty: return None
    m = matches.copy()
    try:
        m["date"] = pd.to_datetime(m["date"]).dt.date
    except Exception:
        return None
    future = m[m["date"] >= date.today()].sort_values("date")
    if future.empty: return None
    return future.iloc[0].to_dict()

def last_match_info(matches: pd.DataFrame):
    if matches.empty: return None
    m = matches.copy()
    try:
        m["date"] = pd.to_datetime(m["date"]).dt.date
    except Exception:
        return None
    past = m[m["date"] <= date.today()].sort_values("date")
    if past.empty: return None
    return past.iloc[-1].to_dict()

def render_header():
    st.markdown(
        """
        <div class='glass hero' style="margin-bottom:12px;">
            <div class="glow"></div>
            <div class="hero-content">
                <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
                    <div class="title">Nile Esports ProClubs Hub</div>
                    <span class='badge'>Live</span>
                </div>
                <div class="small" style="margin-top:6px;">Manage matches, tactics, roster, training & fan hype — all in one place.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    role = st.session_state.auth["role"]
    name = st.session_state.auth["name"]
    st.sidebar.markdown(f"### ⚽ {APP_TITLE}")
    st.sidebar.success(f"Role: {role.upper()} | User: {name}")
    if st.sidebar.button("Logout"):
        logout()

# -------------------------------
# INTRO PAGE (before login)
# -------------------------------
def intro_page():
    # Professional Splash Intro
    st.markdown(f"""
    <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;height:85vh;text-align:center;'>
        <img src='{ "https://scontent.fcai20-4.fna.fbcdn.net/v/t39.30808-6/460331146_122191529468078659_8549609423668977699_n.jpg?_nc_cat=107&ccb=1-7&_nc_sid=6ee11a&_nc_eui2=AeEogfareJPi_JT1tAC-LFAXYDCIEt4d8QBgMIgS3h3xADavaqieLvC-GdEW6JvdlEAm3FAmZUj65l-E9vQlcUh5&_nc_ohc=nyGBiXclu9MQ7kNvwFW61kB&_nc_oc=AdltF6iHSSsAOJ7qpypmR3q-yrBfBYrPVH-Jl8wTNohzgvPZ729IqJ-isR5jSjvz9xI&_nc_zt=23&_nc_ht=scontent.fcai20-4.fna&_nc_gid=nkBEgbDELXlG98EOb9q4kg&oh=00_AfVLKzVIBjgpN_dF2gfRTQ1H8fz_yzvzVseM6ny3psxp_g&oe=68A3E976" }'
             style='width:200px;height:auto;animation:fadeIn 2s ease-in-out;'>
        <h1 class="title" style='margin-top:20px;'>Nile Esports</h1>
        <p class="subtitle">One Club. One Heartbeat. 🖤💚</p>
    </div>
    <style>
        @keyframes fadeIn {{ from {{opacity:0;}} to {{opacity:1;}} }}
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Enter the Hub", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
    with col2:
        if st.button("👀 View Public Fan Wall", use_container_width=True):
            st.session_state.auth = {"role": "fan", "name": "Guest"}
            st.session_state.page = "fan_public_only"
            st.balloons()
            st.rerun()


# -------------------------------
# LOGIN PAGE
# -------------------------------
def login_ui():
    # Branded Login Card
    st.markdown(f"""
    <div class='glass card' style='padding:30px;max-width:420px;margin:auto;text-align:center;'>
        <img src='{ "https://scontent.fcai20-4.fna.fbcdn.net/v/t39.30808-6/460331146_122191529468078659_8549609423668977699_n.jpg?_nc_cat=107&ccb=1-7&_nc_sid=6ee11a&_nc_eui2=AeEogfareJPi_JT1tAC-LFAXYDCIEt4d8QBgMIgS3h3xADavaqieLvC-GdEW6JvdlEAm3FAmZUj65l-E9vQlcUh5&_nc_ohc=nyGBiXclu9MQ7kNvwFW61kB&_nc_oc=AdltF6iHSSsAOJ7qpypmR3q-yrBfBYrPVH-Jl8wTNohzgvPZ729IqJ-isR5jSjvz9xI&_nc_zt=23&_nc_ht=scontent.fcai20-4.fna&_nc_gid=nkBEgbDELXlG98EOb9q4kg&oh=00_AfVLKzVIBjgpN_dF2gfRTQ1H8fz_yzvzVseM6ny3psxp_g&oe=68A3E976" }'
             style='width:100px;height:auto;margin-bottom:10px;'>
        <h2 style='margin:0;'>Sign In</h2>
        <p class="small" style="margin:.3rem 0 1rem 0;">Choose your role and use your access code</p>
    </div>
    """, unsafe_allow_html=True)


    role = st.selectbox("Select your role", ["Admin", "Manager", "Player", "Fan"])
    name = st.text_input("Your name")
    code_required = role != "Fan"
    code = st.text_input("Access code" if code_required else "Access code (not required)",
                         type="password", disabled=not code_required)

    colL, colR = st.columns(2)
    with colL:
        if st.button("Enter", type="primary", use_container_width=True):
            if not name:
                st.warning("Please enter your name.")
                return
            if role == "Fan":
                st.session_state.auth = {"role": "fan", "name": name}
                st.success(f"Welcome, {name}! You're logged in as Fan.")
                st.balloons()
                st.rerun()
            elif role == "Admin":
                valid = ROLE_CODES.get("admin", {}).get(name)
                if valid and code == valid:
                    st.session_state.auth = {"role": "admin", "name": name}
                    st.success("Welcome, Admin!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Invalid admin name or code.")
            elif role == "Manager":
                valid = ROLE_CODES.get("manager", {}).get(name)
                if valid and code == valid:
                    st.session_state.auth = {"role": "manager", "name": name}
                    st.success("Welcome, Manager!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Invalid manager name or code.")
            elif role == "Player":
                if validate_player_login(name, code):
                    st.session_state.auth = {"role": "player", "name": name}
                    st.success(f"Welcome, {name}! Let's ball.")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Invalid player name or code.")
    with colR:
        if st.button("⬅ Back to Intro", use_container_width=True):
            st.session_state.page = "intro"
            st.rerun()
# -------------------------------
# DASHBOARD
# -------------------------------
def page_dashboard():
    matches = read_csv_safe(MATCHES_FILE)
    stats = read_csv_safe(PLAYER_STATS_FILE)

    # Ensure proper date format
    if not matches.empty:
        matches["date"] = pd.to_datetime(matches["date"], errors="coerce").dt.date
        past_matches = matches[matches["date"] < date.today()].sort_values("date", ascending=False)
        upcoming_matches = matches[matches["date"] >= date.today()].sort_values("date", ascending=True)
    else:
        past_matches = pd.DataFrame()
        upcoming_matches = pd.DataFrame()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Last Match")
        if not past_matches.empty:
            lm = past_matches.iloc[0]
            st.metric(label=f"vs {lm['opponent']} on {lm['date']}",
                      value=f"{int(lm['our_score'])}-{int(lm['their_score'])}",
                      delta=lm['result'])
            st.write(lm.get("notes", ""))
        else:
            st.info("No past matches yet.")

    with col2:
        st.subheader("Next Match")
        if not upcoming_matches.empty:
            nm = upcoming_matches.iloc[0]
            days_left = (nm["date"] - date.today()).days
            st.metric(label=f"vs {nm['opponent']} on {nm['date']}",
                      value=f"{max(days_left,0)} days")
            st.write(nm.get("notes", ""))
        else:
            st.info("No upcoming matches scheduled.")

    st.divider()

    # Show full past/upcoming lists
    st.subheader("📋 Match Results")
    if not past_matches.empty:
        st.dataframe(past_matches.reset_index(drop=True), use_container_width=True)
    else:
        st.caption("No results yet.")

    st.subheader("📅 Upcoming Matches")
    if not upcoming_matches.empty:
        st.dataframe(upcoming_matches.reset_index(drop=True), use_container_width=True)
    else:
        st.caption("No upcoming fixtures.")

    st.divider()
    st.subheader("Leaderboards")
    if stats.empty:
        st.info("No player stats yet.")
    else:
        agg = stats.groupby("player_name").agg(
            goals=("goals","sum"),
            assists=("assists","sum"),
            avg_rating=("rating","mean"),
            yellow=("yellow_cards","sum"),
            red=("red_cards","sum"),
            matches=("match_id","count")
        ).reset_index()

        c1, c2 = st.columns(2)
        with c1:
            st.caption("Top Scorers")
            st.plotly_chart(px.bar(agg.sort_values("goals", ascending=False).head(10),
                                   x="player_name", y="goals"), use_container_width=True)
        with c2:
            st.caption("Top Assists")
            st.plotly_chart(px.bar(agg.sort_values("assists", ascending=False).head(10),
                                   x="player_name", y="assists"), use_container_width=True)

        # Best Average Rating with Rank ### CHANGE ###
        st.caption("Best Average Rating (min 3 matches)")
        best = agg[agg["matches"] >= 3].sort_values("avg_rating", ascending=False)
        best.insert(0, "Rank", best["avg_rating"].rank(method="min", ascending=False).astype(int))
        st.dataframe(best, use_container_width=True)


# -------------------------------
# ADMIN PAGES (Matches, Stats, Fan Wall, Reports, PLAYERS CRUD)
# -------------------------------
def admin_matches_page():
    st.subheader("Matches – Upcoming vs Results")

    matches = read_csv_safe(MATCHES_FILE)

    # ---------- Add upcoming fixture (no scores) ----------
    with st.form("add_upcoming"):
        st.markdown("### ➕ Add Upcoming Match")
        c1, c2 = st.columns(2)
        with c1:
            m_date = st.date_input("Match date", value=date.today())
            opponent = st.text_input("Opponent")
        with c2:
            notes = st.text_area("Notes", "")
        submitted_upcoming = st.form_submit_button("Add Upcoming", type="primary")

    if submitted_upcoming:
        if not opponent.strip():
            st.warning("Opponent name is required.")
        elif m_date < date.today():
            st.warning("Upcoming match must be today or later. Use 'Add Match Result' for past dates.")
        else:
            match_id = int(time.time() * 1000)
            new_row = {
                "match_id": match_id,
                "date": m_date.strftime("%Y-%m-%d"),
                "opponent": opponent.strip(),
                "our_score": None,
                "their_score": None,
                "result": None,
                "notes": notes.strip()
            }
            matches = pd.concat([matches, pd.DataFrame([new_row])], ignore_index=True)
            write_csv_safe(matches, MATCHES_FILE)
            st.success("Upcoming match added.")
            st.rerun()

    st.divider()

    # ---------- Add result for existing match ----------
    matches = read_csv_safe(MATCHES_FILE)
    m2 = matches.copy()
    m2["date"] = pd.to_datetime(m2["date"], errors="coerce").dt.date
    for c in ["our_score", "their_score"]:
        m2[c] = pd.to_numeric(m2[c], errors="coerce")

    # Unfinished = matches without scores
    unfinished = m2[m2["our_score"].isna() | m2["their_score"].isna()].sort_values("date")
    if unfinished.empty:
        st.info("No upcoming matches waiting for a result.")
    else:
        with st.form("add_result"):
            st.markdown("### ✅ Add Match Result")
            mid = st.selectbox(
                "Match to finalize",
                options=unfinished["match_id"].astype(int).tolist(),
                format_func=lambda x: match_label_from_id(x, unfinished)  # CHANGE: show date vs opponent
            )
            match_date = unfinished.loc[unfinished["match_id"] == int(mid), "date"].values[0]
            c1, c2, c3 = st.columns(3)
            with c1:
                our = st.number_input("Our score", 0, 99, 0)
            with c2:
                their = st.number_input("Their score", 0, 99, 0)
            with c3:
                notes2 = st.text_area(
                    "Notes (optional)",
                    value=str(unfinished.loc[unfinished["match_id"] == int(mid), "notes"].values[0]
                              if not unfinished.empty else "")
                )
            submit_res = st.form_submit_button("Save Result", type="primary")

        if submit_res:
            if match_date > date.today():
                st.error(f"Cannot add result yet — match date {match_date} is in the future.")
            else:
                res = calc_result(int(our), int(their))
                matches.loc[matches["match_id"] == int(mid),
                            ["our_score", "their_score", "result", "notes"]] = [
                    int(our), int(their), res, notes2
                ]
                write_csv_safe(matches, MATCHES_FILE)
                st.success("Result saved.")
                st.rerun()

    st.divider()

    # ---------- Table & Delete ----------
    matches = read_csv_safe(MATCHES_FILE)
    if matches.empty:
        st.info("No matches yet.")
        return

    show = matches.copy()
    st.dataframe(show.sort_values("date", ascending=False), use_container_width=True)

    del_mid = st.selectbox(
        "Delete match",
        options=show["match_id"].astype(int).tolist(),
        format_func=lambda x: match_label_from_id(x, show)  # CHANGE: show date vs opponent
    )
    if st.button("🗑️ Delete Selected Match"):
        before = len(matches)
        matches = matches[matches["match_id"] != int(del_mid)]
        write_csv_safe(matches, MATCHES_FILE)

        # Cascade delete player stats for that match
        stats = read_csv_safe(PLAYER_STATS_FILE)
        if not stats.empty:
            stats = stats[stats["match_id"].astype(int) != int(del_mid)]
            write_csv_safe(stats, PLAYER_STATS_FILE)

        st.success(f"Deleted {before - len(matches)} match record(s) and related player stats.")
        st.rerun()





def admin_player_stats_page():
    st.subheader("Add Player Stats per Match")

    matches = read_csv_safe(MATCHES_FILE)
    stats = read_csv_safe(PLAYER_STATS_FILE)
    players = read_csv_safe(PLAYERS_FILE)

    if matches.empty:
        st.info("Add a match first.")
        return

    m = matches.copy()
    m["date"] = pd.to_datetime(m["date"], errors="coerce").dt.date
    for c in ["our_score", "their_score"]:
        m[c] = pd.to_numeric(m[c], errors="coerce")

    finished = m[m["our_score"].notna() & m["their_score"].notna()].sort_values("date")
    if finished.empty:
        st.info("No finished matches yet. Add a match result first.")
        return

    player_options = players[players.get("active", True) == True]["name"].tolist() if not players.empty else []

    with st.form("add_stats"):
        col1, col2 = st.columns(2)
        with col1:
            mid = st.selectbox(
                "Match (finished only)",
                options=finished["match_id"].astype(int).tolist(),
                format_func=lambda x: match_label_from_id(x, finished)
            )
            player = st.selectbox("Player", options=player_options)
            position = st.selectbox("Position", ["GK","RB","CB","LB","RWB","LWB","CDM","CM","CAM","RM","LM","RW","LW","ST"])
        with col2:
            goals = st.number_input("Goals", 0, 10, 0)
            assists = st.number_input("Assists", 0, 10, 0)
            rating = st.number_input("Rating (0–10)", 0.0, 10.0, 7.0, step=0.1)
            y = st.number_input("Yellow cards", 0, 2, 0)
            r = st.number_input("Red cards", 0, 1, 0)
        submitted = st.form_submit_button("Save Stats", type="primary")

    if submitted:
        if not player:
            st.warning("Player is required.")
            return
        if mid not in finished["match_id"].astype(int).tolist():
            st.error("You can only add stats to finished matches.")
            return

        new_row = {
            "match_id": int(mid),
            "player_name": player,
            "position": position,
            "goals": int(goals),
            "assists": int(assists),
            "rating": round(float(rating), 1),
            "yellow_cards": int(y),
            "red_cards": int(r),
        }

        if not stats.empty:
            mask = (stats["match_id"].astype(int) == int(mid)) & (stats["player_name"] == player)
            stats = stats[~mask]

        stats = pd.concat([stats, pd.DataFrame([new_row])], ignore_index=True)
        write_csv_safe(stats, PLAYER_STATS_FILE)
        st.success("Stats saved (upserted).")

    st.divider()
    if not stats.empty:
        show = stats.sort_values(["match_id", "player_name"]).reset_index(drop=True)
        st.dataframe(show, use_container_width=True)
        with st.expander("Delete a stat row"):
            idx = st.number_input("Row index to delete (as shown)", 0, len(show) - 1, 0)
            if st.button("Delete row"):
                stats2 = show.drop(show.index[idx]).reset_index(drop=True)
                write_csv_safe(stats2, PLAYER_STATS_FILE)
                st.success("Deleted.")


def admin_players_crud_page():
    st.subheader("👤 Players – Add / Edit / Remove")
    players = read_csv_safe(PLAYERS_FILE)

    with st.form("add_player"):
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        with c1:
            name = st.text_input("Player Name")
        with c2:
            position = st.selectbox("Primary Position", ["GK","RB","CB","LB","RWB","LWB","CDM","CM","CAM","RM","LM","RW","LW","ST"])
        with c3:
            code = st.text_input("Login Code", placeholder="e.g. PL-010")
        with c4:
            active = st.checkbox("Active", value=True)
        submitted = st.form_submit_button("Add Player", type="primary")

    if submitted:
        if not name or not code:
            st.warning("Name and Code are required.")
        else:
            new_id = int(players.get("player_id", pd.Series([0])).max()) + 1 if not players.empty else 1
            new_row = {"player_id": new_id, "name": name, "position": position, "code": code, "active": bool(active)}
            players = pd.concat([players, pd.DataFrame([new_row])], ignore_index=True)
            write_csv_safe(players, PLAYERS_FILE)
            st.success(f"Added {name}.")
            st.rerun()

    st.divider()
    if players.empty:
        st.info("No players yet.")
        return

    st.caption("Current Roster")
    st.dataframe(players, use_container_width=True)

    with st.expander("Quick Edit / Delete"):
        names = players["name"].tolist()
        sel_name = st.selectbox("Select player", options=names)
        row = players[players["name"] == sel_name].iloc[0]
        positions_list = ["GK","RB","CB","LB","RWB","LWB","CDM","CM","CAM","RM","LM","RW","LW","ST"]
        new_name = st.text_input("Name", value=row["name"])
        new_pos = st.selectbox("Position", positions_list, index=positions_list.index(row["position"]))
        new_code = st.text_input("Code", value=str(row["code"]))
        new_active = st.checkbox("Active", value=bool(row.get("active", True)))
        colb1, colb2 = st.columns(2)
        with colb1:
            if st.button("Save Changes"):
                players.loc[players["name"] == sel_name, ["name", "position", "code", "active"]] = [new_name, new_pos, new_code, bool(new_active)]
                write_csv_safe(players, PLAYERS_FILE)
                st.success("Updated.")
                st.rerun()
        with colb2:
            if st.button("Delete Player"):
                players = players[players["name"] != sel_name]
                write_csv_safe(players, PLAYERS_FILE)
                st.success("Deleted.")
                st.rerun()

# -------------------------------
# TRAINING: Admin/Manager/Player
# -------------------------------
def admin_training_sessions_page():
    st.subheader("🏋️ Create / Manage Training Sessions")
    sessions = read_csv_safe(TRAINING_SESSIONS_FILE)

    with st.form("create_session"):
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            tr_date = st.date_input("Date", value=date.today())
        with c2:
            tr_time = st.time_input("Time", value=dtime(20, 0))
        with c3:
            title = st.text_input("Title", value="Team Training")
        loc = st.text_input("Location", value="Club Facility / Online")
        notes = st.text_area("Notes", value=" ")
        submitted = st.form_submit_button("Create Session", type="primary")

    if submitted:
        next_id = (sessions["session_id"].max() + 1) if not sessions.empty else 1
        new = {
            "session_id": int(next_id),
            "date": tr_date.strftime("%Y-%m-%d"),
            "time": tr_time.strftime("%H:%M"),
            "title": title,
            "location": loc,
            "notes": notes,
            "created_by": st.session_state.auth.get("name"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        sessions = pd.concat([sessions, pd.DataFrame([new])], ignore_index=True)
        write_csv_safe(sessions, TRAINING_SESSIONS_FILE)
        st.success("Training session created.")

    st.divider()
    if sessions.empty:
        st.info("No training sessions yet.")
        return

    st.caption("Upcoming & Past Sessions")
    try:
        sessions["dt"] = pd.to_datetime(sessions["date"] + " " + sessions["time"])
    except Exception:
        sessions["dt"] = pd.to_datetime(sessions["date"], errors="coerce")
    st.dataframe(sessions.drop(columns=["dt"]).sort_values(["date", "time"]), use_container_width=True)

    del_id = st.text_input("Delete session by session_id")
    if st.button("Delete Session"):
        if del_id.isdigit():
            before = len(sessions)
            sessions = sessions[sessions["session_id"] != int(del_id)]
            write_csv_safe(sessions, TRAINING_SESSIONS_FILE)
            att = read_csv_safe(TRAINING_ATTEND_FILE)
            att = att[att["session_id"] != int(del_id)] if not att.empty else att
            write_csv_safe(att, TRAINING_ATTEND_FILE)
            st.success(f"Deleted {before - len(sessions)} session(s) & related attendance.")
        else:
            st.warning("Enter a valid numeric session_id.")

def _attendance_color(val: str):
    if str(val).lower() == "yes":
        return "background-color: lightgreen; color: black;"
    if str(val).lower() == "no":
        return "background-color: lightcoral; color: white;"
    return ""

def manager_training_attendance_overview():
    st.subheader("📋 Training Attendance – Session Overview")
    sessions = read_csv_safe(TRAINING_SESSIONS_FILE)
    att = read_csv_safe(TRAINING_ATTEND_FILE)

    if sessions.empty:
        st.info("No training sessions.")
        return

    # pick a session
    sid = st.selectbox(
        "Select session",
        options=sessions["session_id"].astype(int),
        format_func=lambda s: f"{int(s)} | {sessions.loc[sessions['session_id']==int(s),'date'].values[0]} {sessions.loc[sessions['session_id']==int(s),'time'].values[0]} – {sessions.loc[sessions['session_id']==int(s),'title'].values[0]}"
    )

    sess = sessions[sessions["session_id"] == int(sid)].iloc[0]
    st.write(f"**{sess['date']} {sess['time']} – {sess['title']}**  @ {sess['location']}")
    st.caption(sess.get("notes",""))

    subset = att[att["session_id"] == int(sid)]
    if subset.empty:
        st.info("No attendance submitted yet.")
    else:
        table = subset[["player_name","status"]].sort_values("player_name").reset_index(drop=True)
        st.dataframe(table.style.applymap(_attendance_color, subset=["status"]), use_container_width=True)

        # quick counts
        y = (subset["status"].str.lower() == "yes").sum()
        n = (subset["status"].str.lower() == "no").sum()
        st.metric("Yes", y)
        st.metric("No", n)

    with st.expander("Download Attendance CSV"):
        st.download_button(
            "Download CSV",
            data=subset.to_csv(index=False).encode("utf-8"),
            file_name=f"attendance_session_{sid}.csv",
            mime="text/csv"
        )

def player_training_attendance_page(player_name: str):
    st.subheader("🏋️ Training Attendance (My Response)")
    sessions = read_csv_safe(TRAINING_SESSIONS_FILE)
    if sessions.empty:
        st.info("No training sessions scheduled yet.")
        return

    # upcoming only
    try:
        sessions["dt"] = pd.to_datetime(sessions["date"] + " " + sessions["time"])
    except Exception:
        sessions["dt"] = pd.to_datetime(sessions["date"], errors="coerce")
    upcoming = sessions[sessions["dt"] >= pd.Timestamp(date.today())].sort_values(["date","time"])
    if upcoming.empty:
        st.info("No upcoming training sessions.")
        return

    att = read_csv_safe(TRAINING_ATTEND_FILE)

    st.caption("Select your attendance for each upcoming session:")
    for _, row in upcoming.iterrows():
        sid = int(row["session_id"])
        key = f"att_{sid}"
        # existing choice
        existing = None
        if not att.empty:
            q = att[(att["session_id"]==sid) & (att["player_name"].str.lower()==player_name.lower())]
            if not q.empty:
                existing = q.iloc[0]["status"]
        col1, col2, col3 = st.columns([2,2,1])
        with col1:
            st.write(f"**{row['date']} {row['time']} – {row['title']}**  @ {row['location']}")
        with col2:
            choice = st.radio("Attend?", ["Yes","No"], horizontal=True, index=(["Yes","No"].index(existing) if existing in ["Yes","No"] else 0), key=key)
        with col3:
            if st.button("Save", key=f"save_{sid}"):
                if att.empty:
                    att = pd.DataFrame(columns=["session_id","date","player_name","status","timestamp"])
                mask = (att["session_id"]==sid) & (att["player_name"].str.lower()==player_name.lower())
                if mask.any():
                    att.loc[mask, ["status","timestamp","date"]] = [choice, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), row["date"]]
                else:
                    att = pd.concat([att, pd.DataFrame([{
                        "session_id": sid,
                        "date": row["date"],
                        "player_name": player_name,
                        "status": choice,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }])], ignore_index=True)
                write_csv_safe(att, TRAINING_ATTEND_FILE)
                st.success("Saved ✅")
                st.rerun()

    st.divider()
    st.subheader("📊 My Attendance Stats")
    mine = att[att["player_name"].str.lower()==player_name.lower()]
    if mine.empty:
        st.info("No responses yet.")
    else:
        pct = round((mine["status"].str.lower()=="yes").mean()*100, 1)
        st.metric("Attendance %", pct)
        st.dataframe(mine.sort_values(["date","timestamp"], ascending=False), use_container_width=True)

def admin_training_attendance_all():
    st.subheader("📈 Training Attendance – All Players & Sessions")
    att = read_csv_safe(TRAINING_ATTEND_FILE)
    sessions = read_csv_safe(TRAINING_SESSIONS_FILE)
    if att.empty or sessions.empty:
        st.info("No attendance yet.")
        return

    # Color table
    st.caption("Latest Attendance Records")
    show = att.sort_values("timestamp", ascending=False).copy()
    st.dataframe(show.style.applymap(_attendance_color, subset=["status"]), use_container_width=True)

    # Aggregates by player
    st.subheader("By Player – Attendance %")
    byp = att.groupby("player_name")["status"].apply(lambda s: round((s.str.lower()=="yes").mean()*100,1)).reset_index()
    byp.columns = ["player_name","attendance_%"]
    st.dataframe(byp.sort_values("attendance_%", ascending=False), use_container_width=True)

    # Aggregates by session
    st.subheader("By Session – Yes/No Counts")
    yes_counts = (att["status"].str.lower()=="yes").groupby(att["session_id"]).sum().rename("yes")
    no_counts  = (att["status"].str.lower()=="no").groupby(att["session_id"]).sum().rename("no")
    agg = pd.concat([yes_counts, no_counts], axis=1).fillna(0).astype(int).reset_index()
    agg = agg.merge(sessions[["session_id","date","time","title"]], on="session_id", how="left")
    st.dataframe(agg.sort_values(["date","time"]), use_container_width=True)

# -------------------------------
# MANAGER – Tactics (text) & Interactive Visual Board
# -------------------------------
FORMATIONS = ["4-3-3","4-2-3-1","4-4-2","3-5-2","3-4-3","5-2-1-2","4-1-2-1-2"]

def formation_layout(formation: str):
    def line(y, n, x_start=15, x_end=85):
        xs = list(pd.Series(range(n)).apply(lambda i: x_start + (x_end - x_start) * (i/(max(n-1,1)))))
        return [(x, y) for x in xs]

    layout = []
    if formation == "4-3-3":
        layout += [(10,50)]
        layout += [(25,20),(25,40),(25,60),(25,80)]
        layout += [(50,30),(50,50),(50,70)]
        layout += [(75,20),(75,50),(75,80)]
    elif formation == "4-2-3-1":
        layout += [(10,50)]
        layout += [(25,20),(25,40),(25,60),(25,80)]
        layout += [(45,40),(45,60)]
        layout += [(65,20),(65,50),(65,80)]
        layout += [(80,50)]
    elif formation == "4-4-2":
        layout += [(10,50)]
        layout += [(25,20),(25,40),(25,60),(25,80)]
        layout += [(50,20),(50,40),(50,60),(50,80)]
        layout += [(75,40),(75,60)]
    elif formation == "3-5-2":
        layout += [(10,50)]
        layout += [(25,30),(25,50),(25,70)]
        layout += [(50,20),(50,35),(50,65),(50,80),(50,50)]
        layout += [(75,40),(75,60)]
    elif formation == "3-4-3":
        layout += [(10,50)]
        layout += [(25,30),(25,50),(25,70)]
        layout += [(50,25),(50,50),(50,75),(50,10)]
        layout += [(75,25),(75,50),(75,75)]
    elif formation == "5-2-1-2":
        layout += [(10,50)]
        layout += [(25,15),(25,35),(25,50),(25,65),(25,85)]
        layout += [(50,40),(50,60)]
        layout += [(65,50)]
        layout += [(80,40),(80,60)]
    else:  # 4-1-2-1-2
        layout += [(10,50)]
        layout += [(25,20),(25,40),(25,60),(25,80)]
        layout += [(45,50)]
        layout += [(60,30),(60,70)]
        layout += [(75,50)]
        layout += [(85,40),(85,60)]

    labels = []
    if formation.startswith("4"):
        labels = ["GK","RB","RCB","LCB","LB"]
    elif formation.startswith("3"):
        labels = ["GK","RCB","CB","LCB"]
    elif formation.startswith("5"):
        labels = ["GK","RWB","RCB","CB","LCB","LWB"]

    while len(labels) < len(layout):
        if len(labels) < 6:
            labels.append("CDM")
        elif len(labels) < 10:
            labels.append("MID")
        else:
            labels.append("ATT")

    return [(labels[i] if i < len(labels) else f"POS{i}", layout[i][0], layout[i][1]) for i in range(len(layout))]

def draw_pitch(assignments_df: pd.DataFrame, title: str = "Tactics Board"):
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=100, line=dict(width=2))
    fig.add_shape(type="line", x0=50, y0=0, x1=50, y1=100)
    fig.add_shape(type="rect", x0=0, y0=18, x1=18, y1=82, line=dict(width=1))
    fig.add_shape(type="rect", x0=82, y0=18, x1=100, y1=82, line=dict(width=1))
    if not assignments_df.empty:
        fig.add_trace(go.Scatter(
            x=assignments_df["x"], y=assignments_df["y"], mode="markers+text",
            text=assignments_df["label"], textposition="middle right"
        ))
    fig.update_xaxes(range=[0,100], showgrid=False, visible=False)
    fig.update_yaxes(range=[0,100], showgrid=False, visible=False, scaleanchor="x", scaleratio=1)
    fig.update_layout(height=600, title=title, margin=dict(l=20,r=20,t=40,b=20))
    st.plotly_chart(fig, use_container_width=True)

def manager_tactics_text_page():
    st.subheader("Team Tactical Plan (Manager Only)")

    tactics = read_csv_safe(TACTICS_FILE)
    if not tactics.empty:
        st.write("**Current Saved Tactical Plans**")
        st.dataframe(
            tactics.drop(columns=["image_path"], errors="ignore"),
            use_container_width=True
        )
    else:
        st.info("No tactics saved yet.")

    st.divider()
    st.markdown("### 📝 Create / Update Tactical Plan")

    with st.form("tactics_form"):
        formation = st.selectbox("Formation", FORMATIONS)

        style_of_play = st.selectbox(
            "Overall Style",
            ["High Press & Quick Build-up", "Balanced Play", "Defensive & Counter", "Possession Focus"]
        )

        defensive_plan = st.text_area(
            "Defensive Strategy",
            "Maintain a compact defensive block. Press in packs when the ball enters our half. Fullbacks track wingers tightly."
        )

        offensive_plan = st.text_area(
            "Offensive Strategy",
            "Build from the back with short passes. Switch play quickly to stretch the opponent. Overlap fullbacks when chasing a goal."
        )

        key_players = st.text_area(
            "Key Player Instructions",
            """GK: Distribute short and initiate quick counters.
CBs: Hold the line, win aerial duels.
CM: Control tempo, dictate play.
Wingers: Cut inside, exploit half-spaces.
ST: Lead the press, stay central in attack."""
        )

        extra_notes = st.text_area(
            "Additional Notes",
            "Stay composed under pressure. Communicate constantly. Adjust tempo based on match situation."
        )

        submitted = st.form_submit_button("💾 Save Tactical Plan", type="primary")

    if submitted:
        new_row = {
            "formation": formation,
            "roles": key_players,
            "instructions": f"Style: {style_of_play}\n\nDefensive: {defensive_plan}\n\nOffensive: {offensive_plan}",
            "notes": extra_notes,
            "image_path": None,
            "updated_by": st.session_state.auth.get("name"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        tactics = pd.concat([tactics, pd.DataFrame([new_row])], ignore_index=True)
        write_csv_safe(tactics, TACTICS_FILE)
        st.success("Tactical plan saved ✅")



def manager_tactics_board_page():
    st.subheader("Interactive Tactics Board – Assign Players to Formation")

    # === Internal function: formation layout ===
    def formation_layout(formation: str):
        X_GK = 10
        X_DEF = 25
        X_DM  = 42
        X_CM  = 50
        X_AM  = 65
        X_FW  = 82
        X_W   = 75

        layouts = {
            "4-3-3": [
                ("GK",  X_GK, 50),
                ("RB",  X_DEF, 20), ("RCB", X_DEF, 40), ("LCB", X_DEF, 60), ("LB",  X_DEF, 80),
                ("RCM", 50, 40), ("CDM", 50, 50), ("LCM", 50, 60),
                ("RW",  X_W, 30), ("ST",  X_FW, 50), ("LW",  X_W, 70),
            ],
            "4-2-3-1": [
                ("GK",  X_GK, 50),
                ("RB",  X_DEF, 20), ("RCB", X_DEF, 40), ("LCB", X_DEF, 60), ("LB",  X_DEF, 80),
                ("RDM", X_DM, 45), ("LDM", X_DM, 55),
                ("RAM", X_AM, 35), ("CAM", X_AM, 50), ("LAM", X_AM, 65),
                ("ST",  X_FW, 50),
            ],
            "4-4-2": [
                ("GK",  X_GK, 50),
                ("RB",  X_DEF, 20), ("RCB", X_DEF, 40), ("LCB", X_DEF, 60), ("LB",  X_DEF, 80),
                ("RM",  X_CM, 30), ("RCM", X_CM, 45), ("LCM", X_CM, 55), ("LM",  X_CM, 70),
                ("RST", X_FW, 45), ("LST", X_FW, 55),
            ],
            "3-5-2": [
                ("GK",  X_GK, 50),
                ("RCB", 28, 40), ("CB", 28, 50), ("LCB", 28, 60),
                ("RM",  45, 30), 
                ("RDM", 50, 43), ("LDM", 50, 57), 
                ("CAM", X_AM, 50), 
                ("LM",  45, 70),
                ("RST", X_FW, 45), ("LST", X_FW, 55),
            ],
            "3-4-3": [
                ("GK",  X_GK, 50),
                ("RCB", 28, 40), ("CB", 28, 50), ("LCB", 28, 60),
                ("RM", 48, 30), ("RCM", 55, 45), ("LCM", 55, 55), ("LM", 48, 70),
                ("RW",  X_W, 35), ("ST",  X_FW, 50), ("LW",  X_W, 65),
            ],
            "5-2-1-2": [
                ("GK",  X_GK, 50),
                ("RWB", 25, 30), ("RCB", 20, 40), ("CB", 20, 50), ("LCB", 20, 60), ("LWB", 25, 70),
                ("RCM", 52, 45), ("LCM", 52, 55),
                ("CAM", 64, 50),
                ("RST", X_FW, 45), ("LST", X_FW, 55),
            ],
            "4-1-2-1-2": [
                ("GK",  X_GK, 50),
                ("RB",  X_DEF, 20), ("RCB", X_DEF, 40), ("LCB", X_DEF, 60), ("LB",  X_DEF, 80),
                ("CDM", 46, 50),
                ("RCM", 56, 42), ("LCM", 56, 58),
                ("CAM", 66, 50),
                ("RST", X_FW, 45), ("LST", X_FW, 55),
            ],
        }
        return layouts.get(formation, layouts["4-3-3"])

    # === Internal function: draw pitch ===
    def draw_pitch(assignments_df: pd.DataFrame, title: str = "Tactics Board"):
        fig = go.Figure()

        # Pitch outline & markings
        fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=100, line=dict(width=2))
        fig.add_shape(type="line", x0=50, y0=0, x1=50, y1=100, line=dict(width=1))
        fig.add_shape(type="rect", x0=0,  y0=18, x1=18,  y1=82, line=dict(width=1))
        fig.add_shape(type="rect", x0=82, y0=18, x1=100, y1=82, line=dict(width=1))
        fig.add_shape(type="rect", x0=0,  y0=36, x1=6,   y1=64, line=dict(width=1))
        fig.add_shape(type="rect", x0=94, y0=36, x1=100, y1=64, line=dict(width=1))
        fig.add_shape(type="circle", x0=50-9.15, y0=50-9.15, x1=50+9.15, y1=50+9.15, line=dict(width=1))

        if not assignments_df.empty:
            fig.add_trace(go.Scatter(
                x=assignments_df["x"],
                y=assignments_df["y"],
                mode="markers+text",
                marker=dict(size=18, color="blue", line=dict(width=2, color="white")),
                text=assignments_df["label"],
                textposition="top center",
                textfont=dict(color="white")
            ))

        fig.update_xaxes(range=[0, 100], showgrid=False, visible=False)
        fig.update_yaxes(range=[0, 100], showgrid=False, visible=False, scaleanchor="x", scaleratio=1)
        fig.update_layout(height=600, title=title, margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor="green")
        st.plotly_chart(fig, use_container_width=True)

    # === Main logic ===
    players = read_csv_safe(PLAYERS_FILE)
    if players.empty:
        st.info("No players in roster. Ask Admin to add players first.")
        return

    active_players = sorted(players[players.get("active", True) == True]["name"].dropna().astype(str).unique())

    formation = st.selectbox("Formation", FORMATIONS, key="board_formation")
    layout = formation_layout(formation)

    pos_df = read_csv_safe(TACTICS_POS_FILE)
    prev = pos_df[pos_df["formation"] == formation].copy()
    if not prev.empty:
        prev = prev.sort_values("updated_at").groupby("position").tail(1).set_index("position")

    st.caption("Each player can be assigned to **one** position only. Picked players disappear from other dropdowns.")

    assignments = []
    cols = st.columns(3)
    num_slots = len(layout)

    # Initialize defaults
    for idx, (pos_label, x, y) in enumerate(layout):
        key = f"board_sel::{formation}::{pos_label}::{idx}"
        if key not in st.session_state:
            default_player = None
            if isinstance(prev, pd.DataFrame) and not prev.empty and pos_label in prev.index:
                default_player = prev.loc[pos_label, "player_name"]
            if default_player not in active_players:
                default_player = "—"
            st.session_state[key] = default_player if default_player else "—"

    # Render dropdowns with live filtering
    for idx, (pos_label, x, y) in enumerate(layout):
        key = f"board_sel::{formation}::{pos_label}::{idx}"
        taken_elsewhere = {
            st.session_state.get(f"board_sel::{formation}::{layout[j][0]}::{j}", "—")
            for j in range(num_slots) if j != idx
        }
        taken_elsewhere.discard("—")
        current = st.session_state.get(key, "—")
        available = [p for p in active_players if (p not in taken_elsewhere) or (p == current)]
        options = ["—"] + available
        if current not in options:
            current = "—"
            st.session_state[key] = "—"
        with cols[idx % 3]:
            st.selectbox(pos_label, options=options, index=options.index(current), key=key)
        assignments.append({
            "formation": formation,
            "position": pos_label,
            "player_name": None if st.session_state[key] == "—" else st.session_state[key],
            "x": x, "y": y,
        })

    # Save & Clear buttons
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Save Board", use_container_width=True):
            chosen = [a["player_name"] for a in assignments if a["player_name"]]
            dupes = [p for p in set(chosen) if chosen.count(p) > 1]
            if dupes:
                st.error(f"Duplicate selections detected: {', '.join(sorted(dupes))}. Fix before saving.")
            else:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df = read_csv_safe(TACTICS_POS_FILE)
                df = df[df["formation"] != formation]
                for row in assignments:
                    row.update({"updated_by": st.session_state.auth.get("name"), "updated_at": now})
                df = pd.concat([df, pd.DataFrame(assignments)], ignore_index=True)
                write_csv_safe(df, TACTICS_POS_FILE)
                st.success("Board saved.")
                st.rerun()

    with c2:
        if st.button("🧹 Clear Board", type="secondary", use_container_width=True):
            for idx, (pos_label, _, _) in enumerate(layout):
                key = f"board_sel::{formation}::{pos_label}::{idx}"
                st.session_state[key] = "—"
            st.rerun()

    # Draw pitch with assignments
    show = pd.DataFrame(assignments)
    show["label"] = show.apply(lambda r: f"{r['position']} {r['player_name'] or ''}".strip(), axis=1)
    draw_pitch(show, title=f"{formation} – Assigned XI")





# -------------------------------
# PLAYER PAGES
# -------------------------------
def player_my_stats_page(player_name: str):
    st.subheader("My Stats")
    stats = read_csv_safe(PLAYER_STATS_FILE)
    if stats.empty:
        st.info("No stats yet.")
        return
    mine = stats[stats["player_name"].str.lower() == player_name.lower()]
    if mine.empty:
        st.info("No stats recorded for you yet.")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Matches", value=len(mine))
        st.metric("Goals", value=int(mine["goals"].sum()))
        st.metric("Assists", value=int(mine["assists"].sum()))
    with c2:
        st.metric("Avg Rating", value=round(mine["rating"].mean(), 2))
        st.metric("Yellows", value=int(mine["yellow_cards"].sum()))
        st.metric("Reds", value=int(mine["red_cards"].sum()))

    st.plotly_chart(px.line(mine.sort_values("match_id"), x="match_id", y="rating", markers=True, title="Ratings over Matches"), use_container_width=True)





def player_tactics_text_page():
    st.subheader("Team Tactical Plan")
    tactics = read_csv_safe(TACTICS_FILE)
    if tactics.empty:
        st.info("No tactical plan has been set yet.")
        return
    latest = tactics.sort_values("updated_at", ascending=False).iloc[0]
    st.write(f"**Formation:** {latest['formation']}")
    st.write(f"**Instructions:**\n{latest['instructions']}")
    st.write(f"**Key Player Roles:**\n{latest['roles']}")
    if latest.get("notes"):
        st.write(f"**Notes:**\n{latest['notes']}")
    st.caption(f"Last updated by {latest['updated_by']} on {latest['updated_at']}")

def player_tactics_board_page():
    st.subheader("Tactics Board – View Only")

    pos_df = read_csv_safe(TACTICS_POS_FILE)
    if pos_df.empty:
        st.info("No tactics board set yet.")
        return

    # Pick latest update
    latest_time = pos_df["updated_at"].max()
    latest = pos_df[pos_df["updated_at"] == latest_time].copy()
    if latest.empty:
        st.info("No tactics board found.")
        return

    formation = latest["formation"].iloc[0]
    st.write(f"**Formation:** {formation}")
    st.caption(f"Last updated by {latest['updated_by'].iloc[0]} on {latest_time}")

    # Prepare labels for the pitch
    latest["label"] = latest.apply(
        lambda r: f"{r['position']} {r['player_name'] or ''}".strip(),
        axis=1
    )

    # Draw pitch exactly like manager view
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=100, line=dict(width=2))
    fig.add_shape(type="line", x0=50, y0=0, x1=50, y1=100, line=dict(width=1))
    fig.add_shape(type="rect", x0=0,  y0=18, x1=18,  y1=82, line=dict(width=1))
    fig.add_shape(type="rect", x0=82, y0=18, x1=100, y1=82, line=dict(width=1))
    fig.add_shape(type="rect", x0=0,  y0=36, x1=6,   y1=64, line=dict(width=1))
    fig.add_shape(type="rect", x0=94, y0=36, x1=100, y1=64, line=dict(width=1))
    fig.add_shape(type="circle", x0=50-9.15, y0=50-9.15, x1=50+9.15, y1=50+9.15, line=dict(width=1))

    fig.add_trace(go.Scatter(
        x=latest["x"],
        y=latest["y"],
        mode="markers+text",
        marker=dict(size=18, color="blue", line=dict(width=2, color="white")),
        text=latest["label"],
        textposition="top center",
        textfont=dict(color="white")
    ))

    fig.update_xaxes(range=[0, 100], showgrid=False, visible=False)
    fig.update_yaxes(range=[0, 100], showgrid=False, visible=False, scaleanchor="x", scaleratio=1)
    fig.update_layout(height=600, title=f"{formation} – Assigned XI",
                      margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor="green")
    st.plotly_chart(fig, use_container_width=True)



# -------------------------------
# FAN & PUBLIC PAGES
# -------------------------------
def fan_public_page():
    st.subheader("Public Results & Fixtures")
    matches = read_csv_safe(MATCHES_FILE)
    if matches.empty:
        st.info("No matches yet.")
    else:
        st.write("**All Matches**")
        st.dataframe(matches.sort_values("date", ascending=True if hasattr(pd.DataFrame, "sort_values") else True), use_container_width=True)

    st.divider()
    st.subheader("Fan Wall (messages require admin approval)")
    name = st.session_state.auth.get("name", "Fan")
    msg = st.text_input("Leave a short message (max 200 chars)")
    if st.button("Post message"):
        if msg and len(msg) <= 200:
            wall = read_csv_safe(FANWALL_FILE)
            new = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": name, "message": msg, "approved": False}
            wall = pd.concat([wall, pd.DataFrame([new])], ignore_index=True)
            write_csv_safe(wall, FANWALL_FILE)
            st.success("Submitted! Waiting for admin approval.")
        else:
            st.warning("Please write a message under 200 characters.")

    wall = read_csv_safe(FANWALL_FILE)
    if not wall.empty:
        st.write("**Recent approved messages**")
        st.dataframe(wall[wall["approved"]==True].sort_values("timestamp", ascending=False), use_container_width=True)

# -------------------------------
# ADMIN: FAN WALL MODERATION & REPORTS
# -------------------------------
def admin_fanwall_moderation():
    st.subheader("Moderate Fan Wall")
    wall = read_csv_safe(FANWALL_FILE)
    if wall.empty:
        st.info("No messages yet.")
        return
    st.dataframe(wall, use_container_width=True)
    idx = st.number_input("Row index to toggle approval", 0, len(wall)-1, 0)
    if st.button("Toggle approval"):
        wall.loc[idx, "approved"] = not bool(wall.loc[idx, "approved"])
        write_csv_safe(wall, FANWALL_FILE)
        st.success("Toggled.")

def admin_reports_page():
    st.subheader("Auto Match Report Generator")
    matches = read_csv_safe(MATCHES_FILE)
    stats = read_csv_safe(PLAYER_STATS_FILE)
    if matches.empty:
        st.info("Add matches first.")
        return

    finished = matches[matches["our_score"].notna() & matches["their_score"].notna()]
    mid = st.selectbox("Select match", options=finished["match_id"].astype(int),
                   format_func=lambda x: match_label_from_id(x, finished))
    mrow = matches[matches["match_id"] == int(mid)].iloc[0]

    if st.button("Generate report"):
        subset = stats[stats["match_id"] == int(mid)]
        summary = [f"On {mrow['date']}, we played {mrow['opponent']} and the game ended {int(mrow['our_score'])}-{int(mrow['their_score'])} ({mrow['result']})."]
        if not subset.empty:
            top_scorers = subset[subset["goals"] > 0].sort_values("goals", ascending=False)
            if not top_scorers.empty:
                summary.append("Goals: " + ", ".join([f"{r.player_name} ({int(r.goals)})" for r in top_scorers.itertuples()]) + ".")
            top_ast = subset[subset["assists"] > 0].sort_values("assists", ascending=False)
            if not top_ast.empty:
                summary.append("Assists: " + ", ".join([f"{r.player_name} ({int(r.assists)})" for r in top_ast.itertuples()]) + ".")
            motm = subset.sort_values("rating", ascending=False).iloc[0]
            summary.append(f"MOTM: {motm['player_name']} (rating {motm['rating']:.1f}).")
        if str(mrow.get("notes", "")):
            summary.append(f"Notes: {mrow['notes']}")
        st.text_area("Generated Report", " ".join(summary), height=200)
# -------------------------------
# AUTO BEST XI
# -------------------------------
def page_best_xi():
    st.subheader("Auto Best XI (by average rating)")
    stats = read_csv_safe(PLAYER_STATS_FILE)
    if stats.empty:
        st.info("No stats yet.")
        return

    min_matches = st.number_input("Minimum matches played", 1, 50, 3)
    formation = st.selectbox("Formation", FORMATIONS)

    agg = stats.groupby(["player_name","position"]).agg(matches=("match_id","count"), avg_rating=("rating","mean")).reset_index()
    pool = agg[agg["matches"] >= int(min_matches)].sort_values("avg_rating", ascending=False)

    def pick(pos, n):
        return pool[pool["position"]==pos].head(n)

    selection = []
    if formation == "4-3-3":
        selection += [pick("GK",1), pick("RB",1), pick("LB",1), pick("CB",2), pick("CM",2), pick("CDM",1), pick("RW",1), pick("LW",1), pick("ST",1)]
    elif formation == "4-2-3-1":
        selection += [pick("GK",1), pick("RB",1), pick("LB",1), pick("CB",2), pick("CDM",2), pick("CAM",1), pick("RW",1), pick("LW",1), pick("ST",1)]
    elif formation == "4-4-2":
        selection += [pick("GK",1), pick("RB",1), pick("LB",1), pick("CB",2), pick("RM",1), pick("LM",1), pick("CM",2), pick("ST",2)]
    elif formation == "3-5-2":
        selection += [pick("GK",1), pick("CB",3), pick("CDM",1), pick("CM",2), pick("CAM",1), pick("ST",2)]
    elif formation == "3-4-3":
        selection += [pick("GK",1), pick("CB",3), pick("RM",1), pick("LM",1), pick("CM",2), pick("RW",1), pick("LW",1), pick("ST",1)]
    elif formation == "5-2-1-2":
        selection += [pick("GK",1), pick("RWB",1), pick("LWB",1), pick("CB",3), pick("CM",2), pick("CAM",1), pick("ST",2)]
    else:  # 4-1-2-1-2
        selection += [pick("GK",1), pick("RB",1), pick("LB",1), pick("CB",2), pick("CDM",1), pick("CM",2), pick("CAM",1), pick("ST",2)]

    valid_dfs = [x for x in selection if x is not None and not x.empty]
    sel_df = pd.concat(valid_dfs, ignore_index=True) if valid_dfs else pd.DataFrame()

    if sel_df.empty:
        st.info("Not enough data for this formation / filters.")
        return
    st.dataframe(sel_df.head(11), use_container_width=True)


def admin_delete_all_data():
    st.subheader("⚠ Danger Zone – Delete All Data")
    st.warning("This will permanently delete ALL players, matches, stats, tactics, training sessions, attendance, and fan wall data.")

    if st.checkbox("I understand this action cannot be undone"):
        if st.button("🗑 Delete Everything", type="primary"):
            try:
                # List of all CSV files
                files = [
                    PLAYERS_FILE,
                    MATCHES_FILE,
                    PLAYER_STATS_FILE,
                    TACTICS_FILE,
                    TACTICS_POS_FILE,
                    AVAIL_FILE,
                    TRAINING_SESSIONS_FILE,
                    TRAINING_ATTEND_FILE,
                    FANWALL_FILE
                ]
                for f in files:
                    if os.path.exists(f):
                        os.remove(f)
                ensure_csvs()  # recreate empty CSVs
                st.success("✅ All data deleted and reset to empty state.")
            except Exception as e:
                st.error(f"Error while deleting: {e}")


# -------------------------------
# ROUTER PER ROLE
# -------------------------------
def run_admin():
    render_header()
    st.sidebar.header("Admin Menu")
    page = st.sidebar.radio("Go to", [
    "Dashboard",
    "Matches",
    "Player Stats",
    "Players (Add/Edit)",
    "Training Sessions",
    "Training Attendance (All)",
    "Fan Wall Moderation",
    "Auto Reports",
    "Auto Best XI",
    "⚠ Danger Zone (Delete All Data)"
])


    if page == "Dashboard":
        page_dashboard()
    elif page == "Matches":
        admin_matches_page()
    elif page == "Player Stats":
        admin_player_stats_page()
    elif page == "Players (Add/Edit)":
        admin_players_crud_page()
    elif page == "Training Sessions":
        admin_training_sessions_page()
    elif page == "Training Attendance (All)":
        admin_training_attendance_all()
    elif page == "Fan Wall Moderation":
        admin_fanwall_moderation()
    elif page == "Auto Reports":
        admin_reports_page()
    elif page == "Auto Best XI":
        page_best_xi()
    elif page == "⚠ Danger Zone (Delete All Data)":
     admin_delete_all_data()


def run_manager():
    render_header()
    st.sidebar.header("Manager Menu")
    page = st.sidebar.radio("Go to", [
        "Dashboard",
        "Tactics – Text",
        "Tactics – Visual Board",
        "Training Attendance (Session View)",
        "Auto Best XI",
    ])
    if page == "Dashboard":
        page_dashboard()
    elif page == "Tactics – Text":
        manager_tactics_text_page()
    elif page == "Tactics – Visual Board":
        manager_tactics_board_page()
    elif page == "Training Attendance (Session View)":
        manager_training_attendance_overview()
    elif page == "Auto Best XI":
        page_best_xi()

def run_player():
    render_header()
    st.sidebar.header("Player Menu")
    page = st.sidebar.radio("Go to", [
    "Dashboard",
    "My Stats",
    "Training Attendance",
    "Tactics – Text (view)",
    "Tactics – Visual Board (view)",
    "Auto Best XI (view)"
])

    if page == "Dashboard":
        page_dashboard()
    elif page == "My Stats":
        player_my_stats_page(st.session_state.auth.get("name","Player"))
    elif page == "Training Attendance":
        player_training_attendance_page(st.session_state.auth.get("name","Player"))
    elif page == "Auto Best XI (view)":
        page_best_xi()
    elif page == "Tactics – Text (view)":
     player_tactics_text_page()
    elif page == "Tactics – Visual Board (view)":
     player_tactics_board_page()
    

def run_fan():
    render_header()
    st.sidebar.header("Fan Menu")
    page = st.sidebar.radio("Go to", ["Dashboard","Public Results & Fan Wall"])
    if page == "Dashboard":
        page_dashboard()
    elif page == "Public Results & Fan Wall":
        fan_public_page()

# -------------------------------
# MAIN
# -------------------------------
def main():
    ensure_dirs()
    ensure_csvs()
    init_session()

    # Intro / Login routing
    if st.session_state.page == "intro" and st.session_state.auth["role"] is None:
        intro_page()
        return
    elif st.session_state.page == "login" and st.session_state.auth["role"] is None:
        login_ui()
        return
    elif st.session_state.page == "fan_public_only" and st.session_state.auth["role"] == "fan":
        # Minimal fan public preview route
        render_header()
        fan_public_page()
        return

    # Authenticated routes
    role = st.session_state.auth["role"]
    if role == "admin":
        run_admin()
    elif role == "manager":
        run_manager()
    elif role == "player":
        run_player()
    elif role == "fan":
        run_fan()
    else:
        # Fallback -> Intro
        logout()

if __name__ == "__main__":
    main()