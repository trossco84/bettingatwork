### INSTRUCTIONS ####

# Pregame
#1. Login to Red.ag and go to Figures -> Weekly Balance -> Specified Week
#2. highlight the table from the first P of player to the last number in the table
    # don't include the totals row
#3. copy with whatever method you like (ctrl/cmd + c)

# Pressing Play
#4a. RUNS SELECTION IN JUPYTER NOTEBOOK: Press play in the top right
#4b. RUNS SELECTION IN TERMINAL: 
#      i) navigate to this folder (cd folder path)
#      ii) run the app (python3 datapipeline.py)

# Postgame
#5. open backup_data_storage excel file, create a new sheet and paste (ctrl/cmd + p)
    # format as needed
#6. Screenshot important areas and send to intended parties
    #old mac: command + shift + 4
    #new mac: command + ctrl + shift + 4
    #windows: windows button + shift + s


### DATA PIPELINE CODE ###
#Import Packages
##libraries
import numpy as np
import pandas as pd
import warnings
import datetime
##additional code
import master_analysis

#Change Default Settings
warnings.filterwarnings("ignore", category=FutureWarning)
pd.options.mode.chained_assignment = None

#Retrieve Data
this_week = pd.read_clipboard()
pyragt = pd.read_csv('/Users/trevorross/Desktop/My Projects/bettingatwork/players_and_agents.csv')

# kevin's balance
with open("/Users/trevorross/Desktop/My Projects/bettingatwork/kevin.txt") as f:
    kbal = f.readlines()
kbal = kbal[0]
kbal = float(kbal)

# function to update agent and player data
def update_pyragt(w3, pyragt):
    nones = w3[w3.Agent == "None"]
    
    #update pyragt dataframe and csv
    for ind in range(0,len(nones)):
        pyr = nones.iloc[ind].Player
        newplayer = input(f'what is the name for player {pyr}')
        newagent = input('and who is the agent?')
        pyragt.loc[pyr].Name = newplayer
        pyragt.loc[pyr].Agent = newagent
    
    pyragt.reset_index(inplace=True)
    pyragt.to_csv('/Users/trevorross/Desktop/My Projects/bettingatwork/players_and_agents.csv',index=False)
    pyragt.set_index('Player',inplace=True)

    #update weekly df
    w3['Agent'] = [pyragt.loc[x].Agent for x in w3.Player]
    
    return w3, pyragt

# function to add new data to master data file (raw_archives)
def update_master(weekly_records,lm):
    # master_analysis.process_new_week(lm)
    week_string = lm
    raw_data = pd.read_csv('/Users/trevorross/Desktop/My Projects/bettingatwork/raw_archives.csv')
    r2=raw_data.copy()

    nw2 = pd.read_csv(f'/Users/trevorross/Desktop/My Projects/bettingatwork/weekly_outputs/{week_string}.csv')
    
    #processing
    nw2['Amts'] = np.where(nw2['Action']=='Pay',nw2['Amount']*-1,nw2['Amount'])
    nw3 = nw2.groupby('Agent').sum().reset_index().drop(['Amount'],axis=1)
    nw3['Expected Balance'] = nw3.Amts
    nw3.drop(['Amts'],axis=1,inplace=True)
    num_players = pd.DataFrame(nw2.Agent.value_counts())
    num_players['Number of Players'] = num_players.Agent
    num_players.drop(['Agent'],axis=1,inplace=True)
    nw3 = nw3.set_index('Agent').join(num_players).reset_index()
    nw3['Final Balance'] = sum(nw3['Expected Balance'])/len(nw3)

    #adding the week
    nw3['Week'] = week_string

    #updating raw archives
    r3 = r2.append(nw3,ignore_index=True)
    r3.to_csv('/Users/trevorross/Desktop/My Projects/bettingatwork/raw_archives.csv',index=False)
    
    raw_data = r3.copy()
    rgroup = raw_data.groupby('Agent').sum()
    numweeks = len(raw_data.Week.unique())
    rgroup = rgroup.rename(columns={'Expected Balance':'Total Revenue'})
    tots = rgroup[['Total Revenue']]
    tots['Avg Players per Week'] = rgroup['Number of Players']/numweeks
    tots['Avg Revenue per Week'] = tots['Total Revenue']/numweeks
    tots.to_csv('/Users/trevorross/Desktop/My Projects/bettingatwork/agent_totals.csv')


