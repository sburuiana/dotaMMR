import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys
from datetime import datetime

#####################  Default input here ####################################

default_players = [
    ('me', '215090022'),       # https://www.twitch.tv/klapdota
    ('topson', '94054712'),
    ('miracle', '105248644'),
    ('rtz', '242629424'),
    ('matu', '72312627'),
]

##############################################################################

start_date = '2013.01.01'
end_date = '9999.99.99' #elegant hack

start_key = 'start'
end_key = 'end'
usemmr_key = 'usemmr'

def readme():
    print('How to use:')
    print('> py mmr2.py [args]')
    print('    where [args] is a list of either:')
    print('      1. "[name]:[id]"        -- where [name] is a nickname, and [id] is the player ID (e.g. "klap:215090022")')
    print('      2. "default"            -- adds a bunch of defualt players')
    print('      3. "help"               -- displays this menu')
    print('      4. "{}:[YYYY.MM.DD]" -- sets the start of the time interval ({} by default)'.format(start_key, start_date))
    print('      5. "{}:[YYYY.MM.DD]"   -- sets the end of the time interval (present day by default)'.format(end_key))
    print('      6. "{}:[mmr]"       -- labels the mmr on the plot instead of the number of wins;'.format(usemmr_key))
    print('                                 [mmr] is the current mmr of the player; currently only supported for single-players graphs')

if 'help' in sys.argv or len(sys.argv) < 2:
    readme()
    exit()

def badArgument():
    print('Bad argument, see help: {}'.format(arg))
    exit()

ofInterest = []
mmrscale = None

for arg in sys.argv[1:]:
    if arg == 'default':
        ofInterest.extend(default_players)
    elif arg == 'help':
        readme()
    else:
        toks = arg.split(':')
        if len(toks) != 2:
            badArgument()
        [k,v] = toks
        if k == start_key:
            start_date = v
        elif k == end_key:
            end_date = v
        elif k == usemmr_key:
            try:
                mmrscale = int(v)
            except:
                badArgument()
        else:
            ofInterest.append((k, v))

lobby_type_ranked = 7

queries = {'limit': 10000, 'lobby_type': 7} #lobby type 7 = ranked

def getData(playerID):
    res = requests.get('https://api.opendota.com/api/players/{}/Matches'.format(playerID), params = queries)
    data = res.json()
    games = []
    for matches in data:
        dat = datetime.utcfromtimestamp(int(matches['start_time']))
        datstring = dat.strftime('%Y.%m.%d')
        if datstring < start_date or datstring > end_date: continue
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
    if mmrscale is not None and len(games) > 0:
        for idx in range(len(games)):
            games[idx] = games[idx][0], mmrscale + 25 * (games[idx][1] - games[-1][1])
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
