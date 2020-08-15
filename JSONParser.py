import ExerciseDetailsParserJSON
import os
import sys
import pickle
import pprint
with open(os.path.join('dictionary', 'dictionary.pk1'), 'rb') as input:
    sys.setrecursionlimit(10000)
    organized = pickle.load(input)

# pprint.pprint(organized["Neck"])

# failed at Writing: Chest,PectoralSternal,cable


def write_to_file(group_key, muscle_key, type_key):
    hrefs = organized[group_key][muscle_key][type_key]
    path = os.path.join(
        'data', group_key, muscle_key, type_key, "details.json")
    file = open(path, "w+")
    file.write('{"'+type_key+'":[')
    for index, href in enumerate(hrefs):
        try:
            # print(href)
            # pprint.pprint(ExerciseDetailsParserJSON.parse(href['href']))
            if index == len(hrefs)-1:
                file.write(ExerciseDetailsParserJSON.parse(
                    href['href'], index))
            else:
                file.write(ExerciseDetailsParserJSON.parse(
                    href['href'], index) + ',')
        except ValueError as err:
            print(err.args)
    file.write(']}')


group_index_start = 1
muscle_index_start = 1
type_index_start = 3
muscle_group_keys = organized.keys()
for group_index, group_key in enumerate(muscle_group_keys):
    if group_index < group_index_start:
        continue
    muscle_keys = organized[group_key].keys()
    for muscle_index, muscle_key in enumerate(muscle_keys):
        if muscle_index < muscle_index_start and group_index_start == group_index:
            continue
        type_keys = organized[group_key][muscle_key].keys()
        for type_index, type_key in enumerate(type_keys):
            if type_index < type_index_start and muscle_index == muscle_index_start and group_index_start == group_index:
                continue
            print("Writing JSON: " + group_key +
                  "," + muscle_key + "," + type_key)
            try:
                write_to_file(group_key, muscle_key, type_key)
            except Exception as e:
                file = open("json_error.log", "a")
                file.write(group_index + "," + muscle_index +
                           "," + type_index + '\n')
                file.close()
                print(e)


# organized["Neck"]["Sternocleidomastoid"].keys()
# for key in keys:
#     hrefs = organized["Neck"]["Sternocleidomastoid"][key]
#     path = os.path.join(
#         'data', "Neck", "Sternocleidomastoid", key, "details.json")
#     file = open(path, "w+")
#     file.write('{"'+key+'":[')
#     for index, href in enumerate(hrefs):
#         try:
#             # print(href)
#             # pprint.pprint(ExerciseDetailsParserJSON.parse(href['href']))
#             if index == len(hrefs)-1:
#                 file.write(ExerciseDetailsParserJSON.parse(
#                     href['href'], index))
#             else:
#                 file.write(ExerciseDetailsParserJSON.parse(
#                     href['href'], index) + ',')
#         except ValueError as err:
#             print(err.args)
#     file.write(']}')

# individual.parse_webpage("WeightExercises", "Obliques",
#                          "BWAngledSideBridge")
# individual.parse_webpage("Stretches", "Brachioradialis",
#                          "Standing")
# individual.parse_webpage("WeightExercises", "BackGeneral",
#                          "BWSupineRow")
# individual.parse_webpage("WeightExercises", "BackGeneral", "BBBentOverRow")
# individual.parse_webpage(
#     "WeightExercises", "BackGeneral", "CamberedBarLyingRow")
# individual.parse_webpage("WeightExercises", "BackGeneral", "CBOneArmRow")
# individual.parse_webpage("WeightExercises", "BackGeneral",
#                          "CBOneArmTwistingHighRow")