# question logic for adding non-book slips
def any_slips(w2):
    any_more='y'
    while any_more not in ['no',"No","NO","N","n"]:
        slippyr = input("slip player id?")
        amt = int(input("amount to add?"))
        current = w2.loc[slippyr].Weekly
        adjust = current + amt
        w2.Weekly.loc[slippyr] = adjust
        any_more = input('any more slips?')
    return w2

# function to add or adjust player amounts after week close
def adjust_amounts(w2):
    w2.set_index('Player',inplace=True)

    #slips
    slipcheck = input('any slips?')
    yes = ['Yes','yes','Y','y',"YES"]
    if slipcheck in yes:
        w2 = any_slips(w2)

    kb2 = kbal
    #kevin specific
    if 'pyr109' in list(w2.index):
        kcur = w2.loc['pyr109'].Weekly
        #bubble of 100
        if abs(kcur)<100:
            kb2 = kb2 + kcur
            with open("/Users/trevorross/Desktop/My Projects/bettingatwork/kevin.txt",'w') as f:
                f.write(f'{kb2}')
            w2.Weekly.pyr109 = 0
        #5% kickbacks
        elif kcur < -100:
            k5back = int(kcur * 0.95)
            w2.Weekly.pyr109 = k5back
            with open("/Users/trevorross/Desktop/My Projects/bettingatwork/kevin.txt",'w') as f:
                f.write('0')
        else:    
            with open("/Users/trevorross/Desktop/My Projects/bettingatwork/kevin.txt",'w') as f:
                f.write('0')

    #10% kickback for those greater than 1000
    w2.Weekly = w2.Weekly.apply(lambda x: x*0.9 if x < -1000 else x)

    w2.reset_index(inplace=True)
    return w2

# function to initiate the agent updating process
def agent_updates(w3,agents):
    no = ['no',"No","NO","N","n"]
    yes = ['Yes','yes','Y','y',"YES"]
    any_more='y'
    while any_more not in no:
        #player id must be full, example: pyr132
        namecheck = 'n'
        while namecheck in no: 
            pyrid = input("player id?")
            pname = pyragt.loc[pyrid].Name
            print(pname)
            namecheck = input(f'is this the player you wanted to change? ({pname})')
            
        newname = input("who's the new guy? \n (this input must match name in Management)")
        newagt = input(f'new agent? \n current values are: {agents}')
        if newagt not in agents:
            agents.append(newagt)
        
        pyr2 = pyragt.copy()
        pyr2.loc[pyrid].Name = newname
        pyr2.loc[pyrid].Agent = newagt

        any_more = input('any more updates?')

    return pyr2,agents

