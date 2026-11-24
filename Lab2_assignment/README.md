# Lab Assignment 2: Campus Room Booking Service

## Project Description

This project is a REST API for a Campus Room Booking Service built using FastAPI and Pydantic.

The service allows users to:
- Create and view campus rooms.
- Retrieve a room by its ID.
- Create and view bookings.
- Prevent overlapping bookings for the same room.
- Delete existing bookings.
- Handle repeated booking requests idempotently.

## Technologies Used

- Python 3.14
- FastAPI
- Pydantic
- Uvicorn
- HTTPX

## Installation

Install the required packages:

```bash
py -m pip install fastapi uvicorn httpx
```

## Running the Application

Run the following command:

```bash
py -m uvicorn service:app --reload
```

Open the API documentation:

http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Description | Success Status |
|---|---|---|---|
| POST | /rooms | Create a room | 201 |
| GET | /rooms | Get all rooms | 200 |
| GET | /rooms/{room_id} | Get a room by ID | 200 |
| PUT | /bookings/{booking_id} | Create or repeat a booking | 201 / 200 |
| GET | /bookings | Get all bookings | 200 |
| GET | /bookings/{booking_id} | Get a booking by ID | 200 |
| DELETE | /bookings/{booking_id} | Delete a booking | 204 |

## HTTP Status Codes

- **200 OK:** Request completed successfully.
- **201 Created:** A new room or booking was created.
- **204 No Content:** Booking was deleted successfully.
- **404 Not Found:** Requested room or booking does not exist.
- **409 Conflict:** Duplicate room, conflicting booking, or booking ID used with different data.
- **422 Unprocessable Entity:** Request data is invalid.

## Idempotency

The booking endpoint uses PUT:

`PUT /bookings/{booking_id}`

- First request with a new booking ID returns 201 Created.
- Repeating the same request with identical data returns 200 OK.
- Using the same booking ID with different data returns 409 Conflict.

## Testing

The project includes `test_bookings.py`, which uses HTTPX to test the API endpoints.

Run the tests while the FastAPI server is running:

```bash
py test_bookings.py
```

The tests check room creation, booking creation, idempotency, overlapping bookings, retrieving data, and deleting bookings.

All tests passed successfully during testing.

## Data Storage

The application currently uses Python dictionaries as temporary in-memory storage. Data is cleared when the server process restarts.
