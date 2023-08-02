from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime


def get_innings(match_id, info):
    scorecard_url = 'https://www.cricbuzz.com/live-cricket-scorecard/' + str(match_id) + '/' + info
    response = requests.get(scorecard_url, verify=False)
    soup = BeautifulSoup(response.text, 'lxml')

    innings = soup.find_all('div', attrs={'class': 'cb-col cb-col-100 cb-scrd-hdr-rw'})
    inning_list = []
    for val in innings:
        if val.find('span') is not None:
            data = val.text.split('Innings')
            inning_list.append(data[0].strip())
    return inning_list


def inning_info(match_url):
    score = match_url.replace('cricket-scores', 'cricket-scorecard')
    response = requests.get(score, verify=False)
    soup = BeautifulSoup(response.text, 'lxml')

    innings = soup.find_all('div', attrs={'class': 'cb-col cb-col-100 cb-scrd-hdr-rw'})
    inning_count = 2
    teams = list()
    for val in innings:
        team = val.text.split('Innings')[0]
        if inning_count >= 1:
            teams.append(team.strip())
            inning_count -= 1

    return teams



def get_match_facts(match_url):
    base = 'https://www.cricbuzz.com'
    response = requests.get(match_url, verify=False)
    soup = BeautifulSoup(response.text, 'lxml')

    date_time = str(soup.find_all('span', attrs={'itemprop': 'endDate'})).split('"')
    game_day = date_time[1]

    win_margin = ''
    mom = ''

    if soup.find('div', attrs={'class': 'cb-col cb-col-100 cb-min-stts cb-text-complete'}) is not None:
        win_margin = soup.find('div', attrs={'class': 'cb-col cb-col-100 cb-min-stts cb-text-complete'}).text

    if soup.find('a', attrs={'class': 'cb-link-undrln'}) is not None:
        mom = soup.find('a', attrs={'class': 'cb-link-undrln'}).text
    match_facts = soup.find_all('a', attrs={'class': 'cb-nav-tab'})

    for fact in match_facts:
        if fact.text == 'Match Facts':
            match_fact_url = base + fact['href']

    response = requests.get(match_fact_url, verify=False)
    soup = BeautifulSoup(response.text, 'lxml')
    keys = list()
    vals = list()

    for val in soup.find_all('div', attrs={'class': 'cb-col cb-col-73 cb-mat-fct-itm'}):
        vals.append(val.text)

    for key in soup.find_all('div', attrs={'class': 'cb-col cb-col-27 cb-mat-fct-itm text-bold'}):
        keys.append(key.text)

    facts = {keys[i]: vals[i] for i in range(len(keys))}
    facts['Date:'] = game_day
    facts['Win_margin'] = win_margin
    facts['MOM'] = mom
    if 'Playing:' in facts.keys():
        del facts['Playing:']

    if 'Bench:' in facts.keys():
        del facts['Bench:']

    if 'Capacity:' in facts.keys():
        del facts['Capacity:']

    if 'Time:' in facts.keys():
        del facts['Time:']

    return facts


def auto_scraper(match_url, match_id, counts):
    match_facts = get_match_facts(match_url)
    info = match_facts['Match:']
    info = info.replace(',', '')
    info = info.replace(' ', '-')
    info = info.lower()

    teams = inning_info(match_url)

    game_date = datetime.strptime(match_facts['Date:'], '%Y-%m-%d').date()
    match_team, match_info, league = match_facts['Match:'].split(',')
    ipl_year = league[-4:]

    game_info = {'id': counts, 'match_date': game_date, 'Stadium': match_facts['Stadium:'],
                 'Location': match_facts['City:'], 'Match_Result': match_facts['Win_margin'], 'Match_Info': match_info,
                 'Match_Team': match_team, '2': teams[0], '1': teams[1]}

    return game_info


links_df = pd.read_csv(r'2023_match_id.csv')
path = 'D:/pp/scrapper_commentary/2k23/'
counts = 1
df = pd.DataFrame()
for val in links_df['url']:
    if counts != 74:
        match_url = val
        link_data = val.split('/')
        match_id = link_data[4]
        op = auto_scraper(match_url, match_id, counts)
        df = df.append(op, ignore_index=True)
        print('Obtained details of match ' + str(counts))
        counts += 1
    else:
        counts += 1

df.to_csv('2023_full_facts.csv')
