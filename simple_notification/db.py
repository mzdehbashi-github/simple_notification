import os

from sqlmodel import create_engine
from sqlmodel.engine.create import URL
from sqlmodel.ext.asyncio.session import AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker


host = os.environ['POSTGRES_HOST']
port = os.environ['POSTGRES_PORT']
database = os.environ['POSTGRES_DB']
user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
database_url = URL(
    host=host,
    port=port,
    database=database,
    username=user,
    password=password,
    drivername='postgresql+asyncpg',
)

engine = AsyncEngine(create_engine(database_url, echo=True, future=True))


async def get_session() -> AsyncSession:
    """
    Provides an `AsyncSession` instance.

    Can be used in API functions via dependency injection.
    """
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
