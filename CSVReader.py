import csv
from dateutil.parser import parse

def read(league, start_year1, end_year1, start_year2, end_year2):
    players = {}
    with open(league + "_" + start_year1 + "-" + end_year1 + "_to_" + start_year2 + "-" + end_year2 + "_stats.csv", "r") as league_stats:
        stats_reader = csv.reader(league_stats, delimiter=',')
        for row in stats_reader:
            try:
                player_name = row[2].split(" - ")[0].strip().split("*")[0].strip()
                position = row[0]
                team_name = row[12]
                goals = float(row[4])
                assists = float(row[5])
                shots = float(row[7].split('/')[0])
                pm = float(row[6])
                pim = float(row[8])
                points = goals + assists
                age = float(row[18].strip())
                team_g = float(row[14])
                team_a = float(row[15])
                team_p = team_a + team_g
                team_s = float(row[16])
                team_pim = float(row[17])
                season = row[19]
                # ignore most recent season for draft re-doing purposes
                eligibility = parse('September 15, 1996') >= parse(row[3]) >= parse('January 1, 1994')
            except ValueError:
                print( ValueError )
                print( row )
                continue
            if players.get(player_name+season) is None:
                players[player_name+season] = Player(player_name, season, position, eligibility)
            players.get(player_name+season).addStats(team_name, points, goals, assists, shots, pm, pim, age, team_g, team_a, team_p, team_s, team_pim)

        with open(league + "_" + start_year1 + "-" + end_year1 + "_to_" + start_year2 + "-" + end_year2 + "_per_team.csv", "w") as stats_file:
            wr = csv.writer(stats_file)
            wr.writerow(["Player Name", "Position", "Team", "Season", "Games Played", "Goals Per Team Goals %", "Assists Per Team Assists %", "Points Per Team Points %", "Total Points", "Total Team Points", "Player Age", "Draft Eligibility"])
            for player in players.values():
                for stat in player.pPtPT():
                    wr.writerow(stat)


class Player:

    def __init__(self, name, season, position, eligibility):
        self.name = name
        self.season = season
        self.position = position
        self.eligibility = eligibility
        self.p_per_team = {}
        self.g_per_team = {}
        self.a_per_team = {}
        self.s_per_team = {}
        self.pm_per_team = {}
        self.pim_per_team = {}
        self.gp_per_team = {}
        self.team_p = {}
        self.team_g = {}
        self.team_a = {}
        self.team_s = {}
        self.team_pim = {}
        self.age_per_team = {}

    def pPtPT(self):
        team_stats = []
        for key in self.p_per_team.keys():
            try:
                stats = []
                stats.append(self.name)
                stats.append(self.position)
                stats.append(key)
                stats.append(self.season)
                stats.append(self.gp_per_team.get(key))
                stats.append(self.g_per_team.get(key) / self.team_p.get(key))
                stats.append(self.a_per_team.get(key) / self.team_p.get(key))
                stats.append(self.p_per_team.get(key) / self.team_p.get(key))
                stats.append(self.p_per_team.get(key))
                stats.append(self.team_p.get(key))
                stats.append(self.age_per_team.get(key))
                team_stats.append(stats)
                stats.append(self.eligibility)
            except ZeroDivisionError:
                print(0)
        return team_stats

    def addStats(self, team, points, goals, assists, shots, pm, pim, age, team_p, team_g, team_a, team_s, team_pim):
        if self.p_per_team.get(team) is None:
            self.p_per_team[team] = points
        else:
            self.p_per_team[team] += points

        if self.g_per_team.get(team) is None:
            self.g_per_team[team] = goals
        else:
            self.g_per_team[team] += goals

        if self.a_per_team.get(team) is None:
            self.a_per_team[team] = assists
        else:
            self.a_per_team[team] += assists

        if self.s_per_team.get(team) is None:
            self.s_per_team[team] = shots
        else:
            self.s_per_team[team] += shots

        if self.pm_per_team.get(team) is None:
            self.pm_per_team[team] = pm
        else:
            self.pm_per_team[team] += pm

        if self.pim_per_team.get(team) is None:
            self.pim_per_team[team] = pim
        else:
            self.pim_per_team[team] += pim

        if self.gp_per_team.get(team) is None:
            self.gp_per_team[team] = 1
        else:
            self.gp_per_team[team] += 1

        if self.team_p.get(team) is None:
            self.team_p[team] = team_p
        else:
            self.team_p[team] += team_p

        if self.team_g.get(team) is None:
            self.team_g[team] = team_g
        else:
            self.team_g[team] += team_g

        if self.team_a.get(team) is None:
            self.team_a[team] = team_a
        else:
            self.team_a[team] += team_a

        if self.team_s.get(team) is None:
            self.team_s[team] = team_s
        else:
            self.team_s[team] += team_s

        if self.team_pim.get(team) is None:
            self.team_pim[team] = team_pim
        else:
            self.team_pim[team] += team_pim

        if self.age_per_team.get(team) is None:
            self.age_per_team[team] = age
        else:
            self.age_per_team[team] = (age + self.age_per_team[team])/2

read("WHL", "2007", "2008", "2017", "2018")
read("OHL", "2007", "2008", "2017", "2018")
read("QMJHL", "2007", "2008", "2017", "2018")
