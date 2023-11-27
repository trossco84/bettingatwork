### INSTRUCTIONS ####

# Pregame
#1. Login to Red.ag and go to Figures -> Weekly Balance -> Specified Week
#2. highlight the table from the first P of player to the last number in the table
    # don't include the totals row
#3. copy with whatever method you like (ctrl/cmd + c)

# Pressing Play
#4a. RUNS SELECTION IN JUPYTER NOTEBOOK: Press play in the top right/left depending on IDE
#4b. RUNS SELECTION IN TERMINAL: 
#      i) navigate to this folder (cd folder path)
#      ii) run the app (python3 datapipeline.py)

# Postgame
#5. open backup_data_storage excel file, create a new sheet and paste (ctrl/cmd + p) into cell B4
    # format as needed
#6. Screenshot important areas and send to intended parties
    #old mac: command + shift + 4
    #new mac: command + ctrl + shift + 4
    #windows: windows button + shift + s


### DATA PIPELINE CODE ###
#Import Packages
##libraries
import warnings
import datetime
import numpy as np
import pandas as pd
##additional code
# import master_analysis

#Change Default Settings
warnings.filterwarnings("ignore", category=FutureWarning)
pd.options.mode.chained_assignment = None

#Retrieve Data
## copying the clipboard (this may be updated in a later version to screen scraped)
this_week = pd.read_clipboard()
## reading in the players and agents data table
pyragt = pd.read_csv('/Users/trevorross/Desktop/My Projects/bettingatwork/players_and_agents.csv')

# kevin's balance
## opening the file and reading the one line
with open("/Users/trevorross/Desktop/My Projects/bettingatwork/kevin.txt") as f:
    kbal = f.readlines()
