from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.llm.base import LLMProvider
from app.llm.groq_provider import GroqProvider


async def get_llm_provider() -> LLMProvider:
    return GroqProvider()


async def get_database(
    db: AsyncSession = Depends(get_db),
) -> AsyncSession:
    return db


async def get_evaluation_provider(
    prompt_version: str = "v1",
) -> LLMProvider:
    return GroqProvider(
        prompt_version=prompt_version,
    )
