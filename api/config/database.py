from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from api.config.settings import settings

engine = create_async_engine(settings.database_url, echo=False)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    async with async_session_maker() as session:
        yield session
