import constants
import requests
import json


def fetch(start_year, end_year, auth_key):
    event_keys = []
    for i in range(start_year, end_year):
        print("fetching matches keys from " + str(i))
        x = requests.get("https://www.thebluealliance.com/api/v3/events/" + str(i) + "/keys",
                         headers={"X-TBA-Auth-Key": auth_key})
        events = x.json()
        event_keys += events

    event_keys_json = {
        "event_keys": event_keys
    }

    with open("event_keys.json", "w") as outfile:
        outfile.write(json.dumps(event_keys_json, indent=4))
    return event_keys
