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
# PAGE CONFIG (mobile-first)
# -------------------------------
LOGO_URL = "https://github.com/mostafaasaad32/nile/raw/master/images/Artboard_1.png"

st.set_page_config(
    page_title="Nile SC Manager",
    page_icon="⚽",
    layout="centered",   # ✅ full width
    initial_sidebar_state="collapsed"
)

# ✅ Mobile scaling
st.markdown(
    """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    """,
    unsafe_allow_html=True
)

# ===================================
# CLEAN COMBINED GLOBAL CSS
# ===================================
GLOBAL_CSS = """
<style>
/* ====== HIDE STREAMLIT DEFAULT UI ====== */
#MainMenu, footer, header,
.viewerBadge_container__1QSob,
.stDeployButton, .stAppDeployButton {
  display: none !important;
  visibility: hidden !important;
}

/* ====== HIDE WATERMARKS & FULLSCREEN ====== */
a[href="https://streamlit.io"],
div[data-testid="stDecoration"],
div[data-testid="stDecorationContainer"],
section[data-testid="stToolbar"],
[data-testid="StyledFullScreenButton"],
[data-testid="StyledToolbar"],
.stDecoration, .stToolbar,
button[title="View fullscreen"],
div[title="View fullscreen"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    height: 0 !important;
    width: 0 !important;
    pointer-events: none !important;
    overflow: hidden !important;
}

/* ====== LAYOUT RESET ====== */
.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
    width: 100% !important;
    padding-bottom: 20px !important; /* safe space for navbar */
}
.css-ocqkz7, .css-1kyxreq, .stColumn {
    flex: 1 1 100% !important;
    width: 100% !important;
}

/* ====== FORCE FULL-WIDTH INPUTS & BUTTONS ====== */
.stTextInput, .stTextArea, .stSelectbox, .stNumberInput, .stDateInput, .stTimeInput,
.stMultiSelect, .stFileUploader, .stDownloadButton, .stSlider, .stRadio, .stCheckbox,
.stButton > button {
    width: 100% !important;
    max-width: 100% !important;
    display: block !important;
}

/* ====== BUTTON STYLE (SOLID GLASSY GRADIENT) ====== */
.stButton > button {
  font-family: 'WIDE MEDIUM', sans-serif !important;
  font-weight: 600 !important;
  font-size: 16px !important;
  letter-spacing: 0.5px;

  /* Solid gradient background */
  background: linear-gradient(90deg, #00C0FA, #015EEA,#0C182E) !important;
  color: #FFFFFF !important;

  border: none !important;
  border-radius: 7px !important;
  padding: 12px 20px !important;
  min-height: 44px !important;



  transition: all 0.3s ease-in-out !important;
}

.stButton > button:hover {
  transform: translateY(-2px) scale(1.02) !important;

}

.stButton > button:active {
  transform: translateY(1px) scale(0.97) !important;
  opacity: 0.95 !important;
}

/* ====== COLOR PALETTE ====== */
:root {
  --app-bg: #0A1128;
  --sidebar-bg: #0A1128;
  --accent-green: #34D399;
  --accent-blue: #2563EB;
  --text-secondary: #E5E7EB;
  --glass-bg: rgba(255,255,255,0.08);
  --glass-border: rgba(255,255,255,0.18);
}

/* ====== APP BACKGROUND ====== */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .stApp {
  background-color: var(--app-bg) !important;
  color: white !important;
  overflow-x: hidden !important;
}

/* ====== SIDEBAR ====== */
[data-testid="stSidebar"] {
  background-color: var(--sidebar-bg) !important;
}
[data-testid="stSidebar"] * {
  color: white !important;
}

/* ====== GLASS CARDS ====== */
.glass {
  background: linear-gradient(135deg,
    rgba(0,192,250,0.12),
    rgba(1,94,234,0.12),
    rgba(255,255,255,0.08));
  border: 2px solid transparent;
  border-radius: 18px;
  border-image: linear-gradient(90deg, #00C0FA, #015EEA, #FFFFFF) 1;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);

  box-shadow: 0 6px 20px rgba(0,192,250,0.2),
              0 0 16px rgba(1,94,234,0.2);
  padding: 16px;
  transition: all 0.3s ease-in-out;
}
.glass:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 28px rgba(0,192,250,0.35),
              0 0 20px rgba(1,94,234,0.35),
              0 0 30px rgba(255,255,255,0.15);
}

/* ====== HEADER CONTAINER ====== */
.header-container {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin: 0 !important;
  padding: 2px 8px !important;
  gap: 8px;
}

/* ====== TITLES ====== */
.app-title {
  font-family: 'Base Neue Sup Exp Obl', sans-serif !important;
  font-weight: 900 !important;
  font-style: oblique !important;
  letter-spacing: 1.5px;
  color: #ffffff !important;
  font-size: 28px !important;
  margin: 0 !important;
}
.app-subtitle {
  font-family: 'WIDE MEDIUM', sans-serif !important;
  font-weight: 500 !important;
  color: var(--text-secondary) !important;
  font-size: 16px !important;
  letter-spacing: 1px !important;
}

/* ====== MAIN & SECONDARY HEADINGS ====== */
.main-heading, .stTabs [role="tab"][aria-selected="true"], .stSubheader {
  font-family: 'Base Neue Sup Exp Obl', sans-serif !important;
  font-weight: 900 !important;
  font-style: oblique !important;
  letter-spacing: 1.2px !important;
  color: #ffffff !important;
  text-transform: uppercase !important;
}
.secondary-heading, .stTabs [role="tab"] {
  font-family: 'Base Neue Sup Exp Obl', sans-serif !important;
  font-weight: 700 !important;
  font-style: oblique !important;
  letter-spacing: 1px !important;
  color: var(--text-secondary) !important;
}

/* ====== METRICS ====== */
.stMetricLabel {
  font-family: 'Base Neue Sup Exp Obl', sans-serif !important;
  font-weight: 700 !important;
  font-style: oblique !important;
  letter-spacing: 1px !important;
  color: var(--text-secondary) !important;
}
[data-testid="stMetricValue"] {
  font-family: 'Base Neue Sup Exp Obl', sans-serif !important;
  font-weight: 900 !important;
  font-style: oblique !important;
  color: #ffffff !important;
  font-size: 20px !important;
}

/* ====== TABLES ====== */
[data-testid="stDataFrame"] {
  display: block !important;
  overflow-x: auto !important;
  white-space: nowrap !important;
  max-width: 100% !important;
  font-size: 13px !important;
}

/* ====== PLOTS & IMAGES ====== */
.stPlotlyChart, .stAltairChart, .stVegaLiteChart, .stPydeckChart, .stImage {
  max-width: 100% !important;
  width: 100% !important;
  height: auto !important;
  overflow-x: auto !important;
}

/* ====== NAVBAR ====== */
.navbar {
    position: fixed;
    bottom: 0;
    left: 0; right: 0;
    height: 60px;
    background: #111827;
    display: flex;
    justify-content: space-around;
    align-items: center;
    border-top: 1px solid #333;
    z-index: 10000;
    padding-bottom: env(safe-area-inset-bottom, 10px);
    box-sizing: border-box;
}
.navbar a {
    flex: 1;
    text-align: center;
    color: #9CA3AF;
    font-size: 20px;
    text-decoration: none;
    padding: 6px 0;
    transition: all 0.2s ease-in-out;
}
.navbar a.active { color: #10B981; font-weight: bold; }
.navbar a:hover { color: white; }

/* ====== TABS (Gradient Underline) ====== */
.stTabs [role="tablist"] {
    border-bottom: 2px solid rgba(255,255,255,0.1) !important;
    margin-bottom: 14px !important;
}
.stTabs [role="tab"] {
    font-family: 'WIDE MEDIUM', sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #FFFFFF !important;
    padding: 8px 14px !important;
    margin: 0 4px !important;
    background: transparent !important;
    border: none !important;
    cursor: pointer !important;
    transition: all 0.2s ease-in-out;
}
.stTabs [role="tab"]:hover {
    color: #BFDBFE !important;
}
.stTabs [role="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
    font-weight: 800 !important;
    border-bottom: 4px solid transparent !important;
    border-image: linear-gradient(90deg, #00C0FA, #015EEA, #FFFFFF) 1 !important;
}

/* ====== MOBILE ====== */
@media (max-width: 600px) {
  .block-container { padding: 0.25rem !important; max-width: 100% !important; }
  h1, h2, h3, .app-title, .main-heading { font-size: 18px !important; }
  .app-subtitle, p, div, span { font-size: 13px !important; }
  .stButton > button { font-size: 14px !important; padding: 8px 12px !important; }
  .glass { padding: 8px !important; border-radius: 12px !important; }
  .stDataFrame { font-size: 12px !important; }
  .stPlotlyChart, .stAltairChart { height: auto !important; min-height: 260px !important; }
  .header-container img { width: 80px !important; }
  .app-title { font-size: 16px !important; }
}

/* Prevent last fields cut under navbar */
.block-container,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
  padding-bottom: 50px !important;
  box-sizing: border-box !important;
}
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# =======================================
# NILES APP (with Supabase integration)
# =======================================



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
    # Store multiple keys in secrets.toml
    # Example:
    # [keys]
    # GEMINI_API_KEYS = ["key1", "key2", "key3", "key4"]

    api_keys = st.secrets["keys"]["GEMINI_API_KEYS"]

    # Pick one key (random or round robin)
    selected_key = random.choice(api_keys)

    # Configure client with the chosen key
    genai.configure(api_key=selected_key)
    return genai.GenerativeModel("gemini-2.0-flash")



def _table_for_path(path: str) -> str:
    if path not in PATH_TO_TABLE:
        raise ValueError(f"No Supabase table mapping for {path}")
    return PATH_TO_TABLE[path]

def _df_to_rows(df: pd.DataFrame):
    return json.loads(df.where(pd.notnull(df), None).to_json(orient="records"))


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
    """
    Safe Supabase writer:
    - Skips auto-generated 'id' columns (e.g., training_attendance)
    - Validates schema without spamming warnings for expected auto IDs
    - Inserts/Upserts cleanly into Supabase
    - Falls back to local CSV if Supabase write fails
    """
    sb = _supabase_client()
    table = _table_for_path(path)

    # === Adjust expected schema to ignore 'id' for certain tables ===
    expected_cols = EXPECTED_COLUMNS.get(table, [])
    ignore_missing = {"training_attendance", "fan_wall", "tactics", "tactics_positions", "availability"}
    expected_cols = [c for c in expected_cols if not (c == "id" and table in ignore_missing)]

    # === Check schema ===
    missing_cols = [c for c in expected_cols if c not in df.columns]
    if missing_cols:
        st.warning(f"⚠️ Missing columns for {table}: {missing_cols}")

    # === Drop auto-generated IDs ===
    auto_ids = {
        "player_stats": ["id"], "tactics": ["id"], "tactics_positions": ["id"],
        "availability": ["id"], "training_attendance": ["id"], "fan_wall": ["id"],
    }
    safe_df = df.drop(columns=[c for c in auto_ids.get(table, []) if c in df.columns], errors="ignore")

    # === Format dates ===
    if "date" in safe_df.columns:
        safe_df["date"] = pd.to_datetime(safe_df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

    # === Type conversions for player_stats ===
    try:
        if table == "player_stats":
            int_cols = [
                "match_id","goals","assists","shots","passes","dribbles","tackles",
                "offsides","fouls_committed","possession_won","possession_lost",
                "minutes_played","yellow_cards","red_cards","player_id"
            ]
            float_cols = [
                "rating","shot_accuracy","pass_accuracy","dribble_success",
                "tackle_success","distance_covered","distance_sprinted"
            ]
            for col in int_cols:
                if col in safe_df.columns:
                    safe_df[col] = pd.to_numeric(safe_df[col], errors="coerce").fillna(0).astype("Int64")
            for col in float_cols:
                if col in safe_df.columns:
                    safe_df[col] = pd.to_numeric(safe_df[col], errors="coerce").astype(float)
    except Exception as conv_err:
        st.warning(f"⚠️ Column conversion error: {conv_err}")

    # === Type conversions for matches ===
    try:
        if table == "matches":
            for col in ["match_id", "our_score", "their_score"]:
                if col in safe_df.columns:
                    safe_df[col] = pd.to_numeric(safe_df[col], errors="coerce").astype("Int64")
    except Exception as conv_err:
        st.warning(f"⚠️ Column conversion error in matches: {conv_err}")

    # === Convert to dict rows ===
    rows = _df_to_rows(safe_df)
    if not rows:
        st.info(f"ℹ️ No rows to save for {table}")
        return

    try:
        # === UPSERT in chunks ===
        CHUNK = 500
        for i in range(0, len(rows), CHUNK):
            res = sb.table(table).upsert(rows[i:i+CHUNK]).execute()
            if getattr(res, "error", None):
                raise Exception(res.error)
        st.success(f"✅ Saved {len(rows)} rows to Supabase table '{table}'")

        # === Cleanup old rows (delete stale) ===
        try:
            if table == "players":
                ids = [r["player_id"] for r in rows if r.get("player_id") is not None]
                sb.table(table).delete().not_.in_("player_id", ids).execute()

            elif table == "matches":
                ids = [r["match_id"] for r in rows if r.get("match_id") is not None]
                sb.table(table).delete().not_.in_("match_id", ids).execute()

            elif table == "training_sessions":
                ids = [r["session_id"] for r in rows if r.get("session_id") is not None]
                sb.table(table).delete().not_.in_("session_id", ids).execute()

            elif table == "player_stats":
                role = st.session_state.auth.get("role", "").lower()
                if role == "admin":
                    # Admin cleanup: remove old stats for uploaded matches
                    match_ids = [r["match_id"] for r in rows if r.get("match_id") is not None]
                    if match_ids:
                        sb.table(table).delete().in_("match_id", match_ids).execute()
                else:
                    # Player: do not delete other stats
                    pass

            elif table in ["tactics", "tactics_positions", "availability", "training_attendance", "fan_wall"]:
                # No cleanup based on id (keep history)
                pass

        except Exception as delete_err:
            st.warning(f"⚠️ Cleanup issue in {table}: {delete_err}")

    except Exception as e:
        # === Fallback to local CSV ===
        st.error(f"❌ Failed to save {table} to Supabase: {e}")
        try:
            df.to_csv(path, index=False)
            st.warning(f"💾 Saved locally to {path} instead.")
        except Exception as csv_err:
            st.error(f"❌ Could not save CSV backup: {csv_err}")





# -------------------------------
# APP TITLE & PATHS
# -------------------------------
APP_TITLE = "Nile Esports ProClubs Hub"
DATA_DIR = "data"
UPLOADS_DIR = "uploads"


# Simple in-code fallback role codes
ROLE_CODES = {
    "admin": {"Admin": "ADMIN-123"},
    "manager": {"Manager": "MGR-456"},
    "player": {"Player1": "PL-001", "Player2": "PL-002", "Player3": "PL-003"},
}

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
    role = st.session_state.auth.get("role", "Guest")
    name = st.session_state.auth.get("name", "User")

    # === Top Header Row ===
    col_logo, col_spacer, col_refresh, col_logout = st.columns([6, 6, 1, 1])

    # Left: Logo + Title
    with col_logo:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; margin:0; padding:4px;">
            <img src="{LOGO_URL}" style="width:140px; height:auto;">
            <div class="app-title">NILE ESPORTS HUB</div>
            <span style="color:#ff4b4b; font-weight:bold; font-size:22px;">LIVE</span>
        </div>
        """, unsafe_allow_html=True)

    # Right: Refresh button
    with col_refresh:
        if st.button("🔄", key="refresh_btn"):
            st.rerun()

    # Right: Logout button
    with col_logout:
        if st.button("🚪 Logout", key="logout_btn"):
            logout()

    # === User Info ===
    st.markdown(
        f"<div class='secondary-heading' style='font-size:14px; margin:6px 0;'>"
        f"Role: <b>{role.upper()}</b> | User: <b>{name}</b></div>",
        unsafe_allow_html=True
    )





