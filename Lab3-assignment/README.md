Lab Assignment 3: The Exam Scheduler Service

1. Project Description

This project implements an Exam Scheduler Service using FastAPI. The service communicates with the Campus Room Booking Service to automatically find and book suitable rooms for exams.

The Exam Scheduler selects an available room with sufficient capacity and handles service failures using retries and exponential backoff.

2. Project Structure

- "exam_scheduler.py" – Exam Scheduler Service.
- "service.py" – Campus Room Booking Service.
- "test_bookings.py" – Booking tests.
- "README.md" – Project documentation and test results.

3. How to Run the Services

Room Booking Service

Run the following commands in PowerShell:

$env:ROOM_SERVICE_DELAY="1"
py -m uvicorn service:app --reload --port 8000

Exam Scheduler Service

Open another terminal and run:

$env:REQUEST_TIMEOUT="2"
$env:MAX_RETRIES="3"
py -m uvicorn exam_scheduler:app --reload --port 8001

The services run on different ports:

- Room Booking Service: 8000
- Exam Scheduler Service: 8001

4. Retry Mechanism Test

The Room Booking Service was stopped temporarily while the Exam Scheduler Service was running.

The Exam Scheduler attempted to connect and produced the following retry log:

Request failed: timed out. Retrying in 0.5 seconds...
Request failed: timed out. Retrying in 1.0 seconds...
Request failed: timed out. Retrying in 2.0 seconds...
503 Service Unavailable

After restarting the Room Booking Service, the Exam Scheduler successfully created a new exam booking.

5. Exponential Backoff

The service uses exponential backoff to increase the waiting time between retry attempts.

The waiting times are:

- First retry: 0.5 seconds
- Second retry: 1 second
- Third retry: 2 seconds

This reduces repeated requests in a short period when the Room Booking Service is unavailable.

The service retries timeouts, connection errors, and server errors (5xx). It does not retry client errors such as 404 and 409.

6. Idempotency

The booking operation uses the HTTP PUT method with a fixed booking ID based on the exam ID.

If a request is repeated with the same booking ID and identical booking data, the Room Booking Service returns the existing booking instead of creating a duplicate.

This makes retrying a booking request safer when a timeout occurs after the booking may already have been saved.

7. Delay and Timeout Experiments

The Room Booking Service delay was configured to 1 second.

Experiment| Delay| Timeout| Max Retries| Status Code| Response Time
1| 1 second| 0.5 seconds| 3| 503| 3.36 seconds
2| 1 second| 2 seconds| 3| 201| 3.56 seconds
3| 1 second| 3 seconds| 3| 201| 3.76 seconds

8. Results and Trade-offs

When the timeout was shorter than the Room Booking Service delay, the requests timed out and the Exam Scheduler returned 503 after exhausting its retries.

With longer timeout values, the service successfully created exam bookings and returned 201 Created.

A short timeout can detect failures quickly but may cause unnecessary retries. A longer timeout gives slower services more time to respond but can increase the total waiting time.

9. Conclusion

The Exam Scheduler Service successfully communicates with the Room Booking Service, selects suitable rooms, handles service failures using retries, and supports safe repeated booking requests through idempotency.