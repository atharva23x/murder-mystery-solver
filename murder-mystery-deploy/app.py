"""
Murder Mystery Logic Solver - Streamlit Web Application
A clean, interactive detective puzzle game.
Features:
- Dark and Light theme toggle (appearance switcher in sidebar)
- Difficulty levels: Easy, Medium, Hard
- Discovered clues and deduction board
- Mark cards (Eliminate ❌ or Confirm ⭐)
- Custom photos and custom clues builder
- Deploy button, technical jargon, and footer removed
"""
import streamlit as st
import time
import random
from typing import List, Dict, Tuple, Optional

from data import (
    SUSPECTS, LOCATIONS, WEAPONS, CATEGORIES,
    get_var_name, generate_crime_story
)
from logic.propositional import (
    Var, Not, And, Or, Implies, Iff, Xor, Clue
)
from logic.solvers import CSPSolver
from logic.generator import PuzzleGenerator
from logic.nlu import parse_hint
from logic.ai_detective import AIDetective
from audio_tracks import TRACKS, AUDIO_DIR, STING_FILE, ensure_tracks
from assets import (
    get_suspect_avatar_svg, get_location_icon_svg, get_weapon_icon_svg,
    get_case_solved_stamp_svg
)

ensure_tracks()

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Murder Mystery Detective",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "custom_images" not in st.session_state:
    st.session_state.custom_images = {}  # {entity_name: bytes}

if "theme" not in st.session_state:
    st.session_state.theme = st.query_params.get("theme", "dark")

if "puzzle_secret" not in st.session_state:
    gen = PuzzleGenerator(CATEGORIES)
    secret, clues = gen.generate(difficulty="Easy", seed=int(time.time()))
    st.session_state.puzzle_secret = secret
    st.session_state.puzzle_clues = clues
    st.session_state.puzzle_difficulty = "Easy"
    st.session_state.user_board = {}  # {var_name: "POSSIBLE" | "ELIMINATED" | "CONFIRMED"}
    st.session_state.accusation_feedback = None
    st.session_state.custom_case_clues = []
    st.session_state.ai_case = None
    st.session_state.ai_flash = None
    st.session_state.ai_celebrated = False
    st.session_state.ai_sting_played = False

def start_new_game(diff: str):
    """Starts a fresh case with selected difficulty."""
    gen = PuzzleGenerator(CATEGORIES)
    secret, clues = gen.generate(difficulty=diff)
    st.session_state.puzzle_secret = secret
    st.session_state.puzzle_clues = clues
    st.session_state.puzzle_difficulty = diff
    st.session_state.user_board = {}
    st.session_state.accusation_feedback = None
    # The AI Detective keeps its own player-authored case, so a new board
    # puzzle does not wipe an investigation that is already in progress.


# ---------------------------------------------------------
# Permanent Dark Noir Theme Styling
# ---------------------------------------------------------
DARK_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;900&family=Inter:wght@400;500;600;700&display=swap');

/* Hide Deploy button, header menu, footer */
.stDeployButton, [data-testid="stDeployButton"] { display: none !important; }
#MainMenu, footer { visibility: hidden !important; }
header[data-testid="stHeader"] { background-color: transparent !important; }

:root {
    --text-color: #F1F5F9 !important;
    --background-color: #0E1218 !important;
    --secondary-background-color: #151C28 !important;
    --primary-color: #D4AF37 !important;
}

html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {
    background-color: #0E1218 !important;
    color: #F1F5F9 !important;
    font-family: 'Inter', sans-serif !important;
}
h1, h2, h3, h4, h5, h6, [data-testid="stHeadingWithActionElements"] {
    font-family: 'Cinzel', Georgia, serif !important;
    color: #F4F1EA !important;
}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] div,
[data-testid="stMarkdownContainer"] strong,
[data-testid="stCaptionContainer"] p,
p, span, div.stText {
    color: #F1F5F9 !important;
}
[data-testid="stSidebar"], [data-testid="stSidebar"] > div {
    background-color: #121722 !important;
    border-right: 1px solid #1E293B !important;
}
[data-testid="stSidebar"] {
    width: 332px !important;
    min-width: 332px !important;
    max-width: 332px !important;
}
[data-testid="stSidebar"] > div {
    width: 332px !important;
}
.side-heading {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.25rem !important;
    margin: 0.4rem 0 0.6rem 0 !important;
}
.side-heading-icon {
    font-size: 30px !important;
    line-height: 1;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] label p,
[data-testid="stSidebar"] div[data-testid="stRadio"] label span {
    font-size: 1.02rem !important;
}
[data-testid="stSidebar"] .stButton > button {
    font-size: 1rem !important;
    padding: 0.55rem 0.9rem !important;
}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    font-size: 0.88rem !important;
    line-height: 1.45 !important;
}
.stSelectbox label, .stRadio label, .stTextInput label, .stFileUploader label, label[data-testid="stWidgetLabel"] p {
    color: #D4AF37 !important;
    font-weight: 700 !important;
}
div[data-testid="stRadio"] label span, div[data-testid="stRadio"] div[role="radiogroup"] span {
    color: #F1F5F9 !important;
}
div[data-baseweb="select"] > div {
    background-color: #161D2A !important;
    color: #FFFFFF !important;
    border: 1px solid #2A364F !important;
}
div[data-baseweb="select"] span, div[data-baseweb="select"] div {
    color: #FFFFFF !important;
}
div[data-baseweb="popover"], div[data-baseweb="popover"] ul, div[data-baseweb="popover"] li {
    background-color: #161D2A !important;
    color: #FFFFFF !important;
}

.clue-card {
    background: #141B26 !important;
    border: 1px solid #232E40 !important;
    border-left: 6px solid #D4AF37 !important;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 12px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
}
.clue-badge {
    color: #D4AF37 !important;
    font-family: 'Cinzel', serif;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.clue-text {
    font-size: 16px !important;
    color: #FFFFFF !important;
    font-weight: 500;
    line-height: 1.45;
}

.entity-card {
    background-color: #151C28 !important;
    border: 1px solid #232E40 !important;
    border-radius: 10px;
    padding: 10px;
    text-align: center;
    margin-bottom: 8px;
}
.entity-card:hover {
    border-color: #D4AF37 !important;
    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.25);
}
.entity-name {
    font-weight: 700 !important;
    font-size: 14px !important;
    color: #FFFFFF !important;
    margin-bottom: 4px;
}

