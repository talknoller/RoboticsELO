import json
import constants
import fetch_events_keys as event_keys_fetcher
import fetch_all_events as event_data_fetcher
import fetch_all_matches as match_fetcher
import fetch_all_team_keys as team_keys_fetcher
import normalize_teams_data as team_data_fetcher
import ai_data_preperation as ai


def show_teams(teams):
    counter = 1
    for team_top in teams:
        current_top_team = team_top
        for team in teams:
            if teams[team] > teams[current_top_team]:
                current_top_team = team
        if teams[current_top_team] != constants.STARTER_ELO:
            print(str(counter) + "." + current_top_team + ":" + str(teams[current_top_team]))
            counter += 1
        teams[current_top_team] = -1


def get_score(match, alliance_color):
    if match["alliances"]["blue"]["score"] == match["alliances"]["red"]["score"]:
        return 0.5
    if alliance_color == match["winning_alliance"]:
        return 1
    return 0


def get_alliance_elo(team_keys, teams):
    total_elo = 0
    for key in team_keys:
        total_elo += teams[key]
    return total_elo


def prediction(elo1, elo2):
    return 1 / (1 + 10 ** ((elo2 - elo1) / 400))


def elo_gained(elo1, elo2, result):
    return constants.K * (result - prediction(elo1, elo2))


action = input("please select your desired calculation:\n"
               "1. get data (WARNING takes a long time)\n"
               "2. Naive Elo\n"
               "3. wighted Elo\n"
               "4. AI\n")

if action == "1":
    event_keys = event_keys_fetcher.fetch(2014, 2023, constants.AUTH_KEY)
    event_data = event_data_fetcher.fetch(event_keys)
    train_matches = match_fetcher.get_matches_by_year_range(2014, 2021, "train_matches")
    test_matches = match_fetcher.get_matches_by_year_range(2022, 2023, "train_matches")
    team_keys_fetcher.fetch(event_data)
    teams_data = team_data_fetcher.fetch_and_normalize()

if action == '2':
    f = open("teams_normalized_data.json")
    teams_json = "{"
    for team in json.load(f):
        teams_json += "\"" + team + "\":" + str(constants.STARTER_ELO) + ","
    teams_json = json.loads(teams_json[:len(teams_json) - 1] + "}")

    f = open("train_matches.json")
    matches = json.load(f)
    f = open('sample_teams.json')
    teams = json.load(f)
    f = open('sample_matches.json')
    sample_matches = json.load(f)
    f = open('test_matches.json')
    test_matches = json.load(f)

    for match in sample_matches:
        red_alliance = match["alliances"]["red"]["team_keys"]
        blue_alliance = match["alliances"]["blue"]["team_keys"]
        red_elo = get_alliance_elo(red_alliance, teams)
        blue_elo = get_alliance_elo(blue_alliance, teams)
        red_elo_change = elo_gained(red_elo, blue_elo, get_score(match, "red"))
        blue_elo_change = elo_gained(blue_elo, red_elo, get_score(match, "blue"))
        for team in red_alliance:
            teams[team] = teams[team] + red_elo_change
        for team in blue_alliance:
            teams[team] = teams[team] + blue_elo_change
    json_object = json.dumps(teams, indent=4)
    with open("teams_with_naive_elo.json", "w") as outfile:
        outfile.write(json_object)

    correct_guesses = 0
    number_off_guesses = 0
    for match in test_matches:
        red_alliance = match["alliances"]["red"]["team_keys"]
        blue_alliance = match["alliances"]["blue"]["team_keys"]
        red_elo = get_alliance_elo(red_alliance, teams)
        blue_elo = get_alliance_elo(blue_alliance, teams)
        if prediction(blue_elo, red_elo) > 0.6:
            number_off_guesses += 1
            if get_score(match, "blue") == 1:
                correct_guesses += 1
        elif prediction(red_elo, blue_elo) > 0.6:
            number_off_guesses += 1
            if get_score(match, "red") == 1:
                correct_guesses += 1
        red_elo_change = elo_gained(red_elo, blue_elo, get_score(match, "red"))
        blue_elo_change = elo_gained(blue_elo, red_elo, get_score(match, "blue"))

        for team in red_alliance:
            teams[team] += red_elo_change
        for team in blue_alliance:
            teams[team] += blue_elo_change

    print("naive Elo accuracy: " + str(correct_guesses / number_off_guesses))
    print(len(test_matches))

elif action == "3":
    f = open("teams_normalized_data.json")
    teams_json = "{"
    for team in json.load(f):
        teams_json += "\"" + team + "\":" + str(constants.STARTER_ELO) + ","
    teams_json = json.loads(teams_json[:len(teams_json) - 1] + "}")

    f = open("train_matches.json")
    matches = json.load(f)
    f = open('sample_teams.json')
    teams = json.load(f)
    f = open('sample_matches.json')
    sample_matches = json.load(f)
    f = open('test_matches.json')
    test_matches = json.load(f)

    for match in sample_matches:
        red_alliance = match["alliances"]["red"]["team_keys"]
        blue_alliance = match["alliances"]["blue"]["team_keys"]
        red_elo = get_alliance_elo(red_alliance, teams)
        blue_elo = get_alliance_elo(blue_alliance, teams)
        red_elo_change = elo_gained(red_elo, blue_elo, get_score(match, "red"))
        blue_elo_change = elo_gained(blue_elo, red_elo, get_score(match, "blue"))
        for team in red_alliance:
            teams[team] = teams[team] + red_elo_change
        for team in blue_alliance:
            teams[team] = teams[team] + blue_elo_change
    json_object = json.dumps(teams, indent=4)
    with open("teams_with_wighted_elo.json", "w") as outfile:
        outfile.write(json_object)

    correct_guesses = 0
    for match in sample_matches:
        red_alliance = match["alliances"]["red"]["team_keys"]
        blue_alliance = match["alliances"]["blue"]["team_keys"]
        red_elo = get_alliance_elo(red_alliance, teams)
        blue_elo = get_alliance_elo(blue_alliance, teams)
        correct_guesses = correct_guesses + abs(get_score(match, "blue") - prediction(blue_elo, red_elo))
        red_elo_change = elo_gained(red_elo, blue_elo, get_score(match, "red"))
        blue_elo_change = elo_gained(blue_elo, red_elo, get_score(match, "blue"))

        for team in red_alliance:
            team_share = teams[team] / (red_elo * 3)
            teams[team] = teams[team] + (red_elo_change * 3 * team_share)
        for team in blue_alliance:
            team_share = teams[team] / (blue_elo * 3)
            teams[team] = teams[team] + (blue_elo_change * 3 * team_share)
    print("elo wighted accuracy: " + str(1 - (correct_guesses / len(sample_matches))))
    print(len(sample_matches))

elif action == "4":
    f = open("train_matches.json")
    train_matches = json.load(f)

    f = open("teams_normalized_data.json")
    teams_data = json.load(f)

    f = open("test_matches.json")
    test_matches = json.load(f)
    print(len(train_matches))
    print(len(test_matches))
    for i in range(len(test_matches)):
        test_matches[i] = match_fetcher.get_data_from_raw_match(test_matches[i])

    ai.run(ai.flatten_matches(train_matches, teams_data), ai.get_matches_results(train_matches),
           ai.flatten_matches(test_matches, teams_data), ai.get_matches_results(test_matches),
           ai.get_alliances(test_matches))

