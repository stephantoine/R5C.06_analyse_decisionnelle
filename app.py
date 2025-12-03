import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr


# streamlit est une librairie pour afficher une page web, avec du markdown 
st.set_page_config(
    page_title="Analyse d’équité des disciplines",
    layout="wide"
)

st.title("Analyse d’équité des disciplines sportives")
st.write("Outil d’analyse et de statistiques pour aide à la décision")

# load les données 
@st.cache_data
def load_data():
    df_results = pd.read_csv("everything.csv")
    df_dict = pd.read_csv("dictionary_with_medals.csv")
    df_dict.columns = df_dict.columns.str.strip()  
    return df_results, df_dict

df, df_dict = load_data()

# select pour le choix de la discipline
disciplines = sorted(df["Discipline"].unique())
choice = st.selectbox("Choisissez une discipline :", disciplines)


# calcul des médailles par pays
subset = df[df["Discipline"] == choice]
counts = subset["Country"].value_counts().rename("Medals")

counts_df = counts.to_frame().reset_index().rename(columns={"index":"Country"})
merged = counts_df.merge(df_dict, on="Country", how="left")



# calcul des corrélations de spearman

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



# calcul des statistiques (kpi)
std = merged["Medals"].std()
mean_medals = merged["Medals"].mean()
top3_ratio = merged["Medals"].nlargest(3).sum() / merged["Medals"].sum()

# Score dispersion (écart-type relatif)
std_relative = std / mean_medals if mean_medals != 0 else 0
score_dispersion = 1 - np.tanh(std_relative)

# Score top 3
score_top3 = 1 - top3_ratio

# calcul du score d'équité
spearman_penalty = 0
if not np.isnan(rho_gdp):
    spearman_penalty += abs(rho_gdp)
if not np.isnan(rho_pop):
    spearman_penalty += abs(rho_pop)
spearman_penalty /= 2  

score_final = np.mean([score_dispersion, score_top3, 1 - spearman_penalty])



st.markdown("## ")  
st.header(f"Analyse de la discipline : **{choice}**")
st.markdown("---")
st.subheader("Indicateurs")  


#affichage des kpi
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


if score_final >= 0.75:
    verdict = "Équitable"
    recommandation = [
        "La discipline est globalement équilibrée.",
        "Maintenir le niveau d’investissement.",
        "Encourager la participation large."
    ]

elif score_final >= 0.5:
    verdict = "Modérément équilibrée"
    recommandation = [
        "Quelques déséquilibres existent.",
        "Ajustements budgétaires ciblés conseillés.",
        "Programmes pour pays moins performants."
    ]

else:
    verdict = "Inéquitable"
    recommandation = [
        "La discipline présente une forte domination structurelle.",
        "Augmenter le financement pour les pays moins performants.",
        "Réformes d’accès, formation, développement.",
        "Analyses approfondies des barrières socio-économiques."
    ]


#affichae de l'indicateur final pour définir l'équité
#avec les décisions à prendre
st.markdown("---")
st.subheader(f"Score global d’équité : {score_final:.2f}")
st.subheader(f"Verdict : **{verdict}**")
for i in range(len(recommandation)):
    if i == 0: 
        st.write("Situation : ", recommandation[i])
        pass
    elif i == 1 :
        st.write("Décisions : ")
        st.write("- " + recommandation[i])
    else : 
        st.write("- " + recommandation[i])
st.markdown("---")



# ptit graphique du nombre de médailles par pays 
st.subheader("Médailles par pays")
fig, ax = plt.subplots(figsize=(12, 4))
merged.set_index("Country")["Medals"].plot(kind="bar", ax=ax)
ax.set_xlabel("Pays")
ax.set_ylabel("Médailles")
ax.set_title(f"Nombre de médailles par pays")
st.pyplot(fig)

#courbe cumulative pour observer la repartition des médailles en cumulant le nombre de médailles obtenues par pays en partant de celui qui en a le moins
st.subheader("Courbe cumulative des médailles")
sorted_medals = merged.sort_values("Medals")["Medals"]
cumulative = sorted_medals.cumsum() / sorted_medals.sum()

fig3, ax3 = plt.subplots(figsize=(10, 4))
ax3.plot(cumulative.values, marker="o")
ax3.set_title("Courbe cumulative – Concentration des médailles")
ax3.set_xlabel("Pays")
ax3.set_ylabel("Nombre de médailles cumulées")
st.pyplot(fig3)
