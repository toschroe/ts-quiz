import streamlit as st
import pandas as pd
import os
import random

# --- KONFIGURATION & THEMES ---
st.set_page_config(page_title="Flashcard Pro", layout="wide", initial_sidebar_state="expanded")

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

# --- HILFSFUNKTIONEN ---
def get_quiz_structure(base_path="Quizzes"):
    """Liest die Ordnerstruktur und CSV-Dateien alphabetisch ein."""
    if not os.path.exists(base_path):
        os.makedirs(base_path)
        # Dummy Daten für den ersten Start
        os.makedirs(f"{base_path}/Beispiel")
        df = pd.DataFrame([["Was ist 2+2?", "4"], ["Hauptstadt von DE?", "Berlin"]])
        df.to_csv(f"{base_path}/Beispiel/Demo.csv", index=False, header=False)

    categories = sorted([d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))])
    structure = {}
    for cat in categories:
        cat_path = os.path.join(base_path, cat)
        files = sorted([f for f in os.listdir(cat_path) if f.endswith('.csv')])
        if files:
            structure[cat] = files
    return structure

def load_csv(path):
    try:
        df = pd.read_csv(path, header=None, names=["Frage", "Antwort"])
        return df.values.tolist()
    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")
        return [["Fehler", "Datei konnte nicht gelesen werden"]]

# --- SESSION STATE INITIALISIERUNG ---
if 'idx' not in st.session_state:
    st.session_state.idx = 0
if 'reveal' not in st.session_state:
    st.session_state.reveal = False
if 'font_scale' not in st.session_state:
    st.session_state.font_scale = 1.0
if 'theme' not in st.session_state:
    st.session_state.theme = "Hell"
if 'shuffle' not in st.session_state:
    st.session_state.shuffle = False
if 'order' not in st.session_state:
    st.session_state.order = []
if 'last_path' not in st.session_state:
    st.session_state.last_path = ""

# --- LOGIK ---
quiz_structure = get_quiz_structure()

# Sidebar Navigation
with st.sidebar:
    st.title("Settings")

    if not quiz_structure:
        st.warning("Keine Quizzes gefunden. Bitte 'Quizzes/' Ordner füllen.")
        st.stop()

    cat_list = list(quiz_structure.keys())
    selected_cat = st.selectbox("Kategorie", cat_list)

    file_list = quiz_structure[selected_cat]
    selected_file = st.selectbox("Quiz-Datei", file_list)

    full_path = os.path.join("Quizzes", selected_cat, selected_file)

    # State Reset bei Dateiwechsel
    if full_path != st.session_state.last_path:
        st.session_state.last_path = full_path
        data = load_csv(full_path)
        st.session_state.order = list(range(len(data)))
        if st.session_state.shuffle:
            random.shuffle(st.session_state.order)
        st.session_state.idx = 0
        st.session_state.reveal = False
        st.rerun()

    st.divider()

    # Shuffle & Reset
    new_shuffle = st.toggle("Shuffle Modus", value=st.session_state.shuffle)
    if new_shuffle != st.session_state.shuffle:
        st.session_state.shuffle = new_shuffle
        data = load_csv(full_path)
        st.session_state.order = list(range(len(data)))
        if new_shuffle:
            random.shuffle(st.session_state.order)
        st.session_state.idx = 0
        st.rerun()

    if st.button("🔄 Neu Mischen"):
        random.shuffle(st.session_state.order)
        st.session_state.idx = 0
        st.rerun()

    if st.button("🔥 Auffrischen (Hard Reset)"):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    # Theme & Font
    st.session_state.theme = st.radio("Theme", list(THEMES.keys()))
    st.session_state.font_scale = st.slider("Schriftgröße", 0.8, 2.5, 1.2)

# Daten laden
current_data = load_csv(st.session_state.last_path)
total_cards = len(st.session_state.order)
current_card_idx = st.session_state.order[st.session_state.idx]
question, answer = current_data[current_card_idx]

# --- CSS INJECTION ---
t = THEMES[st.session_state.theme]
font_size = 20 * st.session_state.font_scale

