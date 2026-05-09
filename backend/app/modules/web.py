import requests
from bs4 import BeautifulSoup as bs
import datetime
import re

##
from ..modules import json_op, util
from ..modules.config import *

#TODO: Create support for future dates in get_data 


def get_data(url, days_forwarded=0):
    """
    If Timestamp already in Data: skips
    Scrapes whole Website no Filtering yet and writes to JSON

    :param url:
    :return: dictionary
    """
    data = json_op.load_json(DATA_FILE)
    today = util.get_date(days_forwarded)

    try:
        if data is None:
            data = {}

        if today in data:
            print("Already scraped")
            return data
        
        
        response = requests.get(url)
        response.raise_for_status()

        data[today] = {"data": response.text}

        json_op.write_json(DATA_FILE, data)

        return data
    # if Timestamp in Data -> Already scraped not necessary to scrape again

    except requests.exceptions.HTTPError as e:
        print(f"Response: response")
        print(f"HTTP Error: {e}")
        

    except Exception as e:
        print(f"Error: {e}")
        


def filter_data(days_forwarded):
    """
    Filters Data for Rooms and Buildings
    :return:
    """
    
    today_key = util.get_date(days_forwarded)
    room_pattern = re.compile(r"^r\d+")
    building_pattern = re.compile(r"^building_b\d+")

    
    data = json_op.load_json(DATA_FILE)

    if not isinstance(data, dict) or today_key not in data:
        data = get_data(THABELLA_PERIOD_LIST, days_forwarded)
    
    html_content = data[today_key]["data"]
    
    soup = bs(html_content, 'html.parser')
    buildings = soup.find_all('tbody', {'id': building_pattern})
    clean_data = []

    for building in buildings:
        name_span = building.find('span', style=lambda x: x and 'font-weight:bold' in x)
        if not name_span:
            continue
        building_name = name_span.text.strip()
        building_id = name_span["data1"]
        
        rooms = building.find_all('tr', {'id': room_pattern})
        
        clean_data_rooms = []

        for room in rooms:
            room_id = room['id']

            title_td = room.find("td", title=True)
            if title_td:
                raw = title_td['title']
                parts = raw.split(",")
                clean_parts = []

                for part in parts:
                    cleaned = part.strip()
                # Only save it if it's not empty
                    if cleaned:
                        clean_parts.append(cleaned)

                room_name = clean_parts[0]
                other_clean_parts = clean_parts[1:]
                add_info = ", ".join(other_clean_parts)

                clean_data_rooms.append(
                    {
                        "room_id" : room_id, 
                        "room_name" : room_name, 
                        "add_info" : add_info
                     }
                )
        clean_data.append(
            {
           "building_name": building_name,
            "building_id" : building_id,
            "rooms" : clean_data_rooms
            }
        )
    
    return clean_data

def get_occupied_rooms(days_forwarded = 0):
    """
    days_forwarded are for days in the future
    """
    date = util.get_date(days_forwarded)
    thabella_backend_url = THABELLA_BACKEND_MAIN_URL + date

    backend_data = None

    try:
        response = requests.get(thabella_backend_url)
        response.raise_for_status() 
        backend_data = response.json() 

    except FileNotFoundError:
        print("Backend JSON not found, downloading...")
        try:
            backend_data = requests.get(thabella_backend_url)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    except Exception as e:
        print(f"Error: {e}")

    if backend_data:
        occupied_rooms = []
        occupying_events = []
        for data in backend_data:
            start_time_str = data["startDateTime"]
            start_dt = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
            duration_min = data["duration"]
            end_dt = start_dt + datetime.timedelta(minutes=duration_min)

            start_time_clean = start_dt.strftime("%H:%M")
            end_time_clean = end_dt.strftime("%H:%M")
            intervall = f"{start_time_clean}-{end_time_clean}"

            if data["eventTypeDescription"]:
                event = data["eventTypeDescription"]
            else:
                event = "Unbekannt"

            rooms_dict = data.get("room_ident", {})
            if rooms_dict:
                occupied_rooms = list(rooms_dict.values())

            occupying_events.append({"time": intervall ,"event": event, "rooms": occupied_rooms})

        return occupying_events

def complete_data(days_forwarded = 0):
    """
    combines the occupied rooms and the data from filter_data into a single JSON 
    with a bool "occupied" for clean data and easy sorting 
    => Entrypoint
    """
    data = filter_data(days_forwarded)
    occupied_rooms = get_occupied_rooms(days_forwarded)
    now = util.get_date(days_forwarded)
    combined_data = []

    for entry in data:
        building_id = entry["building_id"]
        building_name = entry["building_name"]

        complete_room_data = []


        for room in entry["rooms"]:
            room_id = room["room_id"]
            room_name = room["room_name"]
            additional_info = room["add_info"]
            occupied = False
            time = ""
            event = ""

            for occupying_event in occupied_rooms:
                for room_event in occupying_event["rooms"]:
                    if room_event == room["room_name"]:
                        occupied  = True
                        time = occupying_event["time"]
                        event = occupying_event["event"]

            complete_room_data.append({"Raum_ID": room_id,"Raum" : room_name, "Zusatzinfo" : additional_info, "Besetzt" : occupied, "time": time, "event": event})
    
        combined_data.append(
            {
                "Gebäude" : building_name,
                "Gebäude_ID" : building_id,
                "Räume": complete_room_data
            }
        )
    
    completed_data = json_op.load_json(COMPLETE_DATA)

    if completed_data:
      if not any(entry["date"] == now for entry in completed_data):
        completed_data.append(
            {
                "date" : now,
                "data" : combined_data
            }
        )  
    else:
        completed_data = [ {
        "date" : now,
        "data" : combined_data
        }
        ]

    json_op.write_json(COMPLETE_DATA, completed_data)

