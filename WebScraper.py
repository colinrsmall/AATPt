from bs4 import BeautifulSoup
from selenium import webdriver
import csv
from dateutil.parser import parse

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
leagueStartCodes = {"WHL_2017-2018":1014621, "OHL_2017-2018":22381, "QMJHL_2017-2018":25784}
leagueEndCodes = {"WHL_2017-2018":1015412, "OHL_2017-2018":23061, "QMJHL_2017-2018":26127}
browser = webdriver.Chrome("/Users/colinrsmall/documents/GitHub/Prospect-Prospecting/chromedriver")
second_browser = webdriver.Chrome("/Users/colinrsmall/documents/GitHub/Prospect-Prospecting/chromedriver")
player_birthdays = {}


def getPlayerStats(home, league, row, game_code, html, team_stats):
    columns = row.select("td")
    game_stats = []
    count = 0
    player_name = columns[2].text.split(" - ")[0].strip().split("*")[0].strip()
    print(player_name)
    for cell in columns:
        game_stats.append(cell.text)
        if count/2 == 1:
            birthday = getPlayerBirthday(league, cell, player_name)
            game_stats.append(birthday)
        count = count + 1
    game_stats.append(game_code)
    if league == "OHL":
        game_date = parse(html.select(".gamecentre-matchup__location")[0].text.split(" - ")[1].strip())
        game_stats.append(game_date)
    else:
        game_date = parse(html.select(".gamecentre-matchup__location")[0].text.split(" - ")[2].strip())
        game_stats.append(game_date)
    if home:
        team_name = html.select(".gamecentre-matchup-home .gamecentre-matchup__nickname")[0].text
        game_stats.append(team_name)
    else:
        team_name = html.select(".gamecentre-matchup-away .gamecentre-matchup__nickname")[0].text
        game_stats.append(team_name)
    for stat in team_stats:
        game_stats.append(stat)
    if birthday == "no birthday":
        game_stats.append("no birthday")
    else:
        game_stats.append(int(str((game_date - birthday)).split(",")[0].split(" ")[0]) / 365)
    return game_stats


def getPlayerBirthday(league, cell, name):
    if player_birthdays.get(name) is None:
        url = leagueURLs.get(league) + cell.find('a', href=True)["href"]
        second_browser.get(url)
        player_html = second_browser.execute_script("return document.body.innerHTML")
        parsed_player_html = BeautifulSoup(player_html, "html.parser")
        birthday_text = parsed_player_html.select('[data-reactid=".0.0.0.0.2.3.1"]')
        while len(birthday_text) == 0:
            print("No birthday text?")
            second_browser.refresh()
            player_html = second_browser.execute_script("return document.body.innerHTML")
            parsed_player_html = BeautifulSoup(player_html, "html.parser")
            birthday_text = parsed_player_html.select('[data-reactid=".0.0.0.0.2.3.1"]')
        if len(birthday_text[0].text) != 0:
            birthday = parse(birthday_text[0].text)
        else:
            birthday = "no birthday"
        player_birthdays[name] = birthday
        return birthday
    else:
        return player_birthdays.get(name)


def scrape(league):
    url_base = leagueURLs.get(league)

    with open(league + "_stats.csv", "w") as stats_file:
        wr = csv.writer(stats_file)
        wr.writerow(["position", "number", "name", "birthday", "goals", "assists", "+/-", "shots", "pims", "fow", "game ID", "game date", "team", "game number", "team goals", "team assists", "team shots", "team pims", "player age"])
        for gameCode in range(leagueStartCodes.get(league), leagueEndCodes.get(league)):
            game_url = url_base + "/gamecentre/"+ str(gameCode) + "/boxscore"
            print(game_url)
            browser.get(game_url)
            inner_html = browser.execute_script("return document.body.innerHTML")
            parsed_html = BeautifulSoup(inner_html, "html.parser")
            away_stats = parsed_html.select('tbody[data-reactid=".0.0.3.0.2.0.1.2.0.1"] .table__tr--dark')
            home_stats = parsed_html.select('tbody[data-reactid=".0.0.3.0.2.1.1.2.0.1"] .table__tr--dark')
            home_assists, home_goals, home_shots, home_pims = 0, 0, 0, 0
            away_assists, away_goals, away_shots, away_pims = 0, 0, 0, 0

            for row in home_stats:
                columns = row.select("td")
                home_goals += int(columns[3].text)
                home_assists += int(columns[4].text)
                home_shots += int(columns[6].text)
                home_pims += int(columns[7].text)
            home_team_stats = [home_goals, home_assists, home_shots, home_pims]

            for row in away_stats:
                columns = row.select("td")
                away_goals += int(columns[3].text)
                away_assists += int(columns[4].text)
                away_shots += int(columns[6].text)
                away_pims += int(columns[7].text)
            away_team_stats = [away_goals, away_assists, away_shots, away_pims]

            for row in home_stats:
                wr.writerow(getPlayerStats(True, league, row, gameCode, parsed_html, home_team_stats))

            for row in away_stats:
                wr.writerow(getPlayerStats(False, league, row, gameCode, parsed_html, away_team_stats))


scrape("OHL_2017-2018")
