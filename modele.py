import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.cm import get_cmap, ScalarMappable
from matplotlib.colors import Normalize


def main() -> None:
    df = pd.read_csv("everything.csv")
    disciplines: dict[str, dict[str, int]] = {}
    results: list[tuple[str, int, float]] = []
    for _, row in df.iterrows():
        if row["Discipline"] not in disciplines.keys():
            disciplines[row["Discipline"]] = {}
        if row["Country"] not in disciplines[row["Discipline"]]:
            disciplines[row["Discipline"]][row["Country"]] = 0
        disciplines[row["Discipline"]][row["Country"]] += 1

    for discipline in disciplines.keys():
        results.append(decision(disciplines[discipline], discipline))

    print_results(results)
    print(f"{len(disciplines.keys())} disciplines")
    plot_results(results)


def decision(
    discipline: dict[str, int], discipline_name: str
) -> tuple[str, int, float]:
    medals: list[int] = [nb_medals for nb_medals in discipline.values()]
    nb_country = len(discipline.keys())
    std = np.std(medals, dtype=float)  # ecart type
    return discipline_name, nb_country, std


def print_results(results: list[tuple[str, int, float]]) -> None:
    for result in results:
        print(
            f"{result[0]}\n\tNombre de pays : {result[1]}\n\tÉcart-type : {result[2]}"
        )


def plot_results(results: list[tuple[str, int, float]]) -> None:
    disciplines_names: list[str] = [result[0] for result in results]
    disciplines_country_count: list[int] = [result[1] for result in results]
    disciplines_stdevs: list[float] = [result[2] for result in results]

    # min_nb: int = min(disciplines_country_count)
    max_nb: int = max(disciplines_country_count)

    cmap_name: str = "Blues"
    cmap = get_cmap(cmap_name)

    norm: Normalize = Normalize(0, max_nb)

    colors: list = [
        cmap(norm(country_count)) for country_count in disciplines_country_count
    ]

    fig, ax = plt.subplots(layout="constrained")

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


if __name__ == "__main__":
    main()
