import pandas as pd
import os

# chemins relatifs
script_dir = os.path.dirname(os.path.abspath(__file__))

# Chargement des fichiers CSV
country_df = pd.read_csv(os.path.join(script_dir, "dictionary.csv"))
summer_df = pd.read_csv(os.path.join(script_dir, "summer.csv"))
winter_df = pd.read_csv(os.path.join(script_dir, "winter.csv"))

#affichage des attributs comportant des valeurs manquantes
print("Attributs avec valeurs manquantes dans dictionary.csv :")
print(country_df.isnull().sum())

print("\nAttributs avec valeurs manquantes dans summer.csv :")
print(summer_df.isnull().sum())     

print("\nAttributs avec valeurs manquantes dans winter.csv :")
print(winter_df.isnull().sum())


#calcul du pourcentage de valeurs manquantes 
total_rows = len(country_df) + len(summer_df) + len(winter_df)
print("Nombre total de lignes dans les trois fichiers : ", total_rows)

total_missing = country_df.isnull().sum().sum() + summer_df.isnull().sum().sum() + winter_df.isnull().sum().sum()
print("Nombre total de valeurs manquantes dans les trois fichiers : ", total_missing)

pourcentage_missing = (total_missing / (total_rows * len(country_df.columns))) * 100
print("Pourcentage de valeurs manquantes dans les trois fichiers : {:.2f}%".format(pourcentage_missing))


# =====================================================================
#  FUSION SUMMER + WINTER  (sans Population ni GDP)
# =====================================================================

summer_df['SEASON'] = 'S'
winter_df['SEASON'] = 'W'

everything_df = pd.concat([summer_df, winter_df], ignore_index=True)

print("\n" + "="*80)
print("Fusion des données Summer et Winter")
print("="*80)
print(f"Nombre de lignes Summer: {len(summer_df)}")
print(f"Nombre de lignes Winter: {len(winter_df)}")
print(f"Nombre total de lignes après fusion: {len(everything_df)}")


special_country_codes = {
    'RU1': 'RUS', 'BOH': 'CZE', 'ANZ': 'AUS', 'URS': 'RUS',
    'GDR': 'GER', 'TCH': 'CZE', 'ROU': 'ROM', 'FRG': 'GER',
    'SRB': 'SCG', 'SGP': 'SIN'
}

everything_df['Country'] = everything_df['Country'].replace(special_country_codes)

codes_to_remove = ['ZZX', 'IOP', 'YUG', 'EUN', 'EUA', 'BWI', 'TTO']
everything_df = everything_df[~everything_df['Country'].isin(codes_to_remove)]


everything_path = os.path.join(script_dir, 'everything.csv')
everything_df.to_csv(everything_path, index=False)

print("\n" + "="*80)
print("Fichier everything.csv créé")
print("="*80)
print(f"Nombre total de lignes: {len(everything_df)}")
print(f"Nombre total de colonnes: {len(everything_df.columns)}")
print(f"\nColonnes: {', '.join(everything_df.columns)}")

print("\nAttributs avec valeurs manquantes dans everything.csv :")
print(everything_df.isnull().sum())


medals = everything_df.groupby("Country").size().reset_index(name="MedalCount")

# print(medals)

# print(country_df)

# Fusion sur le code pays
country_with_medals = pd.merge(
    country_df,
    medals,
    left_on="Code",
    right_on="Country",  # colonne du DataFrame medals
    how="left"
)

# On peut supprimer la colonne supplémentaire 'Country' venant de medals
country_with_medals.drop(columns=["Country_y"], inplace=True)
country_with_medals.rename(columns={"Country_x": "Country"}, inplace=True)

# Remplacer les NaN par 0 pour les pays sans médailles
country_with_medals["MedalCount"] = country_with_medals["MedalCount"].fillna(0).astype(int)

# Sauvegarder le fichier final
output_path = os.path.join(script_dir, "dictionary_with_medals.csv")
country_with_medals.to_csv(output_path, index=False)

print(f"Fichier dictionary.csv enrichi avec MedalCount créé : {output_path}")

