import json
import os

# the path to the config file
FILEPATH = "./config.json"

def get_setting(key):
    # gets the setting responding for the given key
    with open(FILEPATH, "r+") as configfile:
        settings = json.load(configfile)
        return settings[key]

def get_settings():
    # returns the saved config as a dictionary
    with open(FILEPATH, "r+") as configfile:
        return json.load(configfile)

def save_setting(key, value):
    # saves a new key and value for it
    try:
        # tries to read the config file
        with open(FILEPATH, "r") as configfile:
            # reads the config file
            settings = json.load(configfile)
        if settings == None:
            settings = {}
    except:
        # if an error occurs, assume that the config file is corrupted, and create a new one
        with open(FILEPATH, "w+"):
            pass
        settings = {}
    settings[key] = value
    with open(FILEPATH, "w") as configfile:
        # saves the new settings dictionary
        json.dump(settings, configfile)

# save path to the config file
save_setting("path", os.getcwd())
