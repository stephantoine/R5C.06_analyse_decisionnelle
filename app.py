import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

# ==========================================
#        CONFIGURATION GÉNÉRALE
# ==========================================
st.set_page_config(
    page_title="Analyse d’équité des disciplines",
    page_icon="🏅",
    layout="wide",
)

st.title("🏅 Analyse d’équité des disciplines sportives")
st.write("Outil d’aide à la décision basé sur les médailles et la concentration du top 3.")

# ==========================================
#        CHARGEMENT DES DONNÉES
# ==========================================
@st.cache_data
def load_data():
    df_results = pd.read_csv("everything.csv")
    df_dict = pd.read_csv("dictionary_with_medals.csv")
    df_dict.columns = df_dict.columns.str.strip()  # nettoyage colonnes
    return df_results, df_dict

df, df_dict = load_data()

# ==========================================
#        CHOIX DE LA DISCIPLINE
# ==========================================
disciplines = sorted(df["Discipline"].unique())
choice = st.selectbox("Choisissez une discipline :", disciplines)

# ==========================================
#        CALCUL DES MÉDAILLES PAR PAYS
# ==========================================
subset = df[df["Discipline"] == choice]
counts = subset["Country"].value_counts().rename("Medals")

counts_df = counts.to_frame().reset_index().rename(columns={"index":"Country"})
merged = counts_df.merge(df_dict, on="Country", how="left")

# ==========================================
#   CORRÉLATIONS SPEARMAN SOCIO-ÉCO
# ==========================================
st.subheader("📐 Corrélations socio-économiques (Spearman)")

merged["Medals"] = pd.to_numeric(merged["Medals"], errors="coerce")
merged["GDP per Capita"] = pd.to_numeric(merged["GDP per Capita"], errors="coerce")
merged["Population"] = pd.to_numeric(merged["Population"], errors="coerce")

# GDP
valid_gdp = merged.dropna(subset=["Medals", "GDP per Capita"])
if len(valid_gdp) > 3:
    rho_gdp, pval_gdp = spearmanr(valid_gdp["Medals"], valid_gdp["GDP per Capita"])
else:
    rho_gdp = np.nan

# Population
valid_pop = merged.dropna(subset=["Medals", "Population"])
if len(valid_pop) > 3:
    rho_pop, pval_pop = spearmanr(valid_pop["Medals"], valid_pop["Population"])
else:
    rho_pop = np.nan

# ==========================================
#        STATISTIQUES DE MÉDAILLES
# ==========================================
std = merged["Medals"].std()
mean_medals = merged["Medals"].mean()
top3_ratio = merged["Medals"].nlargest(3).sum() / merged["Medals"].sum()

# Score dispersion (écart-type relatif)
std_relative = std / mean_medals if mean_medals != 0 else 0
score_dispersion = 1 - np.tanh(std_relative)

# Score top 3
score_top3 = 1 - top3_ratio

# ==========================================
#   SCORE D'ÉQUITÉ FINAL INCLUANT SPEARMAN
# ==========================================
# On considère qu'une corrélation élevée réduit l'équité
spearman_penalty = 0
if not np.isnan(rho_gdp):
    spearman_penalty += abs(rho_gdp)
if not np.isnan(rho_pop):
    spearman_penalty += abs(rho_pop)
spearman_penalty /= 2  # moyenne si les deux existent

# On combine dispersion, top3 et Spearman (le 1 - spearman_penalty réduit l'équité si forte corrélation)
score_final = np.mean([score_dispersion, score_top3, 1 - spearman_penalty])

# ==========================================
#        AFFICHAGE DES KPI
# ==========================================

st.header(f"📊 Analyse de la discipline : **{choice}**")

# On peut utiliser 7 colonnes pour inclure Spearman GDP / Pop
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Pays participants", len(merged))
col2.metric("Écart-type des médailles", f"{std:.2f}")
col3.metric("Moyenne de médailles/pays", f"{mean_medals:.2f}")
col4.metric("Top 3 domination", f"{top3_ratio:.1%}")
col5.metric("Score dispersion", f"{score_dispersion:.2f}")

col6, col7 = st.columns(2)

# Spearman GDP
if not np.isnan(rho_gdp):
    col6.metric(f"Spearman Médailles ↔ GDP", f"{rho_gdp:.2f} (p={pval_gdp:.3f})")
else:
    col6.metric(f"Spearman Médailles ↔ GDP", "Données insuffisantes")

# Spearman Population
if not np.isnan(rho_pop):
    col7.metric(f"Spearman Médailles ↔ Pop", f"{rho_pop:.2f} (p={pval_pop:.3f})")
else:
    col7.metric(f"Spearman Médailles ↔ Pop", "Données insuffisantes")

st.subheader(f"🧠 Score global d’équité : {score_final:.2f}")

# Verdict final
if score_final >= 0.75:
    verdict = "Équitable 🟩"
    recommandation = (
        "La discipline est globalement équilibrée.\n"
        "➡️ Maintenir le niveau d’investissement.\n"
        "➡️ Encourager la participation large."
    )
elif score_final >= 0.5:
    verdict = "Modérément équilibrée 🟨"
    recommandation = (
        "Quelques déséquilibres existent.\n"
        "➡️ Ajustements budgétaires ciblés conseillés.\n"
        "➡️ Programmes pour pays moins performants."
    )
else:
    verdict = "Inéquitable 🟥"
    recommandation = (
        "La discipline présente une forte domination structurelle.\n"
        "➡️ Augmenter le financement pour les pays moins performants.\n"
        "➡️ Réformes d’accès, formation, développement.\n"
        "➡️ Analyses approfondies des barrières socio-économiques."
    )

st.subheader(f"Verdict : **{verdict}**")
st.write(recommandation)

# ==========================================
#   GRAPHIQUE 1 — MÉDAILLES BRUTES PAR PAYS
# ==========================================
st.subheader("📈 Médailles par pays")
fig, ax = plt.subplots(figsize=(12, 4))
merged.set_index("Country")["Medals"].plot(kind="bar", ax=ax)
ax.set_xlabel("Pays")
ax.set_ylabel("Médailles")
ax.set_title(f"Médailles brutes – {choice}")
st.pyplot(fig)

# ==========================================
#   COURBE CUMULATIVE (LORENZ SIMPLE)
# ==========================================
st.subheader("📉 Courbe cumulative des médailles")
sorted_medals = merged.sort_values("Medals")["Medals"]
cumulative = sorted_medals.cumsum() / sorted_medals.sum()

fig3, ax3 = plt.subplots(figsize=(10, 4))
ax3.plot(cumulative.values, marker="o")
ax3.set_title("Courbe cumulative – Concentration des médailles")
ax3.set_xlabel("Pays (du moins au plus performant)")
ax3.set_ylabel("Part cumulée")
st.pyplot(fig3)

st.markdown("---")
st.write("*Analyse combinant performance sportive, concentration des médailles et facteurs socio-économiques.*")