## retreiving the balance as a number to be used later
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

    #10% kickback for those greater than 1500
    # w2.Weekly = w2.Weekly.apply(lambda x: x*0.9 if x < -1000 else x)

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
    #last monday's string date
    today = datetime.datetime.today() 
    last_monday = today - datetime.timedelta(days=today.weekday(),weeks=1)
    lm_string = str(last_monday.date())
    
    
    w3 = w2.copy()
    pyragt.set_index('Player',inplace=True)

    #matching agents to their players
    extra_players = list(set(w3.Player) - set(pyragt.index))
    if len(extra_players)>=1:
        pyragt.reset_index(inplace=True)
        for newguy in extra_players:
            pyragt.loc[len(pyragt.index)] = [newguy,"newname","newagent"]
        pyragt.set_index('Player',inplace=True)
    
    w3['Agent'] = [pyragt.loc[x].Agent for x in w3.Player]
    agents = w3.Agent.unique()
    w3.fillna("None",inplace=True)  
    
    #updating player agent list if there is a new account
    if "None" in agents:
        w3, pyragt = update_pyragt(w3, pyragt)

    if "newagent" in agents:
        w3, pyragt = update_pyragt(w3, pyragt)

    #agent updates
    acheck = input('any agent updates?')
    yes = ['Yes','yes','Y','y',"YES"]
    if acheck in yes:
        pyragt,agents = agent_updates(w3,agents)

    #agent logic
    christians_guys = ['pyr118','pyr123','pyr121','pyr122','pyr130','pyr150','pyr171','pyr183','pyr200']
    marks_guys = ['pyr191']
    for sub_agent in ["christian","mark"]:
        all_C = 0
        if sub_agent == "christian":
            c_accts = christians_guys
            sub_id = "pyr107"
        else:
            c_accts = marks_guys
            sub_id = "pyr136"
        
        # count number of players
        # add 10% kickbacks for negative players
        c_bal = 0
        if set(list(w3.Player)).isdisjoint(set(c_accts)) == False:
            for acct in c_accts:
                if acct in list(w3.Player):
                    all_C = all_C+1
                    weekly = w3.set_index('Player').loc[acct].Weekly
                    if weekly < 0:
                        add = weekly * 0.1
                        c_bal = c_bal+add


        # automatically give 10% kickbacks
        c_bal2 = int(abs(c_bal))
        if c_bal2%3 >1:
            c_bal2 = c_bal2 + 1
        
        # if they bet
        if sub_id in list(w3.Player):
            c_weekly = w3.set_index('Player').loc[sub_id].Weekly
            
            # and if they lost
            if c_weekly<0:
                # they get another 10%
                c_giveback = -(c_weekly*.1)
                c_final =c_bal2+c_giveback
            else:
                c_giveback=0
                c_final=c_bal2
        
        # if they didn't bet
        else:
            c_weekly = 0
            
            # if their players went up
            if w3[w3['Player'].isin(c_accts)].Weekly.sum() > 0:
                # they get 50 bucks flat for collecting
                c_giveback = 50
                c_final =c_bal2+c_giveback
            else:
                # otherwise they get 20% kickbacks 
                c_bal2 = c_bal*2
                c_final = c_bal2
                c_giveback=0
            
        # if all_C >= 5:
        #     if c_weekly<0:
        #         c_giveback = -(c_weekly*.1)
        #         c_final =c_bal2+c_giveback
        #     else:
        #         c_giveback=50
        #         c_final=c_bal2
        # else:
        #     c_final=c_bal2
        #     c_giveback=0 
        if sub_agent == "christian":
            c_logic = f'we each pay {sub_agent} ${int(c_final/3)} total, ${int(c_bal2/3)} for kickbacks and ${int(c_giveback/3)} for 5+ active players'
        else:
            m_logic = f'we each pay {sub_agent} ${int(c_final/3)} total, ${int(c_bal2/3)} for kickbacks and ${int(c_giveback/3)} for 5+ active players'

    #cole/kaufman logic
    if 'pyr160' in list(w3.Player):
        k_bal = w3.set_index('Player').loc['pyr160'].Weekly
        
        w3.set_index('Player',inplace = True)
        w3.Weekly.pyr160 = 0
        w3.reset_index(inplace = True)
        
        if k_bal < 0: 
            k_message = f"cole's guy (kaufman) owes {k_bal}"
        else:
            k_message = f"cole's guy (kaufman) is due {k_bal}"
    else:
        k_message = "cole's guy (kaufman) didn't bet this week"
        
        
    #10% freeplay logic
    # for pyr in w2.index:
    #     if w2.loc[pyr].Weekly < -1000:
    
    freeplay_data = pd.read_csv('/Users/trevorross/Desktop/My Projects/bettingatwork/freeplaydata.csv')
    weekly_fp = w3[w3.Weekly <= -500][["Player","Name","Agent","Weekly"]]
    weekly_fp.rename(columns={"Player":"Player ID",
                              "Name":"Player Name",
                              "Weekly":"Total Losses"}, inplace=True)
    weekly_fp["Date"] = lm_string
    weekly_fp.set_index("Date",inplace=True)
    weekly_fp.reset_index(inplace=True)
    weekly_fp["Freeplay Rule"] = "20%"
    weekly_fp["Freeplay Amount"] = weekly_fp["Total Losses"].abs() * .2
    
    #updating raw archives
    fp_new = freeplay_data.append(weekly_fp,ignore_index=True)
    fp_new.to_csv('/Users/trevorross/Desktop/My Projects/bettingatwork/freeplaydata.csv',index=False)
    
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

    weekly_records_df.to_csv(f'/Users/trevorross/Desktop/My Projects/bettingatwork/weekly_outputs/{lm_string}.csv')

    update_master(weekly_records_df,lm_string)

    print()
    print("Sub Agents")
    print(c_logic)
    print(m_logic)
    print()
    print("Cole's Clients:")
    print(k_message)
    print()
    if len(weekly_fp)>0:
        print("Freeplays:")
        print(weekly_fp.groupby(["Agent","Player ID","Player Name"]).agg({"Total Losses":"sum","Freeplay Amount":"sum"}))
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
    tdf['Final Balance'] = tdf.Amount.sum()/3
    print("TOTALS:")
    print(tdf)
    return tdf

