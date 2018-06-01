# import libraries
from selenium import webdriver
import json
import csv
from astropy.table import Table
from astropy.io import ascii
from oauth2client.service_account import ServiceAccountCredentials
import gspread

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)

gc = gspread.authorize(credentials)

sht = gc.open("icb summer '18")
stats_wks = sht.get_worksheet(0)
summary_wks = sht.get_worksheet(1)
# stats_wks.update_cell(1, 1, 'Foo')
# summary_wks.update_cell(1, 1, 'Foo')

driver = webdriver.Chrome()

icb_pages = ['https://stats.sharksice.timetoscore.com/display-schedule.php?team=2610&season=42&tlev=0&tseq=0&league=1',
             'https://stats.sharksice.timetoscore.com/display-schedule.php?team=2708&season=42&tlev=0&tseq=0&league=1',
             'https://stats.sharksice.timetoscore.com/display-schedule?team=2965&season=42&league=1&stat_class=1',
             'https://stats.sharksice.timetoscore.com/display-schedule.php?team=4122&season=42&tlev=0&tseq=0&league=1'
            ]
data = {}
teams = {
    'Austin': ['Mickey Colombo', 'Dylan Viskochil', 'Jaron Nazaroff', 'Sean Dunbar', 'Jerred Oconnell', 'John Roth',
               'Codie Oconnell', 'Austin Gardiner'],
    'Schlink': ['William Robinson', 'Kevin Hutchins', 'Todd Myers', 'Andrew Germond', 'Jose Arias', 'Victor Cruz',
                'Jonathan Sebring', 'Steven Schlinkert'],
    'Markham': ['Steven Scott', 'Joseph Friesen', 'Kyle Skjerven', 'Martin Jensen Iii', 'Jay Marvin Marvin',
                'Jason Perrucci', 'Daniel Watson', 'Matthew Markham'],
    'Bobby': ['Eric King', 'Derek Truesdale', 'Albert Hong', 'Kevin Kalman', 'Michael Moore', 'Coryndon Coles Iv',
              'Briana Steadman', 'Robert Victorino'],
    'Grant': ['Cecile Nguyen', 'Jordan Dodge', 'Chinh Bui', 'Olli-Pekka Tossavainen', 'Adam Scianna', 'Raymond Bernal',
              'Darrin Ng', 'Grant Gardiner'],
    'Don': ['Tyler Jue', 'Gabe Villalovos', 'Gino Escalante', 'Thomas Dong', 'Antrico Forbes', 'William Jelavich',
            'Jerry Hsu', 'Don Labarbera'],
    'Dunn': ['Eric Sokol', 'Chris Rathjen', 'Rick Chaput', 'Zachary Piper', 'Michael Reed', 'Brian Miyakusu',
             'Yuri Macauley', 'Nickolas Dunn']
}

