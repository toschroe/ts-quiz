import streamlit as st
import pandas as pd
import os

# --- SESSION STATE ---
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'reveal' not in st.session_state: st.session_state.reveal = False
if 'font_scale' not in st.session_state: st.session_state.font_scale = 100

# --- SIDEBAR: STEUERUNG ---
st.sidebar.title("🎨 Design & Steuerung")
st.session_state.font_scale = st.sidebar.slider("Schriftgröße (%)", 50, 150, st.session_state.font_scale, 5)

themes = {
    "Hell (NotebookLM)": {"bg": "#ffffff", "card_bg": "#fdfdfd", "text": "#1a1a1a", "border": "#eeeeee"},
    "Dunkel": {"bg": "#0e1117", "card_bg": "#1d2127", "text": "#fafafa", "border": "#31353f"},
    "Kontrast": {"bg": "#000000", "card_bg": "#000000", "text": "#ffff00", "border": "#ffff00"}
}
selected_theme = st.sidebar.selectbox("Theme", list(themes.keys()))
t = themes[selected_theme]
scale = st.session_state.font_scale / 100.0

# --- CSS: LAYOUT & NAVIGATION ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}
    
    /* NAVIGATION OBEN: Keine Gap, nebeneinander */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        gap: 0px !important; /* Lücke komplett weg */
        margin-bottom: 20px !important;
    }}
    [data-testid="column"] {{
        flex: 1 !important;
        min-width: 0 !important;
    }}

    /* BUTTON STYLING */
    .stButton > button {{
        width: 100% !important;
        border-radius: 0px !important; /* Eckig für nahtlosen Übergang */
        border: 1px solid {t['border']} !important;
        background-color: {t['card_bg']} !important;
        color: {t['text']} !important;
        height: 3em;
    }}
    /* Abrundung nur außen links/rechts */
    [data-testid="column"]:first-child button {{ border-top-left-radius: 12px !important; border-bottom-left-radius: 12px !important; }}
    [data-testid="column"]:last-child button {{ border-top-right-radius: 12px !important; border-bottom-right-radius: 12px !important; }}

    .card {{ 
        padding: {30 * scale}px; border-radius: 20px; 
        background: {t['card_bg']}; color: {t['text']};
        border: 2px solid {t['border']}; text-align: center; 
        font-size: {1.4 * scale}rem; margin-top: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
/* HAUPTCONTAINER OPTIMIERUNG */
    [data-testid="stAppViewBlockContainer"] {{
        padding-top: 1.5rem !important; /* Reduziert den riesigen Freiraum oben */
        padding-bottom: 6rem !important; /* Schafft Platz unten für den Antwort-Knopf */
        max-width: 100% !important;
    }}

    /* NAVIGATION OBEN FIX */
    [data-testid="stHorizontalBlock"] {{
        margin-bottom: 10px !important;
    }}

    /* KARTEN-ANPASSUNG */
    .card {{
        margin-top: 0px !important;
        margin-bottom: 15px !important;
        padding: {20 * scale}px !important;
    }}

    /* MEDIA QUERY FÜR HANDY-SPEZIFISCHE FEINHEITEN */
    @media (max-width: 600px) {{
        .stTitle {{
            font-size: 1.8rem !important;
            padding-bottom: 0px !important;
        }}
        [data-testid="stAppViewBlockContainer"] {{
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }}
    }}    
    .stMarkdown, p, span, label {{ color: {t['text']} !important; }}
    </style>
""", unsafe_allow_html=True)

# --- INHALT LADEN ---
BASE_DIR = "Quizzes"
if os.path.exists(BASE_DIR):
    categories = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
    cat = st.sidebar.selectbox("Kategorie", categories)
    if cat:
        path = os.path.join(BASE_DIR, cat)
        files = [f for f in os.listdir(path) if f.endswith('.csv')]
        quiz = st.sidebar.selectbox("Quiz", files)
        
        if quiz:
            df = pd.read_csv(os.path.join(path, quiz))
            
            # 1. TITEL
            st.title(f"📖 {cat}")

            # 2. NAVIGATION (JETZT OBEN)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("⬅️ Zurück"):
                    st.session_state.idx = (st.session_state.idx - 1) % len(df)
                    st.session_state.reveal = False
                    st.rerun()
            with c2:
                if st.button("Weiter ➡️"):
                    st.session_state.idx = (st.session_state.idx + 1) % len(df)
                    st.session_state.reveal = False
                    st.rerun()

            # 3. FRAGE-BEREICH
            q = df.iloc[st.session_state.idx, 0]
            a = df.iloc[st.session_state.idx, 1]
            st.markdown(f'<div class="card">{q}</div>', unsafe_allow_html=True)
            
            # 4. ANTWORT-LOGIK
            if st.button("Antwort prüfen"):
                st.session_state.reveal = not st.session_state.reveal
            
            if st.session_state.reveal:
                st.info(f"**Antwort:** {a}")
