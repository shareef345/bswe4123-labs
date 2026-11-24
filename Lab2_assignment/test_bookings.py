import httpx
import uuid

BASE_URL = "http://127.0.0.1:8000"

# Use unique IDs so the tests can be run more than once
suffix = uuid.uuid4().hex[:6].upper()
room_id = f"ROOM{suffix}"
booking_id = f"BOOK{suffix}"
second_booking_id = f"BOOK2{suffix}"

client = httpx.Client(base_url=BASE_URL)

def check(description, response, expected):
    result = "PASS" if response.status_code == expected else "FAIL"
    print(
        f"{result}: {description} "
        f"(Expected {expected}, got {response.status_code})"
    )

# Create a room
response = client.post("/rooms", json={
    "id": room_id,
    "building": "Engineering",
    "capacity": 30
})
check("Create room", response, 201)

# Get all rooms
response = client.get("/rooms")
check("List rooms", response, 200)

# Get an existing room
response = client.get(f"/rooms/{room_id}")
check("Get room", response, 200)

# Get a room that does not exist
response = client.get("/rooms/UNKNOWN")
check("Room not found", response, 404)

# Create a booking
booking_data = {
    "id": booking_id,
    "room_id": room_id,
    "date": "2099-01-01",
    "start_hour": 10,
    "end_hour": 12,
    "purpose": "Study session"
}
response = client.put(f"/bookings/{booking_id}", json=booking_data)
check("Create booking", response, 201)

# Repeat the same request (idempotency)
response = client.put(f"/bookings/{booking_id}", json=booking_data)
check("Repeat identical booking", response, 200)

# Try an overlapping booking
overlap_data = {
    "id": second_booking_id,
    "room_id": room_id,
    "date": "2099-01-01",
    "start_hour": 11,
    "end_hour": 13,
    "purpose": "Another study session"
}
response = client.put(f"/bookings/{second_booking_id}", json=overlap_data)
check("Overlapping booking", response, 409)

# List bookings
response = client.get("/bookings")
check("List bookings", response, 200)

# Get an existing booking
response = client.get(f"/bookings/{booking_id}")
check("Get booking", response, 200)

# Get a booking that does not exist
response = client.get("/bookings/UNKNOWN")
check("Booking not found", response, 404)

# Delete the booking
response = client.delete(f"/bookings/{booking_id}")
check("Delete booking", response, 204)

# Delete it again
response = client.delete(f"/bookings/{booking_id}")
check("Delete missing booking", response, 404)

client.close()