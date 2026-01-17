import streamlit as st
import pandas as pd
import os

# --- THEME DEFINITIONEN ---
themes = {
    "Hell (NotebookLM)": {
        "bg": "#ffffff", "card_bg": "#fdfdfd", "text": "#1a1a1a", "border": "#eeeeee"
    },
    "Dunkel": {
        "bg": "#0e1117", "card_bg": "#1d2127", "text": "#fafafa", "border": "#31353f"
    },
    "Kontrast": {
        "bg": "#000000", "card_bg": "#000000", "text": "#ffff00", "border": "#ffff00"
    }
}

st.sidebar.title("🎨 Design & Navigation")
selected_theme = st.sidebar.selectbox("Theme wählen", list(themes.keys()))
t = themes[selected_theme]

# Dynamisches CSS Injektion
st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}
    .stButton>button {{ width: 100%; border-radius: 12px; border: 1px solid {t['border']}; background: {t['card_bg']}; color: {t['text']}; }}
    .card {{ 
        padding: 40px; border-radius: 20px; 
        background: {t['card_bg']}; 
        color: {t['text']};
        border: 2px solid {t['border']};
        text-align: center; font-size: 1.4rem; margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    /* Fix für Tablet/Mobile Sichtbarkeit */
    p, span, label {{ color: {t['text']} !important; }}
    </style>
""", unsafe_allow_html=True)


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
