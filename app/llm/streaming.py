import json
from collections.abc import AsyncIterator


async def sse_stream(
    chunks: AsyncIterator[str],
) -> AsyncIterator[str]:
    async for chunk in chunks:
        payload = json.dumps(
            {"type": "chunk", "content": chunk},
            ensure_ascii=False,
        )

        yield f"data: {payload}\n\n"

    yield 'data: {"type": "done"}\n\n'
