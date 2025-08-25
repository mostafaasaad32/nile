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
from streamlit_cookies_manager import EncryptedCookieManager
import os
import json
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
from supabase import create_client, Client
import time
import httpx
from postgrest.exceptions import APIError
import google.generativeai as genai
import io 
# -------------------------------
# CONFIG (set once, top-level)
# -------------------------------
# -------------------------------
# PAGE CONFIG (mobile-first)
# -------------------------------
st.set_page_config(page_title="Nile SC Manager", page_icon="assets/images/icon.png", layout="centered")

LOGO_URL = "assets/images/icon.png"

# -------------------------------
# GLOBAL STYLES (Desktop + Mobile)
# -------------------------------
appINTRO_CSS = """
<style>
:root {
  --glass-bg: rgba(255,255,255,0.08);
  --glass-brd: rgba(255,255,255,0.18);
  --accent: #1e3a8a;
  --accent-2: #0ea5e9;
  --button-accent: #22c55e;
}

/* Background */
html, body, [data-testid="stAppViewContainer"] {
  background: linear-gradient(180deg, #0b1220, #0d1b2a) !important;
  color: white !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
  background-color: #0b1220 !important;
}
[data-testid="stSidebar"] * {
  color: #ffffff !important;
  font-weight: 500;
}

/* Buttons */
.stButton > button {
  background: linear-gradient(90deg, var(--button-accent), var(--accent-2)) !important;
  color: white !important;
  border-radius: 12px !important;
  border: none !important;
  font-weight: bold !important;
  padding: 10px 14px !important;
}
.stButton > button:hover {
  opacity: 0.9 !important;
}
[data-testid="stSidebar"] .stButton > button {
  background-color: #dc2626 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background-color: #b91c1c !important;
}

/* Glass Cards */
.glass {
  background: var(--glass-bg);
  border: 1px solid var(--glass-brd);
  box-shadow: 0 10px 30px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.06);
  backdrop-filter: blur(10px);
  border-radius: 18px;
  padding: 16px;
}

/* Typography */
.title {
  font-weight: 800;
  font-size: 32px;
  line-height: 1.2;
  text-shadow: 0 6px 20px rgba(34,197,94,.25);
}
.subtitle {
  font-size: 15px;
  opacity: 0.9;
}

/* ---------------- MOBILE ---------------- */
@media (max-width: 600px) {
  .title { font-size: 22px !important; }
  .subtitle { font-size: 13px !important; }
  img { max-width: 120px !important; height: auto !important; }
  .stButton > button { font-size: 14px !important; padding: 8px 10px !important; }
  .glass { padding: 12px !important; border-radius: 14px !important; }
}
</style>
"""
st.markdown(appINTRO_CSS, unsafe_allow_html=True)







# =======================================
# NILES APP (with Supabase integration)
# =======================================



# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(
    page_title="Nile SC Manager",
    page_icon="⚽",
    layout="wide"
)

DATA_DIR = "data"
UPLOADS_DIR = "uploads"

# File constants
MATCHES_FILE = os.path.join(DATA_DIR, "matches.csv")
PLAYER_STATS_FILE = os.path.join(DATA_DIR, "player_stats.csv")
TACTICS_FILE = os.path.join(DATA_DIR, "tactics.csv")
TACTICS_POS_FILE = os.path.join(DATA_DIR, "tactics_positions.csv")
AVAIL_FILE = os.path.join(DATA_DIR, "availability.csv")
FANWALL_FILE = os.path.join(DATA_DIR, "fan_wall.csv")
PLAYERS_FILE = os.path.join(DATA_DIR, "players.csv")
TRAINING_SESSIONS_FILE = os.path.join(DATA_DIR, "training_sessions.csv")
TRAINING_ATTEND_FILE = os.path.join(DATA_DIR, "training_attendance.csv")

# -------------------------------
# DATA LAYER HELPERS (CSV + Supabase bridge)
# -------------------------------
PATH_TO_TABLE = {
    MATCHES_FILE: "matches",
    PLAYER_STATS_FILE: "player_stats",
    TACTICS_FILE: "tactics",
    TACTICS_POS_FILE: "tactics_positions",
    AVAIL_FILE: "availability",
    FANWALL_FILE: "fan_wall",
    PLAYERS_FILE: "players",
    TRAINING_SESSIONS_FILE: "training_sessions",
    TRAINING_ATTEND_FILE: "training_attendance",
}

