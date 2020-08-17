def create_subdirectory(path):
    '''Creates a subdirectory if one doesn't already exist at the path
    path: includes the name of the folder'''
    subdirectory = path
    if not os.path.exists(path):
        os.makedirs(path)


def load_object_from_file(path, recursion_limit=1000):
    '''Loads an object from a persistent pickle file
    path: includes the name of the file'''
    with open(path, 'rb') as input:
        sys.setrecursionlimit(recursion_limit)
        return pickle.load(input)
