#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import re

def fixSeason(seasonText):
    r = re.search('\d{6}', str(seasonText)) 
    if r: return r.group(0)[:4] + "-" + r.group(0)[4:6] + " Regular Season"
    else: return seasonText


'''~~~~~~~~~~~~~ QMJHL ~~~~~~~~~~~~~~~'''

# Read CSV, filter out playoffs and all-star games, drop unnecesary columns
qmjhl_data = pd.read_csv("QMJHL_2007-2008_to_2017-2018_per_team.csv")
qmjhl_data = qmjhl_data[qmjhl_data.Season.str.contains('Playoffs') == False]
qmjhl_data = qmjhl_data[qmjhl_data.Season.str.contains('All-Star') == False]
qmjhl_data = qmjhl_data.drop(['Total Team Points', 'Total Points', 'Assists Per Team Assists %', 'Goals Per Team Goals %'], axis=1)
qmjhl_data['Season'] = qmjhl_data['Season'].apply( lambda x: str(x)[0:8] + ' Regular Season')

# Drop players who have played less than 10 games
qmjhl_data = qmjhl_data[qmjhl_data['Games Played'] > 10]

# Set the index to player name, sort by new index
qmjhl_data = qmjhl_data.set_index(['Player Name'])
qmjhl_data = qmjhl_data.sort_index()

# Calculate Vollman modifier and multiply by existing PPTPt%
qmjhl_data['Vollman Modifier'] = qmjhl_data['Player Age'].apply( lambda x: -0.1606*x + 3.7296 )
qmjhl_data['Adjusted Point %'] = qmjhl_data['Points Per Team Points %'] * qmjhl_data['Vollman Modifier']

# Save position and standard deviation of PPTPt% of players
temp = qmjhl_data.groupby(['Player Name']).agg({'Position':['first'],'Adjusted Point %':['std'], 'Season':['count']})

# Collapse player entries into single entries per player
qmjhl_data_collapsed = qmjhl_data.groupby('Player Name').mean()

# Concat the now collapsed player qmjhl_data with positions and standard deviations
qmjhl_data_collapsed = pd.concat([qmjhl_data_collapsed, temp], axis=1)

# Sort by adjusted PPTPt%
qmjhl_data_collapsed = qmjhl_data_collapsed.sort_values(by=['Adjusted Point %'], ascending=False)

qmjhl_data_collapsed.to_csv("QMJHL_2007-2008_to_2017-2018_per_team_adjusted.csv")

# Make new table of just defensemen
qmjhl_eligible = qmjhl_data.loc[qmjhl_data['Draft Eligibility'] == True]
qmjhl_eligible = qmjhl_eligible.loc[qmjhl_eligible['Season'] == ' 2012-13 Regular Season']
qmjhl_eligible_defensemen = qmjhl_eligible.loc[qmjhl_eligible['Position'] == 'D']

'''~~~~~~~~~~~~~ OHL ~~~~~~~~~~~~~~~'''

# Read CSV, filter out playoffs and all-star games, drop unnecesary columns
ohl_data = pd.read_csv("ohl_2007-2008_to_2017-2018_per_team.csv")
ohl_data = ohl_data[ohl_data.Season.str.contains('Playoffs') == False]
ohl_data = ohl_data[ohl_data.Season.str.contains('All-Star') == False]
ohl_data = ohl_data.drop(['Total Team Points', 'Total Points', 'Assists Per Team Assists %', 'Goals Per Team Goals %'], axis=1)

# Drop players who have played less than 10 games
ohl_data = ohl_data[ohl_data['Games Played'] > 10]

# Set the index to player name, sort by new index
ohl_data = ohl_data.set_index(['Player Name'])
ohl_data = ohl_data.sort_index()

# Calculate Vollman modifier and multiply by existing PPTPt%
ohl_data['Vollman Modifier'] = ohl_data['Player Age'].apply( lambda x: -0.1606*x + 3.7296 )
ohl_data['Adjusted Point %'] = ohl_data['Points Per Team Points %'] * ohl_data['Vollman Modifier']

# Save position and standard deviation of PPTPt% of players
temp = ohl_data.groupby(['Player Name']).agg({'Position':['first'],'Adjusted Point %':['std'], 'Season':['count']})

# Collapse player entries into single entries per player
ohl_data_collapsed = ohl_data.groupby('Player Name').mean()

# Concat the now collapsed player ohl_data with positions and standard deviations
ohl_data_collapsed = pd.concat([ohl_data_collapsed, temp], axis=1)

