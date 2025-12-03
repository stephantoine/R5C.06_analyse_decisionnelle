import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy.stats import spearmanr
import numpy as np
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize, Colormap
from matplotlib.figure import Figure
from matplotlib.axes import Axes

script_dir = os.path.dirname(os.path.abspath(__file__))

df_everything = pd.read_csv(os.path.join(script_dir, "everything.csv"))
df_country = pd.read_csv(os.path.join(script_dir, "dictionary_with_medals.csv"))


# Top 10 des pays par nombre de médailles
top10 = df_country.sort_values("MedalCount", ascending=False).head(10)

print("\nTop 10 des pays avec le plus de médailles :\n")
print(top10[["Country", "MedalCount"]])

# Graphique bâton
plt.figure(figsize=(10, 6))
top10_sorted = top10.sort_values("MedalCount", ascending=True)
plt.barh(top10_sorted["Country"], top10_sorted["MedalCount"], color='skyblue')
plt.xlabel("Nombre de médailles")
plt.title("Top 10 des pays par nombre de médailles")
plt.tight_layout()
plt.show()


# problème avec des variables non numerique -> changement de format et suppression des erreurs
df_country["GDP per Capita"] = pd.to_numeric(df_country["GDP per Capita"], errors='coerce')
df_country["Population"] = pd.to_numeric(df_country["Population"], errors='coerce')
df_country["MedalCount"] = pd.to_numeric(df_country["MedalCount"], errors='coerce')

# filtre utile pour bien calculer la correlation après
valid_gdp = df_country.dropna(subset=["MedalCount", "GDP per Capita"])
valid_pop = df_country.dropna(subset=["MedalCount", "Population"])

# Corrélation Spearman -> utilisée pour etabir la correlation entre deux variables sans que la relation de ces deux variables soit affine
rho_gdp, pval_gdp = spearmanr(valid_gdp["MedalCount"], valid_gdp["GDP per Capita"])
rho_pop, pval_pop = spearmanr(valid_pop["MedalCount"], valid_pop["Population"])

print("Corrélation Spearman Medal ↔ GDP :", rho_gdp, "(p-value =", pval_gdp, ")")
print("Corrélation Spearman Medal ↔ Population :", rho_pop, "(p-value =", pval_pop, ")")


# on normalise pour mettre à l'échelle et pas avoir des points trop grands
sizes = np.sqrt(df_country["MedalCount"]) * 10 

# graphique qui étudie le nombre de médailles par pays en fonction du nombre d'habitants et du GDP (PIB)

plt.figure(figsize=(12, 8))
scatter = plt.scatter(
    df_country["Population"],
    df_country["GDP per Capita"],
    s=sizes,
    c=df_country["MedalCount"],
    cmap="viridis",
    alpha=0.7,
    edgecolors="w",
    linewidth=0.5
)
plt.xscale('log')  
plt.yscale('log')  
plt.colorbar(scatter, label="Nombre de médailles")
plt.xlabel("Population")
plt.ylabel("GDP per Capita")
plt.title("Corrélation Population / GDP vs Nombre de médailles")
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.tight_layout()
plt.show()



disciplines = {}   #dictionnarire qui va contenire toutes les disciplines olympiques

for _, row in df_everything.iterrows():
    discipline = row["Discipline"]
    country = row["Country"]

    if discipline not in disciplines:
        disciplines[discipline] = {}

    if country not in disciplines[discipline]:
        disciplines[discipline][country] = 0

    disciplines[discipline][country] += 1

results = []   

for discipline_name, data in disciplines.items():
    medals = list(data.values())               
    nb_country = len(data.keys())             
    std = np.std(medals, dtype=float)       
    results.append((discipline_name, nb_country, std))


for discipline, nb_country, std in results:
    print(f"{discipline}\n\tNombre de pays : {nb_country}\n\tÉcart-type : {std}")

print(f"{len(disciplines.keys())} disciplines analysées")


disciplines_names = [r[0] for r in results]
disciplines_country_count = [r[1] for r in results]
disciplines_stdevs = [r[2] for r in results]

max_nb = max(disciplines_country_count)

cmap_name = "Blues"
cmap: Colormap = plt.get_cmap(cmap_name)
norm = Normalize(0, max_nb)

colors = [cmap(norm(country_count)) for country_count in disciplines_country_count]

fig: Figure
ax: Axes
fig, ax = plt.subplots(figsize=(16, 8), layout="constrained")

fig.colorbar(
    ScalarMappable(norm=norm, cmap=cmap_name),
    ax=ax,
    orientation="vertical",
    label="Nombre de pays",
)

plt.bar(disciplines_names, disciplines_stdevs, color=colors)
plt.xlabel("Disciplines")
plt.xticks(rotation=90)
plt.ylabel("Écarts-types")
plt.title("Écart-type du nombre de médailles par pays pour chaque discipline")
plt.show()

