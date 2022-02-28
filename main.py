import requests
import json


def is_team_in_alliance(alliance, teamKey):
    for team in alliance:
        if teamKey == team:
            return True
    return False


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

fileToGenerate = input("pick file to generate: \n 1. initialize basic data \n 2. Teams with games \n 3.Matches \n")

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
            if is_team_in_alliance(blueAlliance, team['teamKey']):
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
    for i in range(10000):
        print("gets games from team frc" + str(i))
        x = requests.get(address + 'team/frc' + str(i) + '/matches/2018/simple', headers={"X-TBA-Auth-Key": authKey})
        if x.text[0] != '{':
            team = "{\"teamKey\":\"frc" + str(i) + "\", \"average_normalized_score\":0 \"matches\":"
            team += x.text + "}"
            teamsWithGames += team + ","
    teamsWithGames = teamsWithGames[:len(teamsWithGames) - 2] + "]"
    json_object = json.dumps(json.loads(teamsWithGames), indent=4)
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




