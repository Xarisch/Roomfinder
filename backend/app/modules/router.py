from fastapi import APIRouter, HTTPException
from app.modules.CRUD import RoomFilter

router = APIRouter(prefix="/find")

def __init__(days=0, free=True):        
    filter_instance = RoomFilter(days_forwarded=days, search_free=free)
    return filter_instance

# For Testing purposes. Will be called by Frontend
filter_instance = __init__()

@router.get("/room")
def get_room_by_name(room: str):
    return filter_instance.search_room(room)


@router.get("/rooms-b")
def get_rooms_by_buildings(building: str):
    return filter_instance.get_rooms_in_building(building)


@router.get("/all-rooms")
def get_all_rooms():
    return filter_instance.get_all_free_rooms()