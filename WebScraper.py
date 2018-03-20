from bs4 import BeautifulSoup
from selenium import webdriver

# whl 2017-2018 season: september 22 2017 to march 18 2018
# whl 2017-2018 game codes: 1014621 to 1015412
# whl url: http://whl.ca/gamecentre/1015413/boxscore

# ohl 2017-2018 season: september 21 2017 to march 18 2018
# ohl 2017-2018 game codes: 22381 to 23061
# ohl url: http://ontariohockeyleague.com/gamecentre/22381/boxscore

# qmjhl 2017-2018 season: september 21 2017 to march 18 2018
# qmjl 2017-2018 game codes: 26127 to 25784
# qmjhl url: http://theqmjhl.ca/gamecentre/26127/boxscore

leagueURLs = {"WHL":"http://whl.ca/gamecentre/", "OHL":"http://ontariohockeyleague.com/gamecentre/", "QMJHL":"http://theqmjhl.ca/gamecentre/"}
leagueStartCodes = {"WHL":1014621, "OHL":22381, "QMJHL":26127}
leagueEndCodes = {"WHL":1015412, "OHL":23061, "QMJHL":25784}


def scrape(league):
    url_base = leagueURLs.get(league)
    browser = webdriver.Chrome("/Users/colinrsmall/documents/GitHub/Prospect-Prospecting/chromedriver")
    games_by_player = []
    for gameCode in range( leagueStartCodes.get(league), leagueEndCodes.get(league)):
        game_url = url_base + str(gameCode) + "/boxscore"
        print(game_url)
        browser.get(game_url)
        inner_html = browser.execute_script("return document.body.innerHTML")
        parsed_html = BeautifulSoup(inner_html, "html.parser")
        away_stats = parsed_html.select(".gamecentre-topscorers .stats-data-table")
        home_stats = parsed_html.select(".gamecentre-lastfivegames .stats-data-table .table__tr--dark")
        for row in home_stats:
            columns = row.select("td")
            game_stats = []
            for cell in columns:
                game_stats.append(cell.text)
            game_stats.append(gameCode)
            game_stats.append(parsed_html.select(".gamecentre-matchup__location")[0].text.split("-")[2].strip())
            game_stats.append(parsed_html.select(".gamecentre-matchup-home .gamecentre-matchup__nickname")[0].text)
            game_stats.append(parsed_html.select(".gamecentre-matchup__gamenumber")[0].text.split(":")[1].split("-")[0].strip())
            games_by_player.append(game_stats)
            games_stats = []

        for row in home_stats:
            columns = row.select("td")
            game_stats = []
            for cell in columns:
                game_stats.append(cell.text)
            game_stats.append(gameCode)
            game_stats.append(parsed_html.select(".gamecentre-matchup__location")[0].text.split("-")[2].strip())
            game_stats.append(parsed_html.select(".gamecentre-matchup-away .gamecentre-matchup__nickname")[0].text)
            game_stats.append(parsed_html.select(".gamecentre-matchup__gamenumber")[0].text.split(":")[1].split("-")[0].strip())
            games_by_player.append(game_stats)
            games_stats = []

        print(games_by_player)

scrape("WHL")