.card-status {
    font-size: 12px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 12px;
    display: inline-block;
    margin-top: 6px;
}
.status-possible {
    background: rgba(34, 197, 94, 0.15) !important;
    color: #4ADE80 !important;
    border: 1px solid #22C55E !important;
}
.status-eliminated {
    background: rgba(239, 68, 68, 0.15) !important;
    color: #F87171 !important;
    border: 1px solid #EF4444 !important;
    text-decoration: line-through;
}
.status-confirmed {
    background: rgba(212, 175, 55, 0.25) !important;
    color: #FACC15 !important;
    border: 1px solid #D4AF37 !important;
    box-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
}

button[kind="primary"], .stButton > button[kind="primary"] {
    background-color: #D4AF37 !important;
    color: #0E1218 !important;
    border: none !important;
    font-weight: 700 !important;
}
button[kind="secondary"], .stButton > button[kind="secondary"] {
    background-color: #151C28 !important;
    color: #F1F5F9 !important;
    border: 1px solid #2A364F !important;
}
.stTabs [data-baseweb="tab"] {
    background-color: #131924 !important;
    color: #94A3B8 !important;
}
.stTabs [aria-selected="true"] {
    background-color: #1E293B !important;
    color: #D4AF37 !important;
    border: 1px solid #D4AF37 !important;
    border-bottom: none !important;
}

/* ---- AI Detective ---- */
.stTextArea textarea, .stTextInput input {
    background-color: #161D2A !important;
    color: #F1F5F9 !important;
    border: 1px solid #2A364F !important;
    border-radius: 8px !important;
}
.ai-hero {
    background:
        radial-gradient(120% 160% at 0% 0%, rgba(212, 175, 55, 0.18), rgba(20, 27, 38, 0.2) 46%),
        #141B26;
    border: 1px solid #2A364F;
    border-radius: 14px;
    padding: 18px 22px 16px 22px;
    margin: 4px 0 14px 0;
    box-shadow: 0 10px 26px rgba(0, 0, 0, 0.45);
}
.ai-kicker {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    letter-spacing: 2.2px;
    text-transform: uppercase;
    color: #D4AF37;
    font-weight: 700;
}
.ai-name {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 34px;
    font-weight: 900;
    color: #F4F1EA;
    margin: 6px 0 2px 0;
    line-height: 1.1;
}
.ai-theory {
    font-size: 15px;
    color: #CBD5E1;
}
.ai-theory b { color: #F4F1EA; }
.ai-confidence {
    margin-top: 10px;
    font-size: 13px;
    color: #94A3B8;
}
.ai-confidence b { color: #D4AF37; }
.ai-setup {
    background: #131A26;
    border: 1px solid #263248;
    border-left: 4px solid #D4AF37;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 10px 0 14px 0;
}
.ai-setup-line {
    font-size: 16px;
    color: #F4F1EA;
    margin: 4px 0 2px 0;
}
.ai-setup-line b { color: #D4AF37; }
.ai-case-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 8px 0 4px 0;
}
.ai-case-token {
    background: #0F1622;
    border: 1px solid #2A364F;
    border-radius: 999px;
    padding: 5px 13px;
    font-size: 13.5px;
    color: #F1F5F9 !important;
}
.ai-case-icon {
    font-size: 26px !important;
    line-height: 1;
    vertical-align: -4px;
    margin-right: 5px;
}

/* Large icons in the sidebar case card */
.side-case {
    margin: 4px 0 6px 0;
}
.side-case-row {
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 7px 0;
    border-bottom: 1px solid #1E293B;
}
.side-case-row:last-child { border-bottom: none; }
.side-case-icon {
    font-size: 40px !important;
    line-height: 1;
    width: 52px;
    text-align: center;
    flex: 0 0 52px;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.5));
}
.side-case-label {
    font-size: 10.5px;
    letter-spacing: 1.7px;
    text-transform: uppercase;
    color: #94A3B8 !important;
    font-weight: 700;
}
.side-case-value {
    font-size: 17px;
    font-weight: 700;
    color: #F4F1EA !important;
    line-height: 1.2;
}
.ai-case-token b { color: #D4AF37 !important; }
.ai-case-label {
    color: #94A3B8 !important;
    font-size: 10px;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    margin-right: 6px;
}
.ai-hint {
    background: #121722;
    border: 1px solid #232E40;
    border-left: 4px solid #D4AF37;
    border-radius: 8px;
    padding: 10px 13px;
    margin: 8px 0;
    font-size: 13.5px;
    color: #E2E8F0;
    line-height: 1.45;
}
.ai-hint b { color: #F4F1EA; }
.ai-quiet { color: #94A3B8; font-size: 12.5px; }
</style>
"""

LIGHT_THEME_CSS = """

<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;900&family=Inter:wght@400;500;600;700&display=swap');

/* Hide Deploy button, header menu, footer */
.stDeployButton, [data-testid="stDeployButton"] { display: none !important; }
#MainMenu, footer { visibility: hidden !important; }
header[data-testid="stHeader"] { background-color: transparent !important; }

:root {
    --text-color: #1F2937 !important;
    --background-color: #F4F1EA !important;
    --secondary-background-color: #FFFFFF !important;
    --primary-color: #8B6914 !important;
}

html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {
    background-color: #F4F1EA !important;
    color: #1F2937 !important;
    font-family: 'Inter', sans-serif !important;
}
h1, h2, h3, h4, h5, h6, [data-testid="stHeadingWithActionElements"] {
    font-family: 'Cinzel', Georgia, serif !important;
    color: #3B2F1E !important;
}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] div,
[data-testid="stMarkdownContainer"] strong,
[data-testid="stCaptionContainer"] p,
p, span, div.stText {
    color: #1F2937 !important;
}
[data-testid="stSidebar"], [data-testid="stSidebar"] > div {
    background-color: #EDE7D9 !important;
    border-right: 1px solid #D6CEBD !important;
}
[data-testid="stSidebar"] {
    width: 332px !important;
    min-width: 332px !important;
    max-width: 332px !important;
}
[data-testid="stSidebar"] > div {
    width: 332px !important;
}
.side-heading {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.25rem !important;
    margin: 0.4rem 0 0.6rem 0 !important;
}
.side-heading-icon {
    font-size: 30px !important;
    line-height: 1;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] label p,
[data-testid="stSidebar"] div[data-testid="stRadio"] label span {
    font-size: 1.02rem !important;
}
[data-testid="stSidebar"] .stButton > button {
    font-size: 1rem !important;
    padding: 0.55rem 0.9rem !important;
}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    font-size: 0.88rem !important;
    line-height: 1.45 !important;
}
.stSelectbox label, .stRadio label, .stTextInput label, .stFileUploader label, label[data-testid="stWidgetLabel"] p {
    color: #8B6914 !important;
    font-weight: 700 !important;
}
div[data-testid="stRadio"] label span, div[data-testid="stRadio"] div[role="radiogroup"] span {
    color: #1F2937 !important;
}
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #1F2937 !important;
    border: 1px solid #B8AF9A !important;
}
div[data-baseweb="select"] span, div[data-baseweb="select"] div {
    color: #1F2937 !important;
}
div[data-baseweb="popover"], div[data-baseweb="popover"] ul, div[data-baseweb="popover"] li {
    background-color: #FFFFFF !important;
    color: #1F2937 !important;
}

