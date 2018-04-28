from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
import csv
from dateutil.parser import parse
import progressbar
import time

# whl 2017-2018 season: september 22 2017 to march 18 2018
# whl 2017-2018 game codes: 1014621 to 1015412
# whl url: http://whl.ca/gamecentre/1015413/boxscore

# ohl 2017-2018 season: september 21 2017 to march 18 2018
# ohl 2017-2018 game codes: 22381 to 23061
# ohl url: http://ontariohockeyleague.com/gamecentre/22381/boxscore

# qmjhl 2017-2018 season: september 21 2017 to march 18 2018
# qmjl 2017-2018 game codes: 26127 to 25784
# qmjhl url: http://theqmjhl.ca/gamecentre/26127/boxscore

leagueURLs = {"WHL":"http://whl.ca", "OHL":"http://ontariohockeyleague.com", "QMJHL":"http://theqmjhl.ca"}
# leagueStartCodes = {"WHL_2017-2018":1010576, "OHL_2017-2018":22381, "QMJHL_2017-2018":25784, "WHL_2014-2015":1010890, "OHL_2014-2015":19928, "WHL_2007-2008":1004352, "OHL_2007-2008":14458, "QMJHL_2007-2008":22528}
leagueStartCodes = {"WHL_2017-2018":1010576, "OHL_2017-2018":22381, "QMJHL_2017-2018":25784, "WHL_2014-2015":1010890, "OHL_2014-2015":19928, "WHL_2007-2008":1004352, "OHL_2007-2008":14458, "QMJHL_2007-2008":25119, 'WHL_2000-2001':23081, 'OHL_2000-2001':8334, 'QMJHL_2000-2001':18469}
leagueEndCodes = {"WHL_2017-2018":1015412, "OHL_2017-2018":23058, "QMJHL_2017-2018":26228, 'WHL_2006-2007':1004352, 'OHL_2006-2007':14458, 'QMJHL_2006-2007':25119}
browser = webdriver.Chrome("/Users/colinrsmall/documents/GitHub/Prospect-Prospecting/chromedriver")
second_browser = webdriver.Chrome("/Users/colinrsmall/documents/GitHub/Prospect-Prospecting/chromedriver")
player_birthdays = {}
player_draft_status = {}

def getPlayerStats(home, league, row, game_code, html, team_stats, url):
    columns = row.select("td")
    game_stats = []
    count = 0
    player_name = columns[2].text.split(" - ")[0].strip().split("*")[0].strip()
    for cell in columns:
        if count == 9:
            break
        if count/2 == 1:
            temp = getPlayerBirthday(league, cell, player_name)
            birthday = temp[0]
            draft = temp[1]
            game_stats.append(str(player_name))
            game_stats.append(birthday)
            game_stats.append(draft)
        else:
            game_stats.append(cell.text)
        count = count + 1
    game_stats.append(game_code)

    location_raw = html.select(".gamecentre-matchup__location")

    while len(location_raw) == 0:
        #print("bad date, skipping")
        return ""

    try:
        try:
            if '-' in location_raw[0].text:
                game_date = parse(location_raw[0].text.split(" - ")[2].strip())
                game_stats.append(game_date)
            else:
                game_date = parse(location_raw[0].text)
                game_stats.append(game_date)
        except IndexError:
            game_date = parse(location_raw[0].text.split(" - ")[1].strip())
            game_stats.append(game_date)
    except ValueError:
        #print("bad date 2, skipping")
        return ""

    if home:
        team_name = html.select(".gamecentre-matchup-home .gamecentre-matchup__nickname")[0].text
        game_stats.append(team_name)
    else:
        team_name = html.select(".gamecentre-matchup-away .gamecentre-matchup__nickname")[0].text
        game_stats.append(team_name)
    game_stats.append(html.select('[data-reactid=".0.0.0.3"]')[0].text.split(" - ")[0].split(":")[1].strip())

    for stat in team_stats:
        game_stats.append(stat)
    if birthday == "no birthday":
        game_stats.append("no birthday")
    else:
        game_stats.append(int(str((game_date - birthday)).split(",")[0].split(" ")[0]) / 365)
    season = ""
    for part in html.select('[data-reactid=".0.0.0.3"]')[0].text.split(" - ")[1:]:
        season += part
    game_stats.append(season)
    return game_stats

