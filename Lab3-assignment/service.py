import os
import time
from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel, Field, model_validator
from typing import Dict

app = FastAPI(title="Campus Room Booking Service")

# Configurable delay from environment variable
ROOM_SERVICE_DELAY = float(os.getenv("ROOM_SERVICE_DELAY", "0"))


@app.middleware("http")
async def add_configurable_delay(request, call_next):
    if ROOM_SERVICE_DELAY > 0:
        time.sleep(ROOM_SERVICE_DELAY)
    response = await call_next(request)
    return response


# Room Model
class Room(BaseModel):
    id: str
    building: str
    capacity: int = Field(gt=0)


# Booking Model
class Booking(BaseModel):
    id: str
    room_id: str
    date: str
    start_hour: int = Field(ge=8, le=19)
    end_hour: int = Field(ge=9, le=20)
    purpose: str

    @model_validator(mode="after")
    def validate_hours(self):
        if self.end_hour <= self.start_hour:
            raise ValueError("End hour must be after start hour")
        return self


# Temporary storage
rooms: Dict[str, Room] = {}
bookings: Dict[str, Booking] = {}


@app.get("/")
def home():
    return {"message": "Campus Room Booking Service is running"}


@app.post("/rooms", status_code=201)
def create_room(room: Room):
    if room.id in rooms:
        raise HTTPException(status_code=409, detail="Room already exists")
    rooms[room.id] = room
    return room


@app.get("/rooms")
def get_rooms():
    return list(rooms.values())


@app.get("/rooms/{room_id}")
def get_room(room_id: str):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    return rooms[room_id]


@app.put("/bookings/{booking_id}", status_code=201)
def create_booking(booking_id: str, booking: Booking, response: Response):
    if booking.id != booking_id:
        raise HTTPException(status_code=422, detail="Booking ID does not match URL")

    if booking_id in bookings:
        if bookings[booking_id] == booking:
            response.status_code = 200
            return bookings[booking_id]
        raise HTTPException(
            status_code=409,
            detail="Booking ID already exists with different data"
        )

    if booking.room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")

    for existing in bookings.values():
        if (
            existing.room_id == booking.room_id
            and existing.date == booking.date
            and booking.start_hour < existing.end_hour
            and booking.end_hour > existing.start_hour
        ):
            raise HTTPException(
                status_code=409,
                detail="Room is already booked during this time"
            )

    bookings[booking_id] = booking
    return bookings[booking_id]


@app.get("/bookings")
def get_bookings():
    return list(bookings.values())


@app.get("/bookings/{booking_id}")
def get_booking(booking_id: str):
    if booking_id not in bookings:
        raise HTTPException(status_code=404, detail="Booking not found")
    return bookings[booking_id]


@app.delete("/bookings/{booking_id}", status_code=204)
def delete_booking(booking_id: str):
    if booking_id not in bookings:
        raise HTTPException(status_code=404, detail="Booking not found")
    del bookings[booking_id]
    return None