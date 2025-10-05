"""
ArcanAI - Application Streamlit Tarot (sélection manuelle des cartes, interprétation AI, français)
Workflow :
1. Sélectionner le type de tirage
2. Sélectionner les cartes tirées physiquement
3. Obtenir la signification des positions et l'interprétation AI
"""

import streamlit as st
from typing import List
from llm_utils import LLMHandler, ReadingResponse

# ---------------------------
# Tarot deck
# ---------------------------
TAROT_DECK = [
    "Le Fou", "Le Magicien", "La Papesse", "L'Impératrice", "L'Empereur",
    "Le Pape", "L'Amoureux", "Le Chariot", "La Force", "L'Hermite",
    "La Roue de Fortune", "La Justice", "Le Pendu", "La Mort", "Tempérance",
    "Le Diable", "La Maison Dieu", "L'Étoile", "La Lune", "Le Soleil",
    "Le Jugement", "Le Monde",
]
SUITS = ["Bâtons", "Coupes", "Épées", "Deniers"]
RANKS = ["As", "Deux", "Trois", "Quatre", "Cinq", "Six", "Sept", "Huit", "Neuf", "Dix", "Valet", "Cavalier", "Reine", "Roi"]
for suit in SUITS:
    for rank in RANKS:
        TAROT_DECK.append(f"{rank} de {suit}")

# ---------------------------
# Tirages
# ---------------------------
SPREADS = {
    "Une carte": ["Unique"],
    "Trois cartes (Passé/Présent/Futur)": ["Passé", "Présent", "Futur"],
    "Trois cartes (Esprit/Corps/Âme)": ["Esprit", "Corps", "Âme"],
    "Croix simple": ["Signifiant", "Obstacle", "Racines", "Passé récent", "Objectif", "Futur proche"],
    "Croix celtique": ["Signifiant", "Obstacle", "Fondation", "Passé", "But conscient", "Futur proche", "Image de soi", "Environnement", "Espoirs/Peurs", "Issue"]
}

# ---------------------------
# Prompts
# ---------------------------

def prompt_position_meanings(question: str, spread_name: str, positions: List[str]) -> str:
    pos_list = "\n".join([f"- {i+1}. {pos}" for i, pos in enumerate(positions)])
    return f"Définis le sens de chaque position pour la question : '{question}' et le tirage : '{spread_name}'. Positions:\n{pos_list}"


def prompt_interpretation(question: str, spread_name: str, positions: List[str], cards: List[str]) -> str:
    paired = "\n".join([f"{pos}: {card}" for pos, card in zip(positions, cards)])
    return f"Interprète chaque carte dans le contexte de la question '{question}' et du tirage '{spread_name}'. Cartes:\n{paired}" 

# ---------------------------
# UI Streamlit
# ---------------------------
st.title("ArcanAI — Lecteur de Tarot AI")
st.markdown("Sélectionnez les cartes tirées physiquement et obtenez l'interprétation AI.")

with st.sidebar:
    spread_name = st.selectbox("Choisissez un tirage:", list(SPREADS.keys()))

question = st.text_input("Votre question:", value="Sur quoi devrais-je me concentrer ce mois-ci ?")

llm = LLMHandler()

# ---------------------------
# Session state
# ---------------------------
if "cards" not in st.session_state:
    st.session_state.cards = [None]*len(SPREADS[spread_name])
if "positions_meaning" not in st.session_state:
    st.session_state.positions_meaning = None
if "reading" not in st.session_state:
    st.session_state.reading = None

# ---------------------------
# Sélection des cartes
# ---------------------------
st.subheader("Sélection des cartes tirées")
selected_cards = []
for i, pos in enumerate(SPREADS[spread_name]):
    card = st.selectbox(f"{pos}:", TAROT_DECK, key=f"card_{i}")
    selected_cards.append(card)
st.session_state.cards = selected_cards

# ---------------------------
# Signification des positions
# ---------------------------
if st.button("Obtenir les significations des positions"):
    with st.spinner("Consultation AI pour les positions..."):
        messages_pos = [
            {"role": "system", "content": "Vous êtes un interprète de tarot clair et bienveillant."},
            {"role": "user", "content": prompt_position_meanings(question, spread_name, SPREADS[spread_name])}
        ]
        try:
            st.session_state.positions_meaning = llm.query_llm(messages_pos)
        except Exception as e:
            st.error(f"Erreur lors de l'appel au LLM: {e}")

if st.session_state.positions_meaning:
    st.subheader("Signification des positions")
    for pm in st.session_state.positions_meaning.positions_meaning:
        st.markdown(f"**{pm.position}**: {pm.meaning}")

# ---------------------------
# Interprétation des cartes
# ---------------------------
if st.button("Interpréter le tirage") and st.session_state.cards:
    with st.spinner("Obtention de la lecture AI..."):
        messages_interp = [
            {"role": "system", "content": "Vous êtes un interprète de tarot bienveillant et clair."},
            {"role": "user", "content": prompt_interpretation(question, spread_name, SPREADS[spread_name], st.session_state.cards)}
        ]
        try:
            st.session_state.reading = llm.query_llm(messages_interp)
        except Exception as e:
            st.error(f"Erreur lors de l'appel au LLM: {e}")

if st.session_state.reading:
    st.subheader("Lecture AI")
    if hasattr(st.session_state.reading, 'cards_interpretation'):
        for ci in st.session_state.reading.cards_interpretation:
            st.markdown(f"**{ci.position} ({ci.card})**: {ci.interpretation}")
    if hasattr(st.session_state.reading, 'synthesis'):
        st.markdown(f"**Synthèse**: {st.session_state.reading.synthesis}")