"""Database initialization and session management."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from loguru import logger
from pathlib import Path

from models.database import Base

# SQLite database path
DB_DIR = Path(__file__).parent / "data"
DB_PATH = DB_DIR / "music_producer.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"


async def get_engine():
    """Create async database engine."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    return engine


async def init_db():
    """Initialize database — create all tables."""
    logger.info("Initializing database...")
    engine = await get_engine()
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info(f"Database initialized at {DB_PATH}")
    
    # Verify tables
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
        tables = [row[0] for row in result]
        logger.info(f"Tables created: {tables}")
    
    await engine.dispose()
    return DB_PATH


async def get_session() -> AsyncSession:
    """Get async database session."""
    engine = await get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())
