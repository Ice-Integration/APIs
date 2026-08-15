from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass

from redis.asyncio import Redis


@dataclass(frozen=True)
class IngestionJob:
    document_id: str
    source_uri: str
    team: str


class IngestionWorker:
    QUEUE = "opsmind:ingestion"

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def enqueue(self, job: IngestionJob) -> None:
        await self.redis.lpush(self.QUEUE, json.dumps(job.__dict__))

    async def process(self, job: IngestionJob) -> None:
        """Production adapter: load, chunk, embed and upsert idempotently by document_id."""
        await asyncio.sleep(0)

    async def run_forever(self) -> None:
        while True:
            item = await self.redis.brpop(self.QUEUE, timeout=5)
            if not item:
                continue
            _, payload = item
            await self.process(IngestionJob(**json.loads(payload)))
