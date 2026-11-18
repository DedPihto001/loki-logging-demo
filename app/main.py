import asyncio
import random
import time

import httpx
from fastapi import FastAPI

LOKI_URL = "http://loki:3100"  # имя сервиса в общей docker-сети
app = FastAPI(title="Loki Logging Demo")

counter = 0


def send_log_to_loki(message: str, level: str = "info") -> None:
    """Отправляет одну запись лога в Loki через HTTP API."""
    payload = {
        "streams": [
            {
                "stream": {"app": "my_app", "level": level},
                # Loki ждёт timestamp в НАНОсекундах строкой
                "values": [[str(time.time_ns()), message]],
            }
        ]
    }
    try:
        r = httpx.post(
            f"{LOKI_URL}/loki/api/v1/push",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        r.raise_for_status()
    except Exception as e:  # не роняем приложение, если Loki недоступен
        print(f"failed to send log to loki: {e}")


@app.on_event("startup")
async def start_log_generator():
    """Фоновая задача: генерирует логи каждые 10 секунд."""

    async def generate():
        global counter
        levels = ["info", "info", "warning", "error", "debug"]
        while True:
            counter += 1
            level = random.choice(levels)
            send_log_to_loki(f"background event #{counter}", level)
            await asyncio.sleep(10)

    asyncio.create_task(generate())
    send_log_to_loki("application started", "info")


@app.get("/")
def read_root():
    send_log_to_loki("GET / request received", "info")
    return {"status": "ok", "message": "log sent to loki"}


@app.post("/log")
def create_log(message: str = "manual log", level: str = "info"):
    send_log_to_loki(message, level)
    return {"sent": True, "message": message, "level": level}
