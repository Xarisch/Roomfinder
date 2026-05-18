import json
import os

def del_file(filename):
    """
    Deletes File (DUH)
    :param filename:
    :return:
    """
    try:
        os.remove(filename)
    except Exception as e:
        print(f"Error: {e}")

def load_json(filename):
    """
    Loads JSON with Filename
    :param filename:
    :return dictionary
    """
    try:
        with open(filename) as file:
            data = json.load(file)
            return data
    except  FileNotFoundError as e:
        return []   
    
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return []

    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def write_json(filename, data):
    """
    Writes JSON to File
    :param filename:
    :param data:
    :return: bool
    """
    try:
        with open(filename, 'w') as outfile:
            json.dump(data, outfile, indent=4, ensure_ascii=False)

        return True
    except Exception as e:
        return f"Error: {e}"