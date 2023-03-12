from scipy.special import erfinv
import requests
import constants

alpha = 1.07


def playoff_performance(place):
    if place == 4:
        return 7
    if place == 3:
        return 13
    if place == 2:
        return 20
    if place == 1:
        return 30
    return 0


def rank_points(R, N):
    return int(erfinv((N - 2 * R + 2) / (alpha * N)) * (10 / erfinv(1 / alpha)) + 12.9)


class TeamDpData:
    def __init__(self, key, total_teams, rank, alliance_pick, playoff_score, award_value):
        self.key = key
        self.total_teams = total_teams
        self.rank = rank
        self.alliance_pick = alliance_pick
        self.playoff_rank = playoff_score
        self.award_value = award_value
        self.dp = 0


pass

pick = "y"
teams_array = []
while pick == "y":
    multiplayer = 1
    event_key = input("Enter event key:\n")
    is_event_dcmp = input("is event dcmp:(y\\n)\n")
    if is_event_dcmp == "y":
        multiplayer = 3
    x = requests.get("https://www.thebluealliance.com/api/v3/event/" + event_key + "/teams/statuses",
                     headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
    teams_data = x.json()
    x = requests.get("https://www.thebluealliance.com/api/v3/event/" + event_key + "/awards",
                     headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
    awards = x.json()

    for team in teams_data:
        team_dp_data = TeamDpData(team, teams_data[team]["qual"]["num_teams"], teams_data[team]["qual"]["ranking"]["rank"],
                                  0, 0, 0)
        if teams_array:
            for team_dup in teams_array:
                if team_dup.key == team:
                    team_dp_data.dp = team_dup.dp
                    teams_array.remove(team_dup)
        last_match = teams_data[team]["last_match_key"].split("_")[1]
        if last_match[0] != "s" and last_match[0] != "f":
            team_dp_data.alliance_pick = 0
            team_dp_data.playoff_rank = 0
        else:
            if teams_data[team]["alliance"]["pick"] < 2:
                team_dp_data.alliance_pick = teams_data[team]["alliance"]["number"]
            else:
                team_dp_data.alliance_pick = (17 - teams_data[team]["alliance"]["number"])
            if teams_data[team]["playoff"]["status"] == "won" and last_match[0] == 'f':
                team_dp_data.playoff_rank = 1
            elif last_match[0] == 'f':
                team_dp_data.playoff_rank = 2
            elif last_match[2:4] == "13":
                team_dp_data.playoff_rank = 3
            elif last_match[2:4] == "12":
                team_dp_data.playoff_rank = 4
            else:
                team_dp_data.playoff_rank = 8
            for award in awards:
                if team_dp_data.key == award["recipient_list"][0]["team_key"]:
                    if award["award_type"] == 0:
                        team_dp_data.award_value = 10
                    elif award["award_type"] == 9:
                        team_dp_data.award_value = 8
                    else:
                        team_dp_data.award_value = 5
        team_dp_data.dp += multiplayer * rank_points(team_dp_data.rank, team_dp_data.total_teams)
        team_dp_data.dp += multiplayer * playoff_performance(team_dp_data.playoff_rank)
        team_dp_data.dp += multiplayer * (17 - team_dp_data.alliance_pick)
        team_dp_data.dp += multiplayer * team_dp_data.award_value
        teams_array.append(team_dp_data)
    pick = input("do you want to pick another event? (y\\n)\n")
dp_total = 0
for team in teams_array:
    dp_total += team.dp
    print(team.key + ":" + str(team.dp))
# print("maiden:" + str(dp_total / len(teams_array)))