for page in icb_pages:
    url = page
    driver.get(url)
    skatersTable = driver.find_element_by_xpath("//center[3]/table/tbody")
    skaterRows = skatersTable.find_elements_by_xpath(".//tr")
    playersStats = {}
    for row in skaterRows:
        player = row.find_elements_by_xpath(".//td")
        if len(player) == 15:
            name = player[0].text
            number = player[1].text
            gp = int(player[2].text)
            goals = int(player[3].text)
            assists = int(player[4].text)
            ppg = int(player[5].text)
            ppa = int(player[6].text)
            shg = int(player[7].text)
            sha = int(player[8].text)
            gwg = int(player[9].text)
            gwa = int(player[10].text)
            psg = int(player[11].text)
            eng = int(player[12].text)
            sog = int(player[13].text)
            pts = int(player[14].text)
            fantasy_pts = (goals*2) + (assists*1) + (ppg*1) + (ppa*.5) + (shg*1) + (sha*.5) + (gwg*1) + (gwa*.5)\
                + (psg*1) + (eng*1) + (sog*1)
            team = ''
            for t in teams:
                if name in teams['Austin']:
                    team = 'Austin'
                elif name in teams['Schlink']:
                    team = 'Schlink'
                elif name in teams['Markham']:
                    team = 'Markham'
                elif name in teams['Bobby']:
                    team = 'Bobby'
                elif name in teams['Grant']:
                    team = 'Grant'
                elif name in teams['Don']:
                    team = 'Don'
                elif name in teams['Dunn']:
                    team = 'Dunn'

            if name not in data:
                data[name] = {}
                data[name].update({
                    'name': name,
                    'number': number,
                    'gp': gp,
                    'goals': goals,
                    'assists': assists,
                    'ppg': ppg,
                    'ppa': ppa,
                    'shg': shg,
                    'sha': sha,
                    'gwg': gwg,
                    'gwa': gwa,
                    'psg': psg,
                    'eng': eng,
                    'sog': sog,
                    'pts': pts,
                    'fantasy_pts': fantasy_pts,
                    'team': team
                })
            else:
                person = data[name]
                person['gp'] += gp
                person['goals'] += goals
                person['assists'] += assists
                person['ppg'] += ppg
                person['ppa'] += ppa
                person['shg'] += shg
                person['sha'] += sha
                person['gwg'] += gwg
                person['gwa'] += gwa
                person['psg'] += psg
                person['eng'] += eng
                person['sog'] += sog
                person['pts'] += pts
                person['fantasy_pts'] += fantasy_pts


cols = ['Name', 'Number', 'GP', 'Goals(2)', 'Assists(1)', 'PPG(1)', 'PPA(.5)', 'SHG(1)', 'SHA(.5)', 'GWG(1)', 'GWA(.5)',
        'PSG(1)', 'ENG(1)', 'SOG(1)', 'PTS', 'Fantasy Pts', 'Team']
rows = []
stats_wks.clear()
stats_wks.append_row(cols)
for key, v in data.items():
    row = [v['name'], v['number'], v['gp'], v['goals'], v['assists'], v['ppg'], v['ppa'], v['shg'], v['sha'],
           v['gwg'], v['gwa'], v['psg'], v['eng'], v['sog'], v['pts'], v['fantasy_pts'], v['team']]
    rows.append(row)
    strRow = ''.join(str(e) for e in row)
    stats_wks.append_row(row)
t = Table(rows=rows, names=cols)
print(t)
ascii.write(t, 'icb.csv', format='csv')


cols2 = ['Name', 'Number', 'GP', 'Goals(2)', 'Assists(1)', 'PPG(1)', 'PPA(.5)', 'SHG(1)', 'SHA(.5)', 'GWG(1)',
         'GWA(.5)', 'PSG(1)', 'ENG(1)', 'SOG(1)', 'PTS', 'Fantasy Pts']
rows2 = []
teamCols = ['Austin', 'Schlink', 'Markham', 'Bobby', 'Grant', 'Don', 'Dunn']
blankRow = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
# summary_wks.clear()
# summary_wks.append_row(['Summary:', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
for i in range(len(teamCols)):
    teamRow = [teamCols[i], '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
    teamPts = 0
    rows2.append(teamRow)
    rows2.append(cols2)
    # summary_wks.append_row(teamRow)
    # summary_wks.append_row(cols2)
    for key, v in data.items():
        if v['team'] == teamCols[i]:
            row = [v['name'], v['number'], v['gp'], v['goals'], v['assists'], v['ppg'], v['ppa'], v['shg'], v['sha'],
                   v['gwg'], v['gwa'], v['psg'], v['eng'], v['sog'], v['pts'], v['fantasy_pts']]
            rows2.append(row)
            # summary_wks.append_row(row)
            teamPts += v['fantasy_pts']
    totalPts = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', 'Total:', teamPts]
    # summary_wks.append_row(totalPts)
    rows2.append(totalPts)

tbl = Table(rows=rows2, names=blankRow)
print(tbl)
ascii.write(tbl, 'summary.csv', format='csv')

with open('icb.json', 'w') as outfile:
    json.dump(data, outfile)