USE_SUPABASE = True

@st.cache_resource
def _supabase_client() -> Client:
    url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = (
        st.secrets.get("SUPABASE_KEY")
        or st.secrets.get("SUPABASE_SERVICE_ROLE_KEY")  # 👈 added
        or os.getenv("SUPABASE_KEY")
        or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    )

    if not url or not key:
        st.error("❌ Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_KEY / SUPABASE_SERVICE_ROLE_KEY.")
        raise KeyError("Missing Supabase credentials")

    return create_client(url, key)

@st.cache_resource
def _gemini_client():
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    return genai.GenerativeModel("gemini-1.5-flash")

def _table_for_path(path: str) -> str:
    if path not in PATH_TO_TABLE:
        raise ValueError(f"No Supabase table mapping for {path}")
    return PATH_TO_TABLE[path]

def _df_to_rows(df: pd.DataFrame):
    return json.loads(df.where(pd.notnull(df), None).to_json(orient="records"))

def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)

def ensure_csvs():
    if USE_SUPABASE:
        return
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
            {"player_id":1, "name":"Player1", "position":"ST", "code":"PL-001", "active":True},
            {"player_id":2, "name":"Player2", "position":"CM", "code":"PL-002", "active":True},
            {"player_id":3, "name":"Player3", "position":"CB", "code":"PL-003", "active":True},
        ])
        seed.to_csv(PLAYERS_FILE, index=False)
    if not os.path.exists(TRAINING_SESSIONS_FILE):
        pd.DataFrame(columns=["session_id","date","time","title","location","notes","created_by","created_at"]).to_csv(TRAINING_SESSIONS_FILE, index=False)
    if not os.path.exists(TRAINING_ATTEND_FILE):
        pd.DataFrame(columns=["session_id","date","player_name","status","timestamp"]).to_csv(TRAINING_ATTEND_FILE, index=False)

# Expected columns per table based on your schema
EXPECTED_COLUMNS = {
    "players": ["player_id", "name", "position", "code", "active"],
    "matches": ["match_id", "date", "opponent", "our_score", "their_score", "result", "notes"],
    "player_stats": [
        "id", "match_id", "player_name", "position", "goals", "assists",
        "rating", "yellow_cards", "red_cards"
    ],
    "tactics": ["id", "formation", "roles", "instructions", "notes", "image_path", "updated_by", "updated_at"],
    "tactics_positions": ["id", "formation", "position", "player_name", "x", "y", "updated_by", "updated_at"],
    "availability": ["id", "date", "player_name", "availability"],
    "training_sessions": ["session_id", "date", "time", "title", "location", "notes", "created_by", "created_at"],
    "training_attendance": ["id", "session_id", "date", "player_name", "status", "timestamp"],
    "fan_wall": ["id", "timestamp", "user", "message", "approved"],
}

def read_csv_safe(path: str, retries: int = 3, delay: float = 1.0) -> pd.DataFrame:
    """Read from Supabase with retries, fallback to local CSV if Supabase fails."""
    table = _table_for_path(path)
    sb = _supabase_client()

    attempt = 0
    while attempt < retries:
        try:
            resp = sb.table(table).select("*").execute()
            if resp.data:
                df = pd.DataFrame(resp.data)

                # Normalize dates
                if "date" in df.columns:
                    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

                return df
            else:
                return pd.DataFrame(columns=EXPECTED_COLUMNS.get(table, []))

        except (httpx.ReadError, httpx.RemoteProtocolError, APIError) as e:
            attempt += 1
            if attempt < retries:
                time.sleep(delay * attempt)  # exponential backoff
                continue
            else:
                st.warning(f"⚠️ Supabase read failed after {retries} attempts: {e}")
                # fallback to local CSV
                if os.path.exists(path):
                    try:
                        return pd.read_csv(path)
                    except Exception:
                        return pd.DataFrame(columns=EXPECTED_COLUMNS.get(table, []))
                return pd.DataFrame(columns=EXPECTED_COLUMNS.get(table, []))




