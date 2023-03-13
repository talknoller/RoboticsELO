import json

import numpy as np
from tensorflow import keras


def get_match_result(match):
    if match["winning_alliance"] == 'red':
        return 0
    if match["winning_alliance"] == 'blue':
        return 1
    return 2


def is_match_qual(comp_level_string):
    if comp_level_string == 'qm':
        return 1
    return 0


def flatten_team(team_data):
    return [team_data["number_of_matches"], team_data["number_of_events"],
            team_data["average_playoff_level"], team_data["average_pick"],
            team_data["win_rate"], team_data["average_rank"],
            team_data["average_normalized_score"]]


def get_matches_results(matches):
    match_results = []
    for match in matches:
        match_results.append(get_match_result(match))
    return match_results


def get_alliances(matches):
    match_alliances = []

    for match in matches:
        does_team_exist = True
        blue_teams = []
        red_teams = []
        for team in match["alliances"]["blue"]["team_keys"]:
            try:
                blue_teams.append(team)
            except:
                does_team_exist = False
        for team in match["alliances"]["red"]["team_keys"]:
            try:
                red_teams.append(team)
            except:
                does_team_exist = False
        if does_team_exist:
            match_alliances.append([red_teams, blue_teams])
    return match_alliances


def flatten_matches(matches, teams_data):
    flattened_train_matches = []
    match_train_results = []
    for match in matches:
        does_team_exist = True
        match_train_results.append(get_match_result(match))
        match_data = []
        for team in match["alliances"]["blue"]["team_keys"]:
            try:
                match_data += flatten_team(teams_data[team])
            except:
                does_team_exist = False
        for team in match["alliances"]["red"]["team_keys"]:
            try:
                match_data += flatten_team(teams_data[team])
            except:
                does_team_exist = False
        if does_team_exist:
            match_data.append(is_match_qual(match["comp_level"]))
            flattened_train_matches.append(match_data)
    return flattened_train_matches


def run(flattened_train_matches, match_train_results,
        flattened_test_matches, match_test_results,
        match_test_alliances):
    class_names = ['red win', 'blue win', 'tie']

    model = keras.Sequential([
        keras.layers.Flatten(input_shape=(43,)),
        keras.layers.Dense(16, activation="relu"),
        keras.layers.Dense(3, activation="softmax")
    ])

    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

    model.fit(flattened_train_matches, match_train_results, epochs=5)

    prediction = model.predict(flattened_test_matches)
    correct_guesses = 0
    guesses = 0
    for i in range(len(prediction)):
        if np.amax(prediction[i]) > 0.65:
            guesses += 1
            if match_test_results[i] == np.argmax(prediction[i]):
                correct_guesses += 1

        print("red alliance:")
        print(match_test_alliances[i][0])
        print("blue alliance:")
        print(match_test_alliances[i][1])
        print("prediction:")
        print("red win: " + str(prediction[i][0]))
        print("blue win: " + str(prediction[i][1]))
        print("tie: " + str(prediction[i][2]))
        print("actual result:" + class_names[match_test_results[i]])
    print(correct_guesses / guesses)
