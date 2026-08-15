import asyncio

from redis.asyncio import Redis

from app.core.config import get_settings
from app.ingestion.worker import IngestionWorker


async def main() -> None:
    settings = get_settings()
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    worker = IngestionWorker(redis)
    try:
        await worker.run_forever()
    finally:
        await redis.aclose()


if __name__ == "__main__":
    asyncio.run(main())
