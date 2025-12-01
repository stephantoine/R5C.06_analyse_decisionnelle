import numpy as np
import pandas as pd


def decision(discipline: dict[str, int], name: str) -> None:
    medals: list[int] = [nb_medals for nb_medals in discipline.values()]
    nb_country = len(discipline.keys())
    std = np.std(medals)  # ecart type
    print(f"{name}\n\tNombre de pays : {nb_country}\n\tÉcart-type : {std}")


def main() -> None:
    df = pd.read_csv("everything.csv")
    disciplines: dict[str, dict[str, int]] = {}
    for _, row in df.iterrows():
        if row["Discipline"] not in disciplines.keys():
            disciplines[row["Discipline"]] = {}
        if row["Country"] not in disciplines[row["Discipline"]]:
            disciplines[row["Discipline"]][row["Country"]] = 0
        disciplines[row["Discipline"]][row["Country"]] += 1

    for discipline in disciplines.keys():
        decision(disciplines[discipline], discipline)

    print(f"{len(disciplines.keys())} disciplines")


if __name__ == "__main__":
    main()
