from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from redis.asyncio import Redis


@dataclass(frozen=True)
class Message:
    role: str
    content: str


class ConversationStore:
    def __init__(self, redis: Redis, ttl_seconds: int = 3600, max_messages: int = 20) -> None:
        self.redis = redis
        self.ttl_seconds = ttl_seconds
        self.max_messages = max_messages

    def _key(self, conversation_id: str) -> str:
        return f"opsmind:conversation:{conversation_id}"

    async def append(self, conversation_id: str, message: Message) -> None:
        key = self._key(conversation_id)
        await self.redis.rpush(key, json.dumps(asdict(message)))
        await self.redis.ltrim(key, -self.max_messages, -1)
        await self.redis.expire(key, self.ttl_seconds)

    async def history(self, conversation_id: str) -> list[Message]:
        values = await self.redis.lrange(self._key(conversation_id), 0, -1)
        return [Message(**json.loads(value)) for value in values]
