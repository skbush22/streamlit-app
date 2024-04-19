import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import requests
import warnings
pd.options.mode.chained_assignment = None
import json
from bs4 import BeautifulSoup as soup
import re
from matplotlib.colors import to_rgba
from mplsoccer import Pitch, FontManager, Sbopen, VerticalPitch, PyPizza
import matplotlib.image as image1
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
from matplotlib.colors import LinearSegmentedColormap
from unidecode import unidecode
import time

from itscalledsoccer.client import AmericanSoccerAnalysis

from plottable import Table
from plottable import ColumnDefinition, Table
from plottable.cmap import normed_cmap
from plottable.plots import *

import streamlit as st

headers = {
    'authority': st.secrets.headers.authority,
    'accept': st.secrets.headers.accept,
    'accept-language': st.secrets.headers['accept-language'],
    'cache-control': st.secrets.headers['cache-control'],
    'if-none-match': st.secrets.headers['if-none-match'],
    'origin': st.secrets.headers['origin'],
    'referer': st.secrets.headers.referer,
    'sec-ch-ua-mobile': st.secrets.headers['sec-ch-ua-mobile'],
    'sec-ch-ua-platform': st.secrets.headers['sec-ch-ua-platform'],
    'sec-fetch-dest': st.secrets.headers['sec-fetch-dest'],
    'sec-fetch-mode': st.secrets.headers['sec-fetch-mode'],
    'sec-fetch-site': st.secrets.headers['sec-fetch-site'],
    'user-agent': st.secrets.headers['user_agent'],
}

def test():
    #headers['referer'] = st.secrets.mls.referer
    #headers['origin'] = st.secrets.mls.origin

    time.sleep(10)

    sched_next = requests.get(st.secrets.mls.next_url, 
                              headers={'referer': st.secrets.mls.referer, 'origin':st.secrets.mls.origin,
                              'user-agent': 'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US);'})
    
    #sched_played = requests.get(
    #st.secrets.mls.played_url, 
    #headers=headers)
    
    sched = sched_next.text

    return sched

def executeTest():
    sched_2 = test()
    return sched_2

ref_events = pd.read_excel('Opta_dict.xlsx', sheet_name='Event_Type')

ref_quals = pd.read_excel('Opta_dict.xlsx', sheet_name='Qualifier_Type')

ref_body = pd.read_excel('Opta_dict.xlsx', sheet_name='Body_Part')

def get_asa_data(league):
    asa = AmericanSoccerAnalysis()

    xgoals = asa.get_player_xgoals(leagues=league.lower(), season=2024)

    gadded_all = asa.get_player_goals_added(leagues=league.lower(), season=2024)


    gadded_all['dribbling'] = np.nan
    gadded_all['fouling'] = np.nan
    gadded_all['interrupting'] = np.nan
    gadded_all['passing'] = np.nan
    gadded_all['receiving'] = np.nan
    gadded_all['shooting'] = np.nan

    for i in range(len(gadded_all)):
        gadded_all['dribbling'][i] = gadded_all.data[i][0]['goals_added_above_avg']
        gadded_all['fouling'][i] = gadded_all.data[i][1]['goals_added_above_avg']
        gadded_all['interrupting'][i] = gadded_all.data[i][2]['goals_added_above_avg']
        gadded_all['passing'][i] = gadded_all.data[i][3]['goals_added_above_avg']
        gadded_all['receiving'][i] = gadded_all.data[i][4]['goals_added_above_avg']
        gadded_all['shooting'][i] = gadded_all.data[i][5]['goals_added_above_avg']

    gadded_all['total'] = sum([gadded_all.dribbling, gadded_all.fouling, gadded_all.interrupting, gadded_all.passing, gadded_all.receiving, gadded_all.shooting])



    players = pd.read_csv(f'ASA_Players_{league}.csv')

    players = pd.DataFrame([players.player_id, players.player_name]).transpose()

    for i in range(len(players)):
        try:
            players.player_name[i] = unidecode(players.player_name[i])
        except:
            players.player_name[i] = players.player_name[i]

    gadded_all = gadded_all.merge(players, how='inner', on='player_id')

    gadded = pd.DataFrame([gadded_all.player_id, gadded_all.total]).transpose()

    players_xgoals = xgoals.merge(players, how='inner', on='player_id')

    players_xgoals = players_xgoals.merge(gadded, how='inner', on='player_id')

    return players_xgoals


