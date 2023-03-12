import requests
import json
import constants

matches = []
for i in range(constants.SAMPLE_YEAR_START, constants.SAMPLE_YEAR_END):

    x = requests.get("https://www.thebluealliance.com/api/v3/events/" + str(i),
                     headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
    events = x.json()
    event_keys = []
    for event in events:
        if event["event_type_string"] != "offseason":
            event_keys.append(event["key"])

    for key in event_keys:
        print("fetching matches from: " + key)
        x = requests.get("https://www.thebluealliance.com/api/v3/event/" + key + "/matches/simple",
                         headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
        matches = matches + (x.json())

json_object = json.dumps(matches, indent=4)
with open("all_matches_train.json", "w") as outfile:
    outfile.write(json_object)

for i in range(constants.TEST_YEAR_START, constants.TEST_YEAR_END):

    x = requests.get("https://www.thebluealliance.com/api/v3/events/" + str(i),
                     headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
    events = x.json()
    for event in events:
        if event["event_type_string"] != "offseason":
            event_keys.append(event["key"])

    for key in event_keys:
        print("fetching matches from: " + key)
        x = requests.get("https://www.thebluealliance.com/api/v3/event/" + key + "/matches/simple",
                         headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
        matches = matches + (x.json())

json_object = json.dumps(matches, indent=4)
with open("all_matches_test.json", "w") as outfile:
    outfile.write(json_object)
