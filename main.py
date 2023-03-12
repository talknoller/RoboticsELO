import requests
import json
import random
import sys
import constants

starter_elo = 2000

sys.setrecursionlimit(3000)

k = 72


def get_event_average_alliance_score(event_key):
    print("getting matches from " + event_key)
    x = requests.get("https://www.thebluealliance.com/api/v3/event/" + event_key + "/matches",
                     headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
    matches = x.json()
    average_score = 0
    for match in matches:
        average_score += int(match["alliances"]["red"]["score"])
        average_score += int(match["alliances"]["blue"]["score"])
    if average_score == 0:
        return 0
    average_score = average_score / (len(matches) * 2)
    return average_score


def get_team_alliance_color(team_key, match):
    blue_alliance = match["alliances"]["blue"]["team_keys"]
    red_alliance = match["alliances"]["red"]["team_keys"]
    for key in blue_alliance:
        if key == team_key:
            return "blue"

    for key in red_alliance:
        if key == team_key:
            return "red"
    return None


def did_blue_win(match):
    return match["alliances"]["blue"]["score"] > match["alliances"]["red"]["score"]


def get_score(match, alliance):
    if match["alliances"]["blue"]["score"] == match["alliances"]["red"]["score"]:
        return 0.5

    if did_blue_win(match):
        if alliance == "blue":
            return 1
        return 0

    if alliance == "red":
        return 1
    return 0


def get_alliance_total_elo(team_keys, teams):
    total_elo = 0
    for key in team_keys:
        try:
            total_elo += teams[key]["elo"]
        except:
            total_elo += teams[key]
    return total_elo


def get_alliance_elo(team_keys, teams):
    return get_alliance_total_elo(team_keys, teams) / 3


def prediction(elo1, elo2):
    return 1 / (1 + 10 ** ((elo2 - elo1) / 400))


def elo_gained(elo1, elo2, result):
    return k * (result - prediction(elo1, elo2))


def did_match_happened_first(match1, match2):
    return match1["time"] < match2["time"]


def partition_match_time(array, low, high):
    pivot = array[high]
    i = low - 1
    for j in range(low, high):
        if did_match_happened_first(array[j], pivot):
            i = i + 1
            (array[i], array[j]) = (array[j], array[i])
    (array[i + 1], array[high]) = (array[high], array[i + 1])
    return i + 1


def quick_sort_match_time(array, low, high):
    if low < high:
        pi = partition_match_time(array, low, high)
        quick_sort_match_time(array, low, pi - 1)
        quick_sort_match_time(array, pi + 1, high)


def partition_teams_elo(array, low, high):
    pivot = array[high]
    i = low - 1
    for j in range(low, high):
        if array[j] > pivot:
            i = i + 1
            (array[i], array[j]) = (array[j], array[i])
    (array[i + 1], array[high]) = (array[high], array[i + 1])
    return i + 1


def quick_sort_teams_elo(array, low, high):
    if low < high:
        pi = partition_teams_elo(array, low, high)
        quick_sort_teams_elo(array, low, pi - 1)
        quick_sort_teams_elo(array, pi + 1, high)


fileToGenerate = input("1. get sample and test matches. reset teams' elo \n"
                       "2. reset teams elo\n"
                       "3. calculate teams elo \n"
                       "4. calculate prediction without changing elo \n"
                       "5. calculate wighted elo \n"
                       "6. calculate prediction with changing elo\n"
                       "7. calculate prediction with changing elo wighted\n"
                       "8. show teams elo \n"
                       "9. get events with average score \n"
                       "10. normalize events' score \n"
                       "11. get teams data with normalized elo \n"
                       "12. calculate wighted elo from normalized position \n"
                       "13. calculate prediction without changing elo \n")

if fileToGenerate == '1':
    sample_events = []
    test_events = []
    for i in range(constants.SAMPLE_YEAR_START, constants.SAMPLE_YEAR_END):
        print("fetching data from year " + str(i))
        x = requests.get("https://www.thebluealliance.com/api/v3/events/" + str(i),
                         headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
        events = x.json()
        for event in events:
            if event["event_type_string"] == 'Championship Finals' or event[
                "event_type_string"] == 'Championship Division':
                sample_events.append(event["key"])

    for i in range(constants.TEST_YEAR_START, constants.TEST_YEAR_END):
        print("fetching data from year " + str(i))
        x = requests.get("https://www.thebluealliance.com/api/v3/events/" + str(i),
                         headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
        events = x.json()
        for event in events:
            if event["event_type_string"] == 'Championship Finals' or event[
                "event_type_string"] == 'Championship Division':
                test_events.append(event["key"])

    teams_array = []
    for event in sample_events:
        print("fetching teams from " + event)
        x = requests.get("https://www.thebluealliance.com/api/v3/event/" + event + "/teams/simple",
                         headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
        event_teams = x.json()
        for team in event_teams:
            teams_array.append(team["key"])
    teams_array = list(dict.fromkeys(teams_array))

    for event in test_events:
        print("fetching team's data from " + event)
        x = requests.get("https://www.thebluealliance.com/api/v3/event/" + event + "/teams/simple",
                         headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
        event_teams = x.json()
        for team in event_teams:
            teams_array.append(team["key"])
    teams_array = list(dict.fromkeys(teams_array))

    sample_matches = []
    print("fetching sample events:")
    for i in sample_events:
        print("fetching matches from " + i)
        x = requests.get("https://www.thebluealliance.com/api/v3/event/" + i + "/matches",
                         headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
        eventMatches = x.json()
        sample_matches = sample_matches + eventMatches

    quick_sort_match_time(sample_matches, 0, len(sample_matches) - 1)
    json_object = json.dumps(sample_matches, indent=4)
    with open("sample_matches.json", "w") as outfile:
        outfile.write(json_object)
    print("finished fetching sample events, fetching test events:")

    test_matches = []
    for i in test_events:
        print("fetching matches from " + i)
        x = requests.get("https://www.thebluealliance.com/api/v3/event/" + i + "/matches",
                         headers={"X-TBA-Auth-Key": constants.AUTH_KEY})

        eventMatches = x.json()
        test_matches = test_matches + eventMatches
    quick_sort_match_time(test_matches, 0, len(test_matches) - 1)
    json_object = json.dumps(test_matches, indent=4)
    with open("test_matches.json", "w") as outfile:
        outfile.write(json_object)
    teams = "{"
    for team in teams_array:
        teams = teams + ("\"" + str(team) + "\":" + str(starter_elo) + ",")
    teams = teams[:len(teams) - 1] + "}"
    json_object = json.dumps(json.loads(teams), indent=4)
    with open("sample_teams.json", "w") as outfile:
        outfile.write(json_object)

elif fileToGenerate == '2':
    f = open("sample_teams.json")
    teams = json.load(f)
    for team in teams:
        teams[team] = starter_elo
    json_object = json.dumps(teams, indent=4)
    with open("sample_teams.json", "w") as outfile:
        outfile.write(json_object)

elif fileToGenerate == '3':
    f = open('sample_teams.json')
    teams = json.load(f)
    f = open('sample_matches.json')
    sample_matches = json.load(f)
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
    with open("sample_teams.json", "w") as outfile:
        outfile.write(json_object)

elif fileToGenerate == '4':
    f = open('sample_teams.json')
    teams = json.load(f)
    f = open('test_matches.json')
    sample_matches = json.load(f)
    total_error = 0
    random_prediction_error = 0
    for match in sample_matches:
        red_alliance = match["alliances"]["red"]["team_keys"]
        blue_alliance = match["alliances"]["blue"]["team_keys"]
        red_elo = get_alliance_elo(red_alliance, teams)
        blue_elo = get_alliance_elo(blue_alliance, teams)
        total_error = total_error + abs(get_score(match, "blue") - prediction(blue_elo, red_elo))
        random_prediction_error = random_prediction_error + abs(get_score(match, "blue") - random.randint(0, 1))
    print("elo prediction: " + str(total_error / len(sample_matches)))
    print("random prediction: " + str(random_prediction_error / len(sample_matches)))
    print(len(sample_matches))

elif fileToGenerate == '5':
    f = open('sample_teams.json')
    teams = json.load(f)
    f = open('sample_matches.json')
    sample_matches = json.load(f)
    for match in sample_matches:
        red_alliance = match["alliances"]["red"]["team_keys"]
        blue_alliance = match["alliances"]["blue"]["team_keys"]
        red_elo = get_alliance_elo(red_alliance, teams)
        blue_elo = get_alliance_elo(blue_alliance, teams)
        red_elo_change = elo_gained(red_elo, blue_elo, get_score(match, "red"))
        blue_elo_change = elo_gained(blue_elo, red_elo, get_score(match, "blue"))

        for team in red_alliance:
            team_share = teams[team] / (red_elo * 3)
            teams[team] = teams[team] + (red_elo_change * 3 * team_share)
        for team in blue_alliance:
            team_share = teams[team] / (blue_elo * 3)
            teams[team] = teams[team] + (blue_elo_change * 3 * team_share)
    json_object = json.dumps(teams, indent=4)
    with open("sample_teams.json", "w") as outfile:
        outfile.write(json_object)

elif fileToGenerate == '6':
    f = open('sample_teams.json')
    teams = json.load(f)
    f = open('test_matches.json')
    sample_matches = json.load(f)
    total_error = 0
    random_prediction_error = 0
    for match in sample_matches:
        red_alliance = match["alliances"]["red"]["team_keys"]
        blue_alliance = match["alliances"]["blue"]["team_keys"]
        red_elo = get_alliance_elo(red_alliance, teams)
        blue_elo = get_alliance_elo(blue_alliance, teams)
        total_error = total_error + abs(get_score(match, "blue") - prediction(blue_elo, red_elo))
        random_prediction_error = random_prediction_error + abs(get_score(match, "blue") - random.randint(0, 1))
        red_elo_change = elo_gained(red_elo, blue_elo, get_score(match, "red"))
        blue_elo_change = elo_gained(blue_elo, red_elo, get_score(match, "blue"))

        for team in red_alliance:
            team_share = teams[team] / (red_elo * 3)
            teams[team] = teams[team] + (red_elo_change * 3 * team_share)
        for team in blue_alliance:
            team_share = teams[team] / (blue_elo * 3)
            teams[team] = teams[team] + (blue_elo_change * 3 * team_share)
    print("elo prediction: " + str(total_error / len(sample_matches)))
    print("random prediction: " + str(random_prediction_error / len(sample_matches)))
    print(len(sample_matches))


elif fileToGenerate == '7':
    f = open('sample_teams.json')
    teams = json.load(f)
    f = open('test_matches.json')
    sample_matches = json.load(f)
    total_error = 0
    random_prediction_error = 0
    for match in sample_matches:
        red_alliance = match["alliances"]["red"]["team_keys"]
        blue_alliance = match["alliances"]["blue"]["team_keys"]
        red_elo = get_alliance_elo(red_alliance, teams)
        blue_elo = get_alliance_elo(blue_alliance, teams)
        total_error = total_error + abs(get_score(match, "blue") - prediction(blue_elo, red_elo))
        random_prediction_error = random_prediction_error + abs(get_score(match, "blue") - random.randint(0, 1))
        red_elo_change = elo_gained(red_elo, blue_elo, get_score(match, "red"))
        blue_elo_change = elo_gained(blue_elo, red_elo, get_score(match, "blue"))
        for team in red_alliance:
            team_share = teams[team] / (red_elo * 3)
            teams[team] = teams[team] + (red_elo_change * 3 * team_share)
        for team in blue_alliance:
            team_share = teams[team] / (blue_elo * 3)
            teams[team] = teams[team] + (blue_elo_change * 3 * team_share)
    json_object = json.dumps(teams, indent=4)
    with open("sample_teams.json", "w") as outfile:
        outfile.write(json_object)
    print("elo prediction: " + str(total_error / len(sample_matches)))
    print("random prediction: " + str(random_prediction_error / len(sample_matches)))
    print(len(sample_matches))

elif fileToGenerate == '8':
    f = open('sample_teams.json')
    teams = json.load(f)
    counter = 1
    for team_top in teams:
        current_top_team = team_top
        for team in teams:
            if teams[team] > teams[current_top_team]:
                current_top_team = team
        if teams[current_top_team] != starter_elo:
            print(str(counter) + "." + current_top_team + ":" + str(teams[current_top_team]))
            counter += 1
        teams[current_top_team] = -1

elif fileToGenerate == '9':
    all_events = "{"
    for i in range(constants.SAMPLE_YEAR_START, constants.SAMPLE_YEAR_END):
        x = requests.get("https://www.thebluealliance.com/api/v3/events/" + str(i) + "/simple",
                         headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
        events_raw = x.json()

        events = []
        for event in events_raw:
            if event["event_type"] == 0 or event["event_type"] == 1 or event["event_type"] == 2:
                events.append(event)

        all_events += "\"" + str(i) + "\":"
        single_year_events = "{"
        for event in events:
            single_year_events += "\"" + event["key"] + "\":" + str(
                get_event_average_alliance_score(event["key"])) + ","
        single_year_events = single_year_events[:len(single_year_events) - 1] + "},"
        all_events += single_year_events
    all_events = all_events[:len(all_events) - 1] + "}"
    json_object = json.dumps(json.loads(all_events), indent=4)
    with open("sample_events.json", "w") as outfile:
        outfile.write(json_object)

elif fileToGenerate == '10':
    f = open('sample_events.json')
    events_score = json.load(f)
    for i in range(constants.SAMPLE_YEAR_START, constants.SAMPLE_YEAR_END):
        max_event_score = 0
        for event in events_score[str(i)]:
            if events_score[str(i)][event] > max_event_score:
                max_event_score = events_score[str(i)][event]

        for event in events_score[str(i)]:
            events_score[str(i)][event] = events_score[str(i)][event] / max_event_score

    json_object = json.dumps(events_score, indent=4)
    with open("sample_events.json", "w") as outfile:
        outfile.write(json_object)


elif fileToGenerate == '11':
    teams_data = "{"
    f = open('sample_teams.json')
    teams_elo = json.load(f)
    f = open('sample_events.json')
    events_data = json.load(f)
    for team in teams_elo:
        teams_data += "\"" + team + \
                      "\":{\"number_of_events\":0,\"average_normalized_score\":0,\"elo\":" + str(starter_elo) + "},"
    teams_data = teams_data[:len(teams_data) - 1] + "}"
    teams_data = json.loads(teams_data)

    for i in range(constants.SAMPLE_YEAR_START, constants.SAMPLE_YEAR_END):
        x = requests.get("https://www.thebluealliance.com/api/v3/events/" + str(i) + "/simple",
                         headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
        events = x.json()
        events_keys = []
        for event in events:
            if event["event_type"] == 0 or event["event_type"] == 1 or event["event_type"] == 2:
                events_keys.append(event["key"])
        for key in events_keys:
            print("get data from " + key)
            x = requests.get("https://www.thebluealliance.com/api/v3/event/" + key + "/teams/keys",
                             headers={"X-TBA-Auth-Key": constants.AUTH_KEY})
            teams_in_event = x.json()
            event_normalized_score = events_data[str(i)][key]
            for team in teams_in_event:
                try:
                    teams_data[team]["number_of_events"] = teams_data[team]["number_of_events"] + 1
                    teams_data[team]["average_normalized_score"] += event_normalized_score
                except:
                    continue

    for team in teams_data:
        if teams_data[team]["number_of_events"] != 0:
            teams_data[team]["average_normalized_score"] = teams_data[team]["average_normalized_score"] / \
                                                           teams_data[team]["number_of_events"]
            teams_data[team]["elo"] = (starter_elo / 2) + (starter_elo * teams_data[team]["average_normalized_score"])

    json_object = json.dumps(teams_data, indent=4)
    with open("sample_teams_data.json", "w") as outfile:
        outfile.write(json_object)

elif fileToGenerate == '12':
    f = open('sample_teams_data.json')
    teams = json.load(f)
    f = open('sample_matches.json')
    sample_matches = json.load(f)

    for match in sample_matches:
        red_alliance = match["alliances"]["red"]["team_keys"]
        blue_alliance = match["alliances"]["blue"]["team_keys"]
        red_elo = get_alliance_elo(red_alliance, teams)
        blue_elo = get_alliance_elo(blue_alliance, teams)
        red_elo_change = elo_gained(red_elo, blue_elo, get_score(match, "red"))
        blue_elo_change = elo_gained(blue_elo, red_elo, get_score(match, "blue"))

        for team in red_alliance:
            team_share = teams[team]["elo"] / (red_elo * 3)
            teams[team]["elo"] = teams[team]["elo"] + (red_elo_change * 3 * team_share)
        for team in blue_alliance:
            team_share = teams[team]["elo"] / (blue_elo * 3)
            teams[team]["elo"] = teams[team]["elo"] + (blue_elo_change * 3 * team_share)
    json_object = json.dumps(teams, indent=4)
    with open("sample_teams_data.json", "w") as outfile:
        outfile.write(json_object)

elif fileToGenerate == '13':
    f = open('sample_teams_data.json')
    teams = json.load(f)
    f = open('test_matches.json')
    sample_matches = json.load(f)
    total_error = 0
    random_prediction_error = 0
    for match in sample_matches:
        red_alliance = match["alliances"]["red"]["team_keys"]
        blue_alliance = match["alliances"]["blue"]["team_keys"]
        red_elo = get_alliance_elo(red_alliance, teams)
        blue_elo = get_alliance_elo(blue_alliance, teams)
        total_error = total_error + abs(get_score(match, "blue") - prediction(blue_elo, red_elo))
        random_prediction_error = random_prediction_error + abs(get_score(match, "blue") - random.randint(0, 1))
    print("elo prediction: " + str(total_error / len(sample_matches)))
    print("random prediction: " + str(random_prediction_error / len(sample_matches)))
    print(len(sample_matches))

elif fileToGenerate == '14':
    f = open('sample_teams_data.json')
    teams = json.load(f)
    f = open('test_matches.json')
    sample_matches = json.load(f)
    total_error = 0
    random_prediction_error = 0
    for match in sample_matches:
        red_alliance = match["alliances"]["red"]["team_keys"]
        blue_alliance = match["alliances"]["blue"]["team_keys"]
        red_elo = get_alliance_elo(red_alliance, teams)
        blue_elo = get_alliance_elo(blue_alliance, teams)
        total_error = total_error + abs(get_score(match, "blue") - prediction(blue_elo, red_elo))
        random_prediction_error = random_prediction_error + abs(get_score(match, "blue") - random.randint(0, 1))
        red_elo_change = elo_gained(red_elo, blue_elo, get_score(match, "red"))
        blue_elo_change = elo_gained(blue_elo, red_elo, get_score(match, "blue"))
        for team in red_alliance:
            team_share = teams[team]["elo"] / (red_elo * 3)
            teams[team]["elo"] = teams[team]["elo"] + (red_elo_change * 3 * team_share)
        for team in blue_alliance:
            team_share = teams[team]["elo"] / (blue_elo * 3)
            teams[team]["elo"] = teams[team]["elo"] + (blue_elo_change * 3 * team_share)
    json_object = json.dumps(teams, indent=4)
    with open("sample_teams_data.json", "w") as outfile:
        outfile.write(json_object)
    print("elo prediction: " + str(total_error / len(sample_matches)))
    print("random prediction: " + str(random_prediction_error / len(sample_matches)))
    print(len(sample_matches))

elif fileToGenerate == '15':
    f = open('sample_teams_data.json')
    teams = json.load(f)
    counter = 1
    for team_top in teams:
        current_top_team = team_top
        for team in teams:
            if type(teams[team]) != int and type(teams[current_top_team]) != int:
                if teams[team]["elo"] > teams[current_top_team]["elo"]:
                    current_top_team = team
        if type(teams[current_top_team]) != int:
            if teams[current_top_team]["elo"] != starter_elo:
                print(str(counter) + "." + current_top_team + ":" + str(teams[current_top_team]))
                counter += 1
        teams[current_top_team] = -1

