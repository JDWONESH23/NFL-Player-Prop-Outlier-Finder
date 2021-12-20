from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
import os
import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
"""
url = 'http://mybookie.ag'
r = requests.get(url + '/sportsbook/nfl')
soup = BeautifulSoup(r.content, 'html.parser')
nfl = soup.find('div', attrs={'id': 'main-sportsbook-container'})
links = nfl.find_all('p', attrs={'class': 'game-line__props text-right'})
stub = ''
propStart = 'https://bv2.digitalsportstech.com/widgets?event='
propEnd='&sb=mybookie&jwtToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6IjFjNTM5ZDY4NTM3ZGM2YzZlZjkxYzZm\
ZDZjN2NmYzA1IiwidXNlciI6Ik1CMTIzMDg0MiIsInNiIjoibXlib29raWUiLCJpYXQiOjE2MzgxNTI2NTUsImV4cCI6NjU0NDM1MDQ2OTV9.\
MTV1bzH11uMcMbCM0vxAgaWcX25AoiWGMw6goch-Nzk&currency=USD&theme=mybookiedark'
for link in links:
    if (int(link.a.get_text()[1:3]) < 30):
        continue
    stub = link.a.get('href')[-8:]
    send = propStart + stub + propEnd
    print(send)
    option = Options()
    option.add_argument('--headless')
    chrome_driver = os.getcwd() + '/chromedriver'
    driver = webdriver.Chrome(options=option, executable_path=chrome_driver)
    driver.get(send)
    soup = BeautifulSoup(r.content, 'html.parser')
    gameLines = soup.find_all('app-ou-markets')
    print(gameLines)
    driver.quit()
    


"""

url = 'https://www.pro-football-reference.com'
year = 2021    
r = requests.get(url + '/years/' + str(year) + '/fantasy.htm')
soup = BeautifulSoup(r.content, 'html.parser')
parsed_table = soup.find_all('table')[0]
body = parsed_table.find_all('tbody')[0]

header = 'Name, Team, Over Percentage, Under Percentage, Games, Over Hits, Under Hits, Line\n'
result = header


