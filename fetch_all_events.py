import requests
import json
import constants


def get_pick_from_alliance(alliance, pick_order):
    if pick_order == 0:
        return 1 + (alliance - 1) * 2
    if pick_order == 1:
        return alliance * 2
    return 16 + (9 - alliance)


def playoff_string_to_level(playoff_string):
    if playoff_string == "qf":
        return 1 / 8
    if playoff_string == "sf":
        return 1 / 4
    if playoff_string == "f":
        return 1 / 2
    if playoff_string == "w":
        return 1


def is_event_relevant(event_simple):
    return event_simple["event_type"] > 4 or event_simple["event_type"] < 0


def fetch(event_keys):
    all_events = []

    for event_key in event_keys:
        event_matches = []
        print("check if " + event_key + " is relevant event")
        x = requests.get("https://www.thebluealliance.com/api/v3/event/" + event_key + "/simple",
                         headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
        event_simple = x.json()
        if is_event_relevant(event_simple):
            print(event_key + " is not relevant")
            continue

        print("fetching matches from " + event_key)
        x = requests.get("https://www.thebluealliance.com/api/v3/event/" + event_key + "/matches/simple",
                         headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
        event_matches_raw = x.json()
        for match in event_matches_raw:
            event_matches.append({
                "blue": {
                    "team_keys": match["alliances"]["blue"]["team_keys"],
                    "score": match["alliances"]["blue"]["score"]
                },
                "red": {
                    "team_keys": match["alliances"]["red"]["team_keys"],
                    "score": match["alliances"]["red"]["score"]
                }
            })
        print("fetching team keys from " + event_key)
        x = requests.get("https://www.thebluealliance.com/api/v3/event/" + event_key + "/teams/keys",
                         headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
        team_keys = x.json()
        print("fetching team statuses from " + event_key)
        x = requests.get("https://www.thebluealliance.com/api/v3/event/" + event_key + "/teams/statuses",
                         headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
        event_status_raw_json = x.json()

        team_statuses_simple = "{"
        for team_status in event_status_raw_json:
            if event_status_raw_json[team_status] is None or event_status_raw_json[team_status]["qual"] is None:
                continue
            team_statuses_simple += "\"" + team_status + "\":{"
            team_statuses_simple += "\"rank\":" + str(event_status_raw_json[team_status]["qual"]["ranking"]["rank"]) + ","
            if event_status_raw_json[team_status]["alliance"] is not None:
                team_statuses_simple += "\"pick_number\":" + str(
                    get_pick_from_alliance(event_status_raw_json[team_status]["alliance"]["number"],
                                           event_status_raw_json[team_status]["alliance"]["pick"])) + ","
                team_statuses_simple += "\"playoff_level\":" + str(
                    playoff_string_to_level(event_status_raw_json[team_status]["playoff"]["level"])) + "},"
            else:
                team_statuses_simple += "\"pick_number\":25,\"playoff_level\":0},"
        team_statuses_simple = team_statuses_simple[:len(team_statuses_simple) - 1] + "}"
        if team_statuses_simple is not None and team_statuses_simple != "}" and team_keys and team_keys is not None:
            try:
                event_data = {
                    "key": event_key,
                    "team_keys": team_keys,
                    "team_statuses": json.loads(team_statuses_simple),
                    "matches": event_matches
                }
                all_events.append(event_data)
            except:
                continue
    json_object = json.dumps(all_events, indent=4)
    with open("event_data.json", "w") as outfile:
        outfile.write(json_object)
    return all_events
