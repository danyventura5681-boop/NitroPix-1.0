import os


def create_temp_folder():

    if not os.path.exists("temp"):
        os.makedirs("temp")


def delete_temp_file(path):

    try:
        os.remove(path)
    except:
        pass