from ..modules import json_op, util, web
from ..modules.config import *

class RoomFilter:
    def __init__(self, days_forwarded=0, search_free=True):
        self.days_forwarded = days_forwarded
        self.target_date = util.get_date(days_forwarded)
        self.search_free = search_free
        self.data = []
        # Initialisiert die Daten direkt beim Erstellen des Objekts
        self._ensure_data()

    def _ensure_data(self):
        """Überprüft intern, ob Daten für das Zieldatum existieren, sonst Sync."""
        self.data = json_op.load_json(COMPLETE_DATA) or []
        
        date_exists = any(entry.get("date") == self.target_date for entry in self.data)
        
        if not date_exists:
            # Wenn das Datum fehlt, holen wir es via Scraper
            web.complete_data(self.days_forwarded)
            # Nach dem Scrapen laden wir die Datei neu in den Speicher
            self.data = json_op.load_json(COMPLETE_DATA)

    def search_room(self, desired_room):
        """Sucht nach einem spezifischen Raum am Zieltag."""
        for entry in self.data:
            if entry.get("date") == self.target_date:
                for building in entry.get("data", []):
                    building_name = building.get("Bauteil")
                    
                    for room in building.get("Räume", []):
                        if room.get("Raum") == desired_room:
                            # Logik für die Belegung
                            if self.search_free and room.get("Besetzt"):
                                return "Room not free"
                            
                            return {
                                "building": building_name,
                                "details": room
                            }
        
        return "Room not found"

    def normalize_building_name(self, input_name):
        """
        Convert A into Bauteil A (Backend Notation)
        """
        input_name = input_name.strip().upper()

        # A -> Bauteil A
        if len(input_name) == 1 and input_name.isalpha():
            return f"Bauteil {input_name}"
        
        #Falls schon Bauteil A eingegeben wurde
        return input_name

    def get_all_free_rooms(self):
        """
            Get all free rooms (duh)
        """
        free_rooms = []
        for entry in self.data:
            if entry.get("date") == self.target_date:
                for building in entry.get("data", []):
                        
                    for room in building.get("Räume", []):
                        if not room.get("Besetzt"):
                            free_rooms.append({
                                "building": building.get("Bauteil"),
                                "room": room.get("Raum")
                            })
        return free_rooms
    
    def get_rooms_in_buildings(self, building_name):
        """
            gets all rooms in a building 
            return dic(k)
        """
        
        rooms = []
        real_building_name = self.normalize_building_name(building_name)
        
        for entry in self.data:
            if entry.get("date") == self.target_date:
                for building in entry.get("data", []):
                    if real_building_name == building.get("Gebäude"):
                        for room in building.get("Räume", []):
                            is_free = not room.get("Besetzt")
                            
                            if self.search_free:
                                if is_free:
                                    rooms.append(room)
                            else:
                                rooms.append(room)
        return rooms