# -------------------------------
# INTRO PAGE (before login)
# -------------------------------
def intro_page():
    st.markdown("""
    <style>
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
        }
        .main .block-container {
            padding: 0 !important;
        }
        header, .stToolbar {display: none !important;}

        /* Container */
        .intro-container {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    min-height: auto;
    text-align: center;
    background: transparent !important;   /* same as app background */
    padding: 40px 0;
}
        /* Logo */
        .intro-logo {
            width: 300px;
            animation: fadeInScale 2s ease forwards;
        }

        /* Title plain white */
        .intro-title {
            font-family: 'Base Neue Sup Exp Obl', sans-serif !important;
            font-size: 36px;
            font-weight: 900;
            text-transform: uppercase;
            color: white !important;
            margin-top: 16px;
            opacity: 0;
            animation: slideUp 1.5s ease forwards 1s;
        }

        /* Subtitle plain white */
        .intro-subtitle {
            font-family: 'Base Neue Sup Exp Obl', sans-serif !important;
            font-size: 18px;
            color: white !important;
            margin-top: 8px;
            opacity: 0;
            animation: fadeIn 1.2s ease forwards 2s;
        }

     /* Button wrapper centered */
.button-wrapper {
    margin-top: 30px;
    display: flex;
    flex-direction: column;    /* stacked vertically */
    align-items: center;
    gap: 10px;
    width: 100%;               /* span full row */
}

/* Force each Streamlit button block to center */
.intro-container .stButton {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}

/* Buttons smaller & centered */
.intro-container .stButton > button {
    background: linear-gradient(135deg, #0A1128, #111827) !important;
    color: white !important;
    border: 1px solid #1F2937 !important;
    border-radius: 8px !important;
    font-family: 'Wide Medium', sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    padding: 6px 12px !important;
    min-height: 32px !important;
    width: 160px !important;   /* fixed narrow width */
    text-align: center !important;
    box-shadow: 0 3px 8px rgba(0,0,0,0.25) !important;
    transition: all 0.2s ease-in-out;
}

        .intro-container .stButton > button:hover {
            transform: translateY(-2px);
            opacity: 0.95;
            border: 1px solid #374151 !important;
        }

        /* Animations */
        @keyframes fadeInScale {
            from { opacity: 0; transform: scale(0.8); }
            to { opacity: 1; transform: scale(1); }
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        /* Mobile */
        @media (max-width:600px){
            .intro-logo { max-width: 120px !important; }
            .intro-title { font-size: 24px !important; }
            .intro-subtitle { font-size: 14px !important; }
            .intro-container .stButton > button {
                width: 120px !important;
                font-size: 13px !important;
                padding: 5px 10px !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)



    # =======================
    # Content with Streamlit container
    # =======================
    with st.container():
        st.markdown(f"""
        <div class="intro-container">
            <img src="{LOGO_URL}" class="intro-logo"/>
            <div class="intro-title">NILE ESPORTS HUB</div>
            <div class="intro-subtitle">One Club • One Heartbeat 🖤💚</div>
        </div>
        """, unsafe_allow_html=True)

        # Buttons
        st.markdown("<div class='button-wrapper'>", unsafe_allow_html=True)

        if st.button("🚀 Enter the Hub", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()



        st.markdown("</div>", unsafe_allow_html=True)












# -------------------------------
# LOGIN PAGE
# -------------------------------
def login_ui():
    st.markdown(f"""
    <div style="text-align:center;">
        <img src="{LOGO_URL}" style="width:350px; height:auto; margin-bottom:10px;">
        <h2 style="margin:0;">Sign In</h2>
        <p style="margin:.3rem 0 1rem 0;">Choose your role and use your access code</p>
    </div>
    """, unsafe_allow_html=True)

    role = st.selectbox("Select your role", ["Admin", "Manager", "Player"])
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
    # Fetch data
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

    # ===================== LAST MATCH =====================
    st.markdown("<h2 class='main-heading'>Last Match</h2>", unsafe_allow_html=True)
    if not past_matches.empty:
        lm = past_matches.iloc[0]

        # Ensure integer scores
        import math

        val = lm.get("our_score")
        if val is None or (isinstance(val, float) and math.isnan(val)):
         our_score = 0
        else:
         our_score = int(val)

        val2 = lm.get("their_score")
        if val2 is None or (isinstance(val2, float) and math.isnan(val2)):
         their_score = 0
        else:
         their_score = int(val2)


        st.markdown(f"""
        <div style='
            background: #4CAF50;
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
        '>
            <h3 style='margin:0;'>vs {lm['opponent']}</h3>
            <h2 style='margin:10px 0;'>{our_score} - {their_score}</h2>
            <p style='margin:0;'><b>{lm.get('result', '')}</b></p>
            <p style='margin:0;'>{lm.get('date', '')}</p>
            <p style='margin:0;'>{lm.get('notes', '')}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No past matches yet.")

    # ===================== UPCOMING MATCHES =====================
    st.markdown("<h2 class='main-heading'>📅 Upcoming Matches</h2>", unsafe_allow_html=True)
    if not upcoming_matches.empty:
        next_matches = upcoming_matches.head(3)  # Show only next 3
        cols = st.columns(len(next_matches))

        for idx, (_, row) in enumerate(next_matches.iterrows()):
            days_left = (row["date"] - date.today()).days
            with cols[idx]:
                st.markdown(f"""
                <div style='
                    background: #1E88E5;
                    color: white;
                    padding: 12px;
                    border-radius: 12px;
                    margin: 5px;
                    text-align: center;
                    font-size: 14px;
                '>
                    <h4 style='margin:4px 0; font-size:16px;'>vs {row['opponent']}</h4>
                    <p style='margin:2px 0; font-size:13px;'>📅 {row['date']}</p>
                    <p style='margin:2px 0; font-size:13px;'>{row.get('notes', '')}</p>
                    <div style='
                        font-size: 18px;
                        font-weight: bold;
                        margin-top: 6px;
                    '>{max(days_left, 0)} Days</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.caption("No upcoming fixtures.")

    st.divider()

    # ===================== LEADERBOARDS =====================
    st.markdown("<h2 class='main-heading'>🏆 Leaderboards</h2>", unsafe_allow_html=True)

    if stats.empty:
        st.info("No player stats yet.")
    else:
        # Aggregate stats
        agg = stats.groupby("player_name").agg(
            goals=("goals", "sum"),
            assists=("assists", "sum"),
            avg_rating=("rating", "mean"),
            yellow=("yellow_cards", "sum"),
            red=("red_cards", "sum"),
            matches=("match_id", "count")
        ).reset_index()

        # Convert to integers
        for col in ["goals", "assists", "yellow", "red", "matches"]:
            if col in agg.columns:
                agg[col] = agg[col].fillna(0).astype(int)

        # Top rankings (smaller list)
        top_scorers = agg.sort_values("goals", ascending=False).head(5)
        top_assists = agg.sort_values("assists", ascending=False).head(5)
        top_rating = agg[agg["matches"] >= 3].sort_values("avg_rating", ascending=False).head(5)

        # Theme colors
        scorer_color, assist_color, rating_color = "#1E88E5", "#43A047", "#E53935"
        card_bg, text_color = "#0C182E", "#FFFFFF"

        # ---------- 3 Leaderboards Side by Side ----------
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"<div style='text-align:center; font-size:18px; font-weight:bold; color:{scorer_color};'>⚽ Top Scorers</div>", unsafe_allow_html=True)
            for i, row in enumerate(top_scorers.itertuples(), start=1):
                st.markdown(f"""
                <div style='
                    background:{card_bg};
                    color:{text_color};
                    padding:6px;
                    border-radius:8px;
                    margin:4px 0;
                    border:1px solid {scorer_color};
                    display:flex;
                    justify-content:space-between;
                    font-size:13px;
                '>
                    <span>{i}. {row.player_name}</span>
                    <span style='font-weight:bold;'>{row.goals}</span>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"<div style='text-align:center; font-size:18px; font-weight:bold; color:{assist_color};'>🎯 Top Assists</div>", unsafe_allow_html=True)
            for i, row in enumerate(top_assists.itertuples(), start=1):
                st.markdown(f"""
                <div style='
                    background:{card_bg};
                    color:{text_color};
                    padding:6px;
                    border-radius:8px;
                    margin:4px 0;
                    border:1px solid {assist_color};
                    display:flex;
                    justify-content:space-between;
                    font-size:13px;
                '>
                    <span>{i}. {row.player_name}</span>
                    <span style='font-weight:bold;'>{row.assists}</span>
                </div>
                """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"<div style='text-align:center; font-size:18px; font-weight:bold; color:{rating_color};'>⭐ Top Rating</div>", unsafe_allow_html=True)
            for i, row in enumerate(top_rating.itertuples(), start=1):
                st.markdown(f"""
                <div style='
                    background:{card_bg};
                    color:{text_color};
                    padding:6px;
                    border-radius:8px;
                    margin:4px 0;
                    border:1px solid {rating_color};
                    display:flex;
                    justify-content:space-between;
                    font-size:13px;
                '>
                    <span>{i}. {row.player_name}</span>
                    <span style='font-weight:bold;'>{row.avg_rating:.2f}</span>
                </div>
                """, unsafe_allow_html=True)






# -------------------------------
# ADMIN PAGES (Matches, Stats, Fan Wall, Reports, PLAYERS CRUD)
# -------------------------------
def admin_matches_page():
    st.markdown("<h2 class='main-heading'>⚽ Matches</h2>", unsafe_allow_html=True)

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
                match_row = unfinished.loc[unfinished["match_id"] == int(mid), "notes"]

                if not match_row.empty:
                 default_notes = str(match_row.values[0])
                else:
                 default_notes = ""

                with c3:
                 notes2 = st.text_area("Notes", value=default_notes)
                submit_res = st.form_submit_button("Save Result", type="primary")

            if submit_res:
                res = calc_result(int(our), int(their))

                # 🔥 Force INT for scores
                matches.loc[matches["match_id"] == int(mid),
                            ["our_score", "their_score", "result", "notes"]] = [
                    int(our), int(their), res, notes2
                ]

                # 🔥 Ensure integer columns before saving
                if "our_score" in matches.columns:
                    matches["our_score"] = pd.to_numeric(matches["our_score"], errors="coerce").astype("Int64")
                if "their_score" in matches.columns:
                    matches["their_score"] = pd.to_numeric(matches["their_score"], errors="coerce").astype("Int64")

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
    import math
    import numpy as np
    from datetime import datetime

    st.markdown("<h2 class='main-heading'>📊 Player Stats Moderation</h2>", unsafe_allow_html=True)

    sb = _supabase_client()
    stats = sb.table("player_stats").select("*").execute()
    df = pd.DataFrame(stats.data) if stats.data else pd.DataFrame()

    if df.empty:
        st.info("No player stats available yet.")
        return

    # === Join matches for readability ===
    matches = sb.table("matches").select("*").execute()
    matches_df = pd.DataFrame(matches.data) if matches.data else pd.DataFrame()

    if not matches_df.empty and "match_id" in df.columns:
        matches_df["date"] = pd.to_datetime(matches_df["date"], errors="coerce")
        matches_df = matches_df.sort_values("date", ascending=False)
        match_labels = matches_df.set_index("match_id").apply(
            lambda r: f"{r['date'].date()} vs {r['opponent']}", axis=1, result_type="reduce"
        )
        df = df.merge(match_labels.rename("match_name"),
                      left_on="match_id", right_index=True, how="left")
        latest_match_name = match_labels.iloc[0] if not match_labels.empty else "All"
    else:
        df["match_name"] = df["match_id"].astype(str)
        latest_match_name = "All"

    # === Filters ===
    players = sorted(df["player_name"].unique())
    selected_player = st.selectbox("Filter by Player", ["All"] + players)

    matches_list = sorted(df["match_name"].unique())
    selected_match = st.selectbox(
        "Filter by Match",
        ["All"] + matches_list,
        index=(["All"] + matches_list).index(latest_match_name) if latest_match_name in matches_list else 0
    )

    filtered = df.copy()
    if selected_player != "All":
        filtered = filtered[filtered["player_name"] == selected_player]
    if selected_match != "All":
        filtered = filtered[filtered["match_name"] == selected_match]

    if filtered.empty:
        st.warning("No stats found for this filter.")
        return

    # === Editable table for ALL stats ===
    st.markdown("### ✏️ Edit Player Stats (edit any cell)")
    # Keep DB columns only (drop the helper match_name)
    editable_df = filtered.drop(columns=["match_name"])
    edited_df = st.data_editor(
        editable_df,
        hide_index=True,
        num_rows="dynamic",
        use_container_width=True
    )

    # ---- Sanitizer helper ----
    def sanitize_for_json(value):
        """Return a JSON-safe Python value for Supabase."""
        # pandas / numpy NA
        try:
            if pd.isna(value):
                return None
        except Exception:
            pass

        # numpy scalars
        if isinstance(value, (np.generic,)):
            # integers
            if np.issubdtype(type(value), np.integer):
                return int(value)
            # floats (handle Inf/NaN)
            if np.issubdtype(type(value), np.floating):
                v = float(value)
                if math.isfinite(v):
                    return v
                return None
            # booleans
            if np.issubdtype(type(value), np.bool_):
                return bool(value)

        # plain Python types
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return int(value)
        if isinstance(value, float):
            if math.isfinite(value):
                return float(value)
            return None
        if isinstance(value, (str,)):
            return value

        # pandas Timestamp / datetime
        if isinstance(value, (pd.Timestamp, datetime)):
            # standard ISO string
            return str(value)

        # fallback: try json-serializable or convert to string
        try:
            json.dumps(value)
            return value
        except Exception:
            return str(value)

    # === Save changes back ===
    if st.button("💾 Save All Changes"):
        try:
            sb = _supabase_client()

            # iterate rows and update per id
            updates_count = 0
            for _, row in edited_df.iterrows():
                row_dict = dict(row)  # Series -> dict
                # Extract id
                row_id = row_dict.pop("id", None)
                if row_id is None:
                    # skip rows without primary id
                    continue
                # sanitize all values
                clean_payload = {}
                for k, v in row_dict.items():
                    clean_payload[k] = sanitize_for_json(v)

                # ensure id is a native int for equality check
                try:
                    id_val = int(row_id)
                except Exception:
                    id_val = int(np.int64(row_id)) if isinstance(row_id, np.integer) else row_id

                # perform update
                sb.table("player_stats").update(clean_payload).eq("id", id_val).execute()
                updates_count += 1

            st.success(f"✅ Saved changes for {updates_count} rows.")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Failed to save changes: {e}")

    # === Delete option ===
    st.divider()
    st.markdown("### 🗑️ Delete Stats")
    row_options = filtered.apply(lambda r: f"ID {r['id']} - {r['player_name']} ({r['match_name']})", axis=1)
    selected = st.selectbox("Select stat row to delete", row_options)
    row_id = int(selected.split(" ")[1])

    if st.button("Delete Selected Stat"):
        try:
            sb.table("player_stats").delete().eq("id", row_id).execute()
            st.success("✅ Stat deleted")
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
    st.markdown("<h2 class='main-heading'>👤 Players – Add / Edit / Remove</h2>", unsafe_allow_html=True)
    players = read_csv_safe(PLAYERS_FILE)

    # ---------------- Add Player ----------------
    with st.form("add_player"):
        st.markdown("### ➕ Add Player")
        name = st.text_input("Player Name")
        position = st.selectbox(
            "Position",
            ["Goalkeeper", "Defender", "Midfielder", "Winger", "Striker"]
        )
        code = st.text_input("Login Code", placeholder="e.g. PL-010")
        active = st.checkbox("Active", value=True)
        submitted = st.form_submit_button("Add Player", type="primary")

    if submitted:
        if not name or not code:
            st.warning("Name and Code are required.")
        else:
            # Check duplicates
            duplicate_name = players["name"].str.lower().eq(name.lower()).any()
            duplicate_code = players["code"].astype(str).eq(str(code)).any()

            if duplicate_name:
                st.error(f"A player with the name '{name}' already exists.")
            elif duplicate_code:
                st.error(f"A player with the code '{code}' already exists.")
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
        status_color = "#34D399" if row["active"] else "#EF4444"
        position_color = "#60A5FA"  # blue highlight
        code_color = "#FBBF24"      # gold

        st.markdown(f"""
<div style="
    display:flex;
    justify-content:space-between;
    align-items:center;
    background: rgba(37,99,235,0.08);
    border: 1px solid rgba(37,99,235,0.25);
    border-radius: 10px;
    padding: 8px 12px;
    margin-bottom: 6px;
    font-size: 13px;
">
  <div>
    <div style="font-family:'SUPER EXP BLACK OBLIQUE'; font-size:15px; color:#fff;">
      {row['name']}
    </div>
    <div style="color:{position_color}; font-size:12px;">
      {row['position']}
    </div>
  </div>

  <div style="text-align:right; font-size:12px;">
    <div style="color:{code_color};">Code: {row['code']}</div>
    <div style="color:{status_color}; font-weight:bold;">
      {"Active" if row['active'] else "Inactive"}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.divider()

    # ---------------- Edit / Delete ----------------
    with st.expander("✏️ Quick Edit / Delete"):
        names = players["name"].tolist()
        sel_name = st.selectbox("Select player", options=names)
        row = players[players["name"] == sel_name].iloc[0]

        positions_list = ["Goalkeeper", "Defender", "Midfielder", "Winger", "Striker"]
        current_pos = str(row["position"])
        pos_index = positions_list.index(current_pos) if current_pos in positions_list else 0

        new_name = st.text_input("Name", value=row["name"])
        new_pos = st.selectbox("Position", positions_list, index=pos_index)
        new_code = st.text_input("Code", value=str(row["code"]))
        new_active = st.checkbox("Active", value=bool(row.get("active", True)))

        colb1, colb2 = st.columns(2)
        with colb1:
            if st.button("Save Changes"):
                # Prevent duplicate when editing (exclude current row)
                duplicate_name = players[
                    (players["name"].str.lower() == new_name.lower()) &
                    (players["player_id"] != row["player_id"])
                ]
                duplicate_code = players[
                    (players["code"].astype(str) == str(new_code)) &
                    (players["player_id"] != row["player_id"])
                ]

                if not new_name or not new_code:
                    st.warning("Name and Code are required.")
                elif not duplicate_name.empty:
                    st.error(f"Another player with the name '{new_name}' already exists.")
                elif not duplicate_code.empty:
                    st.error(f"Another player with the code '{new_code}' already exists.")
                else:
                    players.loc[players["player_id"] == row["player_id"], ["name", "position", "code", "active"]] = [
                        new_name, new_pos, new_code, bool(new_active)
                    ]
                    write_csv_safe(players, PLAYERS_FILE)
                    st.success("Updated.")
                    st.rerun()

        with colb2:
            if st.button("Delete Player"):
                delete_player_and_stats(int(row["player_id"]), sel_name)  # deletes stats first
                players = players[players["player_id"] != row["player_id"]]
                if players.empty:
                    players = pd.DataFrame(columns=["player_id", "name", "position", "code", "active"])
                write_csv_safe(players, PLAYERS_FILE)
                st.success(f"Deleted {sel_name} and all their stats.")
                st.rerun()





# -------------------------------
# TRAINING: Admin/Manager/Player
# -------------------------------
def admin_training_sessions_page():
    """Admin: Manage training sessions and mark attendance (Supabase only)."""
    st.markdown("<h2 class='main-heading'>🏋️ Training Sessions Management</h2>", unsafe_allow_html=True)

    sb = _supabase_client()

    tab1, tab2 = st.tabs(["➕ Create / Manage Sessions", "👥 Mark Attendance"])

    with tab1:
        try:
            sessions_data = sb.table("training_sessions").select("*").order("date").order("time").execute()
            sessions = pd.DataFrame(sessions_data.data)
        except Exception as e:
            st.error(f"❌ Failed to fetch sessions from Supabase: {e}")
            sessions = pd.DataFrame()

        with st.form("create_session"):
            c1, c2, c3 = st.columns([1, 1, 2])
            tr_date = c1.date_input("Date", value=date.today())
            tr_time = c2.time_input("Time", value=dtime(20, 0))
            title = c3.text_input("Title", value="Team Training")
            loc = st.text_input("Location", value="Club Facility")
            notes = st.text_area("Notes", value="")
            submitted = st.form_submit_button("Create Session", type="primary")

        if submitted:
            # ✅ use a short random ID instead of timestamp (fits integer safely)
            new_session = {
                "session_id": random.randint(1000, 999999),  # <–– smaller integer ID
                "date": tr_date.strftime("%Y-%m-%d"),
                "time": tr_time.strftime("%H:%M"),
                "title": title.strip(),
                "location": loc.strip(),
                "notes": notes.strip(),
                "created_by": st.session_state.auth.get("name"),
            }

            try:
                sb.table("training_sessions").insert(new_session).execute()
                st.success("✅ Training session created successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to create session: {e}")

        st.divider()
        st.subheader("📋 All Sessions")

        if sessions.empty:
            st.info("No training sessions found.")
        else:
            st.dataframe(sessions.sort_values(["date", "time"]), use_container_width=True)

            del_id = st.text_input("🗑️ Delete session by session_id")
            if st.button("Delete Session"):
                if del_id.isdigit():
                    sid = int(del_id)
                    try:
                        sb.table("training_attendance").delete().eq("session_id", sid).execute()
                        sb.table("training_sessions").delete().eq("session_id", sid).execute()
                        st.success(f"✅ Deleted session {sid} and related attendance records.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to delete session: {e}")
                else:
                    st.warning("⚠️ Enter a valid numeric session_id.")

    # ============================================================
    # 🟦 TAB 2 — MARK ATTENDANCE
    # ============================================================
    with tab2:
        try:
            sessions_data = sb.table("training_sessions").select("session_id, title, date").execute()
            players_data = sb.table("players").select("name, position").execute()
        except Exception as e:
            st.error(f"❌ Failed to load data: {e}")
            return

        sessions = pd.DataFrame(sessions_data.data)
        players = pd.DataFrame(players_data.data)

        if sessions.empty:
            st.info("Please create a session first.")
            return
        if players.empty:
            st.warning("No players found. Add players first.")
            return

        st.markdown("### 👥 Mark Player Attendance")

        sessions["label"] = sessions.apply(lambda x: f"{x['session_id']} - {x['title']} ({x['date']})", axis=1)
        selected_label = st.selectbox("Select Session", sessions["label"])
        selected_row = sessions[sessions["label"] == selected_label].iloc[0]
        sid = int(selected_row["session_id"])
        sdate = selected_row["date"]

        player_name = st.selectbox("Select Player", players["name"].dropna().unique().tolist())
        status = st.radio("Status", ["attend", "absent", "late", "excused"], horizontal=True)

        import random
from datetime import date, time as dtime, datetime
import pandas as pd
import streamlit as st

def admin_training_sessions_page():
    """Admin: Manage training sessions and mark attendance (Supabase only)."""
    st.markdown("<h2 class='main-heading'>🏋️ Training Sessions Management</h2>", unsafe_allow_html=True)

    sb = _supabase_client()

    tab1, tab2 = st.tabs(["➕ Create / Manage Sessions", "👥 Mark Attendance"])

    # ============================================================
    # 🟩 TAB 1 — CREATE & MANAGE SESSIONS
    # ============================================================
    with tab1:
        try:
            sessions_data = sb.table("training_sessions").select("*").order("date").order("time").execute()
            sessions = pd.DataFrame(sessions_data.data)
        except Exception as e:
            st.error(f"❌ Failed to fetch sessions from Supabase: {e}")
            sessions = pd.DataFrame()

        with st.form("create_session"):
            c1, c2, c3 = st.columns([1, 1, 2])
            tr_date = c1.date_input("Date", value=date.today())
            tr_time = c2.time_input("Time", value=dtime(20, 0))
            title = c3.text_input("Title", value="Team Training")
            loc = st.text_input("Location", value="Club Facility")
            notes = st.text_area("Notes", value="")
            submitted = st.form_submit_button("Create Session", type="primary")

        if submitted:
            # ✅ Use a short random numeric ID
            new_session = {
                "session_id": random.randint(1000, 999999),  # <–– small readable ID
                "date": tr_date.strftime("%Y-%m-%d"),
                "time": tr_time.strftime("%H:%M"),
                "title": title.strip(),
                "location": loc.strip(),
                "notes": notes.strip(),
                "created_by": st.session_state.auth.get("name"),
            }

            try:
                sb.table("training_sessions").insert(new_session).execute()
                st.success("✅ Training session created successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to create session: {e}")

        st.divider()
        st.subheader("📋 All Sessions")

        if sessions.empty:
            st.info("No training sessions found.")
        else:
            st.dataframe(sessions.sort_values(["date", "time"]), use_container_width=True)

            del_id = st.text_input("🗑️ Delete session by session_id")
            if st.button("Delete Session"):
                if del_id.isdigit():
                    sid = int(del_id)
                    try:
                        sb.table("training_attendance").delete().eq("session_id", sid).execute()
                        sb.table("training_sessions").delete().eq("session_id", sid).execute()
                        st.success(f"✅ Deleted session {sid} and related attendance records.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to delete session: {e}")
                else:
                    st.warning("⚠️ Enter a valid numeric session_id.")

    # ============================================================
    # 🟦 TAB 2 — MARK ATTENDANCE
    # ============================================================
    with tab2:
        try:
            sessions_data = sb.table("training_sessions").select("session_id, title, date").execute()
            players_data = sb.table("players").select("name, position").execute()
        except Exception as e:
            st.error(f"❌ Failed to load data: {e}")
            return

        sessions = pd.DataFrame(sessions_data.data)
        players = pd.DataFrame(players_data.data)

        if sessions.empty:
            st.info("Please create a session first.")
            return
        if players.empty:
            st.warning("No players found. Add players first.")
            return

        st.markdown("### 👥 Mark Player Attendance")

        # Short label for session dropdown
        sessions["label"] = sessions.apply(lambda x: f"{x['session_id']} - {x['title']} ({x['date']})", axis=1)
        selected_label = st.selectbox("Select Session", sessions["label"])
        selected_row = sessions[sessions["label"] == selected_label].iloc[0]
        sid = int(selected_row["session_id"])
        sdate = selected_row["date"]

        player_name = st.selectbox("Select Player", players["name"].dropna().unique().tolist())
        status = st.radio("Status", ["attend", "absent", "late", "excused"], horizontal=True)

        if st.button("💾 Save Attendance"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            payload = {
                # ✅ Use small, readable random attendance ID
                "id": random.randint(1000, 999999),
                "session_id": sid,
                "date": sdate,
                "player_name": player_name,
                "status": status,
                "marked_at": now,
                "marked_by": st.session_state.auth.get("name"),
            }

            try:
                existing = sb.table("training_attendance") \
                    .select("id") \
                    .eq("session_id", sid) \
                    .eq("player_name", player_name) \
                    .execute()

                if existing.data:
                    att_id = existing.data[0]["id"]
                    sb.table("training_attendance").update(payload).eq("id", att_id).execute()
                    st.success(f"✅ Attendance updated for {player_name}")
                else:
                    sb.table("training_attendance").insert(payload).execute()
                    st.success(f"✅ Attendance added for {player_name}")

                st.rerun()

            except Exception as e:
                st.error(f"❌ Failed to save attendance: {e}")



def _attendance_color(val: str):
    if str(val).lower() == "yes":
        return "background-color: lightgreen; color: black;"
    if str(val).lower() == "no":
        return "background-color: lightcoral; color: white;"
    return ""


def manager_radar_page():
    st.markdown("<h1 class='super-head'>📊 Player Radar Comparison</h1>", unsafe_allow_html=True)

    # Load stats
    stats = read_csv_safe(PLAYER_STATS_FILE)
    players = read_csv_safe(PLAYERS_FILE)

    if stats.empty or players.empty:
        st.info("⚠️ No stats or players available.")
        return

    # === Select Two Players ===
    player_names = players["name"].dropna().unique().tolist()
    col1, col2 = st.columns(2)
    with col1:
        player1 = st.selectbox("👤 Select First Player", player_names, key="cmp_p1")
    with col2:
        player2 = st.selectbox("👤 Select Second Player", player_names, key="cmp_p2")

    if not player1 or not player2 or player1 == player2:
        st.warning("⚠️ Please select two different players.")
        return

    # === Cumulative Metrics Function ===
    def cumulative_metrics(df):
        metrics = {}
        metrics["⚽ Goals"] = df["goals"].sum()
        metrics["🎯 Assists"] = df["assists"].sum()
        metrics["🔫 Shots"] = df["shots"].sum()
        metrics["📨 Passes"] = df["passes"].sum()
        metrics["🎯 Pass Accuracy %"] = (
            round(((df["passes"] * df["pass_accuracy"] / 100).sum() / df["passes"].sum()) * 100, 1)
            if df["passes"].sum() > 0 else 0
        )
        metrics["⚡ Dribbles"] = df["dribbles"].sum()
        metrics["⚡ Dribble Success %"] = (
            round(((df["dribbles"] * df["dribble_success"] / 100).sum() / df["dribbles"].sum()) * 100, 1)
            if df["dribbles"].sum() > 0 else 0
        )
        metrics["🛡️ Tackles"] = df["tackles"].sum()
        metrics["🛡️ Tackle Success %"] = (
            round(((df["tackles"] * df["tackle_success"] / 100).sum() / df["tackles"].sum()) * 100, 1)
            if df["tackles"].sum() > 0 else 0
        )
        metrics["💪 Possession Won"] = df["possession_won"].sum()
        metrics["❌ Possession Lost"] = df["possession_lost"].sum()
        metrics["🏃 Distance Covered (km)"] = round(df["distance_covered"].sum(), 1)
        metrics["⭐ Avg Rating"] = round(df["rating"].mean(), 2) if "rating" in df else 0
        return metrics

    # === Collect Metrics for Both Players ===
    df1 = stats[stats["player_name"] == player1]
    df2 = stats[stats["player_name"] == player2]

    if df1.empty or df2.empty:
        st.warning("⚠️ Stats missing for one of the players.")
        return

    m1 = cumulative_metrics(df1)
    m2 = cumulative_metrics(df2)

    categories = list(m1.keys())
    v1 = list(m1.values())
    v2 = list(m2.values())

    # Normalize to same scale (0–100)
    max_val = max(max(v1), max(v2)) if (v1 and v2) else 1
    norm_v1 = [(v / max_val) * 100 for v in v1]
    norm_v2 = [(v / max_val) * 100 for v in v2]

    # === Radar Chart ===
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=norm_v1, theta=categories, fill="toself",
        name=player1, line_color="#00C0FA", fillcolor="rgba(0,192,250,0.3)"
    ))

    fig.add_trace(go.Scatterpolar(
        r=norm_v2, theta=categories, fill="toself",
        name=player2, line_color="#FF4B4B", fillcolor="rgba(255,75,75,0.3)"
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor="#666")),
        title=f"Radar Comparison – {player1} vs {player2}",
        title_font=dict(color="#00C0FA", size=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=False,
        width=750,
        height=750,
        margin=dict(l=100, r=100, t=100, b=100)
    )
    st.plotly_chart(fig, use_container_width=True)

    # === Styled Comparison Table ===
    st.markdown("### 📋 Player Comparison Table")

    table_html = f"""
    <style>
        .cmp-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .cmp-table th, .cmp-table td {{
            padding: 12px 15px;
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .cmp-table th {{
            background: rgba(0,192,250,0.2);
            color: #00C0FA;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .cmp-table td {{
            color: #FFFFFF;
        }}
        .cmp-table tr:hover {{
            background: rgba(255,255,255,0.05);
        }}
    </style>
    <table class="cmp-table">
        <tr><th>Metric</th><th>{player1}</th><th>{player2}</th></tr>
    """
    for cat, val1, val2 in zip(categories, v1, v2):
        table_html += f"<tr><td>{cat}</td><td>{val1}</td><td>{val2}</td></tr>"
    table_html += "</table>"

    st.markdown(table_html, unsafe_allow_html=True)








def manager_training_attendance_overview():
    
    st.markdown("<h2 class='main-heading'>📋 Training Attendance – Session Overview</h2>", unsafe_allow_html=True)
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

def player_training_attendance_page():
    """Professional, user-friendly attendance dashboard for all players."""
    st.markdown(
        """
        <style>
            /* ====== GLOBAL ====== */
            body, .stApp {
                background-color: #0c1220 !important;
                color: #e2e8f0 !important;
                font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
            h2, h3, h4 {
                font-family: "Inter", sans-serif;
                letter-spacing: 0.3px;
            }
            .main-heading {
                text-align: center;
                font-weight: 700;
                color: #00eaff;
                font-size: 1.8rem;
                margin-bottom: 0.5rem;
            }
            .subheading {
                text-align: center;
                color: #94a3b8;
                margin-bottom: 1.5rem;
            }

            /* ====== PLAYER CARD ====== */
            .player-card {
                background: linear-gradient(145deg, #141c2f 0%, #0f172a 100%);
                border-radius: 16px;
                padding: 1.3rem 1.5rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                margin-bottom: 1.5rem;
                transition: all 0.2s ease-in-out;
                border: 1px solid #1e293b;
            }
            .player-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.45);
            }
            .player-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.8rem;
            }
            .player-name {
                font-size: 1.2rem;
                font-weight: 700;
                color: #ffffff;
            }
            .player-position {
                background: #1e3a8a;
                color: #93c5fd;
                padding: 5px 10px;
                border-radius: 8px;
                font-size: 0.8rem;
                font-weight: 500;
            }

            /* ====== METRICS ====== */
            .metric-container {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 10px;
                text-align: center;
                margin-top: 0.8rem;
            }
            .metric h4 {
                margin: 0;
                font-size: 1.5rem;
                font-weight: 700;
                color: #ffffff;
                text-shadow: 0 0 5px rgba(255,255,255,0.15);
            }
            .metric span {
                display: block;
                font-size: 0.8rem;
                margin-top: 3px;
                letter-spacing: 0.5px;
                text-transform: uppercase;
                font-weight: 500;
            }
            .attend span { color: #00e676; }   /* Bright Green */
            .late span { color: #ffd54f; }     /* Gold */
            .absent span { color: #ff5252; }   /* Soft Red */
            .excused span { color: #40c4ff; }  /* Sky Blue */

            /* ====== PROGRESS ====== */
            .progress-bar {
                width: 100%;
                background: #1e293b;
                border-radius: 8px;
                overflow: hidden;
                height: 10px;
                margin-top: 12px;
            }
            .progress-inner {
                height: 10px;
                border-radius: 8px;
                transition: width 0.4s ease;
            }
        </style>

        <h2 class='main-heading'>🏋️ Player Attendance Dashboard</h2>
        <p class='subheading'>Live analytics of attendance, lateness, absences & excused sessions.</p>
        """,
        unsafe_allow_html=True,
    )

    # ========== LOAD DATA ==========
    try:
        sb = _supabase_client()
        attendance_data = sb.table("training_attendance").select("*").execute()
        players_data = sb.table("players").select("player_id, name, position, active").execute()
        sessions_data = sb.table("training_sessions").select("session_id").execute()

        attendance = pd.DataFrame(attendance_data.data or [])
        players = pd.DataFrame(players_data.data or [])
        sessions = pd.DataFrame(sessions_data.data or [])
    except Exception:
        players = pd.DataFrame([
            {"name": "Ahmed Ali", "position": "Forward"},
            {"name": "Omar Khaled", "position": "Midfielder"},
            {"name": "Youssef Tarek", "position": "Defender"},
            {"name": "Mohamed Nabil", "position": "Goalkeeper"},
        ])
        attendance = pd.DataFrame([
            {"player_name": "Ahmed Ali", "status": "attend"},
            {"player_name": "Ahmed Ali", "status": "absent"},
            {"player_name": "Omar Khaled", "status": "late"},
            {"player_name": "Youssef Tarek", "status": "excused"},
        ])
        sessions = pd.DataFrame([{"session_id": 1}, {"session_id": 2}, {"session_id": 3}])

    total_sessions = len(sessions["session_id"].unique()) or 1
    attendance["status"] = attendance["status"].astype(str).str.lower()
    attendance["player_name"] = attendance["player_name"].astype(str)

    if players.empty:
        st.warning("No players found.")
        return

    # ========== TEAM SUMMARY ==========
    total_records = len(attendance)
    if total_records > 0:
        total_attend = (attendance["status"] == "attend").sum()
        total_absent = (attendance["status"] == "absent").sum()
        total_late = (attendance["status"] == "late").sum()
        total_excused = (attendance["status"] == "excused").sum()

        team_attend_rate = round(total_attend / total_records * 100, 1)
        team_late_rate = round(total_late / total_records * 100, 1)
        team_absent_rate = round(total_absent / total_records * 100, 1)
        team_excused_rate = round(total_excused / total_records * 100, 1)

        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("✅ Attend", f"{team_attend_rate}%")
        c2.metric("⏰ Late", f"{team_late_rate}%")
        c3.metric("❌ Absent", f"{team_absent_rate}%")
        c4.metric("📝 Excused", f"{team_excused_rate}%")

    st.divider()
    st.markdown("### 👥 Player Attendance Overview")

    # ========== PLAYER CARDS ==========
    for _, player in players.iterrows():
        pname = player.get("name", "Unknown")
        pos = player.get("position", "—")
        pdata = attendance[attendance["player_name"].str.lower() == pname.lower()]

        attend = (pdata["status"] == "attend").sum()
        absent = (pdata["status"] == "absent").sum()
        late = (pdata["status"] == "late").sum()
        excused = (pdata["status"] == "excused").sum()

        attend_pct = round(((attend + excused) / total_sessions) * 100, 1)
        absent_pct = round((absent / total_sessions) * 100, 1)
        late_pct = round((late / total_sessions) * 100, 1)
        excused_pct = round((excused / total_sessions) * 100, 1)

        color = "#00e676" if attend_pct >= 80 else "#ffd54f" if attend_pct >= 50 else "#ff5252"

        st.markdown(
            f"""
            <div class="player-card">
                <div class="player-header">
                    <div class="player-name">{pname}</div>
                    <div class="player-position">{pos}</div>
                </div>
                <div class="metric-container">
                    <div class="metric attend"><h4>{attend_pct}%</h4><span>Attend</span></div>
                    <div class="metric late"><h4>{late_pct}%</h4><span>Late</span></div>
                    <div class="metric absent"><h4>{absent_pct}%</h4><span>Absent</span></div>
                    <div class="metric excused"><h4>{excused_pct}%</h4><span>Excused</span></div>
                </div>
                <div class="progress-bar">
                    <div class="progress-inner" style="width:{attend_pct}%; background:{color};"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )



def admin_training_attendance_all():
    st.markdown("<h2 class='main-heading'>📈 Training Attendance – All Players & Sessions</h2>", unsafe_allow_html=True)

    att = read_csv_safe(TRAINING_ATTEND_FILE)
    sessions = read_csv_safe(TRAINING_SESSIONS_FILE)

    if att.empty or sessions.empty:
        st.info("No attendance yet.")
        return

    # 🩹 Backward compatibility: rename old column if exists
    if "timestamp" in att.columns and "marked_at" not in att.columns:
        att = att.rename(columns={"timestamp": "marked_at"})

    # Color table
    st.caption("Latest Attendance Records")
    show = att.sort_values("marked_at", ascending=False).copy()
    st.dataframe(
        show.style.applymap(_attendance_color, subset=["status"]),
        use_container_width=True
    )

    # Aggregates by player
    st.subheader("By Player – Attendance %")
    byp = (
        att.groupby("player_name")["status"]
        .apply(lambda s: round((s.str.lower() == "yes").mean() * 100, 1))
        .reset_index()
    )
    byp.columns = ["player_name", "attendance_%"]
    st.dataframe(byp.sort_values("attendance_%", ascending=False), use_container_width=True)

    # Aggregates by session
    st.subheader("By Session – Yes/No Counts")
    yes_counts = (att["status"].str.lower() == "yes").groupby(att["session_id"]).sum().rename("yes")
    no_counts = (att["status"].str.lower() == "no").groupby(att["session_id"]).sum().rename("no")
    agg = pd.concat([yes_counts, no_counts], axis=1).fillna(0).astype(int).reset_index()
    agg = agg.merge(sessions[["session_id", "date", "time", "title"]], on="session_id", how="left")
    st.dataframe(agg.sort_values(["date", "time"]), use_container_width=True)



# ---------------- Extract Player Stats ----------------
import google.generativeai as genai
import json
import pandas as pd


# ---------------- Extract Player Stats ----------------
import base64

def extract_player_stats(image_file) -> pd.DataFrame:
    """
    Use Gemini to extract per-player stats from an uploaded image.
    Expected columns: player_name, rating, goals, assists
    Returns a pandas DataFrame.
    """
    model = _gemini_client()
    if model is None:
     st.error("Gemini model not available. Check your API key or model name.")
     return pd.DataFrame(columns=["player_name", "rating", "goals", "assists"])

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

POSITION_MAP = {
    # Goalkeeper
    "GK": "Goalkeeper",

    # Defenders
    "CB": "Defender",
    "LCB": "Defender",
    "RCB": "Defender",
    "LB": "Defender",
    "RB": "Defender",
    "RWB": "Defender",
    "LWB": "Defender",

    # Midfielders
    "CDM": "Midfielder",
    "CM": "Midfielder",
    "LCM": "Midfielder",
    "RCM": "Midfielder",
    "CAM": "Midfielder",
    "RM": "Midfielder",
    "LM": "Midfielder",

    # Wingers
    "LW": "Winger",
    "RW": "Winger",

    # Attackers
    "CF": "Striker",
    "ST": "Striker",
    "SS": "Striker"
}

    
def admin_upload_player_stats_page():
    st.title("📸 Upload Stats")

    # ✅ Fetch matches
    matches = _supabase_client().table("matches").select("match_id, opponent, date").execute()
    match_options = [f'{m["match_id"]} - {m["opponent"]} ({m["date"]})' for m in matches.data] if matches.data else []

    if not match_options:
        st.warning("⚠️ No matches found. Please add a match first in the Matches page.")
        return

    selected_match = st.selectbox("Select Match", match_options)
    match_id = int(selected_match.split(" - ")[0])

    # ✅ Fetch players with positions
    players = _supabase_client().table("players").select("player_id, name, position").execute()
    players_df = pd.DataFrame(players.data) if players.data else pd.DataFrame(columns=["player_id", "name", "position"])

    img_file = st.file_uploader("Upload stats photo", type=["jpg", "jpeg", "png"])
    if img_file:
        st.image(img_file, caption="Uploaded stats image", use_container_width=True)

        if st.button("Extract Stats with Gemini"):
            with st.spinner("Extracting stats..."):
                df = extract_player_stats(img_file)  # Your existing OCR/AI extraction function

            if df.empty:
                st.error("❌ No stats extracted. Try with a clearer image.")
                return

            st.success("✅ Stats extracted successfully!")
            st.dataframe(df)

            # Match extracted names to players list (to get player_id and position)
            merged = df.merge(players_df, left_on="player_name", right_on="name", how="left")

            # 🚨 Check for unknown players
            unknown = merged[merged["player_id"].isna()]
            if not unknown.empty:
                st.error(f"❌ These players are not in the squad list: {unknown['player_name'].tolist()}")
                st.warning("⚠️ No stats have been saved. Please fix player names before retrying.")
                return  # 🔥 Stop execution here, nothing gets saved

            # ✅ Only valid players proceed
            valid_rows = merged.dropna(subset=["player_id"])

            # Save stats to Supabase
            for _, row in valid_rows.iterrows():
                try:
                    # ✅ Always get position from players file
                    player_pos = row.get("position") or "N/A"

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
                            "position": player_pos
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
                            "position": player_pos
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
    fig.update_layout(height=400, title=title, margin=dict(l=10,r=10,t=40,b=10))
    st.plotly_chart(fig, use_container_width=True)

def manager_tactics_text_page():
    st.title("📋 Team Tactical Plans")
    st.caption("Manager access only — Create, review, and save tactical strategies.")

    tactics = read_csv_safe(TACTICS_FILE)

    # === CURRENT TACTICAL PLANS ===
    with st.expander("📖 View Saved Tactical Plans", expanded=True):
        if not tactics.empty:
            st.dataframe(
                tactics.drop(columns=["image_path"], errors="ignore"),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("⚠️ No tactical plans saved yet.")

    st.divider()
    st.subheader("📝 Create or Update Tactical Plan")

    # === TACTICAL FORM ===
    with st.form("tactics_form"):
        col1, col2 = st.columns(2)
        with col1:
            formation = st.selectbox("Formation", FORMATIONS, index=0)
        with col2:
            style_of_play = st.selectbox(
                "Style of Play",
                ["High Press & Quick Build-up", "Balanced Play", "Defensive & Counter", "Possession Focus"],
                index=1
            )

        defensive_plan = st.text_area(
            "🛡️ Defensive Strategy",
            placeholder="E.g., Stay compact, press in packs, track wingers tightly..."
        )

        offensive_plan = st.text_area(
            "⚽ Offensive Strategy",
            placeholder="E.g., Build from the back, switch play quickly, overlap fullbacks..."
        )

        key_players = st.text_area(
            "⭐ Key Player Instructions",
            placeholder="E.g., GK: Distribute short, ST: Stay central, Wingers: Cut inside..."
        )

        extra_notes = st.text_area(
            "🗒️ Additional Notes",
            placeholder="Any final reminders or match-specific adjustments..."
        )

        submitted = st.form_submit_button("💾 Save Tactical Plan", type="primary")

    # === SAVE LOGIC ===
    if submitted:
        new_row = {
            "formation": formation,
            "roles": key_players.strip(),
            "instructions": f"Style: {style_of_play}\n\n"
                            f"Defensive: {defensive_plan.strip()}\n\n"
                            f"Offensive: {offensive_plan.strip()}",
            "notes": extra_notes.strip(),
            "image_path": None,
            "updated_by": st.session_state.get("auth", {}).get("name", "Manager"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Prevent duplicate rows by formation + timestamp
        tactics = pd.concat([tactics, pd.DataFrame([new_row])], ignore_index=True)
        write_csv_safe(tactics, TACTICS_FILE)

        st.success("✅ Tactical plan saved successfully!")
        st.rerun()

def manager_tactics_board_page():
    st.subheader("⚽ Manager – Assign Players to Formation")

    # === Internal function: formation layout ===
    def formation_layout(formation: str):
        layouts = {
            "4-3-3": ["GK", "RB", "RCB", "LCB", "LB", "RCM", "CDM", "LCM", "RW", "ST", "LW"],
            "4-2-3-1": ["GK", "RB", "RCB", "LCB", "LB", "RDM", "LDM", "RAM", "CAM", "LAM", "ST"],
            "4-4-2": ["GK", "RB", "RCB", "LCB", "LB", "RM", "RCM", "LCM", "LM", "RST", "LST"],
            "3-5-2": ["GK", "RCB", "CB", "LCB", "RM", "RDM", "LDM", "CAM", "LM", "RST", "LST"],
            "3-4-3": ["GK", "RCB", "CB", "LCB", "RM", "RCM", "LCM", "LM", "RW", "ST", "LW"],
            "5-2-1-2": ["GK", "RWB", "RCB", "CB", "LCB", "LWB", "RCM", "LCM", "CAM", "RST", "LST"],
            "4-1-2-1-2": ["GK", "RB", "RCB", "LCB", "LB", "CDM", "RCM", "LCM", "CAM", "RST", "LST"],
        }
        return layouts.get(formation, layouts["4-3-3"])

    # === Main logic ===
    players = read_csv_safe(PLAYERS_FILE)
    if players.empty:
        st.info("No players in roster. Ask Admin to add players first.")
        return

    active_players = sorted(players[players.get("active", True) == True]["name"].dropna().astype(str).unique())

    formation = st.selectbox("Formation", FORMATIONS, key="board_formation")
    positions = formation_layout(formation)

    pos_df = read_csv_safe(TACTICS_POS_FILE)
    prev = pos_df[pos_df["formation"] == formation].copy()
    if not prev.empty:
        prev = prev.sort_values("updated_at").groupby("position").tail(1).set_index("position")

    st.caption("Each player can be assigned to **one** position only. Picked players disappear from other dropdowns.")

    assignments = []
    cols = st.columns(3)
    num_slots = len(positions)

    # Initialize defaults
    for idx, pos_label in enumerate(positions):
        key = f"board_sel::{formation}::{pos_label}::{idx}"
        if key not in st.session_state:
            default_player = None
            if isinstance(prev, pd.DataFrame) and not prev.empty and pos_label in prev.index:
                default_player = prev.loc[pos_label, "player_name"]
            if default_player not in active_players:
                default_player = "—"
            st.session_state[key] = default_player if default_player else "—"

    # Render dropdowns
    for idx, pos_label in enumerate(positions):
        key = f"board_sel::{formation}::{pos_label}::{idx}"
        taken_elsewhere = {
            st.session_state.get(f"board_sel::{formation}::{positions[j]}::{j}", "—")
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
        })

    # Save & Clear buttons
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Save Lineup", use_container_width=True):
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
                st.success("✅ Lineup saved.")
                st.rerun()

    with c2:
        if st.button("🧹 Clear Lineup", type="secondary", use_container_width=True):
            for idx, pos_label in enumerate(positions):
                key = f"board_sel::{formation}::{pos_label}::{idx}"
                st.session_state[key] = "—"
            st.rerun()

    # === Show as styled list instead of pitch ===
    st.markdown("### 📋 Current Lineup")
    st.markdown(
        """
        <style>
        .lineup-card {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        }
        .lineup-pos {
            font-size: 13px;
            font-weight: bold;
            color: #34D399;
        }
        .lineup-name {
            font-size: 16px;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    for a in assignments:
        if a["player_name"]:
            st.markdown(
                f"""
                <div class="lineup-card">
                    <div class="lineup-pos">{a['position']}</div>
                    <div class="lineup-name">{a['player_name']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    




# -------------------------------
# PLAYER PAGES
# -------------------------------
import re, json

EXPECTED_FIELDS = {
    "player_name": str,
    "position": str,
    "match_id": int,
    "rating": float,
    "goals": int,
    "assists": int,
    "shots": int,
    "shot_accuracy": float,
    "passes": int,
    "pass_accuracy": float,
    "dribbles": int,
    "dribble_success": float,
    "tackles": int,
    "tackle_success": float,
    "offsides": int,
    "fouls_committed": int,
    "possession_won": int,
    "possession_lost": int,
    "minutes_played": int,
    "distance_covered": float,
    "distance_sprinted": float,
    "yellow_cards": int,
    "red_cards": int,
}

def _clean_gemini_text(raw_text: str) -> str:
    """Strip markdown/code fences and return possible JSON string."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n", "", text)
        text = re.sub(r"\n```$", "", text)
    return text

def _safe_parse_json(text: str) -> dict | None:
    """Try to load JSON dict from Gemini text, fallback to regex extract."""
    try:
        data = json.loads(text)
        if isinstance(data, dict): 
            return data
        if isinstance(data, list) and data: 
            return data[0]
    except Exception:
        pass

    # fallback: extract first {...}
    m = re.search(r"(\{.*\})", text, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(1))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return None

def _validate_stats(data: dict) -> dict:
    """Validate and coerce to expected schema with defaults."""
    cleaned = {}
    for key, ftype in EXPECTED_FIELDS.items():
        val = data.get(key)
        if val is None:
            cleaned[key] = "" if ftype is str else 0
        else:
            try:
                cleaned[key] = ftype(val)
            except Exception:
                # if type conversion fails, fallback to default
                cleaned[key] = "" if ftype is str else 0
    return cleaned

def extract_stats_from_image(image_bytes: bytes):
    """
    Send image to Gemini, return validated stats dict or None on failure.
    """
    try:
        model = _gemini_client()
        img = {"mime_type": "image/png", "data": image_bytes}

        prompt = """
You are a precise OCR and data extraction system analyzing a football performance stats screen.

Goal:
Extract ONLY the statistics for the player that is SELECTED or HIGHLIGHTED in the list (the row that is visually highlighted or focused). 
Ignore all other players completely.

Output Schema (all keys required):
{
  "player_name": string,
  "position": string,
  "match_id": string,        // leave "" if not visible
  "rating": float,
  "goals": int,
  "assists": int,
  "shots": int,
  "shot_accuracy": int,      // percent, number only (e.g. 60 not "60%")
  "passes": int,
  "pass_accuracy": int,      // percent, number only
  "dribbles": int,
  "dribble_success": int,    // percent, number only
  "tackles": int,
  "tackle_success": int,     // percent, number only
  "offsides": int,
  "fouls_committed": int,
  "possession_won": int,
  "possession_lost": int,
  "minutes_played": int,
  "distance_covered": float, // km
  "distance_sprinted": float,// km
  "yellow_cards": int,
  "red_cards": int
}

Rules:
- Extract data ONLY for the highlighted player (example: if the row “modric” is highlighted, extract his stats).
- The player's name and position should come from the left-side list.
- Match ID is not shown, so return "".
- Numbers must be raw (no %, km, or symbols).
- Missing data → use 0 (for numbers) or "" (for strings).
- Output MUST be valid JSON — no text or comments outside the JSON.
"""


        resp = model.generate_content([prompt, img])
        raw_text = _clean_gemini_text(resp.text or "")

        parsed = _safe_parse_json(raw_text)
        if not parsed:
            st.error("❌ Could not parse valid JSON from Gemini response.")
            st.code(raw_text, language="json")
            return None

        stats = _validate_stats(parsed)
        return stats

    except Exception as e:
        st.error(f"❌ Error extracting stats: {e}")
        return None



def get_player_id_by_name(name: str):
    """Return player_id (int) for a given player name, or None if not found."""
    name = (name or "").strip()
    if not name:
        return None
    sb = _supabase_client()
    try:
        res = sb.table("players").select("player_id").eq("name", name).execute()
        rows = res.data or []
        if rows:
            return int(rows[0].get("player_id"))
    except Exception:
        # fallback to local CSV
        players = read_csv_safe(PLAYERS_FILE)
        if not players.empty:
            sel = players[players["name"].str.lower() == name.lower()]
            if not sel.empty:
                return int(sel.iloc[0]["player_id"])
    return None


import re
import json
import pandas as pd
import streamlit as st



def player_upload_stats_page():
    st.markdown("<h2 class='main-heading'>📸 Upload My Stats</h2>", unsafe_allow_html=True)
    current_name = st.session_state.auth.get("name", "").strip()
    if not current_name:
        st.error("❌ You must be logged in to upload stats.")
        return

    # ✅ Fetch matches (default to most recent)
    matches = read_csv_safe(MATCHES_FILE)
    match_id_choice = None
    if not matches.empty:
        matches_sorted = matches.sort_values("date", ascending=False)
        labels = [f"{r['date']} – {r['opponent']}" for _, r in matches_sorted.iterrows()]
        label_to_id = {labels[i]: int(matches_sorted.iloc[i]["match_id"]) for i in range(len(labels))}
        chosen_label = st.selectbox("Link to match", labels, index=0)
        match_id_choice = label_to_id.get(chosen_label)

    uploaded = st.file_uploader("Upload your match stats image", type=["png", "jpg", "jpeg"])
    if not uploaded:
        return

    st.image(uploaded, caption="Preview", use_container_width=True)

    if st.button("📤 Extract & Save Stats"):
        try:
            with st.spinner("⏳ Uploading and processing your stats..."):
                img_bytes = uploaded.read()
                parsed = extract_stats_from_image(img_bytes)
                if not parsed:
                    st.error("❌ Could not extract stats. Please try a clearer image.")
                    return

                # ✅ Validate player identity
                parsed_name = (parsed.get("player_name") or "").strip()
                if parsed_name.lower() != current_name.lower():
                    st.error("❌ Player name in uploaded stats does not match your account. Contact admin.")
                    return

                # ✅ Get player_id and position from roster
                sb = _supabase_client()
                player_row = sb.table("players").select("player_id, position").eq("name", current_name).execute()
                if not player_row.data:
                    st.error("❌ Player not found in roster. Contact admin.")
                    return
                player_id = player_row.data[0]["player_id"]
                player_pos = player_row.data[0].get("position") or "N/A"

                # ✅ Determine match_id (parsed > selected > None)
                parsed_match_id = None
                try:
                    if parsed.get("match_id"):
                        parsed_match_id = int(float(parsed["match_id"]))
                except Exception:
                    pass
                match_id = parsed_match_id or match_id_choice
                if match_id is None:
                    st.error("❌ No match found to attach stats to. Please ask admin to create a match first.")
                    return

                # ✅ Prepare record
                record = {"player_name": current_name, "player_id": player_id, "match_id": int(match_id)}
                allowed_keys = [
                    "rating","goals","assists","shots","shot_accuracy","passes","pass_accuracy",
                    "dribbles","dribble_success","tackles","tackle_success","offsides","fouls_committed",
                    "possession_won","possession_lost","minutes_played","distance_covered","distance_sprinted",
                    "yellow_cards","red_cards"
                ]
                for k in allowed_keys:
                    if k in parsed:
                        record[k] = parsed[k]
                record["position"] = player_pos  # ✅ Always take from roster

                # ✅ Call UPSERT function
                sb.rpc("upsert_player_stats", {
                    "p_match_id": record["match_id"],
                    "p_player_name": record["player_name"],
                    "p_position": record["position"],
                    "p_goals": record.get("goals") or 0,
                    "p_assists": record.get("assists") or 0,
                    "p_rating": record.get("rating") or 0.0,
                    "p_yellow_cards": record.get("yellow_cards") or 0,
                    "p_red_cards": record.get("red_cards") or 0,
                    "p_shots": record.get("shots") or 0,
                    "p_passes": record.get("passes") or 0,
                    "p_dribbles": record.get("dribbles") or 0,
                    "p_tackles": record.get("tackles") or 0,
                    "p_offsides": record.get("offsides") or 0,
                    "p_fouls_committed": record.get("fouls_committed") or 0,
                    "p_possession_won": record.get("possession_won") or 0,
                    "p_possession_lost": record.get("possession_lost") or 0,
                    "p_minutes_played": record.get("minutes_played") or 0,
                    "p_shot_accuracy": record.get("shot_accuracy") or 0.0,
                    "p_pass_accuracy": record.get("pass_accuracy") or 0.0,
                    "p_dribble_success": record.get("dribble_success") or 0.0,
                    "p_tackle_success": record.get("tackle_success") or 0.0,
                    "p_distance_covered": record.get("distance_covered") or 0.0,
                    "p_distance_sprinted": record.get("distance_sprinted") or 0.0,
                    "p_player_id": record["player_id"],
                }).execute()

                # ✅ Confirmation message
                st.success(f"✅ Stats uploaded successfully! Position assigned from roster: {player_pos}")

        except Exception as e:
            st.error(f"❌ Error while processing stats: {e}")





# Theme colors
CYAN = "#00C0FA"
DARK_BLUE = "#0C182E"
BLUE = "#015EEA"
WHITE = "#FFFFFF"

import streamlit as st
import streamlit.components.v1 as components

def player_tactics_text_page():
    st.subheader("📋 Team Tactical Plan")

    tactics = read_csv_safe(TACTICS_FILE)
    if tactics.empty:
        st.info("⚠️ No tactical plan has been set yet.")
        return

    latest = tactics.sort_values("updated_at", ascending=False).iloc[0]

    # Replace newlines with <br>
    instructions_html = latest["instructions"].replace("\n", "<br>")
    roles_html = latest["roles"].replace("\n", "<br>")
    notes_html = latest["notes"].replace("\n", "<br>") if latest.get("notes") else ""

    # Full HTML page
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                background: #0C182E;
                color: white;
                font-family: 'Segoe UI', sans-serif;
                margin: 0;
                padding: 0;
            }}
            .tactics-card {{
                background: linear-gradient(160deg, #0C182E 40%, #000000 100%);
                border: 1px solid rgba(0, 192, 250, 0.4);
                border-radius: 20px;
                padding: 30px;
                margin: 20px auto;
                max-width: 900px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.5);
            }}
            .tactics-title {{
                font-size: 30px;
                font-weight: bold;
                text-align: center;
                color: #00C0FA;
                margin-bottom: 25px;
            }}
            .tactics-subtitle {{
                font-size: 22px;
                font-weight: bold;
                margin-top: 20px;
                color: #00C0FA;
                border-bottom: 2px solid rgba(0,192,250,0.4);
                padding-bottom: 5px;
            }}
            .tactics-content {{
                font-size: 18px;
                margin-top: 10px;
                line-height: 1.7;
            }}
            .tactics-footer {{
                font-size: 14px;
                color: rgba(255,255,255,0.7);
                margin-top: 25px;
                text-align: right;
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        <div class="tactics-card">
            <div class="tactics-title">{latest['formation']}</div>

            <div class="tactics-subtitle">📝 Instructions</div>
            <div class="tactics-content">{instructions_html}</div>

            <div class="tactics-subtitle">🎯 Key Player Roles</div>
            <div class="tactics-content">{roles_html}</div>
    """

    if notes_html:
        html_content += f"""
            <div class="tactics-subtitle">📌 Notes</div>
            <div class="tactics-content">{notes_html}</div>
        """

    html_content += f"""
            <div class="tactics-footer">
                Last updated by <b>{latest['updated_by']}</b> on {latest['updated_at']}
            </div>
        </div>
    </body>
    </html>
    """

    # 🔥 Render HTML directly
    components.html(html_content, height=700, scrolling=True)





def player_tactics_board_page():
    st.subheader("📋 Tactics Board – Starting XI")

    pos_df = read_csv_safe(TACTICS_POS_FILE)
    if pos_df.empty:
        st.info("No tactics board set yet.")
        return

    latest_time = pos_df["updated_at"].max()
    latest = pos_df[pos_df["updated_at"] == latest_time].copy()
    if latest.empty:
        st.info("No tactics board found.")
        return

    formation = latest["formation"].iloc[0]
    updated_by = latest["updated_by"].iloc[0] if "updated_by" in latest else "Manager"
    st.caption(f"Formation: **{formation}** | Last updated by **{updated_by}** on {latest_time}")

    # === Group by lines ===
    gk_positions = ["GK"]
    defence_positions = ["RB", "RCB", "CB", "LCB", "LB", "RWB", "LWB"]
    midfield_positions = ["CDM", "RDM", "LDM", "RCM", "LCM", "CM", "CAM", "RAM", "LAM", "RM", "LM"]
    attack_positions = ["RW", "LW", "ST", "RST", "LST"]

    def get_line(pos):
        if pos in gk_positions: return "Goalkeeper"
        if pos in defence_positions: return "Defence"
        if pos in midfield_positions: return "Midfield"
        if pos in attack_positions: return "Attack"
        return "Other"

    latest["line"] = latest["position"].apply(get_line)

    position_order = {
        "GK": 0, "RB": 1, "RCB": 2, "CB": 3, "LCB": 4, "LB": 5,
        "RWB": 6, "LWB": 7,
        "CDM": 8, "RDM": 9, "LDM": 10, "RCM": 11, "LCM": 12,
        "CM": 13, "CAM": 14, "RAM": 15, "LAM": 16,
        "RM": 17, "LM": 18,
        "RW": 19, "LW": 20, "ST": 21, "RST": 22, "LST": 23
    }
    latest["order"] = latest["position"].map(position_order).fillna(99)
    latest = latest.sort_values(["line", "order"])

    # === THEME COLORS ===
    DARK_BLUE = "#0C182E"
    BLUE = "#015EEA"
    SKY_BLUE = "#00C0FA"
    WHITE = "#FFFFFF"

    st.markdown(f"""
    <style>
    /* Import professional sporty fonts */
    @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;700&family=Orbitron:wght@700;900&display=swap');

    /* Background */
    .stApp {{
        background: linear-gradient(160deg, {DARK_BLUE} 40%, #000000 100%);
    }}
    /* Section titles */
    .line-title {{
        font-family: 'Oswald', sans-serif;
        font-size: 24px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 3px;
        text-align: center;
        margin: 25px 0 15px 0;
        color: {SKY_BLUE};
        text-shadow: 0px 0px 6px rgba(255,255,255,0.6);
        font-stretch: expanded;
        font-style: oblique;
    }}
    /* Player grid */
    .line-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 18px;
        margin-bottom: 40px;
    }}
    /* Player card */
    .player-card {{
        background: linear-gradient(145deg, {BLUE} 10%, {DARK_BLUE} 90%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 18px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 6px 18px rgba(0,0,0,0.5);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }}
    .player-card:hover {{
        transform: scale(1.07);
        box-shadow: 0 0 20px {SKY_BLUE};
    }}
    /* Position label */
    .pos-label {{
        font-family: 'Oswald', sans-serif;
        font-size: 15px;
        font-weight: 700;
        font-stretch: semi-expanded;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: {SKY_BLUE};
        margin-bottom: 8px;
    }}
    /* Player name */
    .player-name {{
        font-family: 'Orbitron', sans-serif;
        font-size: 24px;
        font-weight: 900;
        font-stretch: expanded;
        font-style: oblique;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: {WHITE};
    }}
    </style>
""", unsafe_allow_html=True)

    # === Render cards by line ===
    for line in ["Goalkeeper", "Defence", "Midfield", "Attack"]:
        line_players = latest[latest["line"] == line]
        if not line_players.empty:
            st.markdown(f"<div class='line-title'>{line}</div>", unsafe_allow_html=True)
            st.markdown("<div class='line-grid'>", unsafe_allow_html=True)
            for _, row in line_players.iterrows():
                player_name = row["player_name"] if row["player_name"] else "—"
                st.markdown(f"""
                    <div class="player-card">
                        <div class="pos-label">{row['position']}</div>
                        <div class="player-name">{player_name}</div>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)




import plotly.graph_objects as go

def cumulative_metrics(df):
    metrics = {}

    # Totals
    metrics["Shots"] = df["shots"].sum()
    metrics["Passes"] = df["passes"].sum()
    metrics["Dribbles"] = df["dribbles"].sum()
    metrics["Tackles"] = df["tackles"].sum()
    metrics["Goals"] = df["goals"].sum()
    metrics["Assists"] = df["assists"].sum()
    metrics["Possession Won"] = df["possession_won"].sum()
    metrics["Possession Lost"] = df["possession_lost"].sum()
    metrics["Distance Covered (km)"] = df["distance_covered"].sum()
    
    # Ratings → average is still meaningful
    metrics["Rating"] = round(df["rating"].mean(), 2) if "rating" in df else 0

    # Accurate passes
    total_passes = df["passes"].sum()
    success_passes = (df["passes"] * df["pass_accuracy"] / 100).sum()
    metrics["Pass Accuracy %"] = round(success_passes / total_passes * 100, 1) if total_passes > 0 else 0

    # Dribble success
    total_dribbles = df["dribbles"].sum()
    success_dribbles = (df["dribbles"] * df["dribble_success"] / 100).sum()
    metrics["Dribble Success %"] = round(success_dribbles / total_dribbles * 100, 1) if total_dribbles > 0 else 0

    # Tackles success
    total_tackles = df["tackles"].sum()
    success_tackles = (df["tackles"] * df["tackle_success"] / 100).sum()
    metrics["Tackle Success %"] = round(success_tackles / total_tackles * 100, 1) if total_tackles > 0 else 0

    return metrics



import plotly.graph_objects as go

def player_my_stats_page():
    st.markdown("<h1 class='super-head'>📊 My Radar Analysis</h1>", unsafe_allow_html=True)

    # ===== Ensure Current Player =====
    current_name = st.session_state.auth.get("name", "").strip()
    if not current_name:
        st.error("❌ You must be logged in to view your radar stats.")
        return

    # ===== Load Stats & Matches =====
    stats = read_csv_safe(PLAYER_STATS_FILE)
    matches = read_csv_safe(MATCHES_FILE)
    if stats.empty or matches.empty:
        st.info("⚠️ No stats or matches available.")
        return

    # === Merge to bring in result column ===
    df = stats[stats["player_name"].str.lower() == current_name.lower()]
    if df.empty:
        st.warning("⚠️ No stats found for you.")
        return

    df = df.merge(matches[["match_id", "result"]], on="match_id", how="left")

    # === Matches Played & Results ===
    matches_played = df["match_id"].nunique()
    wins = df[df["result"].str.lower().isin(["w", "win"])]["match_id"].nunique()
    draws = df[df["result"].str.lower().isin(["d", "draw"])]["match_id"].nunique()
    losses = df[df["result"].str.lower().isin(["l", "loss"])]["match_id"].nunique()

    st.markdown(f"""
    <div style="background: rgba(0,192,250,0.1); padding:15px; border-radius:10px; margin-bottom:20px; text-align:center;">
        <h3 style="color:#00C0FA; margin:0;">📅 Season Summary</h3>
        <p style="margin:5px 0; font-size:16px; color:white;">
            Matches Played: <b>{matches_played}</b> |
            ✅ Wins: <b>{wins}</b> |
            🤝 Draws: <b>{draws}</b> |
            ❌ Losses: <b>{losses}</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # === Cumulative Metrics Function ===
    def cumulative_metrics(df):
        metrics = {}
        metrics["⚽ Goals"] = df["goals"].sum()
        metrics["🎯 Assists"] = df["assists"].sum()
        metrics["🔫 Shots"] = df["shots"].sum()
        metrics["📨 Passes"] = df["passes"].sum()
        metrics["🎯 Pass Accuracy %"] = (
            round(((df["passes"] * df["pass_accuracy"] / 100).sum() / df["passes"].sum()) * 100, 1)
            if df["passes"].sum() > 0 else 0
        )
        metrics["⚡ Dribbles"] = df["dribbles"].sum()
        metrics["⚡ Dribble Success %"] = (
            round(((df["dribbles"] * df["dribble_success"] / 100).sum() / df["dribbles"].sum()) * 100, 1)
            if df["dribbles"].sum() > 0 else 0
        )
        metrics["🛡️ Tackles"] = df["tackles"].sum()
        metrics["🛡️ Tackle Success %"] = (
            round(((df["tackles"] * df["tackle_success"] / 100).sum() / df["tackles"].sum()) * 100, 1)
            if df["tackles"].sum() > 0 else 0
        )
        metrics["💪 Possession Won"] = df["possession_won"].sum()
        metrics["❌ Possession Lost"] = df["possession_lost"].sum()
        metrics["🏃 Distance Covered (km)"] = round(df["distance_covered"].sum(), 1)
        metrics["⭐ Avg Rating"] = round(df["rating"].mean(), 2) if "rating" in df else 0
        return metrics

    metrics = cumulative_metrics(df)

    # === Radar Chart with Numbers ===
    categories = list(metrics.keys())
    values = list(metrics.values())

    fig = go.Figure()

    # Main radar shape
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        name=current_name,
        line_color="#015EEA"
    ))

    # Push numbers outward along axis
    max_val = max(values) if values else 1
    label_values = [v + (0.08 * max_val) if v > 0 else 0.1 for v in values]

    fig.add_trace(go.Scatterpolar(
        r=label_values,
        theta=categories,
        mode="text",
        text=[str(v) for v in values],
        textfont=dict(color="#66CCFF", size=9, family="Arial Black"),  # 👈 smaller + softer color
        showlegend=False
    ))

    # Layout styling
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                gridcolor="#666",
                linecolor="#888",
                tickfont=dict(color="#00C0FA", size=12),
            ),
            angularaxis=dict(
                tickfont=dict(color="#FFFFFF", size=12)
            )
        ),
        title=f"Radar Analysis – {current_name} (Cumulative Totals)",
        title_font=dict(color="#00C0FA", size=18),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig, use_container_width=True)

    # === Styled Stats Table ===
    st.markdown("### 📋 Detailed Cumulative Stats")

    table_html = """
    <style>
        .stats-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        .stats-table th, .stats-table td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .stats-table th {
            background: rgba(0,192,250,0.2);
            color: #00C0FA;
            font-weight: 700;
            text-transform: uppercase;
        }
        .stats-table td {
            color: #FFFFFF;
        }
        .stats-table tr:hover {
            background: rgba(255,255,255,0.05);
        }
    </style>
    <table class="stats-table">
        <tr><th>Metric</th><th>Value</th></tr>
    """
    for metric, value in metrics.items():
        table_html += f"<tr><td>{metric}</td><td>{value}</td></tr>"
    table_html += "</table>"

    st.markdown(table_html, unsafe_allow_html=True)



def calculate_fair_score(row, match_df):
    """Calculate fair player score with role-specific balanced weightings (match-based only)."""

    def safe_get(r, col, default=0):
        try:
            val = r[col] if col in r else default
            if pd.isna(val):
                return default
            return val
        except Exception:
            return default

    score = 0

    # --- Normalization Factor (per 90 minutes) ---
    minutes = safe_get(row, "minutes_played", 0)
    factor = (minutes / 90) if minutes and minutes > 0 else 1

    pos = (safe_get(row, "position", "") or "").strip()

    # -------------------------
    # 🧤 Goalkeepers
    # -------------------------
    if pos == "Goalkeeper":
        score += (safe_get(row, "goals") * 10) / factor
        score += (safe_get(row, "assists") * 5) / factor
        score += (safe_get(row, "passes") * 0.05) / factor
        score += safe_get(row, "pass_accuracy") * 0.3
        score += (safe_get(row, "possession_won") * 0.3) / factor
        score -= (safe_get(row, "possession_lost") * 0.3) / factor
        score += safe_get(row, "rating") * 2
        # Clean sheet bonus
        if match_df is not None and not match_df.empty:
            match_id = safe_get(row, "match_id")
            opp = match_df[match_df["match_id"] == match_id]["their_score"].values
            if opp.size > 0 and opp[0] == 0:
                score += 7

    # -------------------------
    # 🛡️ Defenders
    # -------------------------
    elif pos == "Defender":
        score += (safe_get(row, "goals") * 7) / factor
        score += (safe_get(row, "assists") * 4) / factor
        score += (safe_get(row, "shots") * 0.5) / factor
        score += (safe_get(row, "tackles") * 1.5) / factor
        score += safe_get(row, "tackle_success") * 0.7
        score += (safe_get(row, "possession_won") * 1.0) / factor
        score -= (safe_get(row, "possession_lost") * 0.5) / factor
        score += (safe_get(row, "passes") * 0.1) / factor
        score += safe_get(row, "pass_accuracy") * 0.3
        score += safe_get(row, "distance_covered") * 0.2 / factor
        score += safe_get(row, "rating") * 2
        # Clean sheet bonus
        if match_df is not None and not match_df.empty:
            match_id = safe_get(row, "match_id")
            opp = match_df[match_df["match_id"] == match_id]["their_score"].values
            if opp.size > 0 and opp[0] == 0:
                score += 5

    # -------------------------
    # 🎩 Midfielders
    # -------------------------
    elif pos == "Midfielder":
        score += (safe_get(row, "goals") * 5) / factor
        score += (safe_get(row, "assists") * 4) / factor
        score += (safe_get(row, "shots") * 0.7) / factor
        score += (safe_get(row, "passes") * 0.2) / factor
        score += safe_get(row, "pass_accuracy") * 0.4
        score += (safe_get(row, "tackles") * 1.0) / factor
        score += safe_get(row, "tackle_success") * 0.5
        score += (safe_get(row, "possession_won") * 0.7) / factor
        score -= (safe_get(row, "possession_lost") * 0.5) / factor
        score += (safe_get(row, "dribbles") * 0.7) / factor
        score += safe_get(row, "dribble_success") * 0.4
        score += safe_get(row, "distance_covered") * 0.3 / factor
        score += safe_get(row, "rating") * 2

    # -------------------------
    # 🌀 Wingers
    # -------------------------
    elif pos == "Winger":
        score += (safe_get(row, "goals") * 4) / factor
        score += (safe_get(row, "assists") * 3) / factor
        score += (safe_get(row, "shots") * 1.0) / factor
        score += (safe_get(row, "dribbles") * 1.5) / factor
        score += safe_get(row, "dribble_success") * 0.7
        score += (safe_get(row, "tackles") * 0.5) / factor
        score += safe_get(row, "tackle_success") * 0.3
        score += (safe_get(row, "possession_won") * 0.5) / factor
        score -= (safe_get(row, "possession_lost") * 0.3) / factor
        score += (safe_get(row, "passes") * 0.1) / factor
        score += safe_get(row, "pass_accuracy") * 0.2
        score += safe_get(row, "distance_covered") * 0.2 / factor
        score += safe_get(row, "rating") * 2

    # -------------------------
    # ⚽ Strikers
    # -------------------------
    elif pos == "Striker":
        score += (safe_get(row, "goals") * 4) / factor
        score += (safe_get(row, "assists") * 2) / factor
        score += (safe_get(row, "shots") * 2.0) / factor
        score += (safe_get(row, "dribbles") * 1.0) / factor
        score += safe_get(row, "dribble_success") * 0.5
        score += (safe_get(row, "tackles") * 0.3) / factor
        score += safe_get(row, "tackle_success") * 0.2
        score += (safe_get(row, "possession_won") * 0.3) / factor
        score -= (safe_get(row, "possession_lost") * 0.2) / factor
        score += (safe_get(row, "passes") * 0.05) / factor
        score += safe_get(row, "pass_accuracy") * 0.1
        score += safe_get(row, "distance_covered") * 0.1 / factor
        score += safe_get(row, "rating") * 2

    return round(score, 2)






import random

def page_competition_hub():
    import streamlit as st

    st.markdown("<h1 style='text-align:center; color:#00C0FA;'>🏗️ Competition Hub</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='
            display:flex;
            flex-direction:column;
            align-items:center;
            justify-content:center;
            height:60vh;
            text-align:center;
            color:#9CA3AF;
        '>
            <h2 style='color:#00C0FA;'>🚧 Page Under Construction 🚧</h2>
            <p style='max-width:500px; font-size:18px;'>
                We're currently working on building an exciting new Competition Hub experience.  
                Stay tuned for updates!
            </p>
            <div style='margin-top:30px;'>
                <img src='https://cdn-icons-png.flaticon.com/512/3534/3534033.png' width='120'>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )




def admin_reports_page():
    
    st.markdown("<h2 class='main-heading'>Auto Match Report Generator</h2>", unsafe_allow_html=True)
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




def admin_competition_moderation_page():
    import streamlit as st

    st.markdown("<h2 style='text-align:center; color:#00C0FA;'>🏗️ Competition Moderation</h2>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style='
            display:flex;
            flex-direction:column;
            align-items:center;
            justify-content:center;
            height:60vh;
            text-align:center;
            color:#9CA3AF;
        '>
            <h3 style='color:#00C0FA;'>🚧 Page Under Construction 🚧</h3>
            <p style='max-width:500px; font-size:18px;'>
                The competition management tools (start, end, and moderation controls) are currently being built.
                Soon you’ll be able to start new competitions, track progress, and archive winners directly here.
            </p>
            <div style='margin-top:30px;'>
                <img src='https://cdn-icons-png.flaticon.com/512/6213/6213731.png' width='120'>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )









# -------------------------------
# ADMIN APP
# -------------------------------
def run_admin():
    render_header()

    # ✅ Add the new tab to the list
    tabs = [
        "🏠 Dashboard",
        "⚽ Matches",
        "📊 Player Stats",
        "📸 Upload Player Stats",
        "👤 Players",
        "📝 Training Sessions",
        "📋 Attendance",
        "📄 Reports",
        "🏆 Competition Moderation"   # 🆕 New tab
    ]

    # ✅ Add the new page mapping
    pages = {
        "🏠 Dashboard": page_dashboard,
        "⚽ Matches": admin_matches_page,
        "📊 Player Stats": admin_player_stats_page,
        "📸 Upload Player Stats": admin_upload_player_stats_page,
        "👤 Players": admin_players_crud_page,
        "📝 Training Sessions": admin_training_sessions_page,
        "📋 Attendance": admin_training_attendance_all,
        "📄 Reports": admin_reports_page,
        "🏆 Competition Moderation": admin_competition_moderation_page   # 🆕 Link to new function
    }

    # ✅ Render tabs and pages
    selected_tab = st.tabs(tabs)
    for i, tab_name in enumerate(tabs):
        with selected_tab[i]:
            pages[tab_name]()





# -------------------------------
# MANAGER APP
# -------------------------------
def run_manager():
    render_header()

    # Main Tabs
    main_tabs = st.tabs([
        "🏠 Dashboard",
        "📄 Tactics",
        "📋 Attendance",
        "📊 Radar",  
    ])

    # Main Tab: Dashboard
    with main_tabs[0]:
        page_dashboard()

    # Main Tab: Tactics (With Sub-Tabs)
    with main_tabs[1]:
        st.subheader("Tactics")
        tactics_tabs = st.tabs(["📝 Text View", "📈 Board View"])

        with tactics_tabs[0]:
            manager_tactics_text_page()

        with tactics_tabs[1]:
            manager_tactics_board_page()

    # Main Tab: Attendance
    with main_tabs[2]:
        manager_training_attendance_overview()

    # Main Tab: Radar
    with main_tabs[3]:
        manager_radar_page()




# -------------------------------
# PLAYER APP
# -------------------------------
def run_player():
    render_header()

    main_tabs = st.tabs([
        "🏠 Dashboard",
        "📊 Stats",
        "📋 Attendance",
        "📄 Tactics",
        "🏆 Competition Hub" 
    ])

    # Dashboard
    with main_tabs[0]:
        page_dashboard()

    # Stats (Upload + My Stats as sub-tabs)
    with main_tabs[1]:
        stats_tabs = st.tabs(["📊 My Stats", "📸 Upload Stats"])
        with stats_tabs[0]:
            player_my_stats_page()
        with stats_tabs[1]:
            player_upload_stats_page()

    # Attendance
    with main_tabs[2]:
        player_training_attendance_page()

    # Tactics
    with main_tabs[3]:
        tactics_tabs = st.tabs(["📝 Text View", "📈 Line Up"])
        with tactics_tabs[0]:
            player_tactics_text_page()
        with tactics_tabs[1]:
            player_tactics_board_page()
    # Competition Hub
    with main_tabs[4]:
        page_competition_hub()   # 🆕 Challenges + Player of Month + Gamification


 

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

        return

    role = st.session_state.auth["role"]
    if role == "admin":
        run_admin()
    elif role == "manager":
        run_manager()
    elif role == "player":
        run_player()

    else:
        logout()


if __name__ == "__main__":
    main()

## HEAD => SUPER EXP BLACK OBLIQUE
##  sub head SUPER EXP OBLIQUE

##  text =>EXPANDED MID
# WIDE MID


## NILE ESPORTS =>SUPER EXP BLACK
## TEXT  =>WIDE MID

## BUTTONS SKY BLUE