st.markdown(f"""
    <style>
    /* Viewport Optimierung */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        background-color: {t['bg']};
    }}

    [data-testid="stSidebar"] {{
        background-color: {t['sidebar']};
    }}

    /* Card Design */
    .flashcard {{
        background-color: {t['card_bg']};
        color: {t['text']};
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        min-height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        border: 1px solid rgba(128,128,128,0.1);
        margin: 2rem 0;
        transition: all 0.3s ease;
    }}

    .question-text {{
        font-size: {font_size}px;
        font-weight: 600;
        line-height: 1.4;
    }}

    .answer-box {{
        background-color: {t['accent']}22;
        border-left: 5px solid {t['accent']};
        padding: 1.5rem;
        margin-top: 2rem;
        border-radius: 8px;
        width: 100%;
        color: {t['text']};
        font-size: {font_size * 0.9}px;
    }}

    /* Buttons Scaling */
    .stButton>button {{
        width: 100%;
        border-radius: 12px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- NAVIGATION LOGIK ---
def next_card():
    st.session_state.idx = (st.session_state.idx + 1) % total_cards
    st.session_state.reveal = False

def prev_card():
    st.session_state.idx = (st.session_state.idx - 1) % total_cards
    st.session_state.reveal = False

def back_10():
    st.session_state.idx = (st.session_state.idx - 10) % total_cards
    st.session_state.reveal = False

def reset_idx():
    st.session_state.idx = 0
    st.session_state.reveal = False

def toggle_reveal():
    st.session_state.reveal = not st.session_state.reveal

# --- MAIN UI ---
# Top Navigation
cols_top = st.columns([1, 2, 1])
with cols_top[1]:
    clean_name = selected_file.replace('.csv', '')
    if st.button(f"Weiter mit **{clean_name}** ➡️", key="next_top", use_container_width=True):
        next_card()
        st.rerun()

# Progress
progress = (st.session_state.idx + 1) / total_cards
st.progress(progress)
st.caption(f"Karte {st.session_state.idx + 1} von {total_cards} • {selected_file}")

# Flashcard Area
st.markdown(f"""
    <div class="flashcard">
        <div class="question-text">{question}</div>
    </div>
""", unsafe_allow_html=True)

# Reveal / Answer
if st.button("Antwort einblenden / verbergen (Leertaste)", key="reveal_btn", type="primary"):
    toggle_reveal()
    st.rerun()

if st.session_state.reveal:
    st.markdown(f"""
        <div class="answer-box">
            <b>Antwort:</b><br>{answer}
        </div>
    """, unsafe_allow_html=True)

st.divider()

# Bottom Navigation
cols_bot = st.columns(3)
with cols_bot[0]:
    if st.button("⬅️ Zurück", key="prev_btn"):
        prev_card()
        st.rerun()
with cols_bot[1]:
    if st.button("⏪ 10 zurück", key="back10_btn"):
        back_10()
        st.rerun()
with cols_bot[2]:
    if st.button("🏠 Auf Anfang", key="reset_btn"):
        reset_idx()
        st.rerun()

# --- KEYBOARD SHORTCUTS (JavaScript) ---
# Emuliert Klicks auf Streamlit-Buttons basierend auf ihren Keys
st.components.v1.html(f"""
    <script>
    const doc = window.parent.document;
    doc.addEventListener('keydown', function(e) {{
        if (e.key === 'ArrowRight') {{
            const btn = Array.from(doc.querySelectorAll('button')).find(el => el.innerText.includes('Weiter mit'));
            if (btn) btn.click();
        }}
        if (e.key === 'ArrowLeft') {{
            const btn = Array.from(doc.querySelectorAll('button')).find(el => el.innerText.includes('Zurück'));
            if (btn) btn.click();
        }}
        if (e.key === 'Enter' || e.key === ' ') {{
            const btn = Array.from(doc.querySelectorAll('button')).find(el => el.innerText.includes('Antwort einblenden'));
            if (btn) btn.click();
        }}
    }});
    </script>
""", height=0)
