from collections.abc import AsyncIterator

import pytest

from app.llm.streaming import sse_stream


async def fake_chunks() -> AsyncIterator[str]:
    yield "hello"
    yield " world"


@pytest.mark.asyncio
async def test_sse_stream() -> None:
    chunks = []

    async for chunk in sse_stream(fake_chunks()):
        chunks.append(chunk)

    assert chunks == [
        'data: {"type": "chunk", "content": "hello"}\n\n',
        'data: {"type": "chunk", "content": " world"}\n\n',
        'data: {"type": "done"}\n\n',
    ]
