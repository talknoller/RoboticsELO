import requests
import json

teamSample = [1573, 1574, 1576, 1577, 1580, 1657, 1690, 1937, 1942, 1954, 2096, 2212, 2230, 2231, 2630, 2679, 3065,
              3075, 3083, 3211, 3316, 3339, 3388, 3835, 4319, 4320, 4338, 4416, 4586, 4590, 4661, 4744, 5315, 5291,
              5554, 5614, 5635, 5715, 5928, 5951, 5987, 5990, 6104, 6168, 6230, 6738, 6740, 6741, 7039, 7067, 7112,
              7177, 7845, 8175, 8223, 8843]


def is_team_in_alliance(alliance, team_key):
    for team in alliance:
        if team_key == team:
            return True
    return False


def get_team_alliance_color(alliances, team_key):
    for team in alliances["blue"]:
        if team_key == team:
            return "blue"
    return "red"

def get_max_score_from_match_array(matches):
    maxScore = 0
    for match in matches:
        blueScore = match['alliances']['blue']['score']
        redScore = match['alliances']['red']['score']
        if maxScore < redScore:
            maxScore = redScore
        if maxScore < blueScore:
            maxScore = blueScore
    return maxScore


address = "https://www.thebluealliance.com/api/v3/"
authKey = "YzqffOp8lwqUOlvNaAokcvujBrjvcp1xzEKB9HYFnafRri6aB2qbAa1ujRKS4C8r"

fileToGenerate = input("pick file to generate: \n"
                       " 1. initialize basic data \n"
                       " 2. Teams with games \n"
                       " 3.Matches \n"
                       " 4. sent request \n")

if fileToGenerate == '1':
    f = open('matches.json')
    matches = json.load(f)
    f = open('teams.json')
    teams = json.load(f)
    maxScore = get_max_score_from_match_array(matches)
    print(maxScore)

    for team in teams:
        averageScore = 0
        for match in team['games']:
            blueAlliance = match['alliances']['blue']['team_keys']
            if is_team_in_alliance(blueAlliance, team['team_key']):
                averageScore += match['alliances']['blue']['score']
            else:
                averageScore += match['alliances']['red']['score']
        averageScore = averageScore / len(team['games'])
        team['averageNormalizedScore'] = averageScore / maxScore

    json_object = json.dumps(json.loads(teams), indent=4)
    with open("teams.json", "w") as outfile:
        outfile.write(json_object)

elif fileToGenerate == '2':
    teamsWithGames = "["
    for i in teamSample:
        print("gets games from team frc" + str(i))
        x = requests.get(address + 'team/frc' + str(i) + '/matches/2018', headers={"X-TBA-Auth-Key": authKey})
        if x.text[0] != '{':
            team = "{\"team_key\":\"frc" + str(i) + "\", \"average_normalized_score\":0, \"matches\":"
            team += x.text + "}"
            teamsWithGames += team + ","
    teamsWithGames = teamsWithGames[:len(teamsWithGames) - 2] + "}]"
    teams = json.loads(teamsWithGames)
    for team in teams:
        total_score = 0
        counted_matches = 0
        for match in team["matches"]:
            if match["score_breakdown"] is not None:
                counted_matches += 1
                total_score += match["alliances"]["blue"]["score"] - match["score_breakdown"]["blue"]["foulPoints"]
        if counted_matches != 0:
            team["average_normalized_score"] = total_score / counted_matches

    json_object = json.dumps(teams, indent=4)
    with open("teams.json", "w") as outfile:
        outfile.write(json_object)

elif fileToGenerate == '3':
    x = requests.get(address + 'events/2018/keys', headers={"X-TBA-Auth-Key": authKey})
    eventKeys = x.json()
    allMatches = "["
    for event in eventKeys:
        print("gets matches from frc event " + str(event))
        x = requests.get(address + 'event/' + event + '/matches', headers={"X-TBA-Auth-Key": authKey})
        eventMatches = x.text
        eventMatches = eventMatches[1:]
        eventMatches = eventMatches[:len(eventMatches) - 2]

        if eventMatches:
            eventMatches = eventMatches + ","
            allMatches += eventMatches

    allMatches = allMatches[:len(allMatches) - 1] + "]"

    json_object = json.dumps(json.loads(allMatches), indent=4)
    with open("matches.json", "w") as outfile:
        outfile.write(json_object)

elif fileToGenerate == '4':
    x = requests.get('https://www.thebluealliance.com/api/v3/team/frc2231/matches/2018', headers={"X-TBA-Auth-Key": authKey})
    print(x.text)
