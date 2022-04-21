import json
import os

# the path to the config file
FILEPATH = "."

def get_setting(path, key):
    # gets the setting responding for the given key
    with open(path + "/config.json", "r+") as configfile:
        settings = json.load(configfile)
        return settings[key]

def get_settings(path):
    # returns the saved config as a dictionary
    with open(path + "/config.json", "r+") as configfile:
        return json.load(configfile)

def save_setting(path, key, value):
    # saves a new key and value for it
    try:
        # tries to read the config file
        with open(path + "/config.json", "r") as configfile:
            # reads the config file
            settings = json.load(configfile)
        if settings == None:
            settings = {}
    except:
        # if an error occurs, assume that the config file is corrupted, and create a new one
        with open(path + "/config.json", "w+"):
            pass
        settings = {}
    settings[key] = value
    with open(path + "/config.json", "w") as configfile:
        # saves the new settings dictionary
        json.dump(settings, configfile)

# save path to the config file
save_setting(FILEPATH, "path", os.getcwd())