def get_sched_MLS(headers):
    headers['referer'] = st.secrets.mls.referer
    headers['origin'] = st.secrets.mls.origin
    
    sched_next = requests.get(f'{st.secrets.mls.next_url}', 
                              headers=headers)
    
    sched_played = requests.get(
    f'{st.secrets.mls.played_url}', 
    headers=headers)
    
    sched = sched_next.text
    sched = sched[43:-1]
    sched_json = json.loads(sched[sched.index('{'):])
    matches = sched_json['match']
    
    played_p = sched_played.text
    played_p = played_p[43:-1]
    played_p_json = json.loads(played_p[played_p.index('{'):])
    played_matches = played_p_json['match']
    
    matches = matches + played_matches
    
    sched = []
    for i in matches:
        date = i['matchInfo']['date'][:-1]
        time = i['matchInfo']['time'][:-1]
        status = i['liveData']['matchDetails']['matchStatus']
    
        home = [j['officialName'] for j in i['matchInfo']['contestant'] if j['position']=='home'][0]
        home_abv = [j['code'] for j in i['matchInfo']['contestant'] if j['position']=='home'][0]
    
        away = [j['officialName'] for j in i['matchInfo']['contestant'] if j['position']=='away'][0]
        away_abv = [j['code'] for j in i['matchInfo']['contestant'] if j['position']=='away'][0]
    
        id_ = i['matchInfo']['id']
        
        if status=='Played' or status=='Final':
            score_box = i['liveData']['matchDetails']['scores']['total']
            score = f"{score_box['home']} : {score_box['away']}"
        else:
            score = '0 : 0'
    
        game_dict = {
            'date': date,
            'time': time,
            'status': status,
            'home': home,
            'home_abv': home_abv,
            'away': away,
            'away_abv': away_abv,
            'id': id_,
            'score': score
        }
    
        sched.append(game_dict)
    
    sched_f = []
    sched_f_ids = []
    for i in sched:
        if i['id'] in sched_f_ids:
            pass
        else:
            sched_f.append(i)
            sched_f_ids.append(i['id'])
    
    played = []
    for i in sched_f:
        if i['status'] == 'Played' or i['status'] == 'Final':
            played.append(i)
    
    return (played)

def get_sched_NWSL(headers):
    headers['referer'] = st.secrets.nwsl.referer
    headers['origin'] = st.secrets.nwsl.origin

    full_sched = requests.get(st.secrets.nwsl.sched_url, 
                              headers=headers)
    sched_json = json.loads(full_sched.text)
    matches = []
    for i in sched_json['data']['matches']:
        for j in range(len(i['events'])):
            matches.append(i['events'][j])
    sched = []
    for i in matches:
        date = i['date'][:-9]
        time = i['time']
        location = i['location']['City']
        stadium = i['location']['Stadium']
        attendance = i['attendance']
        status = i['status']
    
        home = i['team']['title']
        home_abv = i['team']['abbreviation']
    
        away = i['opponent']['title']
        if away == 'NJ/NY Gotham FC':
            away = 'NJ-NY Gotham FC'
        away_abv = i['opponent']['abbreviation']
    
        id_ = i['id']
        slug = i['slug']
    
        score = f"{i['results']['team_score']} : {i['results']['opponent_score']}"
    
        game_dict = {
            'date': date,
            'time': time,
            'location': location,
            'stadium': stadium,
            'attendance': attendance,
            'status': status,
            'home': home,
            'home_abv': home_abv,
            'away': away,
            'away_abv': away_abv,
            'id': id_,
            'slug': slug,
            'score': score
        }
    
        sched.append(game_dict)
    
    played = []
    for i in sched:
        if i['status'] == 'Played' or i['status'] == 'Final':
            played.append(i)
    
    return (played)

