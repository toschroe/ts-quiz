import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd
import os

# --- SESSION STATE FÜR SCHRIFTGRÖSSE ---
if 'font_scale' not in st.session_state:
    st.session_state.font_scale = 100

# --- THEME & NAVIGATION (SIDEBAR) ---
st.sidebar.title("🎨 Design & Steuerung")

# Manuelle Größensteuerung
st.session_state.font_scale = st.sidebar.slider(
    "Schriftgröße (%)", 50, 150, st.session_state.font_scale, 5
)

# Theme Auswahl (wie zuvor)
themes = {
    "Hell (NotebookLM)": {"bg": "#ffffff", "card_bg": "#fdfdfd", "text": "#1a1a1a", "border": "#eeeeee"},
    "Dunkel": {"bg": "#0e1117", "card_bg": "#1d2127", "text": "#fafafa", "border": "#31353f"},
    "Kontrast": {"bg": "#000000", "card_bg": "#000000", "text": "#ffff00", "border": "#ffff00"}
}
selected_theme = st.sidebar.selectbox("Theme", list(themes.keys()))
t = themes[selected_theme]

# --- RESPONSIVE CSS MIT MEDIA QUERIES ---
scale = st.session_state.font_scale / 100.0

st.markdown(f"""
    <style>
    /* Grund-App-Hintergrund */
    .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}
    
    /* Karten-Style */
    .card {{ 
        padding: {30 * scale}px; 
        border-radius: 20px; 
        background: {t['card_bg']}; 
        color: {t['text']};
        border: 2px solid {t['border']};
        text-align: center; 
        font-size: {1.4 * scale}rem; 
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }}
    /* Erzwingt, dass Spalten auf Mobile nebeneinander bleiben */
    [data-testid="column"] {{
        width: 48% !important;
        flex: 1 1 48% !important;
        min-width: 48% !important;
    }}
    
    /* Zusätzlicher Abstand für die Button-Reihe */
    .stHorizontalBlock {{
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        gap: 10px;
    }}
    /* EXPLIZITER FIX FÜR BUTTONS */
    .stButton > button {{
        width: 100%;
        border-radius: 12px;
        border: 1px solid {t['border']} !important;
        background-color: {t['card_bg']} !important;
        color: {t['text']} !important; /* Schriftfarbe des Buttons */
    }}

    /* Fix für Button-Text (manchmal tiefer im DOM) */
    .stButton > button p {{
        color: {t['text']} !important;
    }}

    /* Hover-Effekt: Etwas heller/dunkler als der Hintergrund */
    .stButton > button:hover {{
        border-color: {t['text']} !important;
        background-color: {t['bg']} !important;
        color: {t['text']} !important;
    }}

    /* Alles andere (Sidebar-Labels etc.) auf die richtige Textfarbe zwingen */
    .stMarkdown, p, span, label, .stSelectbox label {{
        color: {t['text']} !important;
    }}
    </style>

""", unsafe_allow_html=True)

# ... (Hier folgt dein CSV-Lade-Code und die Quiz-Logik)


BASE_DIR = "Quizzes"

# Navigation
st.sidebar.title("Navigation")
if not os.path.exists(BASE_DIR):
    st.error(f"Ordner '{BASE_DIR}' nicht gefunden. Bitte erstelle ihn in GitHub.")
else:
    categories = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
    selected_cat = st.sidebar.selectbox("Kategorie", categories) if categories else None

    if selected_cat:
        quiz_path = os.path.join(BASE_DIR, selected_cat)
        quizzes = [f for f in os.listdir(quiz_path) if f.endswith('.csv')]
        selected_quiz = st.sidebar.selectbox("Quiz wählen", quizzes)

        if selected_quiz:
            df = pd.read_csv(os.path.join(quiz_path, selected_quiz))
            
            if 'idx' not in st.session_state: st.session_state.idx = 0
            if 'reveal' not in st.session_state: st.session_state.reveal = False

            # UI
            st.title(f"📖 {selected_cat}")
            
            # Karte anzeigen
            q_text = df.iloc[st.session_state.idx, 0]
            a_text = df.iloc[st.session_state.idx, 1]
            
            st.markdown(f'<div class="card">{q_text}</div>', unsafe_allow_html=True)
            
            if st.button("Antwort anzeigen"):
                st.session_state.reveal = True
            
            if st.session_state.reveal:
                st.success(f"**Antwort:** {a_text}")

            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Previous"):
                    st.session_state.idx = (st.session_state.idx - 1) % len(df)
                    st.session_state.reveal = False
                    st.rerun()
            with col2:
                if st.button("Next"):
                    st.session_state.idx = (st.session_state.idx + 1) % len(df)
                    st.session_state.reveal = False
                    st.rerun()
