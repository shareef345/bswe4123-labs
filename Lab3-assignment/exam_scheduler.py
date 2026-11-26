import os
import time
import httpx

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, model_validator

app = FastAPI(title="Exam Scheduler Service")


# Configuration from environment variables
ROOM_SERVICE_URL = os.getenv(
    "ROOM_SERVICE_URL",
    "http://127.0.0.1:8000"
)

REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "2"))

MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))


# Exam Model
class Exam(BaseModel):
    id: str
    course_code: str
    day: str
    start_hour: int = Field(ge=8, le=19)
    end_hour: int = Field(ge=9, le=20)
    students: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_hours(self):
        if self.end_hour <= self.start_hour:
            raise ValueError("End hour must be after start hour")
        return self


# Home endpoint
@app.get("/")
def home():
    return {"message": "Exam Scheduler Service is running"}


# Configuration endpoint
@app.get("/config")
def get_config():
    return {
        "room_service_url": ROOM_SERVICE_URL,
        "request_timeout": REQUEST_TIMEOUT,
        "max_retries": MAX_RETRIES
    }


# Request with retry and exponential backoff
def request_with_retry(client, method, url, **kwargs):

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.request(
                method,
                url,
                **kwargs
            )

            # Retry only server errors (5xx)
            if response.status_code >= 500:
                response.raise_for_status()

            # Return other responses without retrying
            return response

        except (
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.HTTPStatusError
        ) as error:

            # Do not retry 4xx responses
            if isinstance(error, httpx.HTTPStatusError):
                if error.response.status_code < 500:
                    raise

            # Stop after the maximum number of retries
            if attempt == MAX_RETRIES:
                raise

            # Exponential backoff: 0.5, 1, 2, ...
            delay = 0.5 * (2 ** attempt)
            print(
                f"Request failed: {error}. "
                f"Retrying in {delay} seconds..."
            )
            time.sleep(delay)


# Check if two bookings overlap
def is_overlapping(exam, booking):
    return (
        exam.day == booking["date"]
        and exam.start_hour < booking["end_hour"]
        and exam.end_hour > booking["start_hour"]
    )


# Create an exam and automatically book a room
@app.post("/exams", status_code=201)
def create_exam(exam: Exam):

    # Fixed booking ID prevents duplicate bookings
    booking_id = f"EXAM-{exam.id}"

    booking_data = {
        "id": booking_id,
        "room_id": "",
        "date": exam.day,
        "start_hour": exam.start_hour,
        "end_hour": exam.end_hour,
        "purpose": f"Exam {exam.course_code}"
    }

    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:

            # Get all rooms
            rooms_response = request_with_retry(
                client,
                "GET",
                f"{ROOM_SERVICE_URL}/rooms"
            )
            rooms_response.raise_for_status()
            rooms = rooms_response.json()

            # Get existing bookings
            bookings_response = request_with_retry(
                client,
                "GET",
                f"{ROOM_SERVICE_URL}/bookings"
            )
            bookings_response.raise_for_status()
            bookings = bookings_response.json()

            # Check if this exam was already booked
            for existing in bookings:
                if existing["id"] == booking_id:

                    if (
                        existing["date"] == exam.day
                        and existing["start_hour"] == exam.start_hour
                        and existing["end_hour"] == exam.end_hour
                        and existing["purpose"] == booking_data["purpose"]
                    ):
                        return {
                            "exam_id": exam.id,
                            "course_code": exam.course_code,
                            "room_id": existing["room_id"],
                            "message": "Exam was already booked"
                        }

                    raise HTTPException(
                        status_code=409,
                        detail="Exam ID already exists with different data"
                    )

            # Find suitable available rooms
            available_rooms = []

            for room in rooms:

                if room["capacity"] < exam.students:
                    continue

                conflict = False

                for booking in bookings:
                    if (
                        booking["room_id"] == room["id"]
                        and is_overlapping(exam, booking)
                    ):
                        conflict = True
                        break

                if not conflict:
                    available_rooms.append(room)

            # Choose the smallest suitable room
            available_rooms.sort(
                key=lambda room: room["capacity"]
            )

            if not available_rooms:
                raise HTTPException(
                    status_code=409,
                    detail="No suitable room is available"
                )

            selected_room = available_rooms[0]

            # Prepare the booking
            booking_data["room_id"] = selected_room["id"]

            # Book the selected room with retry
            booking_response = request_with_retry(
                client,
                "PUT",
                f"{ROOM_SERVICE_URL}/bookings/{booking_id}",
                json=booking_data
            )

            if booking_response.status_code == 409:
                raise HTTPException(
                    status_code=409,
                    detail="Room booking conflict"
                )

            booking_response.raise_for_status()

            return {
                "exam_id": exam.id,
                "course_code": exam.course_code,
                "room_id": selected_room["id"],
                "room_capacity": selected_room["capacity"],
                "message": "Exam booked successfully"
            }

    except HTTPException:
        raise

    except (
        httpx.TimeoutException,
        httpx.ConnectError,
        httpx.HTTPStatusError
    ):
        raise HTTPException(
            status_code=503,
            detail="Room Booking Service is unavailable"
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Room Booking Service connection failed"
        )