def get_game_info(match_id, headers):

    headers['referer'] = st.secrets.referer_general
    headers['origin'] = st.secrets.origin_general
    
    response = requests.get(
    f'{st.secrets.url_general}{match_id}?_rt=c&_lcl=en&_fmt=jsonp&_clbk=W30000000000000000000000000000000000000000', 
    headers=headers)
    
    events = response.text
    events = events[43:-1]
    match_data = json.loads(events[events.index('{'):])
    
    events_df = pd.DataFrame(match_data['liveData']['event'])
    
    for i in range(len(events_df)):
        if events_df['periodId'][i]!= 1 and events_df['periodId'][i]!= 2:
            events_df = events_df.drop(i)
        
    events_df.reset_index(drop=True, inplace=True)
    
    match_info = {
        'homeId': [i for i in match_data['matchInfo']['contestant'] if i['position']=='home'][0]['id'],
        'awayId': [i for i in match_data['matchInfo']['contestant'] if i['position']=='away'][0]['id']
    }
    
    type_ = []
    outcome_ = []
    for i in range(len(events_df)):
    
        # Type Clean
        try:
            type_.append(ref_events[ref_events.ID==events_df.typeId[i]]['Name'].reset_index(drop=True)[0])
        except:
            type_.append('Unknown')
        
        # Outcome clean
        try:
            if events_df.outcome[i]==0:
                outcome_.append('Unsuccessful')
            else:
                outcome_.append('Successful')
        except:
            outcome_.append('')
    
        # Qualifier clean
        for z in range(len(events_df.qualifier[i])):
            try:
                events_df['qualifier'][i][z]['Name'] = ref_quals[ref_quals.ID==events_df.qualifier[i][z]['qualifierId']]['Name'].reset_index(drop=True)[0]
            except:
                events_df['qualifier'][i][z]['Name'] = 'not sure!'

    events_df['type'] = type_
    events_df['outcome'] = outcome_
    
    # Add qualifier columns

    events_df['endY'] = np.nan
    events_df['endX'] = np.nan
    events_df['Angle'] = np.nan
    events_df['Zone'] = np.nan
    events_df['Length'] = np.nan
    events_df['longBall'] = np.nan

    events_df['Cross'] = np.nan
    events_df['throughBall'] = np.nan
    events_df['freeKick'] = np.nan
    events_df['Corner'] = np.nan
    events_df['Penalty'] = np.nan
    events_df['Foul'] = np.nan
    events_df['fastBreak'] = np.nan

    events_df['ownGoal'] = np.nan
    events_df['Yellow'] = np.nan
    events_df['Red'] = np.nan
    events_df['jerseyNum'] = np.nan
    events_df['throwIn'] = np.nan
    events_df['goalKick'] = np.nan

    events_df['Saved'] = np.nan
    events_df['Missed'] = np.nan
    events_df['bigChance'] = np.nan
    events_df['blockedX'] = np.nan
    events_df['blockedY'] = np.nan
    events_df['isHeader'] = np.nan

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        for i in events_df.index:
            for j in events_df['qualifier'][i]:
                if j['Name'] == 'Pass End Y':
                    events_df.loc[i, 'endY'] = float(j['value'])
                elif j['Name'] == 'Pass End X':
                    events_df.loc[i, 'endX'] = float(j['value'])
                elif j['Name'] == 'Angle':
                    events_df.loc[i, 'Angle'] = float(j['value'])
                elif j['Name'] == 'Zone':
                    events_df.loc[i, 'Zone'] = j['value']
                elif j['Name'] == 'Length':
                    events_df.loc[i, 'Length'] = float(j['value'])
                elif j['Name'] == 'Long ball':
                    events_df.loc[i, 'longBall'] = True
                elif j['Name'] == 'Cross':
                    events_df.loc[i, 'Cross'] = True
                elif j['Name'] == 'Through ball':
                    events_df.loc[i, 'throughBall'] = True
                elif j['Name'] == 'Free kick taken':
                    events_df.loc[i, 'freeKick'] = True
                elif j['Name'] == 'Corner taken':
                    events_df.loc[i, 'Corner'] = True
                elif j['Name'] == 'Penalty':
                    events_df.loc[i, 'Penalty'] = True
                elif j['Name'] == 'Foul':
                    events_df.loc[i, 'Foul'] = True
                elif j['Name'] == 'Fast break':
                    events_df.loc[i, 'fastBreak'] = True
                elif j['Name'] == 'Own goal':
                    events_df.loc[i, 'ownGoal'] = True
                elif j['Name'] == 'Yellow Card':
                    events_df.loc[i, 'Yellow'] = True
                elif j['Name'] == 'Red card':
                    events_df.loc[i, 'Red'] = True
                elif j['Name'] == 'Jersey number':
                    events_df.loc[i, 'jerseyNum'] = j['value']
                elif j['Name'] == 'Throw-in':
                    events_df.loc[i, 'throwIn'] = True
                elif j['Name'] == 'Goal Kick':
                    events_df.loc[i, 'goalKick'] = True
                elif j['Name'] == 'Blocked':
                    events_df.loc[i, 'Blocked'] = True
                elif j['Name'] == 'Missed':
                    events_df.loc[i, 'Missed'] = True
                elif j['Name'] == 'Big Chance':
                    events_df.loc[i, 'bigChance'] = True
                elif j['Name'] == 'Blocked x co-ordinate':
                    events_df.loc[i, 'blockedX'] = float(j['value'])
                elif j['Name'] == 'Blocked y co-ordinate':
                    events_df.loc[i, 'blockedY'] = float(j['value'])
                elif j['Name'] == 'Head':
                    events_df.loc[i, 'isHeader'] = True
    
    #Team dict
    
    form = [i for i in match_data['liveData']['event'] if i['periodId']==16]
    try:
        first_sub_h = events_df[(events_df.type=='sub_off') & (events_df.contestantId==match_info['homeId'])]['timeMin'].reset_index(drop=True)[0]
    except:
        first_sub_h = events_df[(events_df.type=='end_of_period') & (events_df.periodId==2)].timeMin.reset_index().timeMin[0]
        
    try:
        first_sub_a = events_df[(events_df.type=='sub_off') & (events_df.contestantId==match_info['awayId'])]['timeMin'].reset_index(drop=True)[0]
    except:
        first_sub_a = events_df[(events_df.type=='end_of_period') & (events_df.periodId==2)].timeMin.reset_index().timeMin[0]
    
    home = [i for i in form if i['contestantId']==match_info['homeId']][0]
    away = [i for i in form if i['contestantId']==match_info['awayId']][0]
    
    home_names = list([i for i in home['qualifier'] if i['qualifierId']==30][0]['value'].split(', '))
    away_names = list([i for i in away['qualifier'] if i['qualifierId']==30][0]['value'].split(', '))

    home_nums = list([i for i in home['qualifier'] if i['qualifierId']==59][0]['value'].split(', '))
    away_nums = list([i for i in away['qualifier'] if i['qualifierId']==59][0]['value'].split(', '))

    home_dict = {}
    away_dict = {}
    for i in range(len(home_names)):
        home_dict[home_names[i]] = home_nums[i]
    for i in range(len(away_names)):
        away_dict[away_names[i]] = away_nums[i]
        
    formation_dict = {
        'home_dict': home_dict,
        'away_dict': away_dict,
        'first_sub_h': first_sub_h,
        'first_sub_a': first_sub_a
    }
    
    h_a = []
    for i in range(len(events_df)):
        # team Clean
        if events_df.playerId[i] in formation_dict['home_dict'].keys():
            h_a.append('h')
        elif events_df.playerId[i] in formation_dict['away_dict'].keys():
            h_a.append('a')
        else:
            h_a.append('')
    events_df['h_a'] = h_a                
                    
    return events_df, formation_dict