.clue-card {
    background: #FFFFFF !important;
    border: 1px solid #D6CEBD !important;
    border-left: 6px solid #8B6914 !important;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 12px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
}
.clue-badge {
    color: #8B6914 !important;
    font-family: 'Cinzel', serif;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.clue-text {
    font-size: 16px !important;
    color: #1F2937 !important;
    font-weight: 500;
    line-height: 1.45;
}

.entity-card {
    background-color: #FFFFFF !important;
    border: 1px solid #D6CEBD !important;
    border-radius: 10px;
    padding: 10px;
    text-align: center;
    margin-bottom: 8px;
}
.entity-card:hover {
    border-color: #8B6914 !important;
    box-shadow: 0 4px 12px rgba(139, 105, 20, 0.25);
}
.entity-name {
    font-weight: 700 !important;
    font-size: 14px !important;
    color: #1F2937 !important;
    margin-bottom: 4px;
}

.card-status {
    font-size: 12px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 12px;
    display: inline-block;
    margin-top: 6px;
}
.status-possible {
    background: rgba(34, 197, 94, 0.15) !important;
    color: #16A34A !important;
    border: 1px solid #16A34A !important;
}
.status-eliminated {
    background: rgba(239, 68, 68, 0.15) !important;
    color: #DC2626 !important;
    border: 1px solid #DC2626 !important;
    text-decoration: line-through;
}
.status-confirmed {
    background: rgba(139, 105, 20, 0.25) !important;
    color: #8B6914 !important;
    border: 1px solid #8B6914 !important;
    box-shadow: 0 0 10px rgba(139, 105, 20, 0.5);
}

button[kind="primary"], .stButton > button[kind="primary"] {
    background-color: #8B6914 !important;
    color: #F4F1EA !important;
    border: none !important;
    font-weight: 700 !important;
}
button[kind="secondary"], .stButton > button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #1F2937 !important;
    border: 1px solid #B8AF9A !important;
}
.stTabs [data-baseweb="tab"] {
    background-color: #E8E2D5 !important;
    color: #6B6255 !important;
}
.stTabs [aria-selected="true"] {
    background-color: #D6CEBD !important;
    color: #8B6914 !important;
    border: 1px solid #8B6914 !important;
    border-bottom: none !important;
}

