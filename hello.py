from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
import os
import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import numpy as np


def analyze(players, type, first):
    if (type == 'Fantasy Score' or type == 'Touchdowns'):
        return
    print(type)
    url = 'https://www.pro-football-reference.com'
    year = 2021    
    r = requests.get(url + '/years/' + str(year) + '/fantasy.htm')
    soup = BeautifulSoup(r.content, 'html.parser')
    parsed_table = soup.find_all('table')[0]
    body = parsed_table.find_all('tbody')[0]

    header = 'Name,Team,Deviation,Over Percentage,Under Percentage,Over w/ Push,Under w/ Push,Games,Insight,Line,Type,Opponent,Rank,StatPerGame,Player Link\n'
    result = ''
    if (first == True):
        result = header

    for player in players:
        team = ''
        opp = ''
        rank = 'N/A'
        perGame = None
        injuryReport = ''
        playerName = player['Name']
        bet = player['FantasyPoints']
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
        if (playerName == 'Dillon,A.J.'):
            playerName = 'Dillon,AJ'
        elif (playerName == 'St.Brown,Amon-Ra'):
            playerName = 'St. Brown,Amon-Ra'
        elif (playerName == 'PittmanJr.,Michael'):
            playerName = 'Pittman,Michael'
        data = body.find('td', attrs={'csk': playerName})
        try:
            name = data.a.get_text()
        except:
            print(playerName)
            continue
        stub = data.a.get('href')
        playerLink = url + stub
        r = requests.get(playerLink)
        soup = BeautifulSoup(r.content, 'html.parser')
        parsed_table = soup.find('table', attrs={'id': 'stats'})
        gameStats = parsed_table.find_all('tbody')[0]
        gameStats = gameStats.find_all('tr')
        over = 0
        under = 0
        push = 0
        logs = []
        for row in gameStats:
            statElem = row.find_all('td', attrs={'data-stat': 'pass_td'})
            if (type == 'Pass Yards'):
                statElem = row.find_all('td', attrs={'data-stat': 'pass_yds'})
            elif (type == 'Rush Yards'):
                statElem = row.find_all('td', attrs={'data-stat': 'rush_yds'})
            elif (type == 'Receiving Yards'):
                statElem = row.find_all('td', attrs={'data-stat': 'rec_yds'})
            #elif (type == 'Fantasy Score'):
                #statElem = 
            elif (type == 'Receptions'):
                statElem = row.find_all('td', attrs={'data-stat': 'rec'})
            #elif (type == 'Touchdowns'):
                #statElem = 
            elif (type == 'Pass TDs'):
                statElem = passTd = row.find_all('td', attrs={'data-stat': 'pass_td'})
            elif (type == 'Rec TDs'):
                statElem = row.find_all('td', attrs={'data-stat': 'rec_td'})
            elif (type == 'Pass Completions'):
                statElem = row.find_all('td', attrs={'data-stat': 'pass_cmp'})
            elif (type == 'INT'):
                statElem = row.find_all('td', attrs={'data-stat': 'pass_int'})
            else:
                break
            try:
                stat = statElem[0].get_text()
            except:
                week = row.find('td', attrs={'align': 'right'})
                if (week is not None):
                    if (week.get_text() == '17'):
                        cols = row.find_all('td')
                        team = cols[2].get_text()
                        injuryReport = url + cols[2].a.get('href')
                        opp = cols[4].get_text()
                        stub = cols[4].a.get('href')
                        r = requests.get(url + stub)
                        soup = BeautifulSoup(r.content, 'html.parser')
                        parsed_table = soup.find('table', attrs={'id': 'team_stats'})
                        defense = parsed_table.find_all('tr')[5]
                        oppStats = parsed_table.find_all('tr')[3]
                        if (type == 'Pass Yards'):
                            rank = defense.find('td', attrs={'data-stat': 'pass_yds'}).get_text()
                            perGame = round(float(oppStats.find('td', attrs={'data-stat': 'pass_yds'}).get_text()) / 14.0, 2)
                        elif (type == 'Rush Yards'):
                            rank = defense.find('td', attrs={'data-stat': 'rush_yds'}).get_text()
                            perGame = round(float(oppStats.find('td', attrs={'data-stat': 'rush_yds'}).get_text()) / 14.0, 2)
                        elif (type == 'Receiving Yards'):
                            rank = defense.find('td', attrs={'data-stat': 'pass_yds'}).get_text()
                            perGame = round(float(oppStats.find('td', attrs={'data-stat': 'pass_yds'}).get_text()) / 14.0, 2)
                        elif (type == 'Pass TDs'):
                            rank = defense.find('td', attrs={'data-stat': 'pass_td'}).get_text()
                            perGame = round(float(oppStats.find('td', attrs={'data-stat': 'pass_td'}).get_text()) / 14.0, 2)
                        elif (type == 'Rec TDs'):
                            rank = defense.find('td', attrs={'data-stat': 'pass_td'}).get_text()
                            perGame = round(float(oppStats.find('td', attrs={'data-stat': 'pass_td'}).get_text()) / 14.0, 2)
                        elif (type == 'INT'):
                            rank = defense.find('td', attrs={'data-stat': 'pass_int'}).get_text()
                            perGame = round(float(oppStats.find('td', attrs={'data-stat': 'pass_int'}).get_text()) / 14.0, 2)
                continue
            if stat == '': stat = '0'
            logs.append(float(stat))
            if (float(stat) == float(bet)):
                push += 1
            elif (float(stat) > float(bet)):
                over = over + 1
            else:
                under = under + 1
        games = over + under + push
        tensorLogs = np.array(logs)
        mean = tensorLogs.mean(axis=0)
        tensorLogs -= mean
        std = tensorLogs.std(axis=0, ddof=1)
        if (games == 0):
            continue
        overPerc = round(over * 100 / games, 2)
        underPerc = round(under * 100 / games, 2)
        normalizedBet = float(bet) - mean
        deviation = np.absolute(normalizedBet / std)
        #if (overPerc >= 70.00):
        temp = str(name) + ',' + str(team) + ','  + str(round(deviation, 2)) + ',' + str(round(over * 100 / games, 2)) + '%,'\
        + str(round(under * 100 / games, 2)) + '%,' + str(round((over + push) * 100 / games, 2)) + '%,'\
        + str(round((under + push) * 100 / games, 2)) + '%,' + str(games) + ',' + 'N/A' + ',' + str(bet)\
        + ',' + str(type) + ',' + str(opp) + ',' + str(rank) + ',' + str(perGame) + ',' + str(playerLink)\
        + ',' + str(injuryReport) + '\n'
        result += temp
        #elif (underPerc >= 70.00):
            #temp = str(name) + ',' + str(round(under * 100 / games, 2)) + '%,' + str(games) +\
            #',' + 'UNDER' + ',' + str(bet) + ',' + type + '\n'
            #result += temp
    result = result.split('\n')
    
    with open('assets/NFLInsights.csv', 'a') as file:
        for line in result:
            file.write(line + os.linesep)

