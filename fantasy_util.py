import requests
from bs4 import BeautifulSoup
import os

live_url = 'https://www.livefpl.net/leagues/88270'

root_dir = ''
#root_dir = '/home/tungdt/mysite/'

# return teams who played TML
def read_team_week():
    with open(f'{root_dir}team_week.txt', 'r') as f:
        lines = f.readlines()
    team_week_names = [line[:-1] for line in lines]
    return team_week_names

team_week_names = read_team_week()

# return matches result of a round in a league
# can be played round or live round
def match_round(league, round):
    f = open(f'{root_dir}{league}/{round}.csv', 'r', encoding='utf-8-sig')
    lines = f.readlines()
    f.close()
    if len(lines[0].split(',')) == 4:
        return [line.strip().split(',') for line in lines]
    
    return live_round(live_url, league, round)

# get team names for live round
def get_teams_live(league, live_round):
    f = open(f'{root_dir}{league}/{live_round}.csv', 'r', encoding='utf-8-sig')
    lines = f.readlines()
    f.close()
    return [line.strip().split(',') for line in lines]

# get all rounds in a league by reading csv files in the league folder
def get_rounds(league):
    csv_files = []
    for f in os.listdir(f'{root_dir}{league}'):
        if f.endswith('.csv'):
            csv_files.append(int(f.split('.')[0]))
    csv_files.sort(reverse=True)
    return csv_files

# get live scores of teams from livefpl.net url
def live_scores(url, teams):
    data = extract_data(url, teams)
    # Convert data to dictionary where key is row[1] and value is row[3]
    team_scores = {row[1]: row[3] for row in data}
    return team_scores

# get live scores and hits of teams from livefpl.net url
def live_scores_hits(url, teams):
    data = extract_data(url, teams)
    # Convert data to dictionary where key is row[1] and value is row[3]
    team_scores = {row[1]: f'{row[3]},{row[4]}' for row in data}
    return team_scores

# get live round result
def live_round(url, league, round_no):
    # get teams name from round_no then get live scores
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

# extract data from livefpl.net url
# data includes rank, team name, total points, live points, hits
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
                    data.append([int(cells[0].split()[0].split('\n')[0]), # rank
                                cells[4],                                 # team name
                                int(cells[6].strip()),                    # total points
                                int(cells[7].strip()),                    # live points  
                                int(cells[8].split()[0].strip())])        # hits
            except Exception as e:
                # append error message to log.txt
                with open('log.txt', 'a') as f:
                    f.write('Error type: extract team data\n')
                    f.write(f'Source: {cells}\n')
                    f.write(f'Error: {str(e)} \n')
                    f.write('--------------------------------\n')
    return data

# get league table
# return table of rank, team name, wins, draws, losses, differences, league points, total fantasy points
def league_table(league):
    rounds = get_rounds(league)
    table = {}

    for m in match_round(league, 1):
        table[m[0]] = [0, 0, 0, 0, 0, 0] # wins, draws, losses, differences, league points, total fantasy points
        table[m[1]] = [0, 0, 0, 0, 0, 0] # wins, draws, losses, differences, league points, total fantasy points

    for r in rounds:
        for m in match_round(league, r):
            team1, team2 = m[0], m[1]
            score1, score2 = int(m[2]), int(m[3])
            if score1 - 2  > score2:
                table[team1][0] += 1                    # update wins
                table[team1][4] += 3                    # update league points
                table[team2][2] += 1                    # update losses
                table[team1][3] += (score1 - score2)    # update differences
                table[team2][3] -= (score1 - score2)    # update differences
            elif score2 - 2 > score1:
                table[team2][0] += 1                    # update wins
                table[team2][4] += 3                    # update league points
                table[team1][2] += 1                    # update losses
                table[team2][3] += (score2 - score1)    # update differences
                table[team1][3] -= (score2 - score1)    # update differences
            else:
                table[team1][1] += 1                    # update draws
                table[team1][4] += 1                    # update league points
                table[team2][1] += 1                    # update draws
                table[team2][4] += 1                    # update league points
    
    data = extract_data(live_url, table.keys())
    # add total fantasy points to table
    for d in data:
        table[d[1]][5] = d[2]
    # sort table by league points and differences
    table = {k: v for k, v in sorted(table.items(), key=lambda item: (item[1][4], item[1][3]), reverse=True)}
    # convert table to list of lines, and rank to the 1st column
    table = [[i + 1] + [k] + v for i, (k, v) in enumerate(table.items())]
    # insert header to the first row
    table.insert(0, ['Rank', 'Team', 'Wins', 'Draws', 'Losses', 'Diff', 'Points', 'Fantasy'])

    return table
