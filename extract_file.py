import requests
from bs4 import BeautifulSoup
import os

live_url = 'https://www.livefpl.net/leagues/88270'

def read_team_week():
    with open('team_week.txt', 'r') as f:
        lines = f.readlines()
    team_week_names = [line[:-1] for line in lines]
    return team_week_names

team_week_names = read_team_week()

def match_round(league, round):
    f = open(f'{league}/{round}.csv', 'r', encoding='utf-8-sig')
    lines = f.readlines()
    f.close()
    if len(lines[0].split(',')) == 4:
        return [line.strip().split(',') for line in lines]
    
    return live_round(live_url, league, round)

def get_teams_live(league, round):
    f = open(f'{league}/{round}.csv', 'r', encoding='utf-8-sig')
    lines = f.readlines()
    f.close()
    return [line.strip().split(',') for line in lines]

def get_rounds(league):
    csv_files = []
    for f in os.listdir(league):
        if f.endswith('.csv'):
            csv_files.append(int(f.split('.')[0]))
    csv_files.sort(reverse=True)
    return csv_files

def live_scores(url, teams):
    data = extract_data(url, teams)
    # Convert data to dictionary where key is row[1] and value is row[3]
    team_scores = {row[1]: row[3] for row in data}
    return team_scores

def live_round(url, league, round_no):
    # get teams name from round_no
    team_match = get_teams_live(league, round_no)
    teams = []
    for team1, team2 in team_match:
        teams.append(team1)
        teams.append(team2)
    team_scores = live_scores(url, teams)
    data = []
    for team1, team2 in team_match:
        data.append([team1, team2, team_scores[team1], team_scores[team2]])
    return data

def extract_data(url_link, team_names):
    # Access online link using requests, then save it to reconstructed_soup
    response = requests.get(url_link)
    reconstructed_soup = BeautifulSoup(response.content, 'html.parser')
    
    data = []
    # Search for the row with the specified team name
    for tr in reconstructed_soup.find_all('tr'):
        cells = [td.get_text().strip() for td in tr.find_all('td')]
        for team_name in team_names:
            try:
                if team_name in cells:
                    data.append([int(cells[0].split()[0].split('\n')[0]), 
                                cells[4], 
                                int(cells[6].strip()), 
                                int(cells[7].strip()), 
                                int(cells[8].split()[0].strip())])
            except Exception as e:
                # append error message to log.txt
                with open('log.txt', 'a') as f:
                    f.write('Error type: extract team data\n')
                    f.write(f'Source: {cells}\n')
                    f.write(f'Error: {str(e)} \n')
                    f.write('--------------------------------\n')
    return data
