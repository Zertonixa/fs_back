from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core.config import cfg

async_engine = create_async_engine(
    url=cfg.database.async_database_url,
    echo=cfg.database.echo,
    pool_size=cfg.database.pool_size,
    max_overflow=cfg.database.max_overflow,
    pool_timeout=cfg.database.pool_timeout,
    pool_recycle=cfg.database.pool_recycle,
    pool_pre_ping=cfg.database.pool_pre_ping,
)

async_session_maker = async_sessionmaker(
    autocommit=False, autoflush=True, expire_on_commit=False, bind=async_engine
)
