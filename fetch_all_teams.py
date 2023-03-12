import requests
import json
import constants

teams = "{"
team_keys = []
for i in range(constants.SAMPLE_YEAR_START, constants.SAMPLE_YEAR_END):

    x = requests.get("https://www.thebluealliance.com/api/v3/events/" + str(i) + "/keys",
                     headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
    keys = x.json()

    for key in keys:
        print("fetching matches from: " + key)
        x = requests.get("https://www.thebluealliance.com/api/v3/event/" + key + "/teams/keys",
                         headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
        team_keys += x.json()

team_keys = list(dict.fromkeys(team_keys))
for team_key in team_keys:
    teams += "\"" + team_key + "\":{\"number_of_matches\":0,\"number_of_events\":0,\"average_playoff_level\":0,\"average_pick\":0,\"win_rate\":0,\"average_rank\":0,\"average_normalized_score\":0},"
teams = teams[:len(teams) - 1] + '}'
json_object = json.dumps(json.loads(teams), indent=4)
with open("all_teams_train.json", "w") as outfile:
    outfile.write(json_object)
