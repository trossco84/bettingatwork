import pandas as pd
import numpy as np

pyrdata = pd.read_csv('/Users/trevorross/Desktop/My Projects/bettingatwork/players_and_agents.csv')
pd2 = pyrdata.copy()

pd2.pivot(index=None,columns=['Agent'],values=['Name']).stack().
pd2.groupby(level=0).first()
pd2.stack(level=0)

gabe = 
