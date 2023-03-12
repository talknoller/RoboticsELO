import json


def match_result(match):
    if match["winning_alliance"] == 'red':
        return 0
    if match["winning_alliance"] == 'blue':
        return 1
    return 2


def is_match_qual(match):
    if match["comp_level"] == 'qm':
        return 1
    return 0


f = open("all_matches.json")
matches = json.load(f)
f.close()

f = open("all_teams_train.json")
teams = json.load(f)
f.close()

matches_data_array = []
results = []
for match in matches:
    results.append(match_result(match))
    match_data_array = [is_match_qual(match)]
    teams_in_match = match["alliances"]["blue"]["team_keys"] + match["alliances"]["red"]["team_keys"]

    for team in teams_in_match:
        match_data_array.append(teams[team]["number_of_matches"])
        match_data_array.append(teams[team]["number_of_events"])
        match_data_array.append(teams[team]["average_playoff_level"])
        match_data_array.append(teams[team]["average_pick"])
        match_data_array.append(teams[team]["win_rate"])
        match_data_array.append(teams[team]["average_rank"])
        match_data_array.append(teams[team]["average_normalized_score"])
    matches_data_array.append(match_data_array)

print(matches_data_array)
print(results)
