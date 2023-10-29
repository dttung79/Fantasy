from fantasy_util import get_rounds, match_round, live_round, league_table
import requests, bs4
#print(get_rounds('autumn'))
#print(live_round('https://www.livefpl.net/leagues/88270', 10))
#print(match_round('autumn', 9))
#print(requests.__version__)
#print(bs4.__version__)

print(league_table('autumn'))