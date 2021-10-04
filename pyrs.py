import pandas as pd
import numpy as np

pyrs = pd.read_csv('/Users/trevorross/Desktop/My Projects/bettingatwork/players_and_agents.csv')
pyrs.head()

pyrs.Agent.value_counts()