/* ---- AI Detective ---- */
.stTextArea textarea, .stTextInput input {
    background-color: #FFFFFF !important;
    color: #1F2937 !important;
    border: 1px solid #B8AF9A !important;
    border-radius: 8px !important;
}
.ai-hero {
    background:
        radial-gradient(120% 160% at 0% 0%, rgba(139, 105, 20, 0.18), rgba(200, 190, 170, 0.2) 46%),
        #FFFFFF;
    border: 1px solid #B8AF9A;
    border-radius: 14px;
    padding: 18px 22px 16px 22px;
    margin: 4px 0 14px 0;
    box-shadow: 0 10px 26px rgba(0, 0, 0, 0.08);
}
.ai-kicker {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    letter-spacing: 2.2px;
    text-transform: uppercase;
    color: #8B6914;
    font-weight: 700;
}
.ai-name {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 34px;
    font-weight: 900;
    color: #3B2F1E;
    margin: 6px 0 2px 0;
    line-height: 1.1;
}
.ai-theory {
    font-size: 15px;
    color: #4B5563;
}
.ai-theory b { color: #3B2F1E; }
.ai-confidence {
    margin-top: 10px;
    font-size: 13px;
    color: #6B6255;
}
.ai-confidence b { color: #8B6914; }
.ai-setup {
    background: #FBF8F1;
    border: 1px solid #C9C0AA;
    border-left: 4px solid #8B6914;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 10px 0 14px 0;
}
.ai-setup-line {
    font-size: 16px;
    color: #3B2F1E;
    margin: 4px 0 2px 0;
}
.ai-setup-line b { color: #8B6914; }
.ai-case-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 8px 0 4px 0;
}
.ai-case-token {
    background: #F0EAD9;
    border: 1px solid #B8AF9A;
    border-radius: 999px;
    padding: 5px 13px;
    font-size: 13.5px;
    color: #1F2937 !important;
}
.ai-case-icon {
    font-size: 26px !important;
    line-height: 1;
    vertical-align: -4px;
    margin-right: 5px;
}

/* Large icons in the sidebar case card */
.side-case {
    margin: 4px 0 6px 0;
}
.side-case-row {
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 7px 0;
    border-bottom: 1px solid #D6CEBD;
}
.side-case-row:last-child { border-bottom: none; }
.side-case-icon {
    font-size: 40px !important;
    line-height: 1;
    width: 52px;
    text-align: center;
    flex: 0 0 52px;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}
.side-case-label {
    font-size: 10.5px;
    letter-spacing: 1.7px;
    text-transform: uppercase;
    color: #6B6255 !important;
    font-weight: 700;
}
.side-case-value {
    font-size: 17px;
    font-weight: 700;
    color: #3B2F1E !important;
    line-height: 1.2;
}
.ai-case-token b { color: #8B6914 !important; }
.ai-case-label {
    color: #6B6255 !important;
    font-size: 10px;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    margin-right: 6px;
}
.ai-hint {
    background: #EDE7D9;
    border: 1px solid #D6CEBD;
    border-left: 4px solid #8B6914;
    border-radius: 8px;
    padding: 10px 13px;
    margin: 8px 0;
    font-size: 13.5px;
    color: #374151;
    line-height: 1.45;
}
.ai-hint b { color: #3B2F1E; }
.ai-quiet { color: #6B6255; font-size: 12.5px; }
</style>

"""

if st.session_state.get("theme", "dark") == "dark":
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)
else:
    st.markdown(LIGHT_THEME_CSS, unsafe_allow_html=True)



# ---------------------------------------------------------
# Top Header
# ---------------------------------------------------------
st.title("🕵️ Murder Mystery Detective")
st.caption("Analyze the clues, eliminate suspects and locations, and deduce the real killer.")
st.write("")


# ---------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------
with st.sidebar:
    # ---- Appearance toggle ----
    st.markdown(
        '<h3 class="side-heading"><span class="side-heading-icon">🎨</span> APPEARANCE</h3>',
        unsafe_allow_html=True,
    )
    _theme_choice = st.radio(
        "Color theme",
        ["🌙 Dark", "☀️ Light"],
        index=0 if st.session_state.theme == "dark" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )
    _new_theme = "dark" if _theme_choice.startswith("🌙") else "light"
    if _new_theme != st.session_state.theme:
        st.session_state.theme = _new_theme
        st.query_params["theme"] = _new_theme
        st.rerun()

    st.markdown("---")
    st.markdown(
        '<h3 class="side-heading"><span class="side-heading-icon">🗂️</span> CASE CONTROLS</h3>',
        unsafe_allow_html=True,
    )

    diff_choice = st.radio(
        "Difficulty Level",
        ["🟢 Easy", "🟡 Medium", "🔴 Hard"],
        index=["Easy", "Medium", "Hard"].index(st.session_state.puzzle_difficulty),
        help="Easy: 6 simple clues. Medium: 5 interlinked clues. Hard: 4 challenging conditional clues."
    )
    clean_diff = diff_choice.split(" ")[1]

    if st.button("🎲 Generate New Case", type="primary", use_container_width=True):
        start_new_game(clean_diff)
        st.rerun()

    st.markdown("---")
    st.markdown(
        '<h3 class="side-heading"><span class="side-heading-icon">🧭</span> NAVIGATION</h3>',
        unsafe_allow_html=True,
    )
    app_mode = st.radio(
        "Choose Mode",
        ["🕵️ Detective Game Board", "🤖 AI Detective", "🎨 Custom Case & Images"],
        index=0
    )

    ai_case_preview = st.session_state.get("ai_case")
    if ai_case_preview:
        pw, pl, pk = ai_case_preview["secret"]
        st.markdown("---")
        st.markdown(
            '<h3 class="side-heading"><span class="side-heading-icon">🔒</span> YOUR AI CASE</h3>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="side-case">
              <div class="side-case-row">
                <span class="side-case-icon">🕵️</span>
                <div><div class="side-case-label">Killer</div><div class="side-case-value">{pw}</div></div>
              </div>
              <div class="side-case-row">
                <span class="side-case-icon">{LOCATIONS[pl]['icon']}</span>
                <div><div class="side-case-label">Scene</div><div class="side-case-value">{pl}</div></div>
              </div>
              <div class="side-case-row">
                <span class="side-case-icon">{WEAPONS[pk]['icon']}</span>
                <div><div class="side-case-label">Weapon</div><div class="side-case-value">{pk}</div></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Only you can see this. The AI has to work it out.")

    st.markdown("---")
    st.markdown(
        '<h3 class="side-heading"><span class="side-heading-icon">🎵</span> SOUNDTRACK</h3>',
        unsafe_allow_html=True,
    )
    track_labels = ["🔇 Silence"] + [f"{t['icon']} {t['title']}" for t in TRACKS]
    selected_track = st.selectbox(
        "Murder mystery soundtrack",
        track_labels,
        index=1,
        label_visibility="collapsed",
    )
    if selected_track == track_labels[0]:
        st.caption("The house is silent. Too silent.")
    else:
        track = TRACKS[track_labels.index(selected_track) - 1]
        st.audio(str(AUDIO_DIR / track["file"]), format="audio/wav", autoplay=True, loop=True)
        st.caption(f"{track['description']} Press ▶ if your browser blocks autoplay.")

    st.markdown("---")
    st.caption("🔍 **Your Mission:** Read the clues, eliminate suspects, scenes, and weapons on the board, and submit the warrant when you deduce the truth!")


# =========================================================
# MODE 1: DETECTIVE GAME BOARD
# =========================================================
if app_mode == "🕵️ Detective Game Board":

    col_clues, col_board = st.columns([1, 1.3], gap="large")

    # ------------------ LEFT: CLUES PANEL ------------------
    with col_clues:
        st.markdown(f"### 📜 Clues Discovered ({st.session_state.puzzle_difficulty} Mode)")
        st.caption("Read each clue carefully to deduce who did it, where, and with what.")

        clues = st.session_state.puzzle_clues

        for idx, clue in enumerate(clues, start=1):
            st.markdown(f"""
            <div class="clue-card">
                <div class="clue-badge">CLUE #{idx} &bull; {clue.clue_type.upper()}</div>
                <div class="clue-text">{clue.text}</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        if st.button("💡 Need a Hint?", use_container_width=True):
            secret = st.session_state.puzzle_secret
            innocent_options = [
                s for s in CATEGORIES["WHO"] if s != secret[0]
            ] + [
                l for l in CATEGORIES["WHERE"] if l != secret[1]
            ] + [
                w for w in CATEGORIES["WHAT"] if w != secret[2]
            ]
            import random
            hint_pick = random.choice(innocent_options)
            st.info(f"💡 **Detective Hint:** Re-read the clues closely—**{hint_pick}** is innocent and can be ruled out!")

        st.markdown("---")
        # Final Accusation Submission
        st.markdown("### ⚖️ Submit Your Accusation")
        with st.form("accusation_form"):
            acc_who = st.selectbox("Culprit (Who)", CATEGORIES["WHO"])
            acc_where = st.selectbox("Location (Where)", CATEGORIES["WHERE"])
            acc_what = st.selectbox("Weapon (What)", CATEGORIES["WHAT"])
            submit_btn = st.form_submit_button("🚨 File Murder Warrant", type="primary", use_container_width=True)

            if submit_btn:
                true_w, true_l, true_k = st.session_state.puzzle_secret
                if acc_who == true_w and acc_where == true_l and acc_what == true_k:
                    st.session_state.accusation_feedback = ("CORRECT", (acc_who, acc_where, acc_what))
                else:
                    errors = []
                    if acc_who != true_w:
                        errors.append("Suspect")
                    if acc_where != true_l:
                        errors.append("Location")
                    if acc_what != true_k:
                        errors.append("Weapon")
                    st.session_state.accusation_feedback = ("INCORRECT", errors)

        if st.session_state.accusation_feedback:
            status, info = st.session_state.accusation_feedback
            if status == "CORRECT":
                st.balloons()
                st.success("🎉 CASE SOLVED! Your deductions are 100% correct!")
                st.markdown(get_case_solved_stamp_svg(), unsafe_allow_html=True)
                story = generate_crime_story(info[0], info[1], info[2])
                st.markdown(story)
            else:
                st.error(f"❌ The Inspector rejected the accusation! Mistakes in: **{', '.join(info)}**. Keep deducing!")

    # ------------------ RIGHT: INTERACTIVE DEDUCTION BOARD ------------------
    with col_board:
        st.markdown("### 🕵️ Interactive Detective Board")
        st.caption("You do the detective work! Click on any card below to **Cross Out (❌)** or **Confirm (⭐)** options.")

        # Quick board reset button
        if st.button("↺ Reset All Board Marks", help="Clears your crosses and checks"):
            st.session_state.user_board = {}
            st.rerun()

        # Render 3 categories
        for cat_name, cat_title, cat_icon in [
            ("WHO", "Suspects", "👤"),
            ("WHERE", "Crime Scenes", "📍"),
            ("WHAT", "Murder Weapons", "🔪")
        ]:
            st.markdown(f"#### {cat_icon} {cat_title}")
            cols = st.columns(5)

            for idx, item in enumerate(CATEGORIES[cat_name]):
                var_name = get_var_name(cat_name, item)
                current_state = st.session_state.user_board.get(var_name, "POSSIBLE")

                with cols[idx]:
                    # Check if custom image uploaded
                    has_custom_img = item in st.session_state.custom_images
                    img_data = st.session_state.custom_images.get(item)

                    # Status badge class
                    badge_class = f"status-{current_state.lower()}"
                    status_label = "❓ Possible"
                    if current_state == "ELIMINATED":
                        status_label = "❌ Out"
                    elif current_state == "CONFIRMED":
                        status_label = "⭐ GUILTY!"

                    # Card container
                    st.markdown(f"""
                    <div class="entity-card">
                        <div class="entity-name">{item}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Show image / avatar
                    if has_custom_img:
                        st.image(img_data, use_container_width=True)
                    else:
                        if cat_name == "WHO":
                            st.markdown(get_suspect_avatar_svg(item, width=80, height=95), unsafe_allow_html=True)
                        elif cat_name == "WHERE":
                            st.markdown(get_location_icon_svg(item, size=48), unsafe_allow_html=True)
                        else:
                            st.markdown(get_weapon_icon_svg(item, size=48), unsafe_allow_html=True)

                    st.markdown(f"<div style='text-align:center;'><span class='card-status {badge_class}'>{status_label}</span></div>", unsafe_allow_html=True)

                    # Action buttons to mark options
                    btn_c1, btn_c2 = st.columns(2)
                    with btn_c1:
                        if st.button("❌", key=f"btn_elim_{var_name}", help=f"Eliminate {item}"):
                            st.session_state.user_board[var_name] = "ELIMINATED"
                            st.rerun()
                    with btn_c2:
                        if st.button("⭐", key=f"btn_conf_{var_name}", help=f"Confirm {item}"):
                            st.session_state.user_board[var_name] = "CONFIRMED"
                            st.rerun()

            st.write("")


# =========================================================
# MODE 2: AI DETECTIVE (you write the case, the AI solves it)
# =========================================================
elif app_mode == "🤖 AI Detective":

    st.markdown("## 🤖 AI Detective")
    st.caption(
        "You are the author this time. Decide who really did it, where and how — the computer never sees "
        "the answer. Then feed it hints in plain English and watch it reason its way to your killer."
    )

    ai_case = st.session_state.get("ai_case")

    # ---------------------------------------------------------
    # STEP 1: the player authors the truth
    # ---------------------------------------------------------
    if ai_case is None:
        st.markdown("### 🖋️ Step 1 — You decide the truth")
        st.caption(
            "This is your sealed answer. The AI receives a short case file of clues that are all true for "
            "this version of the crime, but the file is deliberately incomplete — your hints close the gap."
        )

        st.session_state.setdefault("ai_who", random.choice(list(SUSPECTS)))
        st.session_state.setdefault("ai_where", random.choice(list(LOCATIONS)))
        st.session_state.setdefault("ai_what", random.choice(list(WEAPONS)))

        def _surprise_me():
            st.session_state.ai_who = random.choice(list(SUSPECTS))
            st.session_state.ai_where = random.choice(list(LOCATIONS))
            st.session_state.ai_what = random.choice(list(WEAPONS))

        pick1, pick2, pick3 = st.columns(3)
        with pick1:
            who = st.selectbox(
                "Who really did it?",
                list(SUSPECTS),
                format_func=lambda n: f"{n} — {SUSPECTS[n]['title']}",
                key="ai_who",
            )
            st.caption(SUSPECTS[who]["motive"])
        with pick2:
            where = st.selectbox(
                "Where did it happen?",
                list(LOCATIONS),
                format_func=lambda n: f"{LOCATIONS[n]['icon']} {n}",
                key="ai_where",
            )
            st.caption(LOCATIONS[where]["description"])
        with pick3:
            what = st.selectbox(
                "How was it done?",
                list(WEAPONS),
                format_func=lambda n: f"{WEAPONS[n]['icon']} {n}",
                key="ai_what",
            )
            st.caption(WEAPONS[what]["description"])

        depth = st.session_state.get("puzzle_difficulty", "Easy")
        depth_notes = {"Easy": "4 clues", "Medium": "3 clues", "Hard": "2 clues"}
        st.markdown(
            f"""
            <div class="ai-setup">
              <div class="ai-kicker">Sealed answer — the AI will never see this</div>
              <div class="ai-setup-line"><b>{who}</b> &middot; <b>{where}</b> &middot; <b>{what}</b></div>
              <div class="ai-quiet">Case file depth: {depth_notes.get(depth, "3 clues")} ({depth}). Every clue
              is true for this version of the crime, but incomplete. Your hints finish the job.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        btn1, btn2 = st.columns([1, 2.4])
        with btn1:
            st.button("🎲 Surprise me", use_container_width=True, on_click=_surprise_me)
        with btn2:
            if st.button("🔒 Lock the case & start the investigation", type="primary", use_container_width=True):
                gen = PuzzleGenerator(CATEGORIES)
                clues = gen.build_for_solution(
                    (who, where, what), difficulty=depth, ensure_unique=False
                )
                st.session_state.ai_case = {
                    "secret": (who, where, what),
                    "clues": clues,
                    "difficulty": depth,
                }
                st.session_state.ai_detective = AIDetective(clues)
                st.session_state.ai_flash = (
                    "ok",
                    "Case sealed. The AI has opened the file and read its first clue.",
                )
                st.session_state.ai_celebrated = False
                st.session_state.ai_sting_played = False
                st.rerun()

        st.markdown("---")
        st.markdown("#### How it plays")
        st.markdown(
            "1. **You write the truth** — killer, scene and weapon. The AI never sees it.\n"
            "2. **It reads a short case file** of clues that are true for your version of the crime.\n"
            "3. **You hint** in plain English — *Ravi is innocent*, *it happened in the Library*, *not the rope*.\n"
            "4. **It closes in** — when every other theory is ruled out, it names your killer and the whole story is revealed."
        )
        st.stop()

    # ---------------------------------------------------------
    # STEP 2: the AI investigates
    # ---------------------------------------------------------
    ai = st.session_state.get("ai_detective")
    if ai is None:
        ai = AIDetective(ai_case["clues"])
        st.session_state.ai_detective = ai

    truth = ai_case["secret"]
    cat_index = {"WHO": 0, "WHERE": 1, "WHAT": 2}
    cat_label = {"WHO": "killer", "WHERE": "scene", "WHAT": "weapon"}

    def give_hint(text: str):
        """Parse a hint, refuse anything false for the authored case, then apply it."""
        parsed = parse_hint(text)
        if not parsed.effects:
            st.session_state.ai_flash = ("warn", parsed.summary)
            return

        for sign, cat, item in parsed.effects:
            actual = truth[cat_index[cat]]
            if sign == "exclude" and item == actual:
                st.session_state.ai_flash = (
                    "warn",
                    f"That hint rules out the real {cat_label[cat]}. You wrote this case, so the AI "
                    "could never reach the truth from there. Try an observation that is true in your version.",
                )
                return
            if sign == "confirm" and item != actual:
                st.session_state.ai_flash = (
                    "warn",
                    f"That hint points at the wrong {cat_label[cat]}. Your sealed case says otherwise, "
                    "so the AI would never get there. Try an observation that is true in your version.",
                )
                return

        ok, applied, msg = ai.add_hint(parsed.effects, text)
        if ok:
            g = ai.guess()
            st.session_state.ai_flash = (
                "ok",
                f"{parsed.summary} The AI now suspects **{g.who[0]}** in the **{g.where[0]}** "
                f"with the **{g.what[0]}** — {int(round(g.who[2] * 100))}% on the killer.",
            )
        else:
            st.session_state.ai_flash = ("err", msg)

    header_left, header_right = st.columns([3, 1])
    with header_left:
        st.markdown(
            f"""
            <div class="ai-setup">
              <div class="ai-kicker">🔒 Your case — the AI cannot see this</div>
              <div class="ai-case-row">
                <span class="ai-case-token"><span class="ai-case-label">Killer</span><span class="ai-case-icon">🕵️</span><b>{truth[0]}</b></span>
                <span class="ai-case-token"><span class="ai-case-label">Scene</span><span class="ai-case-icon">{LOCATIONS[truth[1]]['icon']}</span><b>{truth[1]}</b></span>
                <span class="ai-case-token"><span class="ai-case-label">Weapon</span><span class="ai-case-icon">{WEAPONS[truth[2]]['icon']}</span><b>{truth[2]}</b></span>
              </div>
              <div class="ai-quiet">{len(ai.clues)} clues in the file &middot; {ai.revealed} read so far &middot;
              the AI has not seen your answer.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with header_right:
        if st.button("🔄 New case", use_container_width=True):
            st.session_state.ai_case = None
            st.session_state.ai_detective = None
            st.session_state.ai_flash = None
            st.session_state.ai_celebrated = False
            st.session_state.ai_sting_played = False
            st.rerun()

    flash = st.session_state.get("ai_flash")
    if flash:
        kind, msg = flash
        if kind == "ok":
            st.success(msg, icon="🧠")
        elif kind == "warn":
            st.warning(msg, icon="🤔")
        else:
            st.error(msg, icon="⚠️")
        st.session_state.ai_flash = None

    guess = ai.guess()
    pct = int(round(guess.who[2] * 100))
    where_pct = int(round(guess.where[2] * 100))
    what_pct = int(round(guess.what[2] * 100))
    solved = guess.total_worlds == 1 and guess.best == truth

    st.markdown(
        f"""
        <div class="ai-hero">
          <div class="ai-kicker">AI Detective · Current theory</div>
          <div class="ai-name">{guess.who[0]}</div>
          <div class="ai-theory">in the <b>{guess.where[0]}</b> with the <b>{guess.what[0]}</b></div>
          <div class="ai-confidence">Killer <b>{pct}%</b> &middot; Scene <b>{where_pct}%</b> &middot; Weapon <b>{what_pct}%</b>
          &nbsp;|&nbsp; {guess.total_worlds} possible versions remain &middot; {ai.revealed} of {len(ai.clues)} clues read</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 1], gap="large")

    # ------------------ LEFT: CASE FILE + HINTS ------------------
    with left:
        st.markdown("### 📜 Case file the AI has read")
        for idx, clue in enumerate(ai.visible_clues(), start=1):
            st.markdown(
                f"""
                <div class="clue-card">
                    <div class="clue-badge">CLUE #{idx} &bull; {clue.clue_type.upper()}</div>
                    <div class="clue-text">{clue.text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if solved:
            st.caption("The AI has closed the case. Reset its hints or author a new case to keep playing.")
        else:
            if ai.hidden_count():
                st.caption(
                    f"{ai.hidden_count()} clue(s) are still sealed in the case file. "
                    "The AI will only reason with what it has actually read."
                )
                if st.button("📖 Let the AI read the next clue", use_container_width=True):
                    ai.reveal_next()
                    g = ai.guess()
                    st.session_state.ai_flash = (
                        "ok",
                        f"The AI read another clue. It now suspects **{g.who[0]}** in the "
                        f"**{g.where[0]}** with the **{g.what[0]}**.",
                    )
                    st.rerun()
            else:
                st.caption("The AI has read the whole case file.")

            st.markdown("---")
            st.markdown("### 🗣️ Give the AI a hint")
            st.caption("Plain English is fine. An NLTK parser turns your sentence into a logical clue.")
            with st.form("ai_hint_form", clear_on_submit=True):
                hint_text = st.text_area(
                    "Your hint",
                    placeholder="e.g. Ravi is innocent\nor: the murder happened in the Library\nor: it wasn't the rope",
                    height=92,
                    label_visibility="collapsed",
                )
                sent = st.form_submit_button("🔎 Send hint to the AI", type="primary", use_container_width=True)
            if sent and hint_text.strip():
                give_hint(hint_text.strip())
                st.rerun()

            st.caption("Quick hints")
            q1, q2, q3 = st.columns(3)
            if q1.button(f"❌ Not {guess.who[0]}", use_container_width=True):
                give_hint(f"{guess.who[0]} is innocent")
                st.rerun()
            if q2.button(f"📍 Not {guess.where[0]}", use_container_width=True):
                give_hint(f"it was not the {guess.where[0]}")
                st.rerun()
            if q3.button(f"🔪 Not {guess.what[0]}", use_container_width=True):
                give_hint(f"the {guess.what[0]} was not used")
                st.rerun()

    # ------------------ RIGHT: REASONING ------------------
    with right:
        st.markdown("### 🧠 How the AI reads the evidence")
        st.caption("Every suspect it has not ruled out, weighted by the number of surviving theories.")
        for name, count, prob in guess.ranking:
            st.markdown(
                f"**{name}** <span class='ai-quiet'>· {count} theor{'y' if count == 1 else 'ies'}</span>",
                unsafe_allow_html=True,
            )
            st.progress(min(1.0, prob), text=f"{prob * 100:.0f}%")

        with st.expander(f"🧾 Hint log ({len(ai.hints)})", expanded=bool(ai.hints)):
            if not ai.hints:
                st.write("No hints yet. The AI is working from the clue file alone.")
            else:
                for h in ai.hints:
                    label = "Ruled out" if h["sign"] == "exclude" else "Locked in"
                    st.markdown(
                        f"<div class='ai-hint'><b>{label}:</b> {h['value']} "
                        f"<span class='ai-quiet'>· “{h['text']}”</span></div>",
                        unsafe_allow_html=True,
                    )

        st.markdown("---")
        st.markdown("### ⚖️ Close the case")
        if solved:
            st.success("Every other theory has been ruled out. The AI is ready to name your killer.")
        else:
            st.caption(
                "The AI refuses to guess while the case is still open. Rule out the remaining theories "
                "with hints or clues, and it will make the accusation itself."
            )
            st.button("🚨 Make the AI accuse", disabled=True, use_container_width=True)
            st.caption(f"{guess.total_worlds} theories still standing.")

        if st.button("↺ Reset the AI's hints", use_container_width=True):
            ai.reset_hints()
            st.session_state.ai_flash = None
            st.session_state.ai_celebrated = False
            st.session_state.ai_sting_played = False
            st.rerun()

    # ------------------ THE REVEAL ------------------
    if solved:
        if not st.session_state.get("ai_celebrated"):
            st.balloons()
            st.session_state.ai_celebrated = True
        if not st.session_state.get("ai_sting_played"):
            st.audio(str(AUDIO_DIR / STING_FILE), format="audio/wav", autoplay=True)
            st.session_state.ai_sting_played = True
        st.markdown("---")
        st.success("🎉 CASE SOLVED — the AI's theory matches the case you wrote.")
        st.markdown(get_case_solved_stamp_svg(), unsafe_allow_html=True)
        visible = ai.visible_clues()
        evidence = visible[-1].text if visible else None
        st.markdown(generate_crime_story(truth[0], truth[1], truth[2], evidence=evidence))
        if st.button("🖋️ Author another case"):
            st.session_state.ai_case = None
            st.session_state.ai_detective = None
            st.session_state.ai_flash = None
            st.session_state.ai_celebrated = False
            st.session_state.ai_sting_played = False
            st.rerun()


# =========================================================
# MODE 3: CUSTOM CASE & CUSTOM IMAGES
# =========================================================
elif app_mode == "🎨 Custom Case & Images":
    st.markdown("## 🎨 Make Your Own Mystery & Add Custom Images")
    st.markdown(
        "Personalize the game! Upload your own photos for suspects, places, and weapons, "
        "and build your own custom case with clues."
    )

    tab_images, tab_custom_clues = st.tabs(["📸 Upload Custom Images", "📝 Build Custom Clues"])

    with tab_images:
        st.markdown("### 📸 Replace Any Character / Item with Your Own Image")
        st.caption("Upload a JPG, PNG, or WEBP photo. It will instantly appear on the Detective Game Board!")

        upload_cat = st.selectbox("Select Category to Customize", ["WHO (Suspects)", "WHERE (Locations)", "WHAT (Weapons)"])
        cat_key = upload_cat.split(" ")[0]

        target_item = st.selectbox(f"Choose which {cat_key} to change image for:", CATEGORIES[cat_key])

        uploaded_file = st.file_uploader(f"Upload portrait / picture for '{target_item}'", type=["png", "jpg", "jpeg", "webp"])

        if uploaded_file is not None:
            st.session_state.custom_images[target_item] = uploaded_file.read()
            st.success(f"✅ Image updated for '{target_item}'! Switch to the Detective Game Board to see it.")

        if target_item in st.session_state.custom_images:
            st.image(st.session_state.custom_images[target_item], width=180, caption=f"Active Custom Image for {target_item}")
            if st.button(f"🗑️ Revert {target_item} to Default Silhouette"):
                del st.session_state.custom_images[target_item]
                st.rerun()

    with tab_custom_clues:
        st.markdown("### 📝 Build a Custom Case from Clues")
        st.caption("Add your own clues using simple English templates. The AI will check for contradictions in real time!")

        clue_type = st.selectbox(
            "What kind of clue do you want to add?",
            [
                "Negation (Someone or something is NOT involved)",
                "Disjunction (Either X or Y is true)",
                "Implication (If X is true, then Y must be true)",
                "Biconditional (X is true IF AND ONLY IF Y is true)",
                "Exclusive OR (Either X or Y, but NOT both)"
            ]
        )

        all_options = []
        for c, items in CATEGORIES.items():
            for it in items:
                all_options.append(f"{it} ({c})")

        col_a, col_b = st.columns(2)
        with col_a:
            ent1 = st.selectbox("Option A", all_options, key="cust_a")
        with col_b:
            ent2_disabled = "Negation" in clue_type
            ent2 = st.selectbox("Option B", all_options, disabled=ent2_disabled, key="cust_b")

        name1, cat1 = ent1.split(" ")[0], ent1.split("(")[1].replace(")", "")
        var1 = get_var_name(cat1, name1)

        if not ent2_disabled:
            name2, cat2 = ent2.split(" ")[0], ent2.split("(")[1].replace(")", "")
            var2 = get_var_name(cat2, name2)
        else:
            name2, var2 = "", ""

        # Build clean plain text clue
        if "Negation" in clue_type:
            formula_obj = Not(Var(var1))
            clue_str = f"The {cat1.lower()} was NOT {name1}."
            ctype = "negation"
        elif "Disjunction" in clue_type:
            formula_obj = Or(Var(var1), Var(var2))
            clue_str = f"Either {name1} or {name2} was involved."
            ctype = "disjunction"
        elif "Implication" in clue_type:
            formula_obj = Implies(Var(var1), Var(var2))
            clue_str = f"If {name1} is true, then {name2} was used."
            ctype = "implication"
        elif "Biconditional" in clue_type:
            formula_obj = Iff(Var(var1), Var(var2))
            clue_str = f"{name1} occurred if and only if {name2} was used."
            ctype = "biconditional"
        else:
            formula_obj = Xor(Var(var1), Var(var2))
            clue_str = f"Either {name1} or {name2} occurred, but NOT both."
            ctype = "xor"

        st.info(f"**Clue Preview:** \"{clue_str}\"")

        c_add, c_clr = st.columns(2)
        with c_add:
            if st.button("➕ Add This Clue", type="primary", use_container_width=True):
                new_c = Clue(f"CUSTOM_{len(st.session_state.custom_case_clues)+1}", clue_str, formula_obj, ctype)
                st.session_state.custom_case_clues.append(new_c)
                st.success("Clue added!")
                st.rerun()
        with c_clr:
            if st.button("🗑️ Clear Custom Clues", use_container_width=True):
                st.session_state.custom_case_clues = []
                st.rerun()

        st.markdown("---")
        st.markdown("#### 📋 Current Custom Clues")
        if not st.session_state.custom_case_clues:
            st.write("No custom clues added yet.")
        else:
            for idx, c in enumerate(st.session_state.custom_case_clues):
                st.markdown(f"**{idx+1}.** {c.text}")

            # AI validation of custom case
            csp = CSPSolver(CATEGORIES)
            res = csp.solve(st.session_state.custom_case_clues)
            if res.status == "SOLVED":
                w, l, k = res.primary_solution
                st.success(f"✅ **Perfect! Exactly 1 unique solution:** {w} in the {l} with the {k}.")
                if st.button("🚀 Play This Custom Case on Board"):
                    st.session_state.puzzle_secret = (w, l, k)
                    st.session_state.puzzle_clues = list(st.session_state.custom_case_clues)
                    st.session_state.user_board = {}
                    st.session_state.accusation_feedback = None
                    st.success("Case loaded to board! Switch to 'Detective Game Board' to play!")
            elif res.status == "CONTRADICTION":
                st.error("🚨 **Contradiction Detected!** The clues are mutually impossible. 0 solutions exist.")
            else:
                st.warning(f"⚠️ **Underconstrained!** {len(res.solutions)} solutions are currently possible. Add more clues to narrow it down to 1.")
