import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Flashcard Hub", layout="centered")

# Styling für den NotebookLM Vibe
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #f0f2f6; }
    .card-box { padding: 20px; border-radius: 15px; border: 1px solid #ddd; background-color: white; min-height: 150px; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 1.2rem; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# 1. Ordner- und Dateiauswahl
st.sidebar.title("📚 Quiz-Kategorien")
folders = [f for f in os.listdir('.') if os.path.isdir(f) and not f.startswith('.')]
category = st.sidebar.selectbox("Kategorie wählen", folders)

if category:
    files = [f for f in os.listdir(category) if f.endswith('.csv')]
    quiz_file = st.sidebar.selectbox("Quiz wählen", files)

    if quiz_file:
        df = pd.read_csv(os.path.join(category, quiz_file))
        
        if 'index' not in st.session_state: st.session_state.index = 0
        if 'show_answer' not in st.session_state: st.session_state.show_answer = False

        # Fortschrittsanzeige
        progress = (st.session_state.index + 1) / len(df)
        st.progress(progress)
        st.write(f"Frage {st.session_state.index + 1} von {len(df)}")

        # Die Karte
        question = df.iloc[st.session_state.index, 0]
        answer = df.iloc[st.session_state.index, 1]

        st.markdown(f'<div class="card-box">{question}</div>', unsafe_allow_html=True)

        if st.button("Antwort zeigen / verbergen"):
            st.session_state.show_answer = not st.session_state.show_answer

        if st.session_state.show_answer:
            st.info(f"**Antwort:**\n\n{answer}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Zurück"):
                st.session_state.index = (st.session_state.index - 1) % len(df)
                st.session_state.show_answer = False
                st.rerun()
        with col2:
            if st.button("Weiter ➡️"):
                st.session_state.index = (st.session_state.index + 1) % len(df)
                st.session_state.show_answer = False
                st.rerun()