def pick_a_player(player, team, league):
    if league == "MLS":
        games = get_sched_MLS(headers)
    else:
        games = get_sched_NWSL(headers)

    try:
        shortened_name = f"{player[0]}. {player.split(' ')[1]}"
    except:
        shortened_name = player
    
    games_p = []
    for i in range(len(games)):
        if games[i]['home']==team or games[i]['away']==team:
            games_p.append(games[i])
            
    player_stats = pd.DataFrame()
    for i in range(len(games_p)):
        events, dict_ = get_game_info(games_p[i]['id'], headers)
        for i in events.index:
            try:
                events.playerName[i] = unidecode(events.playerName[i])
            except:
                events.playerName[i] = events.playerName[i]
        p_events = events[events.playerName==shortened_name]
        player_stats = pd.concat([player_stats, p_events])
        
    return player_stats

def pick_a_player_ASA(player, team, league):
    players_xgoals_p = get_asa_data(league)

    asa_p_xG = players_xgoals_p[players_xgoals_p.player_name==player]
    if len(asa_p_xG) > 0:
        return asa_p_xG
    else:
        return print('Maybe try different spelling?')


def xT_cut(data):
    xT = pd.read_csv('xT_TheAthletic.csv', header=None)
    xT = np.array(xT)
    xT_rows, xT_cols = xT.shape

    data['x_start_bin'] = pd.cut(data['x'], bins=xT_cols, labels=False)
    data['y_start_bin'] = pd.cut(data['y'], bins=xT_rows, labels=False)
    data['x_end_bin'] = pd.cut(data['endX'], bins=xT_cols, labels=False)
    data['y_end_bin'] = pd.cut(data['endY'], bins=xT_rows, labels=False)
    
    data['start_zone_value'] = data[['x_start_bin', 'y_start_bin']].apply(lambda x: xT[x[1]][x[0]], axis=1)
    data['end_zone_value'] = data[['x_end_bin', 'y_end_bin']].apply(lambda x: xT[x[1]][x[0]], axis=1)
    
    data['xT'] = data['end_zone_value'] - data['start_zone_value']

    return(data)


def heatmap(ax, player_stats, cm, bg_color, l_color, kde_color):
    pitch = VerticalPitch(pitch_type='opta', line_color=l_color, line_zorder=2, pitch_color=bg_color, pad_top=10)
    pitch.draw(ax = ax)
    
    kde = pitch.kdeplot(player_stats.x, player_stats.y, ax=ax,
                    fill=True, levels=100,
                    thresh=0,
                    cut=4,  # extended the cut so it reaches the bottom edge
                    cmap=cm)
    
    ax.annotate(xy = (50, 103.5),
                text = "Heatmap",
                size = 12,
                color = l_color,
                font = 'heiti tc', ha='center',
                weight = 'bold')

    return ax

