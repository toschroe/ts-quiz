import streamlit as st
import pandas as pd
import os
import random
import streamlit.components.v1 as components

# --- INITIALISIERUNG ---
# Wir initialisieren die Zustände, falls sie noch nicht existieren.
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'reveal' not in st.session_state: st.session_state.reveal = False
if 'font_scale' not in st.session_state: st.session_state.font_scale = 100
if 'order' not in st.session_state: st.session_state.order = []
if 'last_quiz' not in st.session_state: st.session_state.last_quiz = ""
if 'last_shuffle' not in st.session_state: st.session_state.last_shuffle = False

# --- SIDEBAR: DESIGN & LOGIK ---
st.sidebar.title("🎨 Design & Logik")

themes = {
    "Hell (NotebookLM)": {"bg": "#ffffff", "sidebar": "#f8f9fa", "card_bg": "#fdfdfd", "text": "#1a1a1a", "border": "#eeeeee"},
    "Dunkel": {"bg": "#0e1117", "sidebar": "#161b22", "card_bg": "#1d2127", "text": "#fafafa", "border": "#31353f"},
    "Kontrast": {"bg": "#0a0e14", "sidebar": "#11151c", "card_bg": "#0a0e14", "text": "#ffb86c", "border": "#ffb86c"}
}
selected_theme = st.sidebar.selectbox("Theme wählen", list(themes.keys()))
t = themes[selected_theme]

shuffle_mode = st.sidebar.checkbox("Zufällige Reihenfolge", value=st.session_state.last_shuffle)

if st.sidebar.button("🎲 Neu Mischen"):
    st.session_state.order = []
    st.session_state.idx = 0
    st.rerun()

st.session_state.font_scale = st.sidebar.slider("Schriftgröße (%)", 50, 150, st.session_state.font_scale, 5)
scale = st.session_state.font_scale / 100.0

# --- CSS: VOLLSTÄNDIGE INTEGRATION ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}
    [data-testid="stSidebar"] {{ background-color: {t['sidebar']} !important; border-right: 1px solid {t['border']}; }}
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{ color: {t['text']} !important; }}
    [data-testid="stAppViewBlockContainer"] {{ padding-top: 2rem !important; padding-bottom: 6rem !important; }}

    .card {{ 
        padding: {25 * scale}px; border-radius: 20px; 
        background: {t['card_bg']}; color: {t['text']};
        border: 2px solid {t['border']}; text-align: center; 
        font-size: {1.3 * scale}rem; margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        min-height: 200px;
        display: flex; align-items: center; justify-content: center;
    }}

    .stButton > button {{
        width: 100% !important; border-radius: 12px !important;
        border: 1px solid {t['border']} !important;
        background-color: {t['card_bg']} !important;
        color: {t['text']} !important;
        height: 3.8em !important;
        margin-bottom: 5px !important;
        transition: transform 0.1s ease;
    }}
    .stButton > button:active {{ transform: scale(0.98); }}
    
    header[data-testid="stHeader"] {{ background-color: transparent !important; }}
    header[data-testid="stHeader"] svg {{ fill: {t['text']} !important; }}
    .stMarkdown, p, span, label, .stCaption {{ color: {t['text']} !important; }}
    </style>
""", unsafe_allow_html=True)

# --- KEYBOARD SHORTCUTS (JAVASCRIPT HACK) ---
components.html(
    f"""
    <script>
    const doc = window.parent.document;
    const handleKey = (e) => {{
        if (e.key === 'Enter' || e.code === 'Space') {{
            e.preventDefault();
            const btn = Array.from(doc.querySelectorAll('button')).find(el => el.innerText.includes('Antwort prüfen'));
            if (btn) btn.click();
        }} else if (e.key === 'ArrowRight') {{
            e.preventDefault();
            const btn = Array.from(doc.querySelectorAll('button')).find(el => el.innerText.includes('Weiter mit'));
            if (btn) btn.click();
        }} else if (e.key === 'ArrowLeft') {{
            e.preventDefault();
            const btn = Array.from(doc.querySelectorAll('button')).find(el => el.innerText.includes('Zurück (1 Karte)'));
            if (btn) btn.click();
        }}
    }};
    doc.removeEventListener('keydown', handleKey);
    doc.addEventListener('keydown', handleKey);
    </script>
    """,
    height=0,
)

# --- INHALT LADEN ---
BASE_DIR = "Quizzes"
if os.path.exists(BASE_DIR):
    categories = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
    cat = st.sidebar.selectbox("Kategorie", categories)
    
    if cat:
        path = os.path.join(BASE_DIR, cat)
        files = [f for f in os.listdir(path) if f.endswith('.csv')]
        quiz_file = st.sidebar.selectbox("Quiz", files)
        
        if quiz_file:
            quiz_name_clean = os.path.splitext(quiz_file)[0].replace('_', ' ')
            df = pd.read_csv(os.path.join(path, quiz_file))
            num_cards = len(df)

            # SYNCHRONISATION: Wenn sich das Quiz oder der Modus ändert
            if (st.session_state.last_quiz != quiz_file or 
                st.session_state.last_shuffle != shuffle_mode or 
                not st.session_state.order or 
                len(st.session_state.order) != num_cards):
                
                st.session_state.order = list(range(num_cards))
                if shuffle_mode:
                    random.shuffle(st.session_state.order)
                
                st.session_state.idx = 0
                st.session_state.last_quiz = quiz_file
                st.session_state.last_shuffle = shuffle_mode
                st.session_state.reveal = False
                st.rerun()
            
            # Anzeige der aktuellen Karte
            st.progress((st.session_state.idx + 1) / num_cards)
            st.caption(f"Karte {st.session_state.idx + 1} von {num_cards} | ⌨️ [Enter/Space]: Antwort | [→]: Weiter | [←]: Zurück")

            # 1. NAVIGATION OBEN (Weiter)
            # Wir nutzen einen Key, um Streamlit zu zwingen, den Button-State sauber zu trennen
            if st.button(f"Weiter mit {quiz_name_clean} ➡️", key="next_btn"):
                st.session_state.idx = (st.session_state.idx + 1) % num_cards
                st.session_state.reveal = False
                st.rerun()

            # 2. FRAGE
            # WICHTIG: Wir berechnen die Zeile erst direkt vor der Anzeige
            current_row_idx = st.session_state.order[st.session_state.idx]
            question_text = df.iloc[current_row_idx, 0]
            answer_text = df.iloc[current_row_idx, 1]
            
            st.markdown(f'<div class="card">{question_text}</div>', unsafe_allow_html=True)
            
            # 3. ANTWORT
            if st.button("Antwort prüfen", key="reveal_btn"):
                st.session_state.reveal = not st.session_state.reveal
            
            if st.session_state.reveal:
                st.info(f"**Antwort:** {answer_text}")
                
            # 4. NAVIGATION UNTEN
            st.write("---") 
            if st.button("⬅️ Zurück (1 Karte)", key="back_btn"):
                st.session_state.idx = (st.session_state.idx - 1) % num_cards
                st.session_state.reveal = False
                st.rerun()
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("⏪ 10 zurück", key="back10_btn"):
                    st.session_state.idx = (st.session_state.idx - 10) % num_cards
                    st.session_state.reveal = False
                    st.rerun()
            with c2:
                if st.button("🏠 Anfang", key="reset_btn"):
                    st.session_state.idx = 0
                    st.session_state.reveal = False
                    st.rerun()
else:
    st.warning("Ordner 'Quizzes' nicht gefunden. Bitte erstelle den Ordner 'Quizzes' und lege dort Kategorien (Unterordner) mit CSV-Dateien an.")
