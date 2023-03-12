import json
import constants
import requests

sample_start_year = 2014
sample_end_year = 2021
test_start_year = 2022
test_end_year = 2023
starter_elo = 2000


def playoff_level(team_statues):
    if team_statues is None:
        return 0
    if team_statues["playoff"] is None:
        return 0
    if team_statues["playoff"]["status"] is not None and team_statues["playoff"]["status"] == "won":
        return 1
    if team_statues["playoff"]["level"] is not None:
        if team_statues["playoff"]["level"] == 'qf':
            return 0.25
        if team_statues["playoff"]["level"] == 'sf':
            return 0.5
        if team_statues["playoff"]["level"] == 'f':
            return 0.75
    return 0


def number_of_matches(team_statues):
    if team_statues is None or team_statues["qual"] is None or team_statues["qual"]["ranking"] is None or \
            team_statues["qual"]["ranking"]["matches_played"] is None:
        return 0
    total_events = team_statues["qual"]["ranking"]["matches_played"]
    if team_statues["playoff"] is not None and team_statues["playoff"]["record"] is not None:
        total_events += team_statues["playoff"]["record"]["losses"]
        total_events += team_statues["playoff"]["record"]["ties"]
        total_events += team_statues["playoff"]["record"]["wins"]

    return total_events


def number_of_wins(team_statues):
    if team_statues is None or team_statues["qual"] is None or team_statues["qual"]["ranking"] is None or \
            team_statues["qual"]["ranking"]["record"] is None or team_statues["qual"]["ranking"]["record"][
        "wins"] is None:
        return 0
    total_matches = team_statues["qual"]["ranking"]["record"]["wins"]
    if team_statues["playoff"] is not None and team_statues["playoff"]["record"] is not None:
        total_matches += team_statues["playoff"]["record"]["wins"]

    return total_matches


def alliance_pick(team_statues):
    if team_statues is None:
        return 0
    if team_statues["alliance"] is None:
        return 25
    return team_statues["alliance"]["number"] * (team_statues["alliance"]["pick"] + 1)


def rank_in_event(team_statues):
    if team_statues is None or team_statues["qual"] is None or team_statues["qual"]["ranking"] is None or \
            team_statues["qual"]["ranking"]["rank"] is None:
        return 0

    return team_statues["qual"]["ranking"]["rank"]


f = open("all_matches_train.json")
matches = json.load(f)
f.close()
f = open("all_teams_train.json")
teams = json.load(f)
f.close()

for team in teams:
    teams[team]["number_of_matches"] = 0
    teams[team]["number_of_events"] = 0
    teams[team]["average_playoff_level"] = 0
    teams[team]["average_pick"] = 0
    teams[team]["win_rate"] = 0
    teams[team]["average_rank"] = 0
    teams[team]["average_normalized_score"] = 0

for i in range(constants.SAMPLE_YEAR_START, constants.SAMPLE_YEAR_END):
    x = requests.get("https://www.thebluealliance.com/api/v3/events/" + str(i) + "/keys",
                     headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
    event_keys = x.json()
    for event_key in event_keys:
        print("fetching teams data from: " + event_key)
        x = requests.get("https://www.thebluealliance.com/api/v3/event/" + event_key + "/teams/statuses",
                         headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
        teams_statues = x.json()
        for team in teams_statues:
            if teams[team] is not None:
                teams[team]["number_of_matches"] += number_of_matches(teams_statues[team])
                if number_of_matches(teams_statues[team]) != 0:
                    teams[team]["number_of_events"] += 1
                teams[team]["average_playoff_level"] += playoff_level(teams_statues[team])
                teams[team]["average_pick"] += alliance_pick(teams_statues[team])
                teams[team]["win_rate"] += number_of_wins(teams_statues[team])
                teams[team]["average_rank"] += rank_in_event(teams_statues[team])

json_object = json.dumps(teams, indent=4)
with open("all_teams_train.json", "w") as outfile:
    outfile.write(json_object)
