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
# leagueStartCodes = {"WHL_2017-2018":1010576, "OHL_2017-2018":22381, "QMJHL_2017-2018":25784, "WHL_2014-2015":1010890, "OHL_2014-2015":19928, "WHL_2007-2008":1004352, "OHL_2007-2008":14458, "QMJHL_2007-2008":22528, 'WHL_2000-2001':23081, 'OHL_2000-2001':8334, 'QMJHL_2000-2001':18469}
leagueStartCodes = {"WHL_2017-2018":1010576, "OHL_2017-2018":22381, "QMJHL_2017-2018":25784, "WHL_2014-2015":1010890, "OHL_2014-2015":19928, "WHL_2007-2008":1004352, "OHL_2007-2008":14458, "QMJHL_2007-2008":22528, 'WHL_2000-2001':23638, 'OHL_2000-2001':8834, 'QMJHL_2000-2001':18476}
leagueEndCodes = {"WHL_2017-2018":1015412, "OHL_2017-2018":23058, "QMJHL_2017-2018":26228, 'WHL_2006-2007':1004352, 'OHL_2006-2007':14458, 'QMJHL_2006-2007':22528}
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
            temp = getPlayerBirthdayAndDraft(league, cell, player_name)
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
            if '-' in location_raw[0].text and league != 'QMJHL':
                game_date = parse(location_raw[0].text.split(" - ")[2].strip())
                game_stats.append(game_date)
            elif '-' in location_raw[0].text and league == 'QMJHL':
                game_date = parse(location_raw[0].text.split("-")[1].strip())
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
    if birthday == "no birthday" or birthday == 'Undrafted':
        game_stats.append("no birthday")
    else:
        print(game_date)
        print(birthday)
        game_stats.append(int(str((game_date - birthday)).split(",")[0].split(" ")[0]) / 365)
    season = ""
    for part in html.select('[data-reactid=".0.0.0.3"]')[0].text.split(" - ")[1:]:
        season += part
    game_stats.append(season)
    return game_stats

def getPlayerBirthdayAndDraft(name, league, href):
    
    # Checks if player birthday is known, creates new entry if not
    if player_birthdays.get(name) is None:
        
        # Open player profile page
        url = leagueURLs.get(league) + href
        try:
            second_browser.get(url)
        except selenium.common.exceptions.TimeoutException:
            second_browser.get(url)
        player_html = second_browser.execute_script("return document.body.innerHTML")
        parsed_player_html = BeautifulSoup(player_html, "html.parser")

        # Handle differing player profiles per league
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
            if count > 2:
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
        return {'birthday':player_birthdays.get(name), 'draft_stats':player_draft_status.get(name)}


def scrape(league, first_game, last_game):
    
    url_base = leagueURLs.get(league)
    progress_bar = progressbar.ProgressBar(max_value=(first_game - last_game)).start()
    pb_count = 0

    with open(league + "_" + first_game + "_to_" + last_game + "_stats.csv", "w") as stats_file:
        
        wr = csv.writer(stats_file)
        wr.writerow(["position", "name", "birthday", "ev_g", "pp_g", "sh_g", "ev_p_a", "ev_s_a", "pp_p_a", "pp_s_a", "sh_p_a", "sh_s_a", "shots", "draft status", "game ID", "game date", "team", "game number", "t_ev_g", "t_pp_g", "t_sh_g", "t_ev_p_a", "t_ev_s_a", "t_pp_p_a", "t_pp_s_a", "t_sh_p_a", "t_sh_s_a", "t_os_ph_min_pim", "t_of_ph_maj_pim", "t_non_os_ph_min_pim", "t_non_os_ph_maj_pim", "t_os_fig_pim", "t_non_os_ph_min_pim", "t_non_os_ph_major_pim", "t_av_pim", "t_shots", "player age", "season"])
        
        for gameCode in range(first_game, last_game):
            
            # Skips a bunch of unsued game codes in the OHL
            if league == 'OHL' and gameCode in range(27597,999999): 
                continue
            
            # Open the game page and save tables
            game_url = url_base + "/gamecentre/" + str(gameCode) + "/boxscore"
            browser.get(game_url)
            inner_html = browser.execute_script("return document.body.innerHTML")
            parsed_html = BeautifulSoup(inner_html, "html.parser")
            away_skaters = parsed_html.select('tbody[data-reactid=".0.0.3.0.2.0.1.2.0.1"] .table__tr--dark')
            home_skaters = parsed_html.select('tbody[data-reactid=".0.0.3.0.2.1.1.2.0.1"] .table__tr--dark')
            
            # Try five times to get player stats            
            open_attempts = 0
            skip = False
            while len(away_skaters) == 0 or len(home_skaters) == 0:
                if open_attempts > 1:
                    # print("no stats found after fifth try, skipping")
                    skip = True
                    break
                # print("no stats found, refreshing")
                
                # Repeat same steps as above to reopen the game page
                browser.get(game_url)
                inner_html = browser.execute_script("return document.body.innerHTML")
                parsed_html = BeautifulSoup(inner_html, "html.parser")
                away_skaters = parsed_html.select('tbody[data-reactid=".0.0.3.0.2.0.1.2.0.1"] .table__tr--dark')
                home_skaters = parsed_html.select('tbody[data-reactid=".0.0.3.0.2.1.1.2.0.1"] .table__tr--dark')
                open_attempts += 1
                
            # Skip this game code if no stats found
            if skip:
                continue
            
            # Maps player object to player name so you can add stats to the player later
            player_map = {}
            
            # Initialize total stats
            # Home stats
            h_t_ev_g, h_t_pp_g, h_t_sh_g = 0, 0, 0
            h_t_ev_p_a, h_t_ev_s_a, h_t_pp_p_a, h_t_pp_s_a, h_t_sh_p_a, h_t_sh_s_a = 0, 0, 0, 0, 0, 0
            h_t_os_ph_min_pim, h_t_of_ph_maj_pim, h_t_non_os_ph_min_pim, h_t_non_os_ph_maj_pim, h_t_os_fig_pim, h_t_non_os_ph_min_pim, h_t_non_os_ph_major_pim, h_t_av_pim = 0, 0, 0, 0, 0, 0, 0, 0
            h_t_shots = 0
            # Away stats
            a_t_ev_g, a_t_pp_g, h_t_sh_g = 0, 0, 0
            a_t_ev_p_a, a_t_ev_s_a, a_t_pp_p_a, a_t_pp_s_a, a_t_sh_p_a, a_t_sh_s_a = 0, 0, 0, 0, 0, 0
            a_t_os_ph_min_pim, a_t_of_ph_maj_pim, a_t_non_os_ph_min_pim, a_t_non_os_ph_maj_pim, a_t_os_fig_pim, a_t_non_os_ph_min_pim, a_t_non_os_ph_major_pim, a_t_av_pim = 0, 0, 0, 0, 0, 0, 0, 0
            a_t_shots = 0
            
            for row in home_skaters:
               cells = row.select('td')
               position = cells[0].text
               name = cells[2].select('a').text
               shots = cells[6].text
               temp = getPlayerBirthdayAndDraft(name, league, cells[2].select('a').find_all('a', href=True)['href'])
               birthday = temp['birthday']
               draft_status = temp['draft_status']
               player = Player(name, position, birthday, shots, draft_status)
               player_map[name] = player
               

            for row in away_skaters:
               cells = row.select('td')
               position = cells[0].text
               name = cells[2].select('a').text.split('*')[0].split(' - ')[0].trim()
               shots = cells[6].text
               temp = getPlayerBirthdayAndDraft(name, league, cells[2].select('a').find_all('a', href=True)['href'])
               birthday = temp['birthday']
               draft_status = temp['draft_status']
               player = Player(name, position, birthday, shots, draft_status)
               player_map[name] = player
               
            # Select the goals table
            goals_table_rows = parsed_html.select('[data-reactid=".0.0.3.0.7"] > .gamecentre-playbyplay-event > [data-reactid*=".0.0.3.0.7.1:$goal-summary-"]:last-of-type > div > *')
            for row in goals_table_rows:
                name_parts = row.select('a').text.split(' ')
                name = name_parts[1] + ', ' + name_parts[0]
                power_play = row.find_all('span', text='Power Play')
                short_handed = row.find_all('span', text='Short Handed')
                if len(power_play) > 0:
                    player_map[name].add_pp_g()
                if len(short_handed) > 0:
                    player_map[name].add_sh_g()
                else:
                    player_map[name].add_es_g()

            pb_count += 1
            progress_bar.update(pb_count)