def defensive_heatmap(ax, player_stats, cm, bg_color, l_color, kde_color):
    pitch = VerticalPitch(pitch_type='opta', line_color=l_color, line_zorder=2, pitch_color=bg_color, pad_top=10)
    pitch.draw(ax = ax)
    
    kde = pitch.kdeplot(player_stats.x, player_stats.y, ax=ax,
                    fill=True, levels=100,
                    thresh=0,
                    cut=4,  # extended the cut so it reaches the bottom edge
                    cmap=cm)
    
    ax.annotate(xy = (50, 103.5),
                text = "Heatmap",
                size = 12,
                color = l_color,
                font = 'heiti tc', ha='center',
                weight = 'bold')
    
    ints = player_stats[player_stats.type=='interception']
    chal = player_stats[player_stats.type=='challenge']
    clear = player_stats[player_stats.type=='clearance']
    rec = player_stats[player_stats.type=='ball_recovery']
    bpas = player_stats[player_stats.type=='blocked_pass']
    tack = player_stats[player_stats.type=='tackle']
    def_actions = pd.concat([ints, chal, clear, rec, bpas, tack])
    
    pitch.scatter(ints.x, ints.y, s=20, marker='o', ax=ax, edgecolor=kde_color, zorder=2, color='none', lw=1.25, label='Interception')
    pitch.scatter(chal.x, chal.y, s=20, marker='X', ax=ax, edgecolor=kde_color, zorder=2, color='none', lw=1.25, label='Challenge')
    pitch.scatter(clear.x, clear.y, s=20, marker='^', ax=ax, edgecolor=kde_color, zorder=2, color='none', lw=1.25, label='Clearance')
    pitch.scatter(rec.x, rec.y, s=20, marker='s', ax=ax, edgecolor=kde_color, zorder=2, color='none', lw=1.25, label='Recovery')
    pitch.scatter(bpas.x, bpas.y, s=20, marker='D', ax=ax, edgecolor=kde_color, zorder=2, color='none', lw=1.25, label='Blocked Pass')
    pitch.scatter(tack.x, tack.y, s=20, marker='P', ax=ax, edgecolor=kde_color, zorder=2, color='none', lw=1.25, label='Tackle') 
    
    pitch.lines(def_actions.x.mean(), 0, def_actions.x.mean(), 100, ax = ax, color=kde_color, zorder=2, linestyle='--', linewidth=2, alpha=0.7)
    
    #legend = ax.legend(loc='lower left', labelspacing=1, fontsize=10, 
                       #bbox_to_anchor=(0.065, 0.025), edgecolor=l_color, facecolor='none', labelcolor=l_color)
    return ax

def pitch_plot(ax, bg_color, l_color, kde_color):
    pitch = VerticalPitch(pitch_type='opta', line_color=l_color, line_zorder=1, pitch_color=bg_color, pad_top=10)
    pitch.draw(ax = ax)
    
    hull = pitch.convexhull([30, 30, 70, 70], [0.32, 99.68, 0.32, 99.68])
    poly = pitch.polygon(hull, ax=ax, edgecolor='none', facecolor=bg_color)
    
    ax.annotate(xy = (50, 106),
                text = "Pass Sonar",
                size = 12,
                color = l_color,
                font = 'heiti tc', ha='center',
                weight = 'bold')
    ax.annotate(xy = (50, 103),
                text = "(Segment size determined by pass quantity)",
                size = 11,
                color = l_color,
                font = 'heiti tc', ha='center',
                weight = 'bold')
    return ax

def shotmap(ax, missed, saved, goal, bg_color, l_color, kde_color):
    pitch = VerticalPitch(pitch_type='opta', line_color=l_color, line_zorder=1, pitch_color=bg_color, 
                          pad_bottom=-15, half=True, pad_top=5)
    pitch.draw(ax = ax)

    sc = pitch.scatter(missed.x, missed.y, color='none', ax=ax, hatch='/////////', 
                       edgecolor=kde_color, label='Miss')
    sc_saved = pitch.scatter(saved.x, saved.y, color='none', ax=ax, 
                             edgecolor=kde_color, s=75, label='SOT')
    sc_goal = pitch.scatter(goal.x, goal.y, color=kde_color, ax=ax, 
                            s=100, label='Goal')

    legend = ax.legend(loc='lower left', labelspacing=1, fontsize=10, 
                       bbox_to_anchor=(0.065, 0.025), edgecolor=l_color, facecolor='none', labelcolor=l_color)
    
    ax.set_facecolor('none')
    ax.axis('off')
    
    ax.annotate(xy = (50, 103),
                text = "Shotmap",
                size = 12,
                color = l_color,
                font = 'heiti tc', ha='center',
                weight = 'bold')
    
    return(ax)

