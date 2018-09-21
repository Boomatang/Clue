import os


def file_ext_checker(file_name, ext):

    if file_name.lower().endswith(ext.lower()):
        return True
    else:
        return False


def count_files(path):
    counter = 0
    for root, dirs, files in os.walk(path):
        counter = len(files)

    return counter
