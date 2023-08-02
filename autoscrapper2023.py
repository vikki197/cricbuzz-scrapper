import selenium
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests, time
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


def auto_scraper(match_url, match_id):
    match_facts = get_match_facts(match_url)
    info = match_facts['Match:']
    info = info.replace(',', '')
    info = info.replace(' ', '-')
    info = info.lower()
    inning_list = get_innings(match_id, info)

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(executable_path=r'D:/webdrivers/chrome113/chromedriver.exe')


    driver.get(match_url)
    first = False

    SCROLL_PAUSE_TIME = 7.0

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        if first is False:
            driver.implicitly_wait(15)
            first = True

        # Scroll down to bottom
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        clk_element = driver.find_elements(By.ID, 'full_commentary_btn')
        # print(clk_element, len(clk_element))
        if len(clk_element) > 0:
            driver.execute_script("arguments[0].scrollIntoView();", clk_element[0])
        else:
            pass

        print('waiting after scroll')
        # Wait to load page
        time.sleep(15)
        try:
            # Message: element click intercepted: Element is not clickable at point(346, -847) driver.execute_script("window.scrollTo(0, Y)")
            link = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "full_commentary_btn")))
            link.click()

        except TimeoutException:
            print('scrolling done end it')
            break

        except selenium.common.exceptions.ElementClickInterceptedException:
            time.sleep(5)



        # Calculate new scroll height and compare with last scroll height
        # time.sleep(5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print('end of the line folks')
            break
        last_height = new_height

    over_num = list()
    delivery = list()
    score = list()
    df = pd.DataFrame(columns=['over', 'commentary', 'score'])
    commentary = list(driver.find_elements(By.XPATH,
                                           "//div[@ng-show='isCommentaryRendered']//div[@class='ng-scope']//div[@class='cb-col cb-col-100 ng-scope']//p[@class='cb-com-ln ng-binding ng-scope cb-col cb-col-90']"))
    for val in commentary:
        delivery.append(val.text)

    overs = list(driver.find_elements(By.XPATH,
                                      "//div[@ng-show='isCommentaryRendered']//div[@class='ng-scope']//div[@class='cb-col cb-col-100 ng-scope']//div[@class='cb-col cb-col-8 text-bold ng-scope']//div[@class='cb-mat-mnu-wrp cb-ovr-num ng-binding ng-scope']"))
    for val in overs:
        over_num.append(float(val.text))

    count = 0
    if len(inning_list) > 1:
        team = inning_list[1]
    else:
        team = inning_list[0]
    while count < len(over_num):
        score = ''
        data = delivery[count].split(',')
        players = data[0].split('to')
        runs_scored = data[1].lstrip()

        if 'out' in runs_scored:
            score = 'OUT'
        else:
            if runs_scored == '1 run':
                score = 'ONE'
            elif runs_scored == '2 runs':
                score = 'TWO'
            elif runs_scored == '3 runs':
                score = 'THREE'
            elif runs_scored == 'FOUR':
                score = 'FOUR'
            elif runs_scored == '5 runs':
                score = 'FIVE'
            elif runs_scored == 'SIX':
                score = 'SIX'
            elif runs_scored == 'no run':
                score = 'ZERO'
            else:
                score = 'ZERO'

        df = df.append(
            {'Over_num': over_num[count], 'Commentary': delivery[count], 'score': score, 'batsman': players[1],
             'bowler': players[0], 'Team': team, 'Match_Cricbuzz_URL': match_url}, ignore_index=True)
        if over_num[count] == 0.1:
            team = inning_list[0]
        count += 1

    game_date = datetime.strptime(match_facts['Date:'], '%Y-%m-%d').date()
    match_team, match_info, league = match_facts['Match:'].split(',')
    ipl_year = league[-4:]
    league = league[0:-4]

    df['Match_id'] = match_id
    df['Match_Date'] = game_date
    df['Stadium'] = match_facts['Stadium:']
    df['Location'] = match_facts['City:']
    df['Match_Result'] = match_facts['Win_margin']
    df['IPL_year'] = ipl_year
    df['Match_Info'] = match_info
    df['Match_Team'] = match_team
    driver.quit()
    return df


# to do 54
links_df = pd.read_csv(r'2023_match_id.csv')
path = 'D:/pp/scrapper_commentary/2k23/'
counts = 1
for val in links_df.loc[74:, 'url']:
    match_url = val
    link_data = val.split('/')
    match_id = link_data[4]
    df = auto_scraper(match_url, match_id)
    df = df[['Match_id', 'Team', 'Over_num', 'Commentary', 'batsman', 'score', 'IPL_year', 'Match_Info', 'Match_Team',
             'Match_Result', 'Match_Cricbuzz_URL', 'Stadium', 'Location', 'bowler']]
    df_name = path + str(match_id) + '.csv'
    df.to_csv(df_name)
    print('Obtained details of match ' + match_id)
    counts += 1