def xt_plot(ax, player_passes, cm, bg_color, l_color, kde_color):
    pitch = VerticalPitch(pitch_type='opta', line_color=l_color, line_zorder=2, pitch_color=bg_color, 
                          pad_bottom=0, half=False)
    pitch.draw(ax = ax)
    
    x_subset = player_passes
    
    bin_statistic = pitch.bin_statistic(x_subset.x, x_subset.y, statistic='sum', values=x_subset.xT, bins=(20, 10))
    pcm = pitch.heatmap(bin_statistic, ax=ax, cmap=cm, edgecolors='none')
    
    ax.annotate(xy = (50, 103),
                text = "xT created by zone",
                size = 12,
                color = l_color,
                font = 'heiti tc', ha='center',
                weight = 'bold')

def table_plot(ax, asa_p_xG, shots, SOT, goal, bg_color, l_color, kde_color):
    plotting = pd.DataFrame(columns=['Stat', 'Per 96', 'Total'])
    _96s = round(asa_p_xG.minutes_played[0]/96, 1)
    xG_P = asa_p_xG.xgoals[0]
    xA_P = asa_p_xG.xassists[0]
    g_plus = asa_p_xG.total[0]
    plotting.loc[len(plotting)] = ('Shots', round(len(shots)/_96s, 2), len(shots))
    plotting.loc[len(plotting)] = ('SOT', round(len(SOT)/_96s, 2), len(SOT))
    plotting.loc[len(plotting)] = ('Goals', round(len(goal)/_96s, 2), len(goal))
    plotting.loc[len(plotting)] = ('xG', round(xG_P/_96s, 2), round(xG_P, 2))
    plotting.loc[len(plotting)] = ('xA', round(xA_P/_96s, 2), round(xA_P, 2))
    plotting.loc[len(plotting)] = ('g+', round(g_plus/_96s, 2), round(g_plus, 2))

    plotting = plotting.set_index('Stat')

    col_defs = (
        [
            ColumnDefinition(
                name="Stat",
                textprops={"ha": "left", "weight": "bold"},
                width=1.5,
            ),
            ColumnDefinition(
                name="Per 90",
                textprops={"ha": "left"},
                width=0.75,
            ),
            ColumnDefinition(
                name="Total",
                textprops={"ha": "left"},
                width=0.75,
            )
        ]
    )

    table = Table(
        plotting,
        column_definitions=col_defs,
        row_dividers=True,
        footer_divider=False,
        ax=ax,
        textprops={"fontsize": 14, 'color':l_color},
        row_divider_kw={"linewidth": 1, "linestyle": (0, (1, 5)), 'color':l_color},
        col_label_divider_kw={"linewidth": 1, "linestyle": "-", 'color':l_color},
        column_border_kw={"linewidth": 1, "linestyle": "-", 'color':l_color},
        even_row_color='none',
        odd_row_color='none'
    )
    table.col_label_row.set_facecolor("none")
    
    ax.set_facecolor('none')
    ax.axis('off')
    
    ax.margins(x=0.3, y=0.3)

    return ax

def get_pass_angle(row):
    angle_in_radians = np.arctan2((row.endX - row.x), (row.y - row.endY))
    angle = np.degrees(angle_in_radians)
    
    if angle < 0:
        angle = 360+angle
    
    return angle

def pass_sonars(ax, player_passes, bg_color, l_color, kde_color):

    player_passes['angle'] = player_passes.apply(get_pass_angle, axis=1)

    player_passes.angle.min()

    bin_edges = [0] + [i * 360 / 16 for i in range(1, 17)]

    player_passes['angle_bin'] = pd.cut(player_passes['angle'], bins=bin_edges, labels=range(1, 17))

    binned_sonar = player_passes.groupby(['angle_bin']).id.count().reset_index()

    ax.axis('off')
    
    # Set the coordinates limits
    upperLimit = binned_sonar['id'].max()+2
    lowerLimit = 0

    # Compute max and min in the dataset
    max_ = binned_sonar['id'].max()

    # Let's compute heights: they are a conversion of each item value in those new coordinates
    # In our example, 0 in the dataset will be converted to the lowerLimit (10)
    # The maximum will be converted to the upperLimit (100)
    slope = (max_ - lowerLimit) / max_
    heights = slope * binned_sonar.id + lowerLimit

    width = (2*np.pi)/16
    
    indexes = list(binned_sonar.angle_bin.values)

    # Compute the angle each bar is centered on:
    angles = [element*width for element in indexes]

    # Draw bars
    bars = ax.bar(
        x=angles, 
        height=heights, 
        width=-width, 
        bottom=lowerLimit,
        linewidth=1, 
        edgecolor=bg_color,
        color=kde_color,
        align='edge')
    
    ax.margins(x=0.25, y=0.25)
    
    return ax

