import pandas as pd
new_site_data = pd.read_clipboard()
old_site_data = pd.read_clipboard()

new_site_data.head()
old_site_data.head()

allaction_wb = old_site_data.copy()
p_a = pd.read_csv('/Users/trevorross/Desktop/My Projects/bettingatwork/players_and_agents.csv')
p_dict = p_a[['Player','Name']]

red_aa_wb = allaction_wb[['Player','Balance']]
red_aa_wb.Player = [pyr.lower() for pyr in red_aa_wb.Player]
red_aa_wb.rename(columns={"Balance":"Weekly"},inplace=True)

updated_wb = pd.merge(left=red_aa_wb,right=p_dict,how="left",on="Player")


updated_wb.head()

nsd2 = new_site_data[['Customer','Balance']]
nsd2['Player'] = [pyr.lower() for pyr in nsd2.Customer]
nsd2.rename(columns={"Balance":"Weekly"},inplace=True)
nsd2.drop('Customer',axis=1,inplace=True)
ready_data = pd.merge(left=nsd2,right=p_dict,how="left",on="Player")
ready_data.head()