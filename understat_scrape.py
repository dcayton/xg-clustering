#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thursday March 3rd 16:29:00 2022

Credit to McKay Johns for the baselines of the scrape_understat function.

@author: Donald Cayton
"""
import numpy as np
import pandas as pd

import requests
from bs4 import BeautifulSoup
import json

def scrape_understat(data_type, team=None, season=None, match_id=None):
    """
    Scrapes understat.com for data. Parses into a readable JSON file.
    
    data_type (str): Input team or match to pull data from a team or match.
    team (str): if data_type is team, this is the name of the team to query.
    season: if data_type is team, this is the starting year of the desired season (ex: 2021 for 2021-2022).
    match_id: if the data_type is match, this is the match_id for the desired match.
    """
    if data_type == "team":
        url = f"https://understat.com/{data_type}/{team}/{str(season)}"
    elif data_type == "match":
        url = f"https://understat.com/{data_type}/{str(match_id)}"
    
    matches_res = requests.get(url)
    soup = BeautifulSoup(matches_res.content, 'lxml')
    scripts = soup.find_all('script')
    strings = scripts[1].string

    ind_start = strings.index("('")+2
    ind_end = strings.index("')")

    json_data = strings[ind_start:ind_end]
    json_data = json_data.encode('utf8').decode('unicode_escape')

    data = json.loads(json_data)
    
    return data

def find_match_ids(results):
    """
    Takes in a JSON file containing results scraped from understat.com and returns a list of match IDs.
    
    results: scraped understat style json.
    """
    match_ids = []
    
    for i in np.arange(len(results)):
        if results[i]['isResult'] == True:
            match_ids += [results[i]['id']]
    
    return match_ids

def season_shots(team, opposition_ids):
    """
    Creates a dataframe for a team in a particular season based on a list of their match IDs in a particular season.
    
    team: the name of the team, for which you desire the season shots.
    opposition_ids: a list of match ids gleaned from the find_match_ids() function.
    """
    shots_json = []
    
    for opp_id in opposition_ids:
        shot_data = scrape_understat('match', match_id=opp_id)
        if shot_data['h'][0]['h_team'] == team:
            shots_json += shot_data['h']
        else:
            shots_json += shot_data['a']
    
    shot_data = []  
    for shot in shots_json:
        player_id = shot['player_id']
        player = shot['player']
        minute = shot['minute']
        x = np.round(float(shot['X']), 2)
        y = np.round(float(shot['Y']), 2)
        xG = np.round(float(shot['xG']), 2)
        if shot['h_a'] == 'a':
            opponent = shot['h_team']
        else:
            opponent = shot['a_team']
        situation = shot['situation']
        shot_type = shot['shotType']
        result = shot['result']
        shot_data.append([player_id, player, minute, x, y, xG, opponent, situation, shot_type, result])
    
    shots = pd.DataFrame(data=shot_data, columns=['PlayerId', 'PlayerName', 'Minute', 'X', 'Y', 'xG', 'Opposition', 'PhaseOfPlay', 'ShotType', 'Outcome'])
    return shots