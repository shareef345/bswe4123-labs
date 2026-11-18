import asyncio
import time
import httpx

SERVICES = {
    "Service 1": "http://127.0.0.1:8001/health",
    "Service 2": "http://127.0.0.1:8002/health",
    "Service 3": "http://127.0.0.1:8003/health"
}

TIMEOUT = 1.5
SLOW_LIMIT = 0.5
MAX_FAILURES = 3
MONITOR_DURATION = 60

failures = {name: 0 for name in SERVICES}


async def check_service(client, name, url):
    start = time.perf_counter()

    try:
        response = await client.get(url)
        response.raise_for_status()

        elapsed = time.perf_counter() - start
        failures[name] = 0

        if elapsed > SLOW_LIMIT:
            return f"{name}: SLOW ({elapsed * 1000:.0f} ms)"

        return f"{name}: UP ({elapsed * 1000:.0f} ms)"

    except (httpx.RequestError, httpx.HTTPStatusError):
        failures[name] += 1

        if failures[name] >= MAX_FAILURES:
            return f"{name}: DOWN ({failures[name]} failures)"

        return f"{name}: SUSPECT ({failures[name]}/{MAX_FAILURES} failures)"


async def monitor():
    start_time = time.monotonic()
    round_number = 0

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:

        while time.monotonic() - start_time < MONITOR_DURATION:
            round_number += 1

            print(f"\nRound {round_number}:")

            results = await asyncio.gather(
                *[
                    check_service(client, name, url)
                    for name, url in SERVICES.items()
                ]
            )

            for result in results:
                print(result)

            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(monitor())