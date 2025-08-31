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
# PAGE CONFIG (mobile-first)
# -------------------------------
LOGO_URL = "https://github.com/mostafaasaad32/nile/raw/master/images/Artboard_1.png"

st.set_page_config(
    page_title="Nile SC Manager",
    page_icon="⚽",
    layout="wide",   # ✅ full width
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
    padding-bottom: 90px !important; /* space for mobile navbar */
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

/* ====== BUTTON STYLE ====== */
.stButton > button {
  font-family: 'WIDE MEDIUM', sans-serif !important;
  font-weight: 500 !important;
  font-stretch: expanded;
  font-size: 16px !important;
  letter-spacing: 0.5px;
  background: linear-gradient(90deg, var(--accent-green), var(--accent-blue)) !important;
  color: white !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 10px 16px !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
  transition: 0.2s ease-in-out !important;
  min-height: 44px !important;
}
.stButton > button:hover {
  opacity: 0.9 !important;
  transform: translateY(-1px) !important;
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
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  box-shadow: 0 10px 30px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.06);
  backdrop-filter: blur(10px);
  border-radius: 18px;
  padding: 16px;
}

/* ====== TITLES ====== */
.app-title {
  font-family: 'SUPER EXP BLACK OBLIQUE', sans-serif !important;
  font-weight: 900 !important;
  font-style: oblique !important;
  letter-spacing: 1.5px;
  color: #ffffff !important;
  font-size: 32px !important;
  margin: 0 !important;
}
.app-subtitle {
  font-family: 'WIDE MEDIUM', sans-serif !important;
  font-weight: 500 !important;
  font-stretch: expanded !important;
  color: var(--text-secondary) !important;
  font-size: 18px !important;
  letter-spacing: 1px !important;
}

/* ====== MAIN & SECONDARY HEADINGS ====== */
.main-heading, .stTabs [role="tab"][aria-selected="true"], .stSubheader {
  font-family: 'SUPER EXP BLACK OBLIQUE', sans-serif !important;
  font-weight: 900 !important;
  font-style: oblique !important;
  letter-spacing: 1.2px !important;
  color: #ffffff !important;
  text-transform: uppercase !important;
}
.secondary-heading, .stTabs [role="tab"] {
  font-family: 'SUPER EXP OBLIQUE', sans-serif !important;
  font-weight: 700 !important;
  font-style: oblique !important;
  letter-spacing: 1px !important;
  color: var(--text-secondary) !important;
}

/* ====== METRICS ====== */
.stMetricLabel {
  font-family: 'SUPER EXP OBLIQUE', sans-serif !important;
  font-weight: 700 !important;
  font-style: oblique !important;
  letter-spacing: 1px !important;
  color: var(--text-secondary) !important;
}
[data-testid="stMetricValue"] {
  font-family: 'SUPER EXP BLACK OBLIQUE', sans-serif !important;
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

/* ====== NAVBAR (Mobile Bottom Navigation Fixed) ====== */
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
    font-size: 22px;
    text-decoration: none;
    padding: 6px 0;
    transition: all 0.2s ease-in-out;
}
.navbar a.active { color: #10B981; font-weight: bold; }
.navbar a:hover { color: white; }

/* ====== HEADER CONTAINER ====== */
.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0 !important;
  padding: 0 !important;
  gap: 8px;
}

/* ====== MOBILE RESPONSIVE ====== */
@media (max-width: 600px) {
  .block-container { padding: 0.5rem !important; max-width: 100% !important; }
  h1, h2, h3, .app-title, .main-heading { font-size: 18px !important; }
  .app-subtitle, p, div, span { font-size: 13px !important; }
  .stButton > button { font-size: 14px !important; padding: 8px 12px !important; width: 100% !important; }
  .glass { padding: 8px !important; border-radius: 12px !important; }
  .stDataFrame { font-size: 12px !important; }
  .stPlotlyChart, .stAltairChart { height: auto !important; min-height: 280px !important; }
  .header-container img { width: 80px !important; }
  .app-title { font-size: 16px !important; }
}

