from flask import Flask, render_template, request, jsonify
from fantasy_util import extract_data, team_week_names, live_url, match_round
from fantasy_util import get_rounds, live_round, league_table

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return build_page('tml_tpl.html')

@app.route('/tml')
def tml():
    return build_page('tml_tpl.html')

@app.route('/tmlweek')
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

####### routes for autumn league #######
@app.route('/winter')
def winter():
    return build_page('winter_tpl.html')

@app.route('/winter/week/<int:week_no>')
def winterweek(week_no):
    return jsonify(match_round('winter', week_no))

@app.route('/winter/rounds')
def winterrounds():
    return jsonify(get_rounds('winter'))

@app.route('/winter/live/<int:week_no>')
def winterlive(week_no):
    return jsonify(live_round(live_url, week_no))

@app.route('/winter/table')
def winter_table():
    return build_page('winter_table_tpl.html')

@app.route('/api/winter/table')
def winter_table_api():
    return jsonify(league_table('winter'))


####### routes for winter league #######
@app.route('/autumn')
def autumn():
    return build_page('autumn_tpl.html')

@app.route('/autumn/week/<int:week_no>')
def autumnweek(week_no):
    return jsonify(match_round('autumn', week_no))

@app.route('/autumn/rounds')
def autumnrounds():
    return jsonify(get_rounds('autumn'))

@app.route('/autumn/live/<int:week_no>')
def autumnlive(week_no):
    return jsonify(live_round(live_url, week_no))

@app.route('/autumn/table')
def autumn_table():
    return build_page('autumn_table_tpl.html')

@app.route('/api/autumn/table')
def autumn_table_api():
    return jsonify(league_table('autumn'))


####### general build page function #######
def build_page(filename):
    head = render_template('header_tpl.html')
    content = render_template(filename)
    footer = render_template('footer_tpl.html')
    return head + '\n' + content + '\n' + footer


####### main function #######
if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')