# bulk function that injects new data into existing data and processes agent specific tasks
def process_agents(w2,pyragt):
    w3 = w2.copy()
    pyragt.set_index('Player',inplace=True)

    #matching agents to their players
    w3['Agent'] = [pyragt.loc[x].Agent for x in w3.Player]
    agents = w3.Agent.unique()
    w3.fillna("None",inplace=True)   

    #agent updates
    acheck = input('any agent updates?')
    yes = ['Yes','yes','Y','y',"YES"]
    if acheck in yes:
        pyragt,agents = agent_updates(w3,agents)
    
    #updating player agent list if there is a new account
    if "None" in agents:
        w3, pyragt = update_pyragt(w3, pyragt)

    #christian logic
    all_5 = 0
    c_accts = ['pyr118','pyr123','pyr121','pyr122','pyr130']
    c_bal = 0
    if set(list(w3.Player)).isdisjoint(set(c_accts)) == False:
        for acct in c_accts:
            if acct in list(w3.Player):
                all_5 = all_5+1
                weekly = w3.set_index('Player').loc[acct].Weekly
                if weekly < 0:
                    add = weekly * 0.1
                    c_bal = c_bal+add

    c_bal = int(abs(c_bal))
    if c_bal%4 >1:
        c_bal = c_bal + 1
    
    c_weekly = w3.set_index('Player').loc['pyr107'].Weekly
    if all_5 == 5:
        if c_weekly<0:
            c_giveback = c_weekly*.1

    c_bal =c_bal+c_giveback
    c_logic = f'we each pay christian {int(c_bal/4)}'

    #adding an action column
    w3['Action'] = ['Request' if x < 0 else 'Pay' for x in w3.Weekly]
    w3['Amount'] = [abs(x) for x in w3.Weekly]
    w4 = w3[['Agent','Player','Name','Action','Amount']]
    w5 = w4.groupby(['Agent','Action','Player','Name','Amount']).sum()
    w5.to_clipboard()

    #agent specific views
    weekly_records_df = pd.DataFrame()
    print('AGENTS:')
    for agnt in agents:
        agent_view = w4[w4.Agent == agnt]
        agent_view.set_index('Agent',inplace=True)
        weekly_records_df = weekly_records_df.append(agent_view)
        print(agent_view)
        print()

    #recording the weekly output
    today = datetime.datetime.today() 
    last_monday = today - datetime.timedelta(days=today.weekday(),weeks=1)
    lm_string = str(last_monday.date())
    weekly_records_df.to_csv(f'/Users/trevorross/Desktop/My Projects/bettingatwork/weekly_outputs/{lm_string}.csv')

    update_master(weekly_records_df,lm_string)

    print()
    print('Christian:')
    print(c_logic)
    print()

    return w4,pyragt
        
# function to create totals and values for output
def process_totals(w4):
    w5 = w4.copy()
    w5['Amount'] = np.where(w5['Action']=='Pay',w5['Amount']*-1,w5['Amount'])
    totals_df = w5.groupby('Agent').sum()
    pyr_counts = pd.DataFrame(w5.Agent.value_counts())
    pyr_counts.rename(columns={'Agent':"Num. Players"},inplace=True)
    tdf = pyr_counts.join(totals_df)
    tdf['Final Balance'] = tdf.Amount.sum()/4
    print("TOTALS:")
    print(tdf)
    return tdf

#function to determine settlement transactions amongst agents
def inter_bookie(tdf):
    tdf['Demand'] = [tdf.iloc[x]['Final Balance']-tdf.iloc[x].Amount for x in tdf.reset_index().index]
    na = len(tdf) - 1
    td2 = tdf.sort_values('Demand')
    while td2.Demand.any() >= 0.1:
        if abs(td2.iloc[0,3]) > abs(td2.iloc[na,3]):
            amt = abs(td2.iloc[na,3])
            print(f'{td2.index[0]} pays {td2.index[na]} {amt}')
            td2.iloc[0,3] = td2.iloc[0,3] + amt
            td2.iloc[na,3] = td2.iloc[na,3] - amt
            td2 = td2.sort_values('Demand')
        else:
            amt = abs(td2.iloc[0,3])
            print(f'{td2.index[0]} pays {td2.index[na]} {amt}')
            td2.iloc[0,3] = td2.iloc[0,3] + amt
            td2.iloc[na,3] = td2.iloc[na,3] - amt
            td2 = td2.sort_values('Demand')
        
        if ((td2.Demand< 1.0).all()):
            break

#Process Runner
def weekly_processing(weekly_data,pyragt):
    w2 = weekly_data[['Player','Name','Weekly']]
    if type(w2.Weekly[0]) == type('yo!'):
        w2.Weekly = w2.Weekly.str.replace(',', '').astype(float)
    w2.Player = w2.Player.apply(lambda x: x.lower())
    pyragt.Player = pyragt.Player.apply(lambda x: x.lower())
    w2 = adjust_amounts(w2)
    w4, pyragt = process_agents(w2,pyragt)
    print()
    totalsdf = process_totals(w4)
    print()
    inter_bookie(totalsdf)

#Code Starter
if __name__ == "__main__":
    weekly_processing(this_week,pyragt)

#walk thru's
# weekly_data = this_week
# this_week.head()
# pyragt.head()
