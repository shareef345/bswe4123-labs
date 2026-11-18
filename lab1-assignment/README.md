# Lab Assignment 1: Is the Service Up, Slow or Down?

## 1. Introduction

The goal of this project is to build a service health monitoring system using Python.

The system monitors three services running on ports 8001, 8002, and 8003.

## 2. Technologies Used

- Python
- FastAPI
- Uvicorn
- HTTPX
- Visual Studio Code

## 3. Health Endpoint

The service.py file contains a /health endpoint.

It returns the service status and uptime in seconds.

Example response:

{
    "status": "ok",
    "uptime": 25.4
}

## 4. Monitor Results

The monitor checks all three services every 2 seconds.

The following states are supported:

- UP: The service responds within 500 milliseconds.
- SLOW: The response takes more than 500 milliseconds.
- DOWN: The service fails three consecutive checks.

### Normal Operation

Service 1: UP
Service 2: SLOW
Service 3: UP

### Stopping a Service

I stopped Service 3 using Ctrl+C.

The monitor displayed SUSPECT after the first and second failed checks.

After three consecutive failures, the service was marked as DOWN.

When I restarted Service 3, its status returned to UP.

### Slow Service

Service 2 was started with a delay of 0.8 seconds.

Since 0.8 seconds is greater than 0.5 seconds, the monitor identified it as SLOW.

## 5. Timeout and Consecutive Failures

The timeout was set to 1.5 seconds.

This gives services enough time to respond while preventing long waiting times.

The monitor requires three consecutive failed checks before declaring a service DOWN.

### Advantages

- Reduces false alarms.
- Detects slow services.
- Handles temporary network problems.

### Disadvantages

- A short timeout may cause false failures.
- A long timeout delays failure detection.
- Three failed checks increase detection time.

## 6. Conclusion

The project successfully demonstrates service monitoring using Python.

It identifies healthy, slow, and unavailable services.

The use of consecutive failures makes the monitoring system more reliable.