def getPlayerBirthday(league, cell, name):
    # print("checking birthday of " + name)
    if player_birthdays.get(name) is None:
        # print("no birthday found for " + name + " - setting")
        url = leagueURLs.get(league) + cell.find('a', href=True)["href"]
        try:
            second_browser.get(url)
        except selenium.common.exceptions.TimeoutException:
            second_browser.get(url)
        player_html = second_browser.execute_script("return document.body.innerHTML")
        parsed_player_html = BeautifulSoup(player_html, "html.parser")

        if league != "QMJHL":
            birthday_text = parsed_player_html.select('[data-reactid=".0.0.0.0.2.3.1"]')
            try:
                draft_table = parsed_player_html.select('[data-reactid=".0.0.0.0.2.6.1"]')
                draft_text = draft_table[0].select('div')[0].text
                if 'NHL' not in draft_text:
                    draft_text = 'Undrafted'
            except IndexError as e:
                #print(e)
                draft_text = 'Undrafted'
        else:
            error_output = []
            try:
                qmjhl_player_panel = parsed_player_html.select('.info-con-table01')
                row = qmjhl_player_panel[0].select('tr')[2]
                birthday_text = row.select('span')
                error_output.append(birthday_text[0].text)
            except IndexError as e:
                #print(e)
                error_output.append('no birthday')
            try:
                qmjhl_draft_panel = parsed_player_html.select('.info-con-table02')
                row = qmjhl_draft_panel[0].select('td')[0]
                draft_text = row.text[106:]
                if "NHL" not in row.text:
                    draft_text = 'Undrafted'
                error_output.append(draft_text)
            except IndexError as e:
                #print(e)
                error_output.append('Undrafted')
                return error_output;
        # print(birthday_text)
        count = 0
        while len(birthday_text) == 0 or birthday_text[0].text.strip() == "0000-00-00":
            if count > 5:
                return ["no birthday", 'no draft']
            # print("No birthday text?")
            second_browser.refresh()
            player_html = second_browser.execute_script("return document.body.innerHTML")
            parsed_player_html = BeautifulSoup(player_html, "html.parser")
            birthday_text = parsed_player_html.select('[data-reactid=".0.0.0.0.2.3.1"]')
            count += 1
        if len(draft_text) == 0:
            draft = 'Undrafted'
        else:
            draft = draft_text
        if len(birthday_text[0].text) != 0:
            birthday = parse(birthday_text[0].text)
        else:
            birthday = "no birthday"
        player_birthdays[name] = birthday
        player_draft_status[name] = draft
        #print(name + " " + str(birthday) + " " + draft)
        return [birthday, draft]
    else:
        # print("birthday found for " + name)
        return [player_birthdays.get(name), player_draft_status.get(name)]


def scrape(league, start_year1, end_year1, start_year2, end_year2):
    url_base = leagueURLs.get(league)
    progress_bar = progressbar.ProgressBar(max_value=(leagueEndCodes.get(league+"_"+start_year2+"-"+end_year2) - (leagueStartCodes.get(league+"_"+start_year1+"-"+end_year1)))).start()
    pb_count = 0

    with open(league + "_" + start_year1 + "-" + end_year1 + "_to_" + start_year2 + "-" + end_year2 + "_stats.csv", "w") as stats_file:
        wr = csv.writer(stats_file)
        wr.writerow(["position", "number", "name", "birthday", "draft status","goals", "assists", "+/-", "shots", "pims", "fow", "game ID", "game date", "team", "game number", "team goals", "team assists", "team shots", "team pims", "player age", "season"])
        for gameCode in range(leagueStartCodes.get(league+"_"+start_year1+"-"+end_year1), leagueEndCodes.get(league+"_"+start_year2+"-"+end_year2)):
            game_url = url_base + "/gamecentre/" + str(gameCode) + "/boxscore"
            # print(game_url)
            browser.get(game_url)
            inner_html = browser.execute_script("return document.body.innerHTML")
            parsed_html = BeautifulSoup(inner_html, "html.parser")
            away_stats = parsed_html.select('tbody[data-reactid=".0.0.3.0.2.0.1.2.0.1"] .table__tr--dark')
            home_stats = parsed_html.select('tbody[data-reactid=".0.0.3.0.2.1.1.2.0.1"] .table__tr--dark')
            count = 0
            skip = False
            while len(away_stats) == 0 or len(home_stats) == 0:
                if count > 5:
                    # print("no stats found after fifth try, skipping")
                    skip = True
                    break
                # print("no stats found, refreshing")
                browser.get(game_url)
                inner_html = browser.execute_script("return document.body.innerHTML")
                parsed_html = BeautifulSoup(inner_html, "html.parser")
                away_stats = parsed_html.select('tbody[data-reactid=".0.0.3.0.2.0.1.2.0.1"] .table__tr--dark')
                home_stats = parsed_html.select('tbody[data-reactid=".0.0.3.0.2.1.1.2.0.1"] .table__tr--dark')
                count += 1
            if skip:
                continue
            home_assists, home_goals, home_shots, home_pims = 0, 0, 0, 0
            away_assists, away_goals, away_shots, away_pims = 0, 0, 0, 0

            for row in home_stats:
                columns = row.select("td")
                try:
                    home_goals += int(columns[3].text)
                    home_assists += int(columns[4].text)
                    home_shots += int(columns[6].text)
                    home_pims += int(columns[7].text)
                except ValueError:
                    continue
            home_team_stats = [home_goals, home_assists, home_shots, home_pims]

            for row in away_stats:
                columns = row.select("td")
                try:
                    away_goals += int(columns[3].text)
                    away_assists += int(columns[4].text)
                    away_shots += int(columns[6].text)
                    away_pims += int(columns[7].text)
                except ValueError:
                    continue
            away_team_stats = [away_goals, away_assists, away_shots, away_pims]

            for row in home_stats:
                output = getPlayerStats(True, league, row, gameCode, parsed_html, home_team_stats, game_url)
                if output != "":
                    #print("output=" + str(output))
                    wr.writerow(output)

            for row in away_stats:
                output = getPlayerStats(False, league, row, gameCode, parsed_html, away_team_stats, game_url)
                if output != "":
                    #print("output=" + str(output))
                    wr.writerow(output)

            pb_count += 1
            progress_bar.update(pb_count)

scrape("QMJHL", "2000", "2001", "2006", "2007")
