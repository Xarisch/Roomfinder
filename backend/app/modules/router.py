from fastapi import APIRouter, HTTPException
from app.modules.CRUD import RoomFilter

router = APIRouter(prefix="/find")

def init(days=0, free=True):        
    filter_instance = RoomFilter(days_forwarded=days, search_free=free)
    return filter_instance

@router.get("/room")
def get_room_by_name(room: str, days: int = 0, free: bool = True):
    filter_instance = init(days, free)
    return filter_instance.search_room(room)


@router.get("/rooms-b")
def get_rooms_by_buildings(building: str, days: int = 0, free: bool = True):
    filter_instance = init(days, free)
    return filter_instance.get_rooms_in_building(building)


@router.get("/all-rooms")
def get_all_rooms(days: int = 0, free: bool = True):
    filter_instance = init(days, free)
    return filter_instance.get_all_free_rooms()