import json

f = open("all_matches.json")
matches = json.load(f)
f.close()
f = open("all_teams.json")
teams = json.load(f)
f.close()
f = open("max_score_data.json")
max_score_json = json.load(f)
f.close()

for match in matches:
    red_alliance = match["alliances"]["red"]["team_keys"]
    blue_alliance = match["alliances"]["blue"]["team_keys"]
    for team_key in red_alliance:
        try:
            teams[team_key]["average_normalized_score"] += (
                        match["alliances"]["red"]["score"] / max_score_json[match["event_key"][:4]])
        except:
            continue
    for team_key in blue_alliance:
        try:
            teams[team_key]["average_normalized_score"] += (
                        match["alliances"]["blue"]["score"] / max_score_json[match["event_key"][:4]])
        except:
            continue

max_team_matches = 0
max_events = 0
max_pick = 0
for team in teams:
    if teams[team]["number_of_matches"] > max_team_matches:
        max_team_matches = teams[team]["number_of_matches"]

    if teams[team]["number_of_events"] > max_events:
        max_events = teams[team]["number_of_events"]

    if teams[team]["average_pick"] > max_pick:
        max_pick = teams[team]["average_pick"]

for team in teams:
    if teams[team]["number_of_events"] != 0:
        teams[team]["average_playoff_level"] = teams[team]["average_playoff_level"] / teams[team]["number_of_events"]
        teams[team]["average_pick"] = teams[team]["average_pick"] / teams[team]["number_of_events"]
        teams[team]["average_rank"] = teams[team]["average_rank"] / teams[team]["number_of_events"]
    if teams[team]["number_of_matches"] != 0:
        teams[team]["win_rate"] = teams[team]["win_rate"] / teams[team]["number_of_matches"]
        teams[team]["average_normalized_score"] = teams[team]["average_normalized_score"] / teams[team]["number_of_matches"]
    teams[team]["number_of_matches"] = teams[team]["number_of_matches"] / max_team_matches
    teams[team]["number_of_events"] = teams[team]["number_of_events"] / max_events
    teams[team]["average_pick"] = teams[team]["average_pick"] / max_pick


json_object = json.dumps(teams, indent=4)
with open("all_teams_train.json", "w") as outfile:
    outfile.write(json_object)
