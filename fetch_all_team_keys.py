import json


def fetch(events):
    teams = []
    for event in events:
        teams += event["team_keys"]
    teams = list(dict.fromkeys(teams))
    teams = {
        "team_keys": teams
    }
    json_object = json.dumps(teams, indent=4)
    with open("team_keys.json", "w") as outfile:
        outfile.write(json_object)
