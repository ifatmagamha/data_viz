from __future__ import annotations

import streamlit as st

from src.logging_setup import setup_logging
from src.config import settings
from src.controller import prepare_all, get_proposals, get_figure, get_png

setup_logging()

st.set_page_config(page_title="Auto DataViz (Gemini)", layout="wide")
st.title("Auto DataViz – Streamlit + Gemini")

with st.sidebar:
    st.header("Config")
    st.write(f"Gemini model: **{settings.gemini_model}**")
    st.caption("Upload CSV → Gemini propose 3 viz → tu choisis → export PNG")

question = st.text_area("Problématique", placeholder="Ex: Quel genre maximise la popularité moyenne ?")
uploaded = st.file_uploader("Upload CSV", type=["csv"])

if uploaded is None:
    st.warning("Upload un CSV pour commencer.")
    st.stop()

# Prepare dataset + profiling text
try:
    dataset, profile_text = prepare_all(uploaded)
except Exception as e:
    st.error(f"Erreur chargement/profiling CSV: {e}")
    st.stop()

st.subheader("Aperçu")
st.dataframe(dataset.df.head(settings.max_rows_preview), use_container_width=True)

with st.expander("Schéma envoyé à Gemini"):
    st.code(dataset.schema_summary)

with st.expander("Profil rapide (améliore Gemini)"):
    st.code(profile_text)

if st.button("Générer 3 propositions", type="primary"):
    if not question.strip():
        st.error("Écris une problématique d’abord.")
    else:
        with st.spinner("Gemini réfléchit..."):
            try:
                resp = get_proposals(question, dataset, profile_text)
                st.session_state["proposals"] = resp
            except Exception as e:
                st.error(f"Erreur Gemini/JSON: {e}")

if "proposals" not in st.session_state:
    st.info("Clique sur **Générer 3 propositions**.")
    st.stop()

resp = st.session_state["proposals"]
proposals = resp.proposals

st.divider()
st.subheader("Choisis une proposition")

labels = [f'{p.id}. {p.title} ({p.chart_type})' for p in proposals]
idx = st.radio("Propositions", options=list(range(len(proposals))), format_func=lambda i: labels[i])

chosen = proposals[idx]
st.markdown("**Justification (Gemini)**")
st.write(chosen.reasoning)

try:
    fig = get_figure(dataset.df, chosen)
    st.plotly_chart(fig, use_container_width=True)
    png = get_png(fig)
    st.download_button("Télécharger PNG", data=png, file_name="visualisation.png", mime="image/png")
except Exception as e:
    st.error(f"Erreur génération/exports: {e}")
