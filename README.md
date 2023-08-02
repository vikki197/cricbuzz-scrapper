# cricbuzz-scrapper
This project scrapes ball by ball details of every match of IPL 2023 (can be extrapolated to any IPL)

The get_match_id file will need the cricbuzz url of all matches played in the ipl season from this, the individual games are extracted into a csv file.

2023_scorecard.py get the detailed scorecard of every game played in the season. This helps understand the batting order and the innings order.

2023matchfacts.py gets additional match related info like win margin, date, teams batted in which innings etc.

autoscrapper2023 is the core which reads the excel generated from get_match_id. For every game, ithe code will get ball by ball data and write into an excel file with the game id being the name of the excel file.

All such excel files can be stored in desired folder. By Combining all files into a single file by merger.py code, we get ball by ball data of every game played in an IPL season
