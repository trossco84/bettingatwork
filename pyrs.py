import pandas as pd
import numpy as np

pyrs = pd.read_csv('/Users/trevorross/Desktop/My Projects/bettingatwork/players_and_agents.csv')
pyrs.head()

pyrs[pyrs.Agent=="Orso"][pyrs.Name.str.contains("Chris")]

dataFrame[dataFrame['column name'].str.contains('string')]

pyraccess = pd.read_clipboard()

pa2 = pyraccess.drop_duplicates('Player',keep='last')
pa2.to_clipboard()