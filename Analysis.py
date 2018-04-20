#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd

# Read CSV, filter out playoffs and all-star games, drop unnecesary columns
data = pd.read_csv("OHL_2007-2008_to_2017-2018_per_team.csv")
data = data[data.Season.str.contains('Playoffs') == False]
data = data[data.Season.str.contains('All-Star') == False]
data = data.drop(['Total Team Points', 'Total Points', 'Assists Per Team Assists %', 'Goals Per Team Goals %'], axis=1)

# Drop players who have played less than 10 games
data = data[data['Games Played'] > 10]

# Set the index to player name, sort by new index
data = data.set_index(['Player Name'])
data = data.sort_index()

# Calculate Vollman modifier and multiply by existing PPTPt%
data['Vollman Modifier'] = data['Player Age'].apply( lambda x: -0.1606*x + 3.7296 )
data['Adjusted Point %'] = data['Points Per Team Points %'] * data['Vollman Modifier']

# Save position and standard deviation of PPTPt% of players
temp = data.groupby(['Player Name']).agg({'Position':['first'],'Adjusted Point %':['std'], 'Season':['count']})

# Collapse player entries into single entries per player
data_collapsed = data.groupby('Player Name').mean()

# Concat the now collapsed player data with positions and standard deviations
data_collapsed = pd.concat([data_collapsed, temp], axis=1)

# Sort by adjusted PPTPt%
data_collapsed = data_collapsed.sort_values(by=['Adjusted Point %'], ascending=False)

# data_collapsed.to_csv("OHL_2007-2008_to_2017-2018_per_team_adjusted.csv")
# Make new table of just defensemen
eligible = data.loc[data['Draft Eligibility'] == True]
eligible = eligible.loc[eligible['Season'] == ' 2016-17 Regular Season']
eligible_defensemen = eligible.loc[eligible['Position'] == 'D']
eligible2 = eligible.sort_index()