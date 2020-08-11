import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys
from datetime import datetime

#####################  Input here ####################################

ofInterest = [
    ('me', '215090022'),       # https://www.twitch.tv/klapdota
    ('topson', '94054712'),
    ('miracle', '105248644'),
    ('rtz', '242629424'),
    ('matu', '72312627'),
]

######################################################################

'''
ofInterest = [
    ('topson', '94054712'),
    ('miracle', '105248644'),
    ('rtz', '242629424'),
    ('matu', '72312627'),
    ('GH', '101356886'),
    ('midone', '116585378'),
]
'''

lobby_type_ranked = 7
account_id = ''

queries = {'limit': 10000, 'lobby_type': 7} #lobby type 7 = ranked

def getData(playerID):
    res = requests.get('https://api.opendota.com/api/players/{}/Matches'.format(playerID), params = queries)
    data = res.json()
    games = []
    for matches in data:
        dat = datetime.utcfromtimestamp(int(matches['start_time']))
        if dat.year < 2013: continue
        delta = None
        if matches['radiant_win'] == True and matches['player_slot'] <=127: delta = 1
        elif matches['radiant_win'] == False and matches['player_slot'] >127: delta = 1
        else: delta = -1
        games.append((dat, delta))
    games.sort()
    cur = 0
    for idx in range(len(games)):
        cur += games[idx][1]
        games[idx] = games[idx][0], cur
    return games

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m.%Y'))
#plt.gca().xaxis.set_major_locator(mdates.RRuleLocator(mdates.rrulewrapper(freq=mdates.MONTHLY, interval=8)))

handles = []
for nick, playerID in ofInterest:
    [dates, results] = list(zip(*getData(playerID)))
    handle, = plt.plot(dates, results, label = nick)
    plt.scatter(dates, results, s = plt.rcParams['lines.markersize'] ** 2 / 8)
    handles.append(handle)
plt.legend(handles = handles)
plt.show()