#function to determine settlement transactions amongst agents
def inter_bookie(tdf):
    td2 = tdf.copy()
    print()
    print("calculating splits")
    # print()
    team_eff = True
    week_earnings = td2.Amount.sum()
    try:
        # If we make more than 1K in a week
        if week_earnings > 1000:
            print(' weekly criteria met')
            
            # Check if any agents accounted for > 75% of winnings
            for pyr in list(td2.index):
                if td2.loc[pyr].Amount > (week_earnings * .75):
                    team_eff = False
                    winner = pyr
                    print(f"    {winner} had a good week")
                    
                    # Make sure they don't have the lowest # of players
                    if td2.loc[winner]["Num. Players"] != td2["Num. Players"].min():
                        print(f"    player count criteria met")
                        print()
                        
                        # They get a 40% split for that week (other players get 30%)
                        for_keeps = td2.Amount.sum() * .1
                        print(f"{winner} gets an extra {round(for_keeps*2/3,1)}")
                        for pyr2 in list(td2.index):
                            if pyr2 != pyr:
                                tdf.loc[pyr2, 'Final Balance'] = tdf.loc[pyr2, 'Final Balance'] - (for_keeps / 3)
                        print()
                    else:
                        print(" player count not met")
            
            if team_eff==True:
                print(f"    it was a team effort")
                
        else:
            print(' rough week for the boys')
          
    except:
        print("error calculating splits")
    
    print()
    tdf['Demand'] = [tdf.iloc[x]['Final Balance']-tdf.iloc[x].Amount for x in tdf.reset_index().index]
    na = len(tdf) - 1
    td2 = tdf.sort_values('Demand')
    
    while td2.Demand.any() >= .1:
        if abs(td2.iloc[0,3]) > abs(td2.iloc[na,3]):
            amt = abs(td2.iloc[na,3])
            prntamt = round(amt,2)
            print(f'{td2.index[0]} pays {td2.index[na]} {prntamt}')
            td2.iloc[0,3] = td2.iloc[0,3] + amt
            td2.iloc[na,3] = td2.iloc[na,3] - amt
            td2 = td2.sort_values('Demand')
        else:
            amt = abs(td2.iloc[0,3])
            prntamt = round(amt,2)
            print(f'{td2.index[0]} pays {td2.index[na]} {prntamt}')
            td2.iloc[0,3] = td2.iloc[0,3] + amt
            td2.iloc[na,3] = td2.iloc[na,3] - amt
            td2 = td2.sort_values('Demand')
        
        if ((td2.Demand< 1.0).all()):
            break

#new site, all action, data translation layer
def newsite_datatranslation(new_site_data):
    p_a = pd.read_csv('/Users/trevorross/Desktop/My Projects/bettingatwork/players_and_agents.csv')
    p_dict = p_a[['Player','Name']]
    
    nsd2 = new_site_data[['Customer','Week']]
    nsd2['Player'] = [pyr.lower() for pyr in nsd2.Customer]
    nsd2.rename(columns={"Week":"Weekly"},inplace=True)
    nsd2.drop('Customer',axis=1,inplace=True)
    # nsd2["Balance"] = nsd2.Balance.astype(float)
    ready_data = pd.merge(left=nsd2,right=p_dict,how="left",on="Player")
    # print(ready_data.head())
    return ready_data

#Process Runner
def weekly_processing(weekly_data,pyragt):
    wd1_1 = newsite_datatranslation(weekly_data)
    w2 = wd1_1[['Player','Name','Weekly']]
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
    print()

#Code Starter
if __name__ == "__main__":
    weekly_processing(this_week,pyragt)

#walk thru's
# weekly_data = this_week
# this_week.head()
# pyragt.head()
