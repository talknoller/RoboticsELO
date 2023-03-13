import requests
import json
import constants


def get_data_from_raw_match(raw_match):
    return {
        "key": raw_match["key"],
        "alliances": raw_match["alliances"],
        "winning_alliance": raw_match["winning_alliance"],
        "comp_level": raw_match["comp_level"]
    }


def get_matches_by_year_range(start_year, end_year, file_name):
    matches = []
    for i in range(start_year, end_year):
        x = requests.get("https://www.thebluealliance.com/api/v3/events/" + str(i),
                         headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
        events = x.json()
        event_keys = []
        for event in events:
            if 0 < event["event_type"] < 4:
                event_keys.append(event["key"])

        for key in event_keys:
            print("fetching matches from: " + key)
            x = requests.get("https://www.thebluealliance.com/api/v3/event/" + key + "/matches/simple",
                             headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
            matches = matches + (x.json())
    for i in range(len(matches)):
        matches[i] = get_data_from_raw_match(matches[i])

    json_object = json.dumps(matches, indent=4)
    with open(file_name + ".json", "w") as outfile:
        outfile.write(json_object)
    return matches


def get_matches_by_keys_array(event_keys_array, file_name):
    matches = []
    for key in event_keys_array:
        print("fetching matches from: " + key)
        x = requests.get("https://www.thebluealliance.com/api/v3/event/" + key + "/matches/simple",
                         headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
        matches += x.json()
    for i in range(len(matches)):
        matches[i] = get_data_from_raw_match(matches[i])

    json_object = json.dumps(matches, indent=4)
    with open(file_name + ".json", "w") as outfile:
        outfile.write(json_object)

    return matches



