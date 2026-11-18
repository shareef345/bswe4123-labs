import time
import argparse
from fastapi import FastAPI
import uvicorn

app = FastAPI()

start_time = time.time()

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=8001)
parser.add_argument("--delay", type=float, default=0)
args = parser.parse_args()


@app.get("/health")
async def health():
    if args.delay > 0:
        time.sleep(args.delay)

    uptime = round(time.time() - start_time, 2)

    return {
        "status": "ok",
        "uptime": uptime
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=args.port)