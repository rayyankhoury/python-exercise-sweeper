"""Using a dictionary already loaded in to storage, pulls data from website and stores
    data in details.json files within the directory structure
    """

import os
import sys
import pickle
import ExerciseDetailsParserJSON

# Loads the file in to memory
with open(os.path.join('dictionary', 'dictionary.pk1'), 'rb') as file_input:
    sys.setrecursionlimit(10000)
    organized = pickle.load(file_input)


def write_to_file(group, muscle, mtype):
    """Takes in strings which represent the location of the folders in the system

    Args:
        group (string): overall muscle group string
        muscle (string): individual muscle string
        mtype (string): the type of exercise being stored
    """
    hrefs = organized[group][muscle][mtype]
    path = os.path.join(
        'data', group, muscle, mtype, "details.json")

    with open(path, "w+") as file:
        file.write(f'{{"{mtype}":[')
        try:
            details = ','.join([ExerciseDetailsParserJSON.parse(
                href['href'], index) for index, href in enumerate(hrefs)])
        except ValueError as err:
            print(err.args)
            details = ''
        file.write(f'{details}]}}')


def write_json(dictionary):
    """Writes JSON to a file location based on the dictionary

    Args:
        dictionary (dictionary): a dictionary containing all the relevant website information
    """
    for group_key, group_dict in dictionary.items():
        for muscle_key, muscle_dict in group_dict.items():
            for type_key in muscle_dict.items():
                keystring = f"{group_key}, {muscle_key}, {type_key}"
                print(f"Writing JSON: {keystring}")
                try:
                    write_to_file(group_key, muscle_key, type_key)
                except ValueError as err:
                    with open("json_error.log", "a") as file:
                        file.write(f"{keystring}\n")
                    print(err)


def get_individual_items(errors):
    """ An error testing function that runs on failed items

    Args:
        array (list(list())): a list of lists containing the
        group, muscle and type key of failed items
    """
    for child in errors:
        dict2 = {child[2]: organized[child[0]][child[1]][child[2]]}
        dict1 = {child[1]: dict2}
        dict0 = {child[0]: dict1}
        write_json(dict0)


check = [['Chest', 'PectoralSternal', 'cable'],
         ['Chest', 'PectoralSternal', 'plyometric'],
         ['Chest', 'SerratusAnterior', 'plyometric'],
         ['Waist', 'RectusAbdominis', 'plyometric'],
         ['Waist', 'Obliques', 'plyometric']]


if check is not None:
    get_individual_items(check)