url = 'https://app.prizepicks.com/'
chrome_driver = os.getcwd() + '/chromedriver'
driver = webdriver.Chrome(chrome_driver)
driver.get(url)
driver.find_element_by_class_name("close").click()
driver.find_element_by_xpath("//div[@class='name'][normalize-space()='NFL']").click()
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//*[text() = 'Pass Yards']")))
cats = driver.find_elements_by_xpath("//div[@class='stat ']")
for i in range(len(cats) + 1):
    time.sleep(1)
    projections = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".projection")))
    players = []
    for projection in projections:
        names = projection.find_element_by_xpath('.//div[@class="name"]').text
        points= projection.find_element_by_xpath('.//div[@class="presale-score"]').get_attribute('innerHTML')

        player = {
            'Name': names,
            'FantasyPoints':points,
        }
        players.append(player)

    if (i == 0):
        analyze(players, 'Pass Yards', True)
    else:
        analyze(players, cats[i-1].text, False)
    if (i != len(cats)):
        cats[i].click()
driver.quit()

"""
with open('assets/data/PassingYds.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)
    count = 0
    hits = 0
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
        gameStats = gameStats.find_all('tr')
        over = 0
        under = 0
        pyd15 = -1
        for row in gameStats:
            week = row.find_all('td', attrs={'data-stat': 'week_num'})
            passYd = row.find_all('td', attrs={'data-stat': 'pass_yds'})
            if (week[0].get_text() == '15'):
                pyd15 = float(passYd[0].get_text())
                break
            yd = passYd[0].get_text()
            if (float(yd) > bet):
                over = over + 1
            else:
                under = under + 1
        hit = "NULL"
        if (pyd15 > -1):
            if (float(pyd15) > bet):
                hit = "OVER"
            else:
                hit = "UNDER"
        games = over + under
        overPerc = round(over * 100 / games, 2)
        underPerc = round(under * 100 / games, 2)
        if ((overPerc >= 70.00 and hit == "OVER") or (underPerc >= 70.00 and hit == "UNDER")):
            temp = str(name) + ', ' + str(team) + ',' + str(round(over * 100 / games, 2)) + '%, ' +\
            str(round(under * 100 / games, 2)) + '%, ' + str(games) + ', ' + str(over) + ', '\
            + str(under) + ', ' + str(bet) + ',' + "HIT" + '\n'
            result += temp
            count += 1
            hits += 1
        elif ((overPerc >= 70.00 and hit == "UNDER") or (underPerc >= 70.00 and hit == "OVER")):
            temp = str(name) + ', ' + str(team) + ',' + str(round(over * 100 / games, 2)) + '%, ' +\
            str(round(under * 100 / games, 2)) + '%, ' + str(games) + ', ' + str(over) + ', '\
            + str(under) + ', ' + str(bet) + ',' + "MISS" + '\n'
            result += temp
            count += 1
    result += str(round(hits * 100 / count, 2))
    result = result.split('\n')
with open('assets/insights/PassingYdsInsights.csv', 'w') as file:
    for line in result:
        file.write(line + os.linesep)

result = header

with open('assets/data/Receptions.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)
    count = 0
    hits = 0
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
        gameStats = gameStats.find_all('tr')
        over = 0
        under = 0
        rec15 = -1
        for row in gameStats:
            week = row.find_all('td', attrs={'data-stat': 'week_num'})
            receptions = row.find_all('td', attrs={'data-stat': 'rec'})
            if (week[0].get_text() == '15'):
                rec15 = float(receptions[0].get_text())
                break
            rec = receptions[0].get_text()
            if rec == '': rec = '0'
            if (float(rec) > bet):
                over = over + 1
            else:
                under = under + 1
        hit = "NULL"
        if (rec15 > -1):
            if (float(rec15) > bet):
                hit = "OVER"
            else:
                hit = "UNDER"
        games = over + under
        overPerc = round(over * 100 / games, 2)
        underPerc = round(under * 100 / games, 2)
        if ((overPerc >= 70.00 and hit == "OVER") or (underPerc >= 70.00 and hit == "UNDER")):
            temp = str(name) + ', ' + str(team) + ',' + str(round(over * 100 / games, 2)) + '%, ' +\
            str(round(under * 100 / games, 2)) + '%, ' + str(games) + ', ' + str(over) + ', '\
            + str(under) + ', ' + str(bet) + ',' + "HIT" + '\n'
            result += temp
            count += 1
            hits += 1
        elif ((overPerc >= 70.00 and hit == "UNDER") or (underPerc >= 70.00 and hit == "OVER")):
            temp = str(name) + ', ' + str(team) + ',' + str(round(over * 100 / games, 2)) + '%, ' +\
            str(round(under * 100 / games, 2)) + '%, ' + str(games) + ', ' + str(over) + ', '\
            + str(under) + ', ' + str(bet) + ',' + "MISS" + '\n'
            result += temp
            count += 1
    result += str(round(hits * 100 / count, 2))
    result = result.split('\n')
with open('assets/insights/ReceptionsInsights.csv', 'w') as file:
    for line in result:
        file.write(line + os.linesep)

result = header

with open('assets/data/RecvYds.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)
    count = 0
    hits = 0
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
        gameStats = gameStats.find_all('tr')
        over = 0
        under = 0
        recy15 = -1
        for row in gameStats:
            week = row.find_all('td', attrs={'data-stat': 'week_num'})
            recyds = row.find_all('td', attrs={'data-stat': 'rec_yds'})
            if (week[0].get_text() == '15'):
                recy15 = float(recyds[0].get_text())
                break
            yd = recyds[0].get_text()
            if yd == '': yd = '0'
            if (float(yd) > bet):
                over = over + 1
            else:
                under = under + 1
        hit = "NULL"
        if (recy15 > -1):
            if (float(recy15) > bet):
                hit = "OVER"
            else:
                hit = "UNDER"
        games = over + under
        overPerc = round(over * 100 / games, 2)
        underPerc = round(under * 100 / games, 2)
        if ((overPerc >= 70.00 and hit == "OVER") or (underPerc >= 70.00 and hit == "UNDER")):
            temp = str(name) + ', ' + str(team) + ',' + str(round(over * 100 / games, 2)) + '%, ' +\
            str(round(under * 100 / games, 2)) + '%, ' + str(games) + ', ' + str(over) + ', '\
            + str(under) + ', ' + str(bet) + ',' + "HIT" + '\n'
            result += temp
            count += 1
            hits += 1
        elif ((overPerc >= 70.00 and hit == "UNDER") or (underPerc >= 70.00 and hit == "OVER")):
            temp = str(name) + ', ' + str(team) + ',' + str(round(over * 100 / games, 2)) + '%, ' +\
            str(round(under * 100 / games, 2)) + '%, ' + str(games) + ', ' + str(over) + ', '\
            + str(under) + ', ' + str(bet) + ',' + "MISS" + '\n'
            result += temp
            count += 1
    result += str(round(hits * 100 / count, 2))
    result = result.split('\n')
with open('assets/insights/RecvYdsInsights.csv', 'w') as file:
    for line in result:
        file.write(line + os.linesep)

result = header

with open('assets/data/RushingYds.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)
    count = 0
    hits = 0
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
        gameStats = gameStats.find_all('tr')
        over = 0
        under = 0
        rush15 = -1
        for row in gameStats:
            week = row.find_all('td', attrs={'data-stat': 'week_num'})
            rushyds = row.find_all('td', attrs={'data-stat': 'rush_yds'})
            if (week[0].get_text() == '15'):
                rush15 = float(rushyds[0].get_text())
                break
            yd = rushyds[0].get_text()
            if yd == '': yd = '0'
            if (float(yd) > bet):
                over = over + 1
            else:
                under = under + 1
        hit = "NULL"
        if (rush15 > -1):
            if (float(rush15) > bet):
                hit = "OVER"
            else:
                hit = "UNDER"
        games = over + under
        overPerc = round(over * 100 / games, 2)
        underPerc = round(under * 100 / games, 2)
        if ((overPerc >= 70.00 and hit == "OVER") or (underPerc >= 70.00 and hit == "UNDER")):
            temp = str(name) + ', ' + str(team) + ',' + str(round(over * 100 / games, 2)) + '%, ' +\
            str(round(under * 100 / games, 2)) + '%, ' + str(games) + ', ' + str(over) + ', '\
            + str(under) + ', ' + str(bet) + ',' + "HIT" + '\n'
            result += temp
            count += 1
            hits += 1
        elif ((overPerc >= 70.00 and hit == "UNDER") or (underPerc >= 70.00 and hit == "OVER")):
            temp = str(name) + ', ' + str(team) + ',' + str(round(over * 100 / games, 2)) + '%, ' +\
            str(round(under * 100 / games, 2)) + '%, ' + str(games) + ', ' + str(over) + ', '\
            + str(under) + ', ' + str(bet) + ',' + "MISS" + '\n'
            result += temp
            count += 1
    result += str(round(hits * 100 / count, 2))
    result = result.split('\n')
with open('assets/insights/RushingYdsInsights.csv', 'w') as file:
    for line in result:
        file.write(line + os.linesep)

"""