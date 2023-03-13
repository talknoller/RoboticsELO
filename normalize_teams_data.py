import json


def fetch_and_normalize():
    f = open("team_keys.json")
    team_keys = json.load(f)["team_keys"]
    f = open("event_data.json")
    events = json.load(f)
    f = open("max_score_data.json")
    max_score_data = json.load(f)

    team_data = "{"
    for team in team_keys:
        team_data += "\"" + team + "\":{\"number_of_matches\":0,\"number_of_events\":0,\"average_playoff_level\":0,\"average_pick\":0,\"win_rate\":0,\"average_rank\":0,\"average_normalized_score\":0}"
        team_data += ","

    team_data = team_data[:len(team_data) - 1] + "}"
    team_data = json.loads(team_data)

    for event in events:
        event_year = event["key"][0:4]
        for team in event["team_statuses"]:
            team_data[team]["number_of_events"] += 1
            team_data[team]["average_playoff_level"] += event["team_statuses"][team]["playoff_level"]
            team_data[team]["average_pick"] += event["team_statuses"][team]["pick_number"]
            team_data[team]["average_rank"] += event["team_statuses"][team]["rank"] / len(event["team_statuses"])

        for match in event["matches"]:
            for team in match["blue"]["team_keys"]:
                team_data[team]["number_of_matches"] += 1
                team_data[team]["average_normalized_score"] += match["blue"]["score"] / max_score_data[event_year]

            for team in match["red"]["team_keys"]:
                team_data[team]["number_of_matches"] += 1
                team_data[team]["average_normalized_score"] += match["red"]["score"] / max_score_data[event_year]

            if match["blue"]["score"] > match["red"]["score"]:
                for team in match["blue"]["team_keys"]:
                    team_data[team]["win_rate"] += 1
                else:
                    for team in match["red"]["team_keys"]:
                        team_data[team]["win_rate"] += 1

    max_matches = 0
    max_events = 0
    for team in team_data:
        if team_data[team]["number_of_matches"] > max_matches:
            max_matches = team_data[team]["number_of_matches"]
        if team_data[team]["number_of_events"] > max_events:
            max_events = team_data[team]["number_of_events"]

    for team in team_data:
        if team_data[team]["number_of_events"] != 0 and team_data[team]["number_of_matches"] != 0:
            team_data[team]["average_playoff_level"] = team_data[team]["average_playoff_level"] / team_data[team]["number_of_events"]
            team_data[team]["average_pick"] = (team_data[team]["average_pick"] / team_data[team]["number_of_events"]) / 25
            team_data[team]["average_rank"] = (team_data[team]["average_rank"] / team_data[team]["number_of_events"])
            team_data[team]["win_rate"] = team_data[team]["win_rate"] / team_data[team]["number_of_matches"]
            team_data[team]["average_normalized_score"] = team_data[team]["average_normalized_score"] / team_data[team]["number_of_matches"]
            team_data[team]["number_of_matches"] = team_data[team]["number_of_matches"] / max_matches
            team_data[team]["number_of_events"] = team_data[team]["number_of_events"] / max_events

    json_object = json.dumps(team_data, indent=4)
    with open("teams_normalized_data.json", "w") as outfile:
        outfile.write(json_object)
    return team_data
