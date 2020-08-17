import os
import sys
import pickle


class Input_Switcher(object):
    """Takes in an argument from the command line and performs
    a function based on the input argument

    Args:
        object (string): Requested input from the terminal
    """

    def switch(self, input_string):
        method_name = input_string
        method = getattr(self, method_name, default=self.default())
        return method()

    def no(self):
        sys.exit("Exiting")

    def yes(self):
        print('Overwriting')
        return True

    def dir(self):
        print("Creating directory structure")
        return False

    def default(self):
        sys.exit("Wrong value entered, exiting")


value = input('''
This is dangerous and will overwrite JSON details files.
To overwrite type yes.
To create directory structure without overwriting type dir.
To exit type no\n''')

overwrite = Input_Switcher().switch(value)


def create_subdirectory(path):
    '''Creates a subdirectory if one doesn't already exist at the path
    path: includes the name of the folder'''
    if not os.path.exists(path):
        os.makedirs(path)


def load_object_from_file(path, recursion_limit=1000):
    '''Loads an object from a persistent pickle file
    path: includes the name of the file'''
    with open(path, 'rb') as file_input:
        sys.setrecursionlimit(recursion_limit)
        return pickle.load(file_input)


organized = load_object_from_file(
    os.path.join('dictionary', 'dictionary.pk1'), 10000)

# Create the directory structure from a dictionary and an optional path


create_subdirectory("data")
for key in organized:
    create_subdirectory(os.path.join("data", key))
    for muscle in organized[key]:
        create_subdirectory(os.path.join("data", key, muscle))
        for exercisetype in organized[key][muscle]:
            create_subdirectory(os.path.join(
                "data", key, muscle, exercisetype))
            if overwrite:
                open(os.path.join("data", key, muscle,
                                  exercisetype, "details.json"), "w+")