with open('assets/data/PassingTds.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)
    for line in reader:
        playerName = line[0]
        team = line[1]
        bet = float(line[4])
        first = True
        firstName = ''
        lastName = ''
        for i in playerName:
            if (i == ' '):
                first = False
            elif (first):
                firstName = firstName + i
            else:
                lastName = lastName + i
        playerName = lastName + ',' + firstName
        data = body.find('td', attrs={'csk': lastName + ',' + firstName})
        name = data.a.get_text()
        stub = data.a.get('href')
        r = requests.get(url + stub)
        soup = BeautifulSoup(r.content, 'html.parser')
        parsed_table = soup.find('table', attrs={'id': 'stats'})
        gameStats = parsed_table.find_all('tbody')[0]
        passTds = gameStats.find_all('td', attrs={'data-stat': 'pass_td'})
        over = 0
        under = 0
        for row in passTds:
            td = row.get_text()
            if (float(td) > bet):
                over = over + 1
            else:
                under = under + 1
        games = over + under
        temp = str(name) + ', ' + str(team) + ',' + str(round(over * 100 / games, 2)) + '%, ' +\
        str(round(under * 100 / games, 2)) + '%, ' + str(games) + ', ' + str(over) + ', '\
        + str(under) + ', ' + str(bet) + '\n'
        result += temp
    result = result.split('\n')
with open('assets/insights/PassingTdsInsights.csv', 'w') as file:
    for line in result:
        file.write(line + os.linesep)

result = header

with open('assets/data/PassingYds.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)
    for line in reader:
        playerName = line[0]
        team = line[1]
        bet = float(line[4])
        first = True
        firstName = ''
        lastName = ''
        for i in playerName:
            if (i == ' '):
                first = False
            elif (first):
                firstName = firstName + i
            else:
                lastName = lastName + i
        playerName = lastName + ',' + firstName
        data = body.find('td', attrs={'csk': lastName + ',' + firstName})
        name = data.a.get_text()
        stub = data.a.get('href')
        r = requests.get(url + stub)
        soup = BeautifulSoup(r.content, 'html.parser')
        parsed_table = soup.find('table', attrs={'id': 'stats'})
        gameStats = parsed_table.find_all('tbody')[0]
        passYds = gameStats.find_all('td', attrs={'data-stat': 'pass_yds'})
        over = 0
        under = 0
        for row in passYds:
            yd = row.get_text()
            if (float(yd) > bet):
                over = over + 1
            else:
                under = under + 1
        games = over + under
        temp = str(name) + ', ' + str(team) + ',' + str(round(over * 100 / games, 2)) + '%, ' +\
        str(round(under * 100 / games, 2)) + '%, ' + str(games) + ', ' + str(over) + ', '\
        + str(under) + ', ' + str(bet) + '\n'
        result += temp
    result = result.split('\n')
with open('assets/insights/PassingYdsInsights.csv', 'w') as file:
    for line in result:
        file.write(line + os.linesep)

result = header

with open('assets/data/Receptions.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)
    for line in reader:
        playerName = line[0]
        team = line[1]
        bet = float(line[4])
        first = True
        firstName = ''
        lastName = ''
        for i in playerName:
            if (i == ' '):
                first = False
            elif (first):
                firstName = firstName + i
            else:
                lastName = lastName + i
        playerName = lastName + ',' + firstName
        data = body.find('td', attrs={'csk': lastName + ',' + firstName})
        try:
            name = data.a.get_text()
        except:
            continue
        stub = data.a.get('href')
        r = requests.get(url + stub)
        soup = BeautifulSoup(r.content, 'html.parser')
        parsed_table = soup.find('table', attrs={'id': 'stats'})
        gameStats = parsed_table.find_all('tbody')[0]
        receptions = gameStats.find_all('td', attrs={'data-stat': 'rec'})
        over = 0
        under = 0
        for row in receptions:
            rec = row.get_text()
            if rec == '': rec = '0'
            if (float(rec) > bet):
                over = over + 1
            else:
                under = under + 1
        games = over + under
        temp = str(name) + ', ' + str(team) + ',' + str(round(over * 100 / games, 2)) + '%, ' +\
        str(round(under * 100 / games, 2)) + '%, ' + str(games) + ', ' + str(over) + ', '\
        + str(under) + ', ' + str(bet) + '\n'
        result += temp
    result = result.split('\n')
with open('assets/insights/ReceptionsInsights.csv', 'w') as file:
    for line in result:
        file.write(line + os.linesep)

result = header

with open('assets/data/RecvYds.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)
    for line in reader:
        playerName = line[0]
        team = line[1]
        bet = float(line[4])
        first = True
        firstName = ''
        lastName = ''
        for i in playerName:
            if (i == ' '):
                first = False
            elif (first):
                firstName = firstName + i
            else:
                lastName = lastName + i
        playerName = lastName + ',' + firstName
        data = body.find('td', attrs={'csk': lastName + ',' + firstName})
        try:
            name = data.a.get_text()
        except:
            continue
        stub = data.a.get('href')
        r = requests.get(url + stub)
        soup = BeautifulSoup(r.content, 'html.parser')
        parsed_table = soup.find('table', attrs={'id': 'stats'})
        gameStats = parsed_table.find_all('tbody')[0]
        recvYds = gameStats.find_all('td', attrs={'data-stat': 'rec_yds'})
        over = 0
        under = 0
        for row in recvYds:
            yd = row.get_text()
            if yd == '': yd = '0'
            if (float(yd) > bet):
                over = over + 1
            else:
                under = under + 1
        games = over + under
        temp = str(name) + ', ' + str(team) + ',' + str(round(over * 100 / games, 2)) + '%, ' +\
        str(round(under * 100 / games, 2)) + '%, ' + str(games) + ', ' + str(over) + ', '\
        + str(under) + ', ' + str(bet) + '\n'
        result += temp
    result = result.split('\n')
with open('assets/insights/RecvYdsInsights.csv', 'w') as file:
    for line in result:
        file.write(line + os.linesep)

result = header

with open('assets/data/RushingYds.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)
    for line in reader:
        playerName = line[0]
        team = line[1]
        bet = float(line[4])
        first = True
        firstName = ''
        lastName = ''
        for i in playerName:
            if (i == ' '):
                first = False
            elif (first):
                firstName = firstName + i
            else:
                lastName = lastName + i
        playerName = lastName + ',' + firstName
        data = body.find('td', attrs={'csk': lastName + ',' + firstName})
        try:
            name = data.a.get_text()
        except:
            continue
        stub = data.a.get('href')
        r = requests.get(url + stub)
        soup = BeautifulSoup(r.content, 'html.parser')
        parsed_table = soup.find('table', attrs={'id': 'stats'})
        gameStats = parsed_table.find_all('tbody')[0]
        rushYds = gameStats.find_all('td', attrs={'data-stat': 'rush_yds'})
        over = 0
        under = 0
        for row in rushYds:
            yd = row.get_text()
            if yd == '': yd = '0'
            if (float(yd) > bet):
                over = over + 1
            else:
                under = under + 1
        games = over + under
        temp = str(name) + ', ' + str(team) + ',' + str(round(over * 100 / games, 2)) + '%, ' +\
        str(round(under * 100 / games, 2)) + '%, ' + str(games) + ', ' + str(over) + ', '\
        + str(under) + ', ' + str(bet) + '\n'
        result += temp
    result = result.split('\n')
with open('assets/insights/RushingYdsInsights.csv', 'w') as file:
    for line in result:
        file.write(line + os.linesep)