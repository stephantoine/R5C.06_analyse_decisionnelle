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
st.write("Outil d’aide à la décision basé sur les médailles, la population et le GDP per capita.")

# ==========================================
#        CHARGEMENT DES DONNÉES
# ==========================================

@st.cache_data
def load_data():
    df_results = pd.read_csv("everything.csv")
    df_dict = pd.read_csv("dictionary_with_medals.csv")
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

# merge avec données socio-éco
merged = counts.to_frame().merge(df_dict, on="Country", how="left")

# nettoyage basique
merged["Population"].replace(0, np.nan, inplace=True)
merged["Population"].fillna(merged["Population"].median(), inplace=True)
merged["GDP per Capita"].fillna(merged["GDP per Capita"].median(), inplace=True)

# NORMALISATIONS
merged["Medals_per_capita"] = merged["Medals"] / merged["Population"]
merged["Medals_per_GDP"] = merged["Medals"] / merged["GDP per Capita"]

# STATISTIQUES GLOBALES
std = merged["Medals"].std()
mean_medals = merged["Medals"].mean()
top3_ratio = merged["Medals"].nlargest(3).sum() / merged["Medals"].sum()

# corrélations structurelles (avec filtrage)
valid_pop = merged.dropna(subset=["Medals", "Population"])
valid_gdp = merged.dropna(subset=["Medals", "GDP per Capita"])

rho_gdp, pval_gdp = spearmanr(valid_gdp["MedalCount"], valid_gdp["GDP per Capita"])
rho_pop, pval_pop = spearmanr(valid_pop["MedalCount"], valid_pop["Population"])

print("Corrélation Spearman Medal ↔ GDP :", rho_gdp, "(p-value =", pval_gdp, ")")
print("Corrélation Spearman Medal ↔ Population :", rho_pop, "(p-value =", pval_pop, ")")


max_medals_per_capita = merged["Medals_per_capita"].max() if not merged["Medals_per_capita"].isna().all() else np.nan

# ==========================================
#        AFFICHAGE DES KPI
# ==========================================

st.header(f"📊 Analyse de la discipline : **{choice}**")

col1, col2, col3 = st.columns(3)
col1.metric("Pays participants", len(merged))
col2.metric("Écart-type des médailles", f"{std:.2f}")
col3.metric("Moyenne de médailles/pays", f"{mean_medals:.2f}")

col4, col5 = st.columns(2)
col4.metric("Top 3 domination", f"{top3_ratio:.1%}")
col5.metric("Corr. Spearman médailles ↔ population",
            f"{rho_pop:.2f}" if not np.isnan(rho_pop) else "N/A")

col6, col7 = st.columns(2)
col6.metric("Corr. Spearman médailles ↔ GDP per capita",
            f"{rho_gdp:.2f}" if not np.isnan(rho_gdp) else "N/A")
col7.metric("Médaille / million hab. (max)",
            f"{max_medals_per_capita:.4f}" if not np.isnan(max_medals_per_capita) else "N/A")

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
#   GRAPHIQUE 2 — MÉDAILLES NORMALISÉES
# ==========================================

st.subheader("⚖️ Médailles normalisées par population")
fig2, ax2 = plt.subplots(figsize=(12, 4))
merged.set_index("Country")["Medals_per_capita"].plot(kind="bar", ax=ax2)
ax2.set_xlabel("Pays")
ax2.set_ylabel("Médailles / Population")
ax2.set_title("Médailles par habitant")
st.pyplot(fig2)

# ==========================================
#   DÉCISIONNAIRE (modèle déterministe)
# ==========================================

st.header("🧠 Verdict d’équité")
score = 0

if std < 2: score += 1
if top3_ratio < 0.5: score += 1
if not np.isnan(rho_pop) and abs(rho_pop) < 0.2: score += 1
if not np.isnan(rho_gdp) and abs(rho_gdp) < 0.2: score += 1

if score >= 3:
    verdict = "Équitable"
    color = "🟩"
    recommandation = (
        "La discipline est globalement équilibrée.\n"
        "➡️ Maintenir le niveau d’investissement.\n"
        "➡️ Encourager la participation large."
    )
elif score == 2:
    verdict = "Modérément équilibrée"
    color = "🟨"
    recommandation = (
        "Quelques déséquilibres existent.\n"
        "➡️ Ajustements budgétaires ciblés conseillés.\n"
        "➡️ Programmes pour pays moins performants."
    )
else:
    verdict = "Inéquitable"
    color = "🟥"
    recommandation = (
        "La discipline présente une forte domination structurelle.\n"
        "➡️ Augmenter le financement pour les pays moins performants.\n"
        "➡️ Réformes d’accès, formation, développement.\n"
        "➡️ Analyses approfondies des barrières socio-économiques."
    )

st.subheader(f"{color} Verdict : **{verdict}**")
st.write(recommandation)

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
st.write("*Analyse combinant performance sportive et contexte socio-économique.*")
