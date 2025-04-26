from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from api.core.config import settings

engine = create_async_engine(settings.DB_URL, echo=False)
async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
