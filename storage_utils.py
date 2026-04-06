import json
import logging
from pathlib import Path


def open_file(function_name):
    try:
        with open("mangaData.json", "r") as outfile:
            data = json.load(outfile)
    except FileNotFoundError:
        logging.error("File not found, error in " + function_name)
        return -1
    except json.decoder.JSONDecodeError:
        logging.error("Error decoding JSON, error in " + function_name)
        return -1
    except PermissionError:
        logging.error("Permission denied, error in " + function_name)
        return -1
    except Exception as e:
        logging.error("Unexpeced Error in opening or editing data file at: " + function_name  + " " + str(e))
        return -1 
    #end file handling
    return data

def insert_to_file(new_entry):
    try:
        with open('mangaData.json', "r") as outfile:
            data = json.load(outfile)
        data.append(new_entry)
        with open('mangaData.json', "w") as outfile:
            json.dump(data, outfile, indent=4)
    except FileNotFoundError:
        logging.error("File not found, error in insert_to_file()")
        exit()
    except json.decoder.JSONDecodeError:
        logging.error("Error decoding JSON, error in insert_to_file()")
        exit()
    except PermissionError:
        logging.error("Permission denied, error in insert_to_file()")
        exit()
    except Exception as e:
        logging.error("Unexpeced Error in opening or editing data file at: insert_to_file(): " + str(e))
        exit()
    

def update_file(data):
    try:
        with open('mangaData.json', "w") as outfile:
            json.dump(data, outfile, indent=4)
    except FileNotFoundError:
        logging.error("File not found, error in update_file()")
        exit()
    except json.decoder.JSONDecodeError:
        logging.error("Error decoding JSON, error in update_file()")
        exit()
    except PermissionError:
        logging.error("Permission denied, error in update_file()")
        exit()
    except Exception as e:
        logging.error("Unexpeced Error in opening or editing data file at: update_file(): " + str(e))
        exit()

