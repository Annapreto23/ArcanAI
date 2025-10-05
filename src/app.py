"""
ArcanAI - Application Streamlit Tarot (sélection manuelle des cartes, interprétation AI, français)
Workflow :
1. Sélectionner le type de tirage
2. Sélectionner les cartes tirées physiquement
3. Obtenir la signification des positions et l'interprétation AI
"""


import streamlit as st
from typing import List
from llm_utils import LLMHandler

# ---------------------------
# Configuration
# ---------------------------
st.set_page_config(page_title="ArcanAI — Les Arcanes Parlent", layout="wide")

# Style mystique
st.markdown("""
<style>
body {
    background-color: #0b0b0d;
    color: #e6d5b8;
    font-family: 'Georgia', serif;
}
h1, h2, h3 {
    color: #d4af37;
    text-align: center;
    text-shadow: 0px 0px 8px #d4af37;
}
.card-icon {
    width: 50px;
    height: 80px;
    border: 1px solid #d4af37;
    border-radius: 6px;
    background: rgba(212,175,55,0.08);
    display: inline-block;
    margin: 3px;
    box-shadow: 0 0 8px rgba(212,175,55,0.3);
}
.card-icon:hover {
    background: rgba(212,175,55,0.2);
    cursor: pointer;
}
div[data-testid="stButton"] > button {
    background-color: #1f1f23;
    color: #d4af37;
    border-radius: 10px;
    border: 1px solid #d4af37;
    transition: all 0.2s ease;
}
div[data-testid="stButton"] > button:hover {
    background-color: #d4af37;
    color: #1f1f23;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Jeu de tarot
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
    "Trois cartes (Passé / Présent / Futur)": ["Passé", "Présent", "Futur"],
    "Croix simple": ["Signifiant", "Obstacle", "Racines", "Passé récent", "Objectif", "Futur proche"],
}

# ---------------------------
# Prompts
# ---------------------------
def prompt_position_meanings(question: str, spread_name: str, positions: List[str]) -> str:
    pos_list = "\n".join([f"- {i+1}. {pos}" for i, pos in enumerate(positions)])
    return f"Pour la question : '{question}', décris ce que symbolise chaque position du tirage '{spread_name}'.\n{pos_list}"

def prompt_interpretation(question: str, spread_name: str, positions: List[str], cards: List[str]) -> str:
    paired = "\n".join([f"{pos}: {card}" for pos, card in zip(positions, cards)])
    return f"Pour la question '{question}', révèle le message que portent ces cartes dans le tirage, en expliquant d'abord ce que signifie la carte de manière générale, avant d'expliquer son lien avec la question '{spread_name}'.\n{paired}"

# ---------------------------
# Interface principale
# ---------------------------
st.title("✨ ArcanAI ✨")
st.markdown("#### *Laisse parler les Arcanes...*")

st.markdown("### Choisis la disposition du tirage :")

cols = st.columns(len(SPREADS))
for i, (spread_name, positions) in enumerate(SPREADS.items()):
    with cols[i]:
        st.markdown(f"#### {spread_name}")
        if spread_name == "Une carte":
            st.markdown("<div class='card-icon'></div>", unsafe_allow_html=True)
        elif "Trois cartes" in spread_name:
            st.markdown("<div>" + " ".join(["<div class='card-icon'></div>" for _ in range(3)]) + "</div>", unsafe_allow_html=True)
        elif "Croix" in spread_name:
            st.markdown("""
                <div style='display:grid; grid-template-columns: repeat(3, 1fr); gap:8px; justify-items:center;'>
                    <div></div><div class='card-icon'></div><div></div>
                    <div class='card-icon'></div><div class='card-icon'></div><div class='card-icon'></div>
                    <div></div><div class='card-icon'></div><div></div>
                </div>
            """, unsafe_allow_html=True)
        if st.button("Choisir", key=f"spread_{i}"):
            st.session_state.selected_spread = spread_name

if "selected_spread" not in st.session_state:
    st.stop()

spread_name = st.session_state.selected_spread
positions = SPREADS[spread_name]

st.markdown(f"### Tirage sélectionné : **{spread_name}**")

question = st.text_input("Formule ta question :", value="Sur quoi devrais-je concentrer mon énergie ce mois-ci ?")

# ---------------------------
# Sélection manuelle des cartes
# ---------------------------
st.markdown("### Sélectionne les cartes révélées :")
selected_cards = []
cols = st.columns(len(positions))
for i, (pos, col) in enumerate(zip(positions, cols)):
    with col:
        st.markdown(f"**{pos}**")
        card = st.selectbox("", TAROT_DECK, key=f"card_{i}")
        selected_cards.append(card)

st.session_state.cards = selected_cards

# ---------------------------
# Invocation de l'Oracle
# ---------------------------
llm = LLMHandler()

if st.button("Révéler la signification des positions"):
    with st.spinner("Les arcanes murmurent..."):
        messages_pos = [
            {"role": "system", "content": "Tu es l'oracle qui révèle le sens profond de chaque position du tirage."},
            {"role": "user", "content": prompt_position_meanings(question, spread_name, positions)}
        ]
        st.session_state.positions_meaning = llm.query_llm(messages_pos)

if "positions_meaning" in st.session_state and st.session_state.positions_meaning:
    st.markdown("### ✴ Signification des positions ✴")
    for pm in st.session_state.positions_meaning.positions_meaning:
        st.markdown(f"**{pm.position}** — {pm.meaning}")

if st.button("Révéler le message des cartes"):
    with st.spinner("Les cartes s'alignent dans le silence..."):
        messages_interp = [
            {"role": "system", "content": "Tu es l'oracle qui dévoile le message du tirage avec bienveillance et clarté."},
            {"role": "user", "content": prompt_interpretation(question, spread_name, positions, st.session_state.cards)}
        ]
        st.session_state.reading = llm.query_llm(messages_interp)

if "reading" in st.session_state and st.session_state.reading:
    st.markdown("### 🔮 Lecture des Arcanes 🔮")
    for ci in st.session_state.reading.cards_interpretation:
        st.markdown(f"**{ci.position} ({ci.card})** — {ci.interpretation}")
    st.markdown(f"**Synthèse** — {st.session_state.reading.synthesis}")