class Player:
    
    def __init__(self, name, position, birthday, shots, draft_status):
        self.name = name
        self.position = position
        self.birthday = birthday
        self.shots = shots
        self.draft_status = draft_status
        self.es_g = 0 # even strength goals
        self.pp_g = 0
        self.sh_g = 0
        self.es_p_a = 0 # even strength primary assits
        self.pp_p_a = 0
        self.sh_p_a = 0
        self.ev_s_a = 0 # even strength secondary assits
        self.pp_s_a = 0
        self.sh_s_a = 0
        self.os_ph_min_pim = 0 # offsetting physical minor penalties (offsetting roughing minors, etc.)
        self.os_ph_maj_pim = 0 # major penalties
        self.os_fig_pim = 0 # fighting penalties
        self.non_os_ph_min_pim = 0 # non-offsetting physical minor penalties (non-offsetting roughing, kneeing, etc.)
        self.non_os_ph_maj_pim = 0 # non-offsetting physical major penalties
        self.av_pim = 0 # avoidable penalties (tripping, high-sticking, holding, etc.)
        
        
    def add_es_g(self):
        self.es_g += 1
        
    def add_pp_g(self):
        self.pp_g += 1
        
    def add_sh_g(self):
        self.sh_g += 1
        
    def add_es_p_a(self):
        self.es_p_a += 1
        
    def add_es_s_a(self):
        self.es_s_a += 1
        
    def add_pp_p_a(self):
        self.pp_p_a += 1
        
    def add_pp_s_a(self):
        self.pp_s_a += 1
        
    def add_sh_p_a(self):
        self.sh_p_a += 1
        
    def add_sh_s_a(self):
        self.sh_s_a += 1
        
    def add_os_ph_min_pim(self, mins):
        self.of_ph_min_pim += mins
        
    def add_os_ph_min_pim(self, mins):
        self.of_ph_maj_pim += mins
    
    def add_os_fig_pim(self, mins):
        self.os_fig_pim += mins
    
    def add_non_os_ph_min_pim(self, mins):
        self.non_os_ph_min_pims += mins
    
    def add_non_os_ph_maj_pim(self, mins):
        self.non_os_ph_maj_pim += mins
        
    def add_av_pim(self, mins):
        self.av_pim += mins

while True:
    league_input = input("Enter a league (OHL, QMJHL, CHL): ")
    league_start_years = input('Please enter a start season (written as "year-year"): ')
    league_end_years = input('Please enter an end season (written as "year-year"): ')
    try:
        scrape(str(league_input), str(league_start_years).split('-')[0], str(league_start_years).split('-')[1], str(league_end_years).split('-')[0], str(league_end_years).split('-')[1])
        break
    except Exception as e:
        print(e)
        print("Please enter valid input")
        