# Sort by adjusted PPTPt%
ohl_data_collapsed = ohl_data_collapsed.sort_values(by=['Adjusted Point %'], ascending=False)

ohl_data_collapsed.to_csv("ohl_2007-2008_to_2017-2018_per_team_adjusted.csv")

# Make new table of just defensemen
ohl_eligible = ohl_data.loc[ohl_data['Draft Eligibility'] == True]
ohl_qmjhl_eligible = ohl_eligible.loc[ohl_eligible['Season'] == ' 2012-13 Regular Season']
ohl_eligible_defensemen = ohl_eligible.loc[ohl_eligible['Position'] == 'D']

'''~~~~~~~~~~~~~ WHL ~~~~~~~~~~~~~~~'''

# Read CSV, filter out playoffs and all-star games, drop unnecesary columns
whl_data = pd.read_csv("whl_2007-2008_to_2017-2018_per_team.csv")
whl_data = whl_data[whl_data.Season.str.contains('Playoffs') == False]
whl_data = whl_data[whl_data.Season.str.contains('All-Star') == False]
whl_data = whl_data.drop(['Total Team Points', 'Total Points', 'Assists Per Team Assists %', 'Goals Per Team Goals %'], axis=1)
whl_data['Season'] = whl_data['Season'].apply( lambda x: fixSeason(x) )

# Drop players who have played less than 10 games
whl_data = whl_data[whl_data['Games Played'] > 10]

# Set the index to player name, sort by new index
whl_data = whl_data.set_index(['Player Name'])
whl_data = whl_data.sort_index()

# Calculate Vollman modifier and multiply by existing PPTPt%
whl_data['Vollman Modifier'] = whl_data['Player Age'].apply( lambda x: -0.1606*x + 3.7296 )
whl_data['Adjusted Point %'] = whl_data['Points Per Team Points %'] * whl_data['Vollman Modifier']

# Save position and standard deviation of PPTPt% of players
temp = whl_data.groupby(['Player Name']).agg({'Position':['first'],'Adjusted Point %':['std'], 'Season':['count']})

# Collapse player entries into single entries per player
whl_data_collapsed = whl_data.groupby('Player Name').mean()

# Concat the now collapsed player whl_data with positions and standard deviations
whl_data_collapsed = pd.concat([whl_data_collapsed, temp], axis=1)

# Sort by adjusted PPTPt%
whl_data_collapsed = whl_data_collapsed.sort_values(by=['Adjusted Point %'], ascending=False)
whl_data.to_csv('whl_data.csv')
whl_data_collapsed.to_csv("whl_2007-2008_to_2017-2018_per_team_adjusted.csv")

# Make new table of just defensemen
whl_eligible = whl_data.loc[whl_data['Draft Eligibility'] == True]
whl_eligible = whl_eligible.loc[whl_eligible['Season'] == ' 2012-13 Regular Season']
whl_eligible_defensemen = whl_eligible.loc[whl_eligible['Position'] == 'D']

'''~~~~~~~~~~~~~ Other Stuff ~~~~~~~~~~~~~~~'''

qmjhl_data['League Adjusted Point %'] = qmjhl_data['Adjusted Point %'].apply( lambda x: 1.18038183*x)
whl_data['League Adjusted Point %'] = whl_data['Adjusted Point %'].apply( lambda x: 0.9718157182*x)
ohl_data['League Adjusted Point %'] = ohl_data['Adjusted Point %']
qmjhl_data['League'] = 'QMJHL'
whl_data['League'] = 'WHL'
ohl_data['League'] = 'OHL'
complete_data = qmjhl_data.append(whl_data).append(ohl_data)
complete_data_ell = complete_data.loc[complete_data['Draft Eligibility'] == True]

temp = complete_data.groupby(['Player Name']).agg({'Position':['first'],'Adjusted Point %':['std'], 'Season':['count'], 'League':['first']})

# Collapse player entries into single entries per player
complete_data_collapsed = complete_data.groupby('Player Name').mean()

# Concat the now collapsed player whl_data with positions and standard deviations
complete_data.to_csv('complete_data.csv')
complete_data_collapsed = pd.concat([complete_data_collapsed, temp], axis=1)
complete_data_collapsed_ell = complete_data_collapsed.loc[complete_data_collapsed['Draft Eligibility'] == True]
complete_data_collapsed.to_csv('complete_data_collapsed.csv')
complete_data_collapsed_ell.to_csv('complete_data_collapsed_ell.csv')




