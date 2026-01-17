import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="NotebookLM Quiz Clone", layout="centered")

# CSS für den minimalistischen Look
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; border: 1px solid #ddd; background: white; transition: 0.3s; }
    .stButton>button:hover { border-color: #4CAF50; color: #4CAF50; }
    .card { padding: 30px; border-radius: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); background: #fdfdfd; border: 1px solid #f0f0f0; margin-bottom: 20px; text-align: center; font-size: 1.3rem; line-height: 1.5; }
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
