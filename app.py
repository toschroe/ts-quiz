import streamlit as st
import pandas as pd
import os
import random

# --- KONFIGURATION & THEMES ---
st.set_page_config(
    page_title="Flashcard Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Design-Tokens für die NotebookLM-Ästhetik
THEMES = {
    "Hell": {
        "bg": "#f8f9fa",
        "card_bg": "#ffffff",
        "text": "#212529",
        "sidebar": "#f1f3f5",
        "accent": "#007bff"
    },
    "Dunkel": {
        "bg": "#0e1117",
        "card_bg": "#262730",
        "text": "#fafafa",
        "sidebar": "#161b22",
        "accent": "#58a6ff"
    },
    "Kontrast": {
        "bg": "#000000",
        "card_bg": "#1a1a1a",
        "text": "#ffb86c",
        "sidebar": "#111111",
        "accent": "#ffb86c"
    }
}

# --- HILFSFUNKTIONEN MIT CACHING ---

@st.cache_data
def get_quiz_structure(base_path="Quizzes"):
    """Scannt das Verzeichnis alphabetisch nach Kategorien und Dateien."""
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    categories = sorted([d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))])
    structure = {}
    for cat in categories:
        cat_path = os.path.join(base_path, cat)
        files = sorted([f for f in os.listdir(cat_path) if f.endswith('.csv')])
        if files:
            structure[cat] = files
    return structure

@st.cache_data
def load_csv_data(path):
    """Lädt CSV-Inhalte (Frage in Spalte 1, Antwort in Spalte 2)."""
    if not path or not os.path.exists(path):
        return [["Keine Daten", "Bitte Datei auswählen"]]
    try:
        # Einlesen ohne Header für maximale Flexibilität
        df = pd.read_csv(path, header=None, names=["Frage", "Antwort"])
        return df.values.tolist()
    except Exception as e:
        return [[f"Ladefehler", f"Die Datei konnte nicht gelesen werden: {e}"]]

# --- SESSION STATE INITIALISIERUNG ---
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'reveal' not in st.session_state: st.session_state.reveal = False
if 'font_scale' not in st.session_state: st.session_state.font_scale = 1.2
if 'theme' not in st.session_state: st.session_state.theme = "Hell"
if 'shuffle' not in st.session_state: st.session_state.shuffle = False
if 'order' not in st.session_state: st.session_state.order = []
if 'last_path' not in st.session_state: st.session_state.last_path = None

# --- SIDEBAR LOGIK ---
quiz_structure = get_quiz_structure()

with st.sidebar:
    st.title("NotebookLM Quiz")

    if not quiz_structure:
        st.info("Erstelle einen Ordner 'Quizzes/' mit Unterordnern und CSV-Dateien.")
        st.stop()

    # Auswahl-Kette
    sel_cat = st.selectbox("Themenbereich", list(quiz_structure.keys()))
    sel_file = st.selectbox("Datei auswählen", quiz_structure[sel_cat])
    current_full_path = os.path.join("Quizzes", sel_cat, sel_file)

    # Detektion von Quiz-Wechseln (Source of Truth Check)
    if current_full_path != st.session_state.last_path:
        st.session_state.last_path = current_full_path
        raw_content = load_csv_data(current_full_path)
        st.session_state.order = list(range(len(raw_content)))
        if st.session_state.shuffle:
            random.shuffle(st.session_state.order)
        st.session_state.idx = 0
        st.session_state.reveal = False

    st.divider()

    # Steuerungs-Optionen
    is_shuffle = st.toggle("Shuffle Modus", value=st.session_state.shuffle)
    if is_shuffle != st.session_state.shuffle:
        st.session_state.shuffle = is_shuffle
        st.session_state.idx = 0
        if is_shuffle:
            random.shuffle(st.session_state.order)
        else:
            st.session_state.order.sort()
        st.rerun()

    if st.button("🔄 Neu durchmischen"):
        random.shuffle(st.session_state.order)
        st.session_state.idx = 0
        st.rerun()

    if st.button("🔥 Auffrischen (Cache Reset)"):
        st.cache_data.clear()
        st.session_state.last_path = None
        st.rerun()

    st.divider()
    st.session_state.theme = st.radio("Theme", list(THEMES.keys()))
    st.session_state.font_scale = st.slider("Schriftgröße", 0.8, 2.5, 1.2)

# --- DATEN FÜR DIE ANZEIGE ---
current_data = load_csv_data(current_full_path)
total_cards = len(st.session_state.order)

if total_cards == 0:
    st.warning("Dieses Quiz enthält keine gültigen Daten.")
    st.stop()

# Sicherstellen, dass der Index valide ist
if st.session_state.idx >= total_cards:
    st.session_state.idx = 0

current_card_pos = st.session_state.order[st.session_state.idx]
question, answer = current_data[current_card_pos]

