import numpy as np

def decision(discipline: dict[str, int], name: str)-> str:
    medals:list[int] = [nb_medals for nb_medals in discipline.values()]
    nb_country = len(discipline.keys())
    std = np.std(medals) #ecart type
    print(f"Nombre de pays {nb_country} : ecart-type {std}")
    return 0

swimming: dict[str, int] = {
    "HUN" : 1,
    "GRE" : 7 ,
    "AUT" : 2
}