/* ====== EXTRA MOBILE LAYOUT FIXES ====== */
@media (max-width: 1000px) {
  body, .block-container, [data-testid="stAppViewContainer"] {
    zoom: 1;
    -moz-transform: scale(0.7);
    -moz-transform-origin: 0 0;
  }
  .stTabs [role="tablist"] {
    flex-wrap: wrap !important;
    justify-content: space-around !important;
    gap: 4px !important;
  }
  .stTabs [role="tab"] {
    flex: 1 1 45% !important;
    margin: 2px !important;
    font-size: 0.85rem !important;
    padding: 6px 4px !important;
  }
}
/* ====== SCROLLABLE HORIZONTAL TABS (Dark Blue + White Text) ====== */
.stTabs [role="tablist"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    scrollbar-width: none !important;
    -ms-overflow-style: none !important;
    white-space: nowrap !important;
    background: linear-gradient(90deg, #0A1128, #1E3A8A) !important; /* navy → deep blue */
    border-bottom: 2px solid #1E40AF !important;
    padding: 0 !important;
    margin-bottom: 12px !important;
}
.stTabs [role="tablist"]::-webkit-scrollbar {
    display: none !important;
}

/* Tabs text (all white, expanded font) */
.stTabs [role="tab"] {
    flex: 0 0 auto !important;
    text-align: center !important;
    padding: 10px 16px !important;
    margin: 0 !important;
    border-radius: 0 !important;
    background: transparent !important;
    font-family: 'WIDE MEDIUM', sans-serif !important;  /* 👈 expanded font */
    font-stretch: expanded !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #FFFFFF !important;  /* 👈 always white text */
    border: none !important;
    transition: all 0.2s ease-in-out;
    cursor: pointer !important;
}

/* Active tab */
.stTabs [role="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
    border-bottom: 3px solid #3B82F6 !important; /* cyan underline */
    font-weight: 800 !important;
}

/* Hover */
.stTabs [role="tab"]:hover {
    color: #BFDBFE !important; /* slightly lighter hover white-blue */
}
/* ====== HEADERS FONT CONTROL ====== */

/* Main headers (big / strong) */
h1, h2, h3,
.main-heading,
.stTabs [role="tab"][aria-selected="true"],
.stSubheader {
  font-family: 'SUPER EXP BLACK OBLIQUE', sans-serif !important;
  font-weight: 900 !important;
  font-style: oblique !important;
  letter-spacing: 1.2px !important;
  color: #ffffff !important;
  text-transform: uppercase !important;
}

/* Subheaders (medium weight) */
h4, h5, h6,
.secondary-heading,
.stTabs [role="tab"]:not([aria-selected="true"]) {
  font-family: 'SUPER EXP OBLIQUE', sans-serif !important;
  font-weight: 700 !important;
  font-style: oblique !important;
  letter-spacing: 1px !important;
  color: var(--text-secondary) !important;
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
    """
    Safe Supabase writer:
    - Validates schema before writing.
    - Attempts UPSERT first, deletes stale rows only on success.
    - Logs full Supabase errors.
    - Falls back to local CSV if Supabase write fails.
    """
    sb = _supabase_client()
    table = _table_for_path(path)

    # 🔍 Check expected schema
    expected_cols = EXPECTED_COLUMNS.get(table, [])
    missing_cols = [c for c in expected_cols if c not in df.columns]
    if missing_cols:
        st.warning(f"⚠️ Missing columns for {table}: {missing_cols}")

    # 🚫 Drop auto-generated ID columns
    auto_ids = {
        "player_stats": ["id"], "tactics": ["id"], "tactics_positions": ["id"],
        "availability": ["id"], "training_attendance": ["id"], "fan_wall": ["id"],
    }
    safe_df = df.drop(columns=[c for c in auto_ids.get(table, []) if c in df.columns], errors="ignore")

    # 📅 Format date columns
    if "date" in safe_df.columns:
        safe_df["date"] = pd.to_datetime(safe_df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

    # 🔢 Numeric conversions
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

    # 🔄 Convert to rows
    rows = _df_to_rows(safe_df)
    if not rows:
        st.info(f"ℹ️ No rows to save for {table}")
        return

    try:
        # 🚀 UPSERT rows in chunks
        CHUNK = 500
        for i in range(0, len(rows), CHUNK):
            res = sb.table(table).upsert(rows[i:i+CHUNK]).execute()
            if getattr(res, "error", None):
                raise Exception(res.error)
        st.success(f"✅ Saved {len(rows)} rows to Supabase table '{table}'")

        # 🧹 Clean up stale rows only if UPSERT succeeded
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
                sb.table(table).delete().neq("match_id", -1).execute()
            elif table in ["tactics", "tactics_positions", "availability", "training_attendance", "fan_wall"]:
                sb.table(table).delete().neq("id", -1).execute()
        except Exception as delete_err:
            st.warning(f"⚠️ Cleanup issue in {table}: {delete_err}")

    except Exception as e:
        # ❌ If Supabase fails, fallback to CSV
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
    role = st.session_state.auth.get("role", "Guest")
    name = st.session_state.auth.get("name", "User")

    # === Top header row (Logo + Title + Logout) ===
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; margin:0; padding:0;">
            <img src="{LOGO_URL}" style="width:140px; height:auto;">
            <div class="app-title">NILE ESPORTS HUB</div>
            <span style="color:#ff4b4b; font-weight:bold; font-size:22px;">LIVE</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("Logout", key="logout_btn"):
            logout()

    # === User info row ===
    st.markdown(
        f"<div class='secondary-heading' style='font-size:14px; margin:6px 0;'>"
        f"Role: <b>{role.upper()}</b> | User: <b>{name}</b></div>",
        unsafe_allow_html=True
    )



# -------------------------------
# INTRO PAGE (before login)
# -------------------------------
def intro_page():
    # Remove all default Streamlit padding/margin
    st.markdown("""
    <style>
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
        }
        .main .block-container {
            padding: 0 !important;
        }
        header, .stToolbar {display: none !important;} /* Hide Streamlit's header bar */
    </style>
    """, unsafe_allow_html=True)

    # =======================
    # Animated Intro Content
    # =======================
    st.markdown(f"""
    <style>
        .intro-container {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            text-align: center;
            background: linear-gradient(135deg, #0A1128, #111827);
            overflow: hidden;
        }}

        .intro-logo {{
            width: 300px;
            animation: fadeInScale 2s ease forwards;
        }}

        .intro-title {{
            font-family: 'SUPER EXP BLACK OBLIQUE', sans-serif !important;
            font-size: 40px;
            font-weight: 900;
            color: white;
            margin-top: 12px;
            text-transform: uppercase;
            opacity: 0;
            animation: slideUp 1.5s ease forwards 1.2s;
        }}

        .intro-subtitle {{
            font-family: 'SUPER EXP OBLIQUE', sans-serif !important;
            font-size: 18px;
            color: #34D399;
            margin-top: 6px;
            opacity: 0;
            animation: fadeIn 1.2s ease forwards 2.5s;
        }}

        /* Animations */
        @keyframes fadeInScale {{
            from {{ opacity: 0; transform: scale(0.8); }}
            to {{ opacity: 1; transform: scale(1); }}
        }}
        @keyframes slideUp {{
            from {{ opacity: 0; transform: translateY(40px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}

        /* Mobile tweaks */
        @media (max-width:600px){{
            .intro-logo {{ max-width: 140px !important; }}
            .intro-title {{ font-size: 22px !important; }}
            .intro-subtitle {{ font-size: 14px !important; }}
        }}
    </style>

    <div class="intro-container">
        <img src="{LOGO_URL}" class="intro-logo"/>
        <div class="intro-title">NILE ESPORTS HUB</div>
        <div class="intro-subtitle">One Club • One Heartbeat 🖤💚</div>
    </div>
    """, unsafe_allow_html=True)


    # Buttons (closer to subtitle)
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
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
    st.markdown(f"""
    <div style="text-align:center;">
        <img src="{LOGO_URL}" style="width:350px; height:auto; margin-bottom:10px;">
        <h2 style="margin:0;">Sign In</h2>
        <p style="margin:.3rem 0 1rem 0;">Choose your role and use your access code</p>
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
        
        st.markdown("<h2 class='main-heading'>Last Match</h2>", unsafe_allow_html=True)

        if not past_matches.empty:
            lm = past_matches.iloc[0]
            st.metric(label=f"vs {lm['opponent']} on {lm['date']}",
                      value=f"{safe_int(lm.get('our_score'))}-{safe_int(lm.get('their_score'))}",
                      delta=lm['result'])
            st.write(lm.get("notes", ""))
        else:
            st.info("No past matches yet.")

    with col2:
        
        st.markdown("<h2 class='main-heading'>Next Match</h2>", unsafe_allow_html=True)
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
    st.markdown("<h2 class='main-heading'>📋 Match Results</h2>", unsafe_allow_html=True)

    if not past_matches.empty:
        st.dataframe(past_matches.reset_index(drop=True), use_container_width=True)
    else:
        st.caption("No results yet.")

    
    st.markdown("<h2 class='main-heading'>📅 Upcoming Matches</h2>", unsafe_allow_html=True)
    if not upcoming_matches.empty:
        st.dataframe(upcoming_matches.reset_index(drop=True), use_container_width=True)
    else:
        st.caption("No upcoming fixtures.")

    st.divider()
    
    st.markdown("<h2 class='main-heading'>Leaderboards</h2>", unsafe_allow_html=True)
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
            st.plotly_chart(
                px.bar(
                    agg.sort_values("goals", ascending=False).head(10),
                    x="player_name", y="goals"
                ),
                use_container_width=True,
                config={"staticPlot": True}  # disable interactivity
            )
        with c2:
            st.caption("Top Assists")
            st.plotly_chart(
                px.bar(
                    agg.sort_values("assists", ascending=False).head(10),
                    x="player_name", y="assists"
                ),
                use_container_width=True,
                config={"staticPlot": True}  # disable interactivity
            )

        # Best Average Rating with Rank
        
        st.markdown("<h2 class='main-heading'>Best Average Rating (min 3 matches)</h2>", unsafe_allow_html=True)
        best = agg[agg["matches"] >= 3].sort_values("avg_rating", ascending=False)
        best.insert(0, "Rank", best["avg_rating"].rank(method="min", ascending=False).astype(int))
        st.dataframe(best, use_container_width=True)



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
        matches_df = matches_df.sort_values("date", ascending=False)  # latest first
        match_labels = matches_df.set_index("match_id").apply(
            lambda r: f"{r['date'].date()} vs {r['opponent']}", axis=1, result_type="reduce"
        )
        df = df.merge(match_labels.rename("match_name"),
                      left_on="match_id", right_index=True, how="left")

        # 🆕 Auto-select the latest match
        latest_match_name = match_labels.iloc[0] if not match_labels.empty else "All"
    else:
        df["match_name"] = df["match_id"].astype(str)
        latest_match_name = "All"

    # === Filters (auto-set last match) ===
    players = sorted(df["player_name"].unique())
    selected_player = st.selectbox("Filter by Player", ["All"] + players)

    matches = sorted(df["match_name"].unique())
    selected_match = st.selectbox(
        "Filter by Match",
        ["All"] + matches,
        index=(["All"] + matches).index(latest_match_name) if latest_match_name in matches else 0
    )

    filtered = df.copy()
    if selected_player != "All":
        filtered = filtered[filtered["player_name"] == selected_player]
    if selected_match != "All":
        filtered = filtered[filtered["match_name"] == selected_match]

    # === Card UI for stats ===
    if filtered.empty:
        st.warning("No stats found for this filter.")
    else:
        for _, row in filtered.iterrows():
            st.markdown(f"""
            <div class="glass" style="margin-bottom:12px; padding:14px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-size:16px; font-weight:900; font-family:'SUPER EXP BLACK OBLIQUE'; color:#ffffff;">
                        {row['player_name']}
                    </div>
                    <div style="font-size:13px; color:#60A5FA;">
                        {row['match_name']}
                    </div>
                </div>
                <div style="margin-top:8px; font-size:14px; color:#E5E7EB;">
                    ⚽ Goals: <span style="color:#34D399; font-weight:bold;">{row.get('goals',0)}</span> &nbsp; | &nbsp;
                    🎯 Assists: <span style="color:#60A5FA; font-weight:bold;">{row.get('assists',0)}</span> &nbsp; | &nbsp;
                    ⭐ Rating: <span style="color:#FBBF24; font-weight:bold;">{row.get('rating',0):.1f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # === Admin actions (delete only) ===
    st.divider()
    st.markdown("### 🗑️ Delete Individual Stat")
    selected = st.selectbox(
        "Select stat row to delete",
        df.apply(lambda r: f"ID {r['id']} - {r['player_name']} ({r['match_name']})", axis=1)
    )
    if st.button("Delete Selected Stat"):
        row_id = int(selected.split(" ")[1])
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
            "Primary Position",
            ["GK","RB","CB","LB","RWB","LWB","CDM","CM","CAM","RM","LM","RW","LW","ST"]
        )
        code = st.text_input("Login Code", placeholder="e.g. PL-010")
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
    
    st.markdown("<h2 class='main-heading'>🏋️ Create / Manage Training Sessions</h2>", unsafe_allow_html=True)
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
    
    st.markdown("<h2 class='main-heading'>📈 Training Attendance – All Players & Sessions</h2>", unsafe_allow_html=True)
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
    st.title("📸 Upload Stats")

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
def player_my_stats_page():
    # ===== Ensure current player =====
    current_name = st.session_state.auth.get("name", "").strip()
    if not current_name:
        st.error("❌ You must be logged in to view your stats.")
        return

    # ====== Global Theme & Fonts ======
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
    html, body, [class*="css"] {
        background: linear-gradient(160deg, #0C182E 40%, #000000 100%);
        color: #FFFFFF;
    }
    .super-head { font-family:'Montserrat'; font-weight:900; font-style:oblique; font-size:40px; color:#00C0FA; text-align:center; }
    .sub-head { font-family:'Montserrat'; font-weight:700; font-style:oblique; font-size:28px; color:#00C0FA; }
    .text-mid { font-family:'Montserrat'; font-weight:500; font-size:16px; color:#FFFFFF; }
    .card,.metric-card,.chart-card {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    }
    .metric-grid,.chart-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px,1fr));
        gap: 20px; margin-bottom: 30px;
    }
    .metric-value { font-size:28px; font-weight:700; color:#015EEA; }
    .metric-label { font-size:14px; color:#FFFFFF; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='super-head'>📊 My Performance Dashboard</h1>", unsafe_allow_html=True)

    # ===== Player Record =====
    players = read_csv_safe(PLAYERS_FILE)
    player = players[players["name"].str.lower() == current_name.lower()]
    if player.empty:
        st.error("❌ Player profile not found.")
        return
    player = player.iloc[0]

    stats = read_csv_safe(PLAYER_STATS_FILE)
    matches = read_csv_safe(MATCHES_FILE)

    if stats.empty:
        st.info("No stats yet.")
        return

    # Only this player's stats
    mine = stats[stats["player_name"].str.lower() == current_name.lower()]
    if mine.empty:
        st.info("No stats recorded for you yet.")
        return

    # ===== Join with Matches for readable match names =====
    if not matches.empty and "match_id" in mine.columns:
        match_labels = matches.set_index("match_id").apply(
            lambda r: f"{r['date']} vs {r['opponent']}", axis=1
        )
        mine = mine.merge(match_labels.rename("match_name"), left_on="match_id", right_index=True, how="left")
    else:
        mine["match_name"] = mine["match_id"].astype(str)

    # ===== Hero Card =====
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:25px;">
        <div class="card">
            <h2 class="sub-head">{player['name']}</h2>
            <p class="text-mid">Position: {player['position']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ===== KPI Cards =====
    matches_played = len(mine)
    avg_rating = round(mine["rating"].mean(), 2) if not mine["rating"].isna().all() else "N/A"
    avg_shots = round(mine["shots"].mean(), 1) if "shots" in mine else "N/A"
    avg_pass_acc = f"{round(mine['pass_accuracy'].mean(),1)}%" if "pass_accuracy" in mine else "N/A"
    avg_dribble_succ = f"{round(mine['dribble_success'].mean(),1)}%" if "dribble_success" in mine else "N/A"
    avg_tackles = round(mine["tackles"].mean(), 1) if "tackles" in mine else "N/A"
    avg_distance = round(mine["distance_covered"].mean(), 1) if "distance_covered" in mine else "N/A"

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card"><div class="metric-value">{matches_played}</div><div class="metric-label">Matches</div></div>
        <div class="metric-card"><div class="metric-value">{avg_rating}</div><div class="metric-label">Avg Rating</div></div>
        <div class="metric-card"><div class="metric-value">{avg_shots}</div><div class="metric-label">Avg Shots</div></div>
        <div class="metric-card"><div class="metric-value">{avg_pass_acc}</div><div class="metric-label">Pass Accuracy</div></div>
        <div class="metric-card"><div class="metric-value">{avg_dribble_succ}</div><div class="metric-label">Dribble Success</div></div>
        <div class="metric-card"><div class="metric-value">{avg_tackles}</div><div class="metric-label">Avg Tackles</div></div>
        <div class="metric-card"><div class="metric-value">{avg_distance} km</div><div class="metric-label">Distance Covered</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ===== Charts =====
    st.markdown("<h2 class='sub-head'>📈 Performance Tracker</h2>", unsafe_allow_html=True)
    mine = mine.sort_values("match_id")

    fig1 = px.bar(mine, x="match_name", y=["shots", "passes"], barmode="group",
                  title="🔫 Shots & 🎯 Passes per Match", color_discrete_sequence=["#015EEA", "#00C0FA"])
    fig2 = px.bar(mine, x="match_name", y=["dribbles", "tackles"], barmode="group",
                  title="⚡ Dribbles & 🛡️ Tackles per Match", color_discrete_sequence=["#00C0FA", "#FF5733"])
    fig3 = px.bar(mine, x="match_name", y=["possession_won", "possession_lost"], barmode="group",
                  title="📊 Possession Won vs Lost", color_discrete_sequence=["#28A745", "#DC3545"])
    fig4 = px.line(mine, x="match_name", y=["distance_covered","distance_sprinted"], markers=True,
                   title="🏃 Distance Covered & Sprinted", color_discrete_sequence=["#00C0FA", "#015EEA"])
    fig5 = px.line(mine, x="match_name", y="rating", markers=True,
                   title="⭐ Ratings Over Matches", color_discrete_sequence=["#FFD700"])
    fig5.update_yaxes(range=[0, 10])

    st.markdown("<div class='chart-grid'>", unsafe_allow_html=True)
    for fig in [fig1, fig2, fig3, fig4, fig5]:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True})
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ===== Detailed Stats Table =====
    st.markdown("<h2 class='sub-head'>📋 Detailed Stats per Match</h2>", unsafe_allow_html=True)
    exclude = ["id","goals","assists"]
    table_cols = [c for c in mine.columns if c not in exclude]
    st.dataframe(mine[table_cols].reset_index(drop=True), use_container_width=True)




import re
import json


def extract_stats_from_image(image_bytes: bytes):
    """
    Send image bytes to Gemini and return parsed JSON (dict) or None on failure.
    This function is robust to code fences and extra text in Gemini response.
    """
    try:
        model = _gemini_client()
        img = {"mime_type": "image/png", "data": image_bytes}

        # Prompt: ask for JSON only (tweak keys as you want)
        prompt = """
        You are a precise data extractor. Return ONLY valid JSON, no explanations.
        Extract the following keys for the PLAYER shown (if a key is missing return null):
        ["player_name","position","rating","match_id",
         "goals","assists",
         "shots","shot_accuracy","passes","pass_accuracy",
         "dribbles","dribble_success","tackles","tackle_success",
         "offsides","fouls_committed","possession_won","possession_lost",
         "minutes_played","distance_covered","distance_sprinted",
         "yellow_cards","red_cards"]
        """

        resp = model.generate_content([prompt, img])
        raw_text = resp.text.strip()

        # Remove markdown fences if present
        if raw_text.startswith("```"):
            raw_text = re.sub(r"^```[a-zA-Z]*\n", "", raw_text)
            raw_text = re.sub(r"\n```$", "", raw_text)

        # Try direct JSON load
        try:
            parsed = json.loads(raw_text)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            # Try to extract first JSON object in text as fallback
            m = re.search(r"(\{.*\})", raw_text, flags=re.DOTALL)
            if m:
                try:
                    parsed = json.loads(m.group(1))
                    if isinstance(parsed, dict):
                        return parsed
                except Exception:
                    pass

        # If we reach here, parsing failed
        st.error("❌ Could not parse JSON from AI response. See raw output below for debugging.")
        st.code(raw_text)
        return None

    except Exception as e:
        st.error(f"❌ Error calling extraction model: {e}")
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

    # Let player pick a match (defaults to most recent)
    matches = read_csv_safe(MATCHES_FILE)
    match_id_choice = None
    if not matches.empty:
        matches_sorted = matches.sort_values("date", ascending=False)
        labels = [f"{r['date']} – {r['opponent']}" for _, r in matches_sorted.iterrows()]
        label_to_id = {labels[i]: int(matches_sorted.iloc[i]["match_id"]) for i in range(len(labels))}
        chosen_label = st.selectbox("Link to match", ["(auto) Latest match"] + labels)
        if chosen_label != "(auto) Latest match":
            match_id_choice = label_to_id[chosen_label]
        else:
            match_id_choice = int(matches_sorted.iloc[0]["match_id"]) if not matches_sorted.empty else None

    uploaded = st.file_uploader("Upload your match stats image", type=["png", "jpg", "jpeg"])
    if not uploaded:
        return

    st.image(uploaded, caption="Preview", use_container_width=True)

    if st.button("📤 Extract & Save Stats"):
        try:
            img_bytes = uploaded.read()
            parsed = extract_stats_from_image(img_bytes)
            if not parsed:
                return

            # Validate player identity
            parsed_name = (parsed.get("player_name") or "").strip()
            if parsed_name.lower() != current_name.lower():
                st.error("❌ Player name in uploaded stats does not match your account. Contact admin.")
                return

            # Get player_id
            player_id = get_player_id_by_name(current_name)
            if player_id is None:
                st.error("❌ Player not found in roster. Contact admin.")
                return

            # Determine match_id
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

            # Prepare record
            record = {"player_name": current_name, "player_id": player_id, "match_id": int(match_id)}
            allowed_keys = [
                "position","rating","goals","assists","shots","shot_accuracy","passes","pass_accuracy",
                "dribbles","dribble_success","tackles","tackle_success","offsides","fouls_committed",
                "possession_won","possession_lost","minutes_played","distance_covered","distance_sprinted",
                "yellow_cards","red_cards"
            ]
            for k in allowed_keys:
                if k in parsed:
                    record[k] = parsed[k]

            # Call UPSERT function
            sb = _supabase_client()
            sb.rpc("upsert_player_stats", {
                "p_match_id": record["match_id"],
                "p_player_name": record["player_name"],
                "p_position": record.get("position") or "N/A",
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

            st.success("✅ Stats uploaded successfully!")

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
        st.dataframe(wall[wall["approved"]==True].sort_values("timestamp", ascending=False), use_container_width=True,height=300)

# -------------------------------
# ADMIN: FAN WALL MODERATION & REPORTS
# -------------------------------
def admin_fanwall_moderation():
    
    st.markdown("<h2 class='main-heading'>Moderate Fan Wall</h2>", unsafe_allow_html=True)

    wall = read_csv_safe(FANWALL_FILE)
    if wall.empty:
        st.info("No messages yet.")
        return
    st.dataframe(wall, use_container_width=True,height=300)
    idx = st.number_input("Row index to toggle approval", 0, len(wall)-1, 0)
    if st.button("Toggle approval"):
        wall.loc[idx, "approved"] = not bool(wall.loc[idx, "approved"])
        write_csv_safe(wall, FANWALL_FILE)
        st.success("Toggled.")

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
    st.dataframe(sel_df.head(11), use_container_width=True,height=300)


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




# ============================
# Professional Tab Navigation
# ============================

def tab_nav(pages: dict, default: str):
    """Render professional Streamlit tabs for navigation."""

    # --- CSS Styling for Pro Tabs ---
    st.markdown("""
    <style>
    .stTabs [role="tablist"] {
        justify-content: center;
        border-bottom: 2px solid #222;
    }
    .stTabs [role="tab"] {
        font-family: 'WIDE MEDIUM', sans-serif !important;
        font-size: 14px;
        font-weight: 500;
        padding: 8px 16px;
        border-radius: 8px 8px 0 0;
        background-color: #0A1128;
        color: #9CA3AF;
        margin: 0 4px;
    }
    .stTabs [role="tab"]:hover {
        background-color: #111827;
        color: white;
    }
    .stTabs [role="tab"][aria-selected="true"] {
        background: linear-gradient(90deg, #10B981, #2563EB);
        color: white !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Render Tabs ---
    labels = list(pages.keys())
    icons  = [pages[l][0] for l in labels]
    funcs  = [pages[l][1] for l in labels]

    tab_labels = [f"{icons[i]} {labels[i]}" for i in range(len(labels))]
    tabs = st.tabs(tab_labels)

    for i, tab in enumerate(tabs):
        with tab:
            funcs[i]()













# -------------------------------
# ADMIN APP
# -------------------------------
def run_admin():
     render_header() 
     tabs = [ "🏠 Dashboard", "⚽ Matches", "📊 Player Stats", "📸 Upload Player Stats", "👤 Players", "📝 Training Sessions", "📋 Attendance", "💬 Fan Wall", "📄 Reports", "⭐ Best XI", "⚠️ Danger Zone" ] 
     pages = { "🏠 Dashboard": page_dashboard, "⚽ Matches": admin_matches_page, "📊 Player Stats": admin_player_stats_page, "📸 Upload Player Stats": admin_upload_player_stats_page, "👤 Players": admin_players_crud_page, "📝 Training Sessions": admin_training_sessions_page, "📋 Attendance": admin_training_attendance_all, "💬 Fan Wall": admin_fanwall_moderation, "📄 Reports": admin_reports_page, "⭐ Best XI": page_best_xi, "⚠️ Danger Zone": admin_delete_all_data }
     selected_tab = st.tabs(tabs) 
     for i, tab_name in enumerate(tabs): 
         with selected_tab[i]: pages[tab_name]()




# -------------------------------
# MANAGER APP
# -------------------------------
def run_manager():
    render_header()

    tabs = [
        "🏠 Dashboard",
        "📄 Tactics",
        "📈 Board",
        "📋 Attendance",
        "⭐ Best XI",
    ]

    pages = {
        "🏠 Dashboard": page_dashboard,
        "📄 Tactics": manager_tactics_text_page,
        "📈 Board": manager_tactics_board_page,
        "📋 Attendance": manager_training_attendance_overview,
        "⭐ Best XI": page_best_xi,
    }

    selected_tabs = st.tabs(tabs)
    for i, tab_name in enumerate(tabs):
        with selected_tabs[i]:
            pages[tab_name]()



# -------------------------------
# PLAYER APP
# -------------------------------
def run_player():
    render_header()

    tabs = [
        "🏠 Dashboard",
        "📊 My Stats",
        "📸 Upload My Stats",   # ✅ new tab
        "📋 Attendance",
        "📄 Tactics",
        "📈 Board",
        "⭐ Best XI",
    ]

    pages = {
        "🏠 Dashboard": page_dashboard,
        "📊 My Stats": player_my_stats_page,
        "📸 Upload My Stats": player_upload_stats_page,  # ✅ new page
        "📋 Attendance": lambda: player_training_attendance_page(st.session_state.auth.get("name", "Player")),
        "📄 Tactics": player_tactics_text_page,
        "📈 Board": player_tactics_board_page,
        "⭐ Best XI": page_best_xi,
    }

    selected_tabs = st.tabs(tabs)
    for i, tab_name in enumerate(tabs):
        with selected_tabs[i]:
            page_func = pages.get(tab_name)
            if page_func is not None and callable(page_func):
                page_func()
            else:
                st.warning(f"⚠️ Page '{tab_name}' is not available.")



# -------------------------------
# FAN APP
# -------------------------------
def run_fan():
    render_header()

    tabs = [
        "🏠 Dashboard",
        "💬 Fan Wall",
    ]

    pages = {
        "🏠 Dashboard": page_dashboard,
        "💬 Fan Wall": fan_public_page,
    }

    selected_tabs = st.tabs(tabs)
    for i, tab_name in enumerate(tabs):
        with selected_tabs[i]:
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

## HEAD => SUPER EXP BLACK OBLIQUE
##  sub head SUPER EXP OBLIQUE

##  text =>EXPANDED MID
# WIDE MID


## NILE ESPORTS =>SUPER EXP BLACK
## TEXT  =>WIDE MID

## BUTTONS SKY BLUE