# --- RESPONSIVE CSS INJECTION ---
t = THEMES[st.session_state.theme]
font_size = 20 * st.session_state.font_scale

st.markdown(f"""
    <style>
    /* Globales Layout & NotebookLM Ästhetik */
    .block-container {{
        background-color: {t['bg']};
        max-width: 900px;
        margin: auto;
        padding-top: 1.5rem !important;
        padding-bottom: 6rem !important;
        transition: all 0.3s ease;
    }}

    [data-testid="stSidebar"] {{
        background-color: {t['sidebar']};
    }}

    /* Die Flashcard */
    .flashcard {{
        background-color: {t['card_bg']};
        color: {t['text']};
        padding: 2.5rem;
        border-radius: 28px;
        box-shadow: 0 12px 45px rgba(0,0,0,0.1);
        min-height: 350px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        border: 1px solid rgba(128,128,128,0.1);
        margin: 1rem 0;
    }}

    .question-text {{
        font-size: {font_size}px;
        font-weight: 600;
        line-height: 1.4;
    }}

    .answer-box {{
        background-color: {t['accent']}15;
        border-left: 6px solid {t['accent']};
        padding: 1.5rem;
        margin-top: 1.5rem;
        border-radius: 12px;
        width: 100%;
        color: {t['text']};
        font-size: {font_size * 0.9}px;
        animation: fadeIn 0.3s ease-out;
    }}

    @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}

    /* RESPONSIVE DESIGN */
    @media (max-width: 640px) {{
        .block-container {{ padding: 1rem !important; }}
        .flashcard {{ min-height: 280px; padding: 1.5rem; }}
        .question-text {{ font-size: {font_size * 0.8}px; }}
    }}

    /* UI Fixes */
    .stButton>button {{ width: 100%; border-radius: 12px; height: 3rem; }}
    header[data-testid="stHeader"] {{ background: transparent !important; }}
    </style>
""", unsafe_allow_html=True)

# --- NAVIGATION FUNKTIONEN ---
def go_next():
    st.session_state.idx = (st.session_state.idx + 1) % total_cards
    st.session_state.reveal = False

# --- MAIN UI ---
clean_name = sel_file.replace('.csv', '')

# Obere Statuszeile
meta_col, next_col = st.columns([1, 1])
with meta_col:
    st.caption(f"Karte {st.session_state.idx + 1} von {total_cards} • {clean_name}")
with next_col:
    if st.button(f"Weiter ➡️", key="btn_next_top"):
        go_next()
        st.rerun()

st.progress((st.session_state.idx + 1) / total_cards)

# Flashcard Bereich
st.markdown(f"""
    <div class="flashcard">
        <div class="question-text">{question}</div>
    </div>
""", unsafe_allow_html=True)

# Interaktion
if st.button("Antwort einblenden / verbergen", type="primary", use_container_width=True):
    st.session_state.reveal = not st.session_state.reveal
    st.rerun()

if st.session_state.reveal:
    st.markdown(f"""
        <div class="answer-box">
            <b>Lösung:</b><br>{answer}
        </div>
    """, unsafe_allow_html=True)

st.divider()

# Untere Navigation (Adaptive Buttons)
b1, b2, b3 = st.columns(3)
with b1:
    if st.button("⬅️ Zurück", use_container_width=True):
        st.session_state.idx = (st.session_state.idx - 1) % total_cards
        st.session_state.reveal = False
        st.rerun()
with b2:
    if st.button("⏪ -10", use_container_width=True):
        st.session_state.idx = (st.session_state.idx - 10) % total_cards
        st.session_state.reveal = False
        st.rerun()
with b3:
    if st.button("🏠 Start", use_container_width=True):
        st.session_state.idx = 0
        st.session_state.reveal = False
        st.rerun()

# --- JAVASCRIPT BRIDGE (Shortcuts & Swipe) ---
st.components.v1.html(f"""
    <script>
    const p_doc = window.parent.document;

    // Keyboard Listener
    p_doc.addEventListener('keydown', (e) => {{
        if (e.key === 'ArrowRight') {{
            const b = Array.from(p_doc.querySelectorAll('button')).find(el => el.innerText.includes('Weiter'));
            if (b) b.click();
        }}
        if (e.key === ' ' || e.key === 'Enter') {{
            const b = Array.from(p_doc.querySelectorAll('button')).find(el => el.innerText.includes('Antwort einblenden'));
            if (b) b.click();
        }}
    }});

    // Swipe Geste
    let startX = 0;
    p_doc.addEventListener('touchstart', e => {{ startX = e.changedTouches[0].screenX; }}, false);
    p_doc.addEventListener('touchend', e => {{
        let endX = e.changedTouches[0].screenX;
        if (startX - endX > 100) {{
            const b = Array.from(p_doc.querySelectorAll('button')).find(el => el.innerText.includes('Weiter'));
            if (b) b.click();
        }}
    }}, false);
    </script>
""", height=0)
