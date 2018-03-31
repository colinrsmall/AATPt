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
# leagueStartCodes = {"WHL":1014621, "OHL":22381, "QMJHL":25784}
leagueStartCodes = {"WHL":1014621, "OHL":22782, "QMJHL":25784}
leagueEndCodes = {"WHL":1015412, "OHL":23061, "QMJHL":26127}

def scrape(league):
    url_base = leagueURLs.get(league)
    browser = webdriver.Chrome("/Users/colinrsmall/documents/GitHub/Prospect-Prospecting/chromedriver")
    second_browser = webdriver.Chrome("/Users/colinrsmall/documents/GitHub/Prospect-Prospecting/chromedriver")
    games_by_player = []

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
            home_assists, home_goals, home_shots, home_pims = 0, 0, 0, 0;
            away_assists, away_goals, away_shots, away_pims = 0, 0, 0, 0;

            for row in home_stats:
                columns = row.select("td")
                count = 0
                for cell in columns:
                    if count/3 == 1:
                        home_goals += int(cell.text)
                    if count/4 == 1:
                        home_assists += int(cell.text)
                    if count / 6 == 1:
                         home_shots += int(cell.text)
                    if count / 7 == 1:
                        home_pims += int(cell.text)
                    count = count+1

            for row in away_stats:
                columns = row.select("td")
                count = 0
                for cell in columns:
                    if count/3 == 1: # / not % because I only want the cell in the 4th position
                        away_goals += int(cell.text)
                    if count/4 == 1:
                        away_assists += int(cell.text)
                    if count / 6 == 1:
                        away_shots += int(cell.text)
                    if count / 7 == 1:
                        away_pims += int(cell.text)
                    count = count+1

            for row in home_stats:
                columns = row.select("td")
                game_stats = []
                count = 0
                for cell in columns:
                    game_stats.append(cell.text)
                    if count/2 == 1:
                        url = url_base + (cell.find('a', href=True)["href"])
                        second_browser.get(url)
                        player_html = second_browser.execute_script("return document.body.innerHTML")
                        parsed_player_html = BeautifulSoup(player_html, "html.parser")
                        birthday_text = parsed_player_html.select('[data-reactid=".0.0.0.0.2.3.1"]')
                        while len(birthday_text)==0:
                            print("No text?")
                            second_browser.refresh()
                            player_html = second_browser.execute_script("return document.body.innerHTML")
                            parsed_player_html = BeautifulSoup(player_html, "html.parser")
                            birthday_text = parsed_player_html.select('[data-reactid=".0.0.0.0.2.3.1"]');
                        if len(birthday_text[0].text) != 0:
                            birthday = parse(birthday_text[0].text)
                        else:
                            birthday = "no birthday"
                        game_stats.append(birthday)
                    count = count+1
                game_stats.append(gameCode)
                if league == "WHL":
                    game_date = parse(parsed_html.select(".gamecentre-matchup__location")[0].text.split(" - ")[2].strip())
                    game_stats.append(game_date)
                if league == "OHL":
                    game_date = parse(parsed_html.select(".gamecentre-matchup__location")[0].text.split(" - ")[1].strip())
                    game_stats.append(game_date)
                game_stats.append(parsed_html.select(".gamecentre-matchup-home .gamecentre-matchup__nickname")[0].text)
                game_stats.append(parsed_html.select(".gamecentre-matchup__gamenumber")[0].text.split(":")[1].split("-")[0].strip())
                game_stats.append(home_goals)
                game_stats.append(home_assists)
                game_stats.append(home_shots)
                game_stats.append(home_pims)
                if birthday == "no birthday":
                    game_stats.append("no birthday")
                else:
                    game_stats.append(int(str((game_date - birthday)).split(",")[0].split(" ")[0])/365)
                wr.writerow(game_stats)
                games_stats = []

            for row in away_stats:
                columns = row.select("td")
                game_stats = []
                count = 0
                for cell in columns:
                    game_stats.append(cell.text)
                    if count / 2 == 1:
                        url = url_base + (cell.find('a', href=True)["href"])
                        second_browser.get(url)
                        player_html = second_browser.execute_script("return document.body.innerHTML")
                        parsed_player_html = BeautifulSoup(player_html, "html.parser")
                        while len(birthday_text)==0:
                            print("No text?")
                            second_browser.refresh()
                            player_html = second_browser.execute_script("return document.body.innerHTML")
                            parsed_player_html = BeautifulSoup(player_html, "html.parser")
                            birthday_text = parsed_player_html.select('[data-reactid=".0.0.0.0.2.3.1"]');
                        if len(birthday_text[0].text) != 0:
                            birthday = parse(birthday_text[0].text)
                        else:
                            birthday = "no birthday"
                        game_stats.append(birthday)
                    count = count+1
                game_stats.append(gameCode)
                if league != "OHL":
                    game_date = parse(parsed_html.select(".gamecentre-matchup__location")[0].text.split(" - ")[2].strip())
                    game_stats.append(game_date)
                if league == "OHL":
                    game_date = parse(parsed_html.select(".gamecentre-matchup__location")[0].text.split(" - ")[1].strip())
                    game_stats.append(game_date)
                game_stats.append(parsed_html.select(".gamecentre-matchup-away .gamecentre-matchup__nickname")[0].text)
                game_stats.append(parsed_html.select(".gamecentre-matchup__gamenumber")[0].text.split(":")[1].split("-")[0].strip())
                game_stats.append(away_goals)
                game_stats.append(away_assists)
                game_stats.append(away_shots)
                game_stats.append(away_pims)
                if birthday == "no birthday":
                    game_stats.append("no birthday")
                else:
                    game_stats.append(int(str((game_date - birthday)).split(",")[0].split(" ")[0])/365)
                wr.writerow(game_stats)
                games_stats = []

            print(games_by_player)

scrape("OHL")