def create_player_report(player, team, player_stats, missed, saved, goal, player_passes, cm, asa_p_xG, shots, SOT, league, bg_color, kde_color, l_color):
    plt.rcParams["font.family"] = ["heiti tc"]

    if league == 'NWSL':
        translator = {
         'Bay FC':'Bay FC',
         'North Carolina Courage': 'North Carolina Courage',
         'Kansas City Current': 'Kansas City Current',
         'Orlando Pride': 'Orlando Pride',
         'Washington Spirit': 'Washington Spirit',
         'Houston Dash': 'Houston Dash',
         'Utah Royals': 'Utah Royals',
         'Portland Thorns FC': 'Portland Thorns FC',
         'Racing Louisville FC': 'Racing Louisville FC',
         'Seattle Reign FC': 'Seattle Reign FC',
         'San Diego Wave FC': 'San Diego Wave FC',
         'Chicago Red Stars': 'Chicago Red Stars',
         'Angel City FC': 'Angel City FC',
         'NJ/NY Gotham FC': 'NJ-NY Gotham FC'
        }

        fig = plt.figure(figsize=(20,10), dpi=300, facecolor=bg_color)
        gs = fig.add_gridspec(nrows = 2, ncols = 6)

        fig.tight_layout()

        plt.subplots_adjust(hspace=-0.05)
        plt.subplots_adjust(wspace=-0.0)

        heatmap_ax = fig.add_subplot(gs[:, :2])
        shotmap_ax = fig.add_subplot(gs[1, 2:4])
        text_ax = fig.add_subplot(gs[0, 2:4])
        sonar_ax_2 = fig.add_subplot(gs[:, 4:])
        sonar_ax = fig.add_subplot(gs[:, 4:], polar=True)

        heatmap(heatmap_ax, player_stats, cm, bg_color, l_color, kde_color)
        shotmap(shotmap_ax, missed, saved, goal, bg_color, l_color, kde_color)
        pitch_plot(sonar_ax_2, bg_color, l_color, kde_color)
        pass_sonars(sonar_ax, player_passes, bg_color, l_color, kde_color)
        table_plot(text_ax, asa_p_xG, shots, SOT, goal, bg_color, l_color, kde_color)

        logo = Image.open(f"{league}_Logos/{translator[team]}.png")
        desired_width = 200 
        aspect_ratio = logo.size[1] / logo.size[0]
        desired_height = int(desired_width / aspect_ratio)
        resized_logo = logo.resize([desired_height, desired_width])

        imax = fig.add_axes([0.15, 0.9, 0.1, 0.1])
        imax.set_axis_off()
        imagebox = OffsetImage(resized_logo, zoom = 0.3)
        ab = AnnotationBbox(imagebox, (0.12, 0.525), frameon = False)
        imax.add_artist(ab)


        fig.text(s=f'{player} Player Dashboard', 
             x=0.19, y=0.95, color=l_color, size=30, font='heiti tc', ha='left', weight='medium')
        fig.text(s=f"{team} | 2024 season so far | Data via Opta, ASA | Made using @{league.lower()}stat's app", 
             x=0.19, y=0.92, color=l_color, size=16, font='heiti tc', ha='left', weight='regular', alpha=0.5)

        return(fig)

    else:
        translator = {
             'Atlanta United FC': 'Atlanta United',
             'Austin FC': 'Austin FC',
             'Charlotte FC': 'Charlotte FC',
             'Chicago Fire FC': 'Chicago Fire FC',
             'Club Internacional de Fútbol Miami': 'Inter Miami CF',
             'Club de Foot Montréal': 'CF Montreal',
             'Colorado Rapids': 'Colorado Rapids',
             'Columbus Crew': 'Columbus Crew',
             'DC United': 'DC United',
             'FC Cincinnati': 'FC Cincinnati',
             'FC Dallas': 'FC Dallas',
             'Houston Dynamo FC': 'Houston Dynamo FC',
             'LA Galaxy': 'LA Galaxy',
             'Los Angeles FC': 'Los Angeles FC',
             'Minnesota United FC': 'Minnesota United',
             'Nashville SC': 'Nashville SC',
             'New England Revolution': 'New England Revolution',
             'New York City Football Club': 'New York City FC',
             'New York Red Bulls': 'New York Red Bulls',
             'Orlando City SC': 'Orlando City',
             'Philadelphia Union': 'Philadelphia Union',
             'Portland Timbers': 'Portland Timbers',
             'Real Salt Lake': 'Real Salt Lake',
             'San Jose Earthquakes': 'San Jose Earthquakes',
             'Seattle Sounders FC': 'Seattle Sounders FC',
             'Sporting Kansas City': 'Sporting Kansas City',
             'St. Louis City SC': 'St. Louis City',
             'Toronto FC': 'Toronto FC',
             'Vancouver Whitecaps FC': 'Vancouver Whitecaps'
        }

        fig = plt.figure(figsize=(20,10), dpi=300, facecolor=bg_color)
        gs = fig.add_gridspec(nrows = 2, ncols = 6)

        fig.tight_layout()

        plt.subplots_adjust(hspace=-0.05)
        plt.subplots_adjust(wspace=-0.0)

        heatmap_ax = fig.add_subplot(gs[:, :2])
        shotmap_ax = fig.add_subplot(gs[1, 2:4])
        text_ax = fig.add_subplot(gs[0, 2:4])
        sonar_ax_2 = fig.add_subplot(gs[:, 4:])
        sonar_ax = fig.add_subplot(gs[:, 4:], polar=True)

        heatmap(heatmap_ax, player_stats, cm, bg_color, l_color, kde_color)
        shotmap(shotmap_ax, missed, saved, goal, bg_color, l_color, kde_color)
        pitch_plot(sonar_ax_2, bg_color, l_color, kde_color)
        pass_sonars(sonar_ax, player_passes, bg_color, l_color, kde_color)
        table_plot(text_ax, asa_p_xG, shots, SOT, goal, bg_color, l_color, kde_color)

        logo = Image.open(f"{league}_Logos/{translator[team]}.png")
        desired_width = 200 
        aspect_ratio = logo.size[1] / logo.size[0]
        desired_height = int(desired_width / aspect_ratio)
        resized_logo = logo.resize([desired_height, desired_width])

        imax = fig.add_axes([0.15, 0.9, 0.1, 0.1])
        imax.set_axis_off()
        imagebox = OffsetImage(resized_logo, zoom = 0.3)
        ab = AnnotationBbox(imagebox, (0.12, 0.525), frameon = False)
        imax.add_artist(ab)


        fig.text(s=f'{player} Player Dashboard', 
             x=0.19, y=0.95, color=l_color, size=30, font='heiti tc', ha='left', weight='medium')
        fig.text(s=f"{team} | 2024 season so far | Data via Opta, ASA | Made using @{league.lower()}stat's app", 
             x=0.19, y=0.92, color=l_color, size=16, font='heiti tc', ha='left', weight='regular', alpha=0.5)

        return(fig)

