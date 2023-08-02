from bs4 import BeautifulSoup
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import pandas as pd


def get_name(player_url):
    response = requests.get(player_url, verify=False)
    soup = BeautifulSoup(response.text, 'lxml')

    name = soup.find('h1', attrs={'class': 'cb-font-40'})
    return name.text.lower()


def get_scorecard(match_url):
    base = 'https://www.cricbuzz.com'
    response = requests.get(match_url, verify=False)
    soup = BeautifulSoup(response.text, 'lxml')
    match_id = match_url.split('/')[4]
    op = pd.DataFrame()

    inning1 = soup.find('div', attrs={'id': 'innings_1'})
    board1 = inning1.find('div', attrs={'class': 'cb-col cb-col-100 cb-ltst-wgt-hdr'})
    scores1 = board1.find_all('div', attrs={'class': 'cb-col cb-col-100 cb-scrd-itms'})

    first_count = 0
    for val in scores1[0:-3]:
        info = val.text.split(' ')
        player = ''
        if len(info[3]) > 1 and len(info[4]) > 1 and info[4] != '(c)' and info[4] != '(wk)' and info[4] != '(c':
            player = info[3] + ' ' + info[4]
            player = player.lower()
        else:
            item = val.find('div', attrs={'class': 'cb-col cb-col-25'})
            profile = item.find('a')
            player_url = base + profile['href']
            player = get_name(player_url)
        first_count += 1
        row = pd.DataFrame([{'Match_id': match_id, 'inning': 1, 'batter_full_name': player, 'position': first_count}])
        op = pd.concat([op, row])

    inning2 = soup.find('div', attrs={'id': 'innings_2'})
    board2 = inning2.find('div', attrs={'class': 'cb-col cb-col-100 cb-ltst-wgt-hdr'})
    scores2 = board2.find_all('div', attrs={'class': 'cb-col cb-col-100 cb-scrd-itms'})

    first_count = 0
    for val in scores2[0:-3]:
        info = val.text.split(' ')
        player = ''
        if len(info[3]) > 1 and len(info[4]) > 1 and info[4] != '(c)' and info[4] != 'wk' and info[4] != '(c & wk)':
            player = info[3] + ' ' + info[4]
            player = player.lower()
        else:
            item = val.find('div', attrs={'class': 'cb-col cb-col-25'})
            profile = item.find('a')
            player_url = base + profile['href']
            player = get_name(player_url)
        first_count += 1
        row = pd.DataFrame([{'Match_id': match_id, 'inning': 2, 'batter_full_name': player, 'position': first_count}])
        op = pd.concat([op, row])
    return op


#print(get_scorecard('https://www.cricbuzz.com/cricket-scores/66190/rcb-vs-mi-5th-match-indian-premier-league-2023'))

links_df = pd.read_csv(r'2023_match_id.csv')
counts = 1
df = pd.DataFrame()
for val in links_df['url']:
    if counts != 74 and counts != 45:
        match_url = val
        match_url = match_url.replace('cricket-scores', 'live-cricket-scorecard')
        link_data = val.split('/')
        match_id = link_data[4]
        print('Extracting details of match ' + str(counts))
        op = get_scorecard(match_url)
        df = pd.concat([df, op])
        print('Obtained details of match ' + str(counts))
        counts += 1
    else:
        counts += 1

df.to_csv('2023_batter_pos.csv')