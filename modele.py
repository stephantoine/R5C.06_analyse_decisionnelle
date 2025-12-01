import numpy as np
import pandas as pd


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


if __name__ == "__main__":
    main()