def run_player_graphic(player, team, league):


    if league == 'MLS':
        bg_color = '#fdf6e3'
        l_color = 'black'
        kde_color = '#287170'

        team_colors = pd.read_csv('MLS_Logos/Team_Colors.csv')

        player = unidecode(player)

        player_stats = pick_a_player(player, team, league)

        asa_p_xG = pick_a_player_ASA(player, team, league)

        player_passes = xT_cut(player_stats[(player_stats.type=='pass') & (player_stats.outcome=='Successful')])

        saved = player_stats[(player_stats.type=='attempt_saved') & (player_stats.Blocked!=True)]
        goal = player_stats[player_stats.type=='goal']
        missed = pd.concat([player_stats[player_stats.type=='post'], player_stats[(player_stats.type=='attempt_saved') & (player_stats.Blocked==True)], player_stats[player_stats.type=='miss']])

        colors = [bg_color, kde_color] # first color is black, last is red
        cm = LinearSegmentedColormap.from_list(
            "Custom", colors, N=50)

        asa_p_xG = asa_p_xG.reset_index(drop=True)
        shots = pd.concat([saved, goal, missed])
        SOT = pd.concat([saved, goal])

        fig = create_player_report(player, team, player_stats, missed, saved, goal, player_passes, cm, asa_p_xG, shots, SOT, league, bg_color, kde_color, l_color)

        return fig
    else:
        bg_color = '#0c1f2e'
        l_color = 'white'
        kde_color = '#82daf2'

        team_colors = pd.read_csv('NWSL_Logos/Team_Colors.csv')

        player = unidecode(player)

        player_stats = pick_a_player(player, team, league)

        asa_p_xG = pick_a_player_ASA(player, team, league)

        player_passes = xT_cut(player_stats[(player_stats.type=='pass') & (player_stats.outcome=='Successful')])

        saved = player_stats[(player_stats.type=='attempt_saved') & (player_stats.Blocked!=True)]
        goal = player_stats[player_stats.type=='goal']
        missed = pd.concat([player_stats[player_stats.type=='post'], player_stats[(player_stats.type=='attempt_saved') & (player_stats.Blocked==True)], player_stats[player_stats.type=='miss']])

        colors = [bg_color, kde_color] # first color is black, last is red
        cm = LinearSegmentedColormap.from_list(
            "Custom", colors, N=50)

        asa_p_xG = asa_p_xG.reset_index(drop=True)
        shots = pd.concat([saved, goal, missed])
        SOT = pd.concat([saved, goal])

        fig = create_player_report(player, team, player_stats, missed, saved, goal, player_passes, cm, asa_p_xG, shots, SOT, league, bg_color, kde_color, l_color)

        return fig







    

