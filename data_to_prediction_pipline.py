import json

import requests

import constants
import fetch_events_keys as event_keys_fetcher
import fetch_all_events as event_data_fetcher
import fetch_all_matches as match_fetcher
import fetch_all_team_keys as team_keys_fetcher
import normalize_teams_data as team_data_fetcher
import ai_data_preperation as ai

generate_data = input("do you want to fetch the data? WARINIG: takes a long time (Y/n)\n")
if generate_data != "n":
    event_keys = event_keys_fetcher.fetch(2014, 2023, constants.AUTH_KEY)
    event_data = event_data_fetcher.fetch(event_keys)
    train_matches = match_fetcher.get_matches_by_year_range(2014, 2023, "train_matches")
    test_matches = match_fetcher.get_matches_by_keys_array(["2023isde1", "2023isde2"], "test_matches")
    team_keys_fetcher.fetch(event_data)
    teams_data = team_data_fetcher.fetch_and_normalize()
else:
    f = open("train_matches.json")
    train_matches = json.load(f)

    f = open("teams_normalized_data.json")
    teams_data = json.load(f)

    f = open("test_matches.json")
    test_matches = json.load(f)

x = requests.get("https://www.thebluealliance.com/api/v3/event/2023isde3/matches/simple",
                 headers={"X-TBA-Auth-Key": constants.AUTH_KEY})

test_matches = x.json()
for i in range(len(test_matches)):
    test_matches[i] = match_fetcher.get_data_from_raw_match(test_matches[i])

ai.run(ai.flatten_matches(train_matches, teams_data), ai.get_matches_results(train_matches),
       ai.flatten_matches(test_matches, teams_data), ai.get_matches_results(test_matches),
       ai.get_alliances(test_matches), test_matches)
