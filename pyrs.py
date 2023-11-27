import pandas as pd
import numpy as np
from pandas.core.base import DataError


player_data = pd.read_csv('/Users/trevorross/Desktop/My Projects/bettingatwork/players_and_agents.csv')
player_data.head()
player_data[player_data["Name"]=="OPEN"]

def retrieve_players(player_data):
    pyrs = player_data.copy()
    trev = [(pyrs.iloc[x].Player,pyrs.iloc[x].Name) for x in pyrs.index if pyrs.iloc[x].Agent == "Trev"]
    gabe = [(pyrs.iloc[x].Player,pyrs.iloc[x].Name) for x in pyrs.index if pyrs.iloc[x].Agent == "Gabe"]
    orso = [(pyrs.iloc[x].Player,pyrs.iloc[x].Name) for x in pyrs.index if pyrs.iloc[x].Agent == "Orso"]
    none = [(pyrs.iloc[x].Player,pyrs.iloc[x].Name) for x in pyrs.index if pyrs.iloc[x].Agent == "None"]

    trev_ids = [x[0] for x in trev]
    trev_names = [x[1] for x in trev]
    orso_ids = [x[0] for x in orso]
    orso_names = [x[1] for x in orso]
    gabe_ids = [x[0] for x in gabe]
    gabe_names = [x[1] for x in gabe]
    none_ids = [x[0] for x in none]
    none_names = [x[1] for x in none]

    stup = [("Trev","Player ID"),("Trev","Player Name"),("Orso","Player ID"),("Orso","Player Name"),("Gabe","Player ID"),("Gabe","Player Name"),("None","Player ID"),("None","Player Name")]
    id4 = pd.MultiIndex.from_tuples(stup)
    dta = [trev_ids,trev_names,orso_ids,orso_names,gabe_ids,gabe_names,none_ids,none_names]

    for_output = pd.DataFrame(dta,index=id4).transpose()
    for_output.to_clipboard(excel=True)


retrieve_players(player_data)



