import requests
import pandas as pd
from bs4 import BeautifulSoup

# Add the url for the year you want to extract
url = 'https://www.cricbuzz.com/cricket-series/5945/indian-premier-league-2023/matches'
response = requests.get(url, verify=False)
soup = BeautifulSoup(response.text, 'lxml')

base = 'https://www.cricbuzz.com'

matches = soup.find_all('a', attrs={'class': 'text-hvr-underline'})

match_df = pd.DataFrame()
counts = 0

for match in matches:
    match_url = base+match['href']
    match_df = match_df.append({'url': match_url}, ignore_index=True)

print(match_df)
match_df.to_csv('2023_match_id.csv')
