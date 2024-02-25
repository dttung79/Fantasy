from flask import Flask, render_template, request, jsonify
from fantasy_util import extract_data, team_week_names, live_url, match_round
from fantasy_util import get_rounds, live_round, get_league_table

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return build_page('tml_tpl.html')

@app.route('/tml')
def tml():
    return build_page('tml_tpl.html')

@app.route('/api/tmlweek')
def tmlweek():
    # columns = ['Rank', 'Team', 'GW Points', 'Total Points', 'Hits']
    data = extract_data(live_url, team_week_names)
    if len(data) == 0:
        return jsonify([])
    # Convert data to dictionary where key is row[1] and value is row[3]
    data = {row[1]: row[3] for row in data}

    f =  open('week.csv', 'r', encoding='utf-8-sig')
    lines = f.readlines()
    last_column = lines[0].split(',')[-1].strip()
    new_column = 'W' + str(int(last_column[1:]) + 1)
    header = lines[0].strip() + ',' + new_column + '\n'

    week_table = {}
    for i in range(1, len(lines)):
        team_name = lines[i].split(',')[0]
        points = lines[i].strip('\n').split(',')[1:]
        week_table[team_name] = ','.join(points) + ',' + str(data[team_name])
        # add new data to week_table
    f.close()
    # convert week_table to list of lines
    lines = [f'{key},{value}\n' for key, value in week_table.items()]
    # remove \n from each line then split by comma
    lines = [line.strip().split(',') for line in lines]
    # insert header to the first row
    lines.insert(0, header.strip().split(','))
    
    return jsonify(lines)


####### routes for a league #######
# route to build league rounds page
@app.route('/<league_name>')
def league(league_name):
    return build_league_page('league_tpl.html', league_name)

# route to build league table page
@app.route('/<league_name>/table')
def league_table(league_name):
    return build_league_page('league_table_tpl.html', league_name)

# route api to get result of a week round in a league
@app.route('/api/<league_name>/week/<int:week_no>')
def league_week(league_name, week_no):
    return jsonify(match_round(league_name, week_no))

# route api to get all rounds in a league
@app.route('/api/<league_name>/rounds')
def league_rounds(league_name):
    return jsonify(get_rounds(league_name))

# route api to get live round result in a league
@app.route('/api/live/<league_name>/<int:week_no>')
def live(league_name, week_no):
    return jsonify(live_round(live_url, league_name, week_no))

# route api to get league table result
@app.route('/api/<league_name>/table')
def league_table_api(league_name):
    return jsonify(get_league_table(league_name))

####### general build pages function #######
def build_page(filename):    
    head = render_template('header_tpl.html')
    content = render_template(filename)
    footer = render_template('footer_tpl.html')
    return head + '\n' + content + '\n' + footer

def build_league_page(filename, league_name):
    head = render_template('header_tpl.html')
    content = render_template(filename, league_name=league_name)
    footer = render_template('footer_tpl.html')
    return head + '\n' + content + '\n' + footer

####### main function #######
if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')