def write_csv_safe(df: pd.DataFrame, path: str):
    """Safely write a dataframe to Supabase.
       - Deletes missing rows based on primary keys
       - Skips auto-increment IDs where needed
       - Ensures correct types before upsert
    """
    sb = _supabase_client()
    table = _table_for_path(path)

    auto_ids = {
        "player_stats": ["id"],
        "tactics": ["id"],
        "tactics_positions": ["id"],
        "availability": ["id"],
        "training_attendance": ["id"],
        "fan_wall": ["id"],
    }
    cols_to_skip = auto_ids.get(table, [])
    safe_df = df.drop(columns=[c for c in cols_to_skip if c in df.columns], errors="ignore")

    # 🔧 Ensure proper date type
    if "date" in safe_df.columns:
        safe_df["date"] = pd.to_datetime(safe_df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

    # 🔧 Force integer columns to real ints
    int_columns = {
        "players": ["player_id"],
        "matches": ["match_id", "our_score", "their_score"],
        "player_stats": ["match_id", "goals", "assists", "yellow_cards", "red_cards"],
        "tactics_positions": ["x", "y"],
        "training_sessions": ["session_id"],
        "training_attendance": ["session_id"],
    }
    if table in int_columns:
        for col in int_columns[table]:
            if col in safe_df.columns:
                safe_df[col] = pd.to_numeric(safe_df[col], errors="coerce").dropna().astype("Int64")
                safe_df[col] = safe_df[col].astype(object).where(safe_df[col].notnull(), None)

    # Convert to rows
    rows = _df_to_rows(safe_df)
    if not rows:
        return

    # DELETE strategy (same as before, per table type)
    if table == "players":
        current_ids = [r["player_id"] for r in rows if r.get("player_id") is not None]
        sb.table(table).delete().not_.in_("player_id", current_ids).execute()

    elif table == "matches":
        current_ids = [r["match_id"] for r in rows if r.get("match_id") is not None]
        sb.table(table).delete().not_.in_("match_id", current_ids).execute()

    elif table == "training_sessions":
        current_ids = [r["session_id"] for r in rows if r.get("session_id") is not None]
        sb.table(table).delete().not_.in_("session_id", current_ids).execute()

    elif table == "player_stats":
        sb.table(table).delete().neq("match_id", -1).execute()

    elif table in ["tactics", "tactics_positions", "availability", "training_attendance", "fan_wall"]:
        sb.table(table).delete().neq("id", -1).execute()

    # UPSERT in chunks
    CHUNK = 500
    for i in range(0, len(rows), CHUNK):
        sb.table(table).upsert(rows[i:i+CHUNK]).execute()


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
# AUTH & SESSION
# -------------------------------
cookies = EncryptedCookieManager(prefix="nile_app_", password="super-secret-key")  # change key!
if not cookies.ready():
    st.stop()

def init_session():
    if "auth" not in st.session_state:
        # only try to read cookies if ready
        if cookies.ready() and cookies.get("role") and cookies.get("name"):
            st.session_state.auth = {
                "role": cookies.get("role"),
                "name": cookies.get("name"),
            }
        else:
            st.session_state.auth = {"role": None, "name": None}

    if "page" not in st.session_state:
        st.session_state.page = "intro"
def save_login(role, name):
    st.session_state.auth = {"role": role, "name": name}
    cookies["role"] = role
    cookies["name"] = name
    cookies.save()

def logout():
    st.session_state.auth = {"role": None, "name": None}
    st.session_state.page = "intro"
    cookies["role"] = ""
    cookies["name"] = ""
    cookies.save()
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
    <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;height:80vh;text-align:center;'>
        <img src='{LOGO_URL}'
             style='width:160px;height:auto;animation:fadeIn 2s ease-in-out;'>
        <h1 class="title" style='margin-top:15px;'>Nile Esports</h1>
        <p class="subtitle">One Club. One Heartbeat. 🖤💚</p>
    </div>
    <style>
        @keyframes fadeIn {{ from {{opacity:0;}} to {{opacity:1;}} }}
        @media (max-width:600px){{
            img {{ max-width:120px !important; }}
            .title {{ font-size:22px !important; }}
            .subtitle {{ font-size:14px !important; }}
        }}
    </style>
    """, unsafe_allow_html=True)

    # ✅ On mobile → stack buttons vertically (no columns)
    if st.button("🚀 Enter the Hub", use_container_width=True):
        st.session_state.page = "login"
        st.rerun()

    if st.button("👀 View Public Fan Wall", use_container_width=True):
        save_login("fan", "Guest")
        st.session_state.page = "fan_public_only"
        st.balloons()
        st.rerun()


# -------------------------------
# LOGIN PAGE
# -------------------------------
def login_ui():
    # Branded Login Card
    st.markdown(f"""
    <div class='glass card' style='padding:24px;max-width:380px;margin:auto;text-align:center;'>
        <img src='{LOGO_URL}' style='width:90px;height:auto;margin-bottom:10px;'>
        <h2 style='margin:0;'>Sign In</h2>
        <p class="small" style="margin:.3rem 0 1rem 0;">Choose your role and use your access code</p>
    </div>
    """, unsafe_allow_html=True)

    role = st.selectbox("Select your role", ["Admin", "Manager", "Player", "Fan"])
    name = st.text_input("Your name")
    code_required = role != "Fan"
    code = st.text_input(
        "Access code" if code_required else "Access code (not required)",
        type="password", disabled=not code_required
    )

    # ✅ Stack buttons full-width (better for thumbs on mobile)
    if st.button("Enter", type="primary", use_container_width=True):
        if not name:
            st.warning("Please enter your name.")
            return

        if role == "Fan":
            save_login("fan", name)
            st.success(f"Welcome, {name}! You're logged in as Fan.")
            st.balloons()
            st.rerun()

        elif role == "Admin":
            valid = ROLE_CODES.get("admin", {}).get(name)
            if valid and code == valid:
                save_login("admin", name)
                st.success("Welcome, Admin!")
                st.balloons()
                st.rerun()
            else:
                st.error("Invalid admin name or code.")

        elif role == "Manager":
            valid = ROLE_CODES.get("manager", {}).get(name)
            if valid and code == valid:
                save_login("manager", name)
                st.success("Welcome, Manager!")
                st.balloons()
                st.rerun()
            else:
                st.error("Invalid manager name or code.")

        elif role == "Player":
            if validate_player_login(name, code):
                save_login("player", name)
                st.success(f"Welcome, {name}! Let's ball.")
                st.balloons()
                st.rerun()
            else:
                st.error("Invalid player name or code.")

    if st.button("⬅ Back to Intro", use_container_width=True):
        st.session_state.page = "intro"
        st.rerun()


# -------------------------------
# DASHBOARD
# -------------------------------

def safe_int(val, default=0):
    try:
        if val is None or str(val).strip() == "" or str(val).lower() == "nan":
            return default
        return int(val)
    except Exception:
        return default
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
                      value=f"{safe_int(lm.get('our_score'))}-{safe_int(lm.get('their_score'))}",
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
    st.subheader("⚽ Matches")

    tab1, tab2, tab3 = st.tabs(["➕ Add Upcoming", "✅ Add Result", "📋 All Matches"])

    matches = read_csv_safe(MATCHES_FILE)

    # ---------------- TAB 1: Add Upcoming Match ----------------
    with tab1:
        with st.form("add_upcoming"):
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
                st.warning("Match must be today or later.")
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
                st.success("Upcoming match added ✅")
                st.rerun()

    # ---------------- TAB 2: Add Result ----------------
    with tab2:
        m2 = matches.copy()
        m2["date"] = pd.to_datetime(m2["date"], errors="coerce").dt.date
        unfinished = m2[m2["our_score"].isna() | m2["their_score"].isna()].sort_values("date")

        if unfinished.empty:
            st.info("No upcoming matches waiting for a result.")
        else:
            with st.form("add_result"):
                mid = st.selectbox(
                    "Match to finalize",
                    options=unfinished["match_id"].astype(int).tolist(),
                    format_func=lambda x: match_label_from_id(x, unfinished)
                )
                c1, c2, c3 = st.columns(3)
                with c1: our = st.number_input("Our score", 0, 99, 0)
                with c2: their = st.number_input("Their score", 0, 99, 0)
                with c3:
                    notes2 = st.text_area("Notes", value=str(
                        unfinished.loc[unfinished["match_id"] == int(mid), "notes"].values[0]
                    ))
                submit_res = st.form_submit_button("Save Result", type="primary")

            if submit_res:
                res = calc_result(int(our), int(their))
                matches.loc[matches["match_id"] == int(mid),
                            ["our_score", "their_score", "result", "notes"]] = [
                    int(our), int(their), res, notes2
                ]
                write_csv_safe(matches, MATCHES_FILE)
                st.success("Result saved ✅")
                st.rerun()

    # ---------------- TAB 3: View All Matches ----------------
    with tab3:
        if matches.empty:
            st.info("No matches yet.")
        else:
            st.dataframe(matches.sort_values("date", ascending=False), use_container_width=True)
            del_mid = st.selectbox(
                "Delete match",
                options=matches["match_id"].astype(int).tolist(),
                format_func=lambda x: match_label_from_id(x, matches)
            )
            if st.button("🗑️ Delete Selected Match"):
                sb = _supabase_client()
                sb.table("player_stats").delete().eq("match_id", int(del_mid)).execute()
                sb.table("matches").delete().eq("match_id", int(del_mid)).execute()
                st.success("Match and stats deleted ✅")
                st.rerun()








def admin_player_stats_page():
    st.header("📊 Player Stats")

    stats = _supabase_client().table("player_stats").select("*").execute()
    df = pd.DataFrame(stats.data) if stats.data else pd.DataFrame()

    if df.empty:
        st.info("No player stats available yet.")
        return

    st.dataframe(df)

    # Select a row to delete
    selected = st.selectbox(
        "Select stat row to delete",
        df.apply(lambda r: f"ID {r['id']} - {r['player_name']} (Match {r['match_id']})", axis=1)
    )

    if st.button("🗑️ Delete Selected Stat"):
        row_id = int(selected.split(" ")[1])  # extract ID
        try:
            _supabase_client().table("player_stats").delete().eq("id", row_id).execute()
            st.success("✅ Stat deleted")

            # ⚡️ Force refresh so UI updates (even if last row was deleted)
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed to delete stat: {e}")

def delete_player_and_stats(player_id: int, player_name: str):
    """Delete a player and all their stats from Supabase + local CSV fallback."""
    sb = _supabase_client()

    # 1. Delete stats first
    try:
        sb.table("player_stats").delete().eq("player_id", player_id).execute()
    except Exception as e:
        st.warning(f"⚠️ Could not delete stats for {player_name}: {e}")

    # 2. Delete the player
    try:
        sb.table("players").delete().eq("player_id", player_id).execute()
    except Exception as e:
        st.error(f"❌ Could not delete player {player_name}: {e}")


def admin_players_crud_page():
    st.subheader("👤 Players – Add / Edit / Remove")
    players = read_csv_safe(PLAYERS_FILE)

    # ---------------- Add Player ----------------
    with st.form("add_player"):
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        with c1:
            name = st.text_input("Player Name")
        with c2:
            position = st.selectbox(
                "Primary Position",
                ["GK","RB","CB","LB","RWB","LWB","CDM","CM","CAM","RM","LM","RW","LW","ST"]
            )
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

            new_row = {
                "player_id": new_id,
                "name": name,
                "position": position,
                "code": code,
                "active": bool(active)
            }
            players = pd.concat([players, pd.DataFrame([new_row])], ignore_index=True)
            write_csv_safe(players, PLAYERS_FILE)
            st.success(f"Added {name}.")
            st.rerun()

    st.divider()

    # ---------------- Current Players ----------------
    if players.empty:
        st.info("No players yet.")
        return

    st.caption("Current Roster")

    for _, row in players.iterrows():
        cols = st.columns([3, 2, 2, 2])
        with cols[0]:
            st.write(f"**{row['name']}**")
        with cols[1]:
            st.write(row["position"])
        with cols[2]:
            st.write(row["code"])
        with cols[3]:
            st.write("✅ Active" if row["active"] else "❌ Inactive")

    st.divider()

    # ---------------- Edit / Delete ----------------
    with st.expander("Quick Edit / Delete"):
        names = players["name"].tolist()
        sel_name = st.selectbox("Select player", options=names)
        row = players[players["name"] == sel_name].iloc[0]

        positions_list = ["GK","RB","CB","LB","RWB","LWB","CDM","CM","CAM","RM","LM","RW","LW","ST"]
        current_pos = str(row["position"]).upper()
        pos_index = positions_list.index(current_pos) if current_pos in positions_list else 0

        new_name = st.text_input("Name", value=row["name"])
        new_pos = st.selectbox("Position", positions_list, index=pos_index)
        new_code = st.text_input("Code", value=str(row["code"]))
        new_active = st.checkbox("Active", value=bool(row.get("active", True)))

        colb1, colb2 = st.columns(2)
        with colb1:
            if st.button("Save Changes"):
                players.loc[players["name"] == sel_name, ["name", "position", "code", "active"]] = [
                    new_name, new_pos, new_code, bool(new_active)
                ]
                write_csv_safe(players, PLAYERS_FILE)
                st.success("Updated.")
                st.rerun()

        with colb2:
            if st.button("Delete Player"):
                delete_player_and_stats(int(row["player_id"]), sel_name)  # deletes stats first
                players = players[players["name"] != sel_name]
                if players.empty:
                    players = pd.DataFrame(columns=["player_id","name","position","code","active"])
                write_csv_safe(players, PLAYERS_FILE)
                st.success(f"Deleted {sel_name} and all their stats.")
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



# ---------------- Extract Player Stats ----------------
import google.generativeai as genai
import json
import pandas as pd

# ---------------- Gemini Setup ----------------
@st.cache_resource
def _gemini_client():
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    return genai.GenerativeModel("gemini-1.5-flash")

# ---------------- Extract Player Stats ----------------
import base64

def extract_player_stats(image_file) -> pd.DataFrame:
    """
    Use Gemini to extract per-player stats from an uploaded image.
    Expected columns: player_name, rating, goals, assists
    Returns a pandas DataFrame.
    """
    model = _gemini_client()

    prompt = """
    You are a data extractor. The image shows football match stats in table format.
    Extract the data as JSON array of objects with exactly these keys:
    - player_name (string)
    - rating (float or int)
    - goals (int)
    - assists (int)

    Example output:
    [
      {"player_name":"Mo Salah","rating":8.7,"goals":2,"assists":1},
      {"player_name":"Amr El Solia","rating":7.2,"goals":0,"assists":1}
    ]

    Return ONLY valid JSON without extra commentary.
    """

    import base64
    image_bytes = image_file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    image_part = {
        "mime_type": image_file.type,
        "data": image_base64
    }

    response = model.generate_content(
        [
            {"text": prompt},
            {"inline_data": image_part}
        ],
        generation_config={"response_mime_type": "application/json"}
    )

    try:
        stats_list = json.loads(response.text)
        df = pd.DataFrame(stats_list)

        # Normalize names in case Gemini returns "name" instead of "player_name"
        rename_map = {"name": "player_name", "player": "player_name"}
        df = df.rename(columns=rename_map)

        # Ensure required cols exist
        for col in ["player_name", "rating", "goals", "assists"]:
            if col not in df.columns:
                df[col] = None

        return df[["player_name", "rating", "goals", "assists"]]

    except Exception as e:
        st.error(f"Parsing error: {e}")
        return pd.DataFrame(columns=["player_name", "rating", "goals", "assists"])



    
def admin_upload_player_stats_page():
    st.title("📸 Upload Player Stats from Photo")

    # ✅ Fetch matches
    matches = _supabase_client().table("matches").select("match_id, opponent, date").execute()
    match_options = [f'{m["match_id"]} - {m["opponent"]} ({m["date"]})' for m in matches.data] if matches.data else []

    if not match_options:
        st.warning("⚠️ No matches found. Please add a match first in the Matches page.")
        return

    selected_match = st.selectbox("Select Match", match_options)
    match_id = int(selected_match.split(" - ")[0])

    # ✅ Fetch players
    players = _supabase_client().table("players").select("player_id, name").execute()
    players_df = pd.DataFrame(players.data) if players.data else pd.DataFrame(columns=["player_id", "name"])

    img_file = st.file_uploader("Upload stats photo", type=["jpg", "jpeg", "png"])
    if img_file:
        st.image(img_file, caption="Uploaded stats image", use_container_width=True)

        if st.button("Extract Stats with Gemini"):
            with st.spinner("Extracting stats..."):
                df = extract_player_stats(img_file)  # Your existing extraction function

            if df.empty:
                st.error("❌ No stats extracted. Try with a clearer image.")
                return

            st.success("✅ Stats extracted successfully!")
            st.dataframe(df)

            # Match extracted names to players list
            merged = df.merge(players_df, left_on="player_name", right_on="name", how="left")

            # Warn about unknown players
            unknown = merged[merged["player_id"].isna()]
            if not unknown.empty:
                st.warning(f"⚠️ These players are not in the squad list: {unknown['player_name'].tolist()}")

            # Only keep rows with valid player IDs
            valid_rows = merged.dropna(subset=["player_id"])

            # Insert/update each row in Supabase
            for _, row in valid_rows.iterrows():
                try:
                    # Check if stats for this player and match already exist
                    existing = _supabase_client().table("player_stats") \
                        .select("id") \
                        .eq("match_id", match_id) \
                        .eq("player_id", int(row["player_id"])) \
                        .execute()

                    if existing.data:
                        # Update existing row
                        _supabase_client().table("player_stats").update({
                            "rating": row.get("rating"),
                            "goals": row.get("goals"),
                            "assists": row.get("assists"),
                            "position": "N/A"
                        }).eq("match_id", match_id).eq("player_id", int(row["player_id"])).execute()
                    else:
                        # Insert new row
                        _supabase_client().table("player_stats").insert({
                            "match_id": match_id,
                            "player_id": int(row["player_id"]),
                            "player_name": row.get("player_name"),
                            "rating": row.get("rating"),
                            "goals": row.get("goals"),
                            "assists": row.get("assists"),
                            "position": "N/A"
                        }).execute()

                except Exception as e:
                    st.error(f"❌ Failed to save row for {row.get('player_name')}: {e}")

            st.success("📤 Stats saved/updated in Supabase!")







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


import plotly.express as px
import streamlit as st

def player_my_stats_page(player_name: str):
    st.subheader("📊 My Stats")

    players = read_csv_safe(PLAYERS_FILE)
    player = players[players["name"].str.lower() == player_name.lower()].iloc[0]

    stats = read_csv_safe(PLAYER_STATS_FILE)
    if stats.empty:
        st.info("No stats yet.")
        return

    mine = stats[stats["player_name"].str.lower() == player_name.lower()]
    if mine.empty:
        st.info("No stats recorded for you yet.")
        return

    # --- Summary Metrics ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Matches", value=len(mine))
    c2.metric("Goals", value=int(mine["goals"].sum()))
    c3.metric("Assists", value=int(mine["assists"].sum()))
    avg_rating = round(mine["rating"].mean(), 2) if not mine["rating"].isna().all() else "N/A"
    c4.metric("Avg Rating", value=avg_rating)

    st.divider()

    # --- Performance Tracker ---
    st.subheader("📈 Performance Tracker")

    # Eye-comfortable colors
    line_color = "#6CA0DC"       # soft blue
    marker_color = "#88B04B"     # soft green
    background_color = "#F7F7F7" # light gray
    axis_color = "#333333"       # dark for labels/grid lines

    fig = px.line(
        mine.sort_values("match_id"),
        x="match_id",
        y="rating",
        markers=True,
        title="Ratings over Matches",
        labels={"match_id": "Match ID", "rating": "Rating"}
    )

    # Customize line and marker
    fig.update_traces(
        line=dict(color=line_color, width=3),
        marker=dict(color=marker_color, size=10, line=dict(width=1, color="white"))
    )

    # Update layout for readability
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor=background_color,
        paper_bgcolor=background_color,
        title=dict(font=dict(size=20, color=axis_color)),
        xaxis=dict(
            showgrid=True,
            gridcolor="#AAAAAA",  # darker gray
            linecolor=axis_color,
            tickfont=dict(size=14, color=axis_color),
            title=dict(text="Match ID", font=dict(size=16, color=axis_color))
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#AAAAAA",  # darker gray
            linecolor=axis_color,
            tickfont=dict(size=14, color=axis_color),
            title=dict(text="Rating", font=dict(size=16, color=axis_color)),
            range=[0, 10]
        )
    )

    # Disable interactions
    config = {
        "staticPlot": True,
        "displayModeBar": False
    }

    st.plotly_chart(fig, use_container_width=True, config=config)









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

    # Draw pitch
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
    fig.update_layout(
        height=600,
        title=f"{formation} – Assigned XI",
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="green"
    )

    # -------------------------------
    # Disable all interactions for view-only
    # -------------------------------
    config = {
        "staticPlot": True,  # disables zoom, pan, drag
        "displayModeBar": False  # hide toolbar
    }

    st.plotly_chart(fig, use_container_width=True, config=config)


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
    if mid is not None and str(mid).strip() != "":
     try:
        mid_int = int(mid)
        mrow = matches[matches["match_id"] == mid_int].iloc[0]
     except (ValueError, IndexError):
        st.warning("⚠️ Could not find match with that ID.")
    else:
     st.warning("⚠️ No match selected.")


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
# ROUTER PER ROLE (Tabs Layout with Icons)
# -------------------------------
def run_admin():
    render_header()
    tabs = [
        "🏠 Dashboard",
        "⚽ Matches",
        "📊 Player Stats",
        "📸 Upload Player Stats",
        "👤 Players",
        "📝 Training Sessions",
        "📋 Attendance",
        "💬 Fan Wall",
        "📄 Reports",
        "⭐ Best XI",
        "⚠️ Danger Zone"
    ]

    pages = {
        "🏠 Dashboard": page_dashboard,
        "⚽ Matches": admin_matches_page,
        "📊 Player Stats": admin_player_stats_page,
        "📸 Upload Player Stats": admin_upload_player_stats_page,
        "👤 Players": admin_players_crud_page,
        "📝 Training Sessions": admin_training_sessions_page,
        "📋 Attendance": admin_training_attendance_all,
        "💬 Fan Wall": admin_fanwall_moderation,
        "📄 Reports": admin_reports_page,
        "⭐ Best XI": page_best_xi,
        "⚠️ Danger Zone": admin_delete_all_data
    }

    selected_tab = st.tabs(tabs)
    for i, tab_name in enumerate(tabs):
        with selected_tab[i]:
            pages[tab_name]()


def run_manager():
    render_header()
    tabs = [
        "🏠 Dashboard",
        "📄 Tactics Text",
        "📊 Tactics Board",
        "📋 Attendance",
        "⭐ Best XI"
    ]

    pages = {
        "🏠 Dashboard": page_dashboard,
        "📄 Tactics Text": manager_tactics_text_page,
        "📊 Tactics Board": manager_tactics_board_page,
        "📋 Attendance": manager_training_attendance_overview,
        "⭐ Best XI": page_best_xi
    }

    selected_tab = st.tabs(tabs)
    for i, tab_name in enumerate(tabs):
        with selected_tab[i]:
            pages[tab_name]()


def run_player():
    render_header()
    tabs = [
        "🏠 Dashboard",
        "📊 My Stats",
        "📋 Attendance",
        "📄 Tactics Text",
        "📊 Tactics Board",
        "⭐ Best XI"
    ]

    pages = {
        "🏠 Dashboard": page_dashboard,
        "📊 My Stats": lambda: player_my_stats_page(st.session_state.auth.get("name", "Player")),
        "📋 Attendance": lambda: player_training_attendance_page(st.session_state.auth.get("name", "Player")),
        "📄 Tactics Text": player_tactics_text_page,
        "📊 Tactics Board": player_tactics_board_page,
        "⭐ Best XI": page_best_xi
    }

    selected_tab = st.tabs(tabs)
    for i, tab_name in enumerate(tabs):
        with selected_tab[i]:
            pages[tab_name]()


def run_fan():
    render_header()
    tabs = [
        "🏠 Dashboard",
        "💬 Public Results & Fan Wall"
    ]

    pages = {
        "🏠 Dashboard": page_dashboard,
        "💬 Public Results & Fan Wall": fan_public_page
    }

    selected_tab = st.tabs(tabs)
    for i, tab_name in enumerate(tabs):
        with selected_tab[i]:
            pages[tab_name]()



# -------------------------------
# MAIN
# -------------------------------
def main():
    init_session()

    if st.session_state.page == "intro" and st.session_state.auth["role"] is None:
        intro_page()
        return
    elif st.session_state.page == "login" and st.session_state.auth["role"] is None:
        login_ui()
        return
    elif st.session_state.page == "fan_public_only" and st.session_state.auth["role"] == "fan":
        render_header()
        fan_public_page()
        return

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
        logout()


if __name__ == "__main__":
    main()

