import sys
import logging
import asyncio
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager

# Configure selector event loop policy on Windows for psycopg3 async compatibility
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from psycopg_pool import AsyncConnectionPool
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    from langgraph.checkpoint.memory import MemorySaver
    HAS_POSTGRES_CHECKPOINTER = True
except ImportError as e:
    logger.warning("langgraph-checkpoint-postgres or psycopg_pool not installed: %s", e)
    from langgraph.checkpoint.memory import MemorySaver
    HAS_POSTGRES_CHECKPOINTER = False
    AsyncPostgresSaver = None
    AsyncConnectionPool = None


def get_postgres_conn_string() -> str:
    """
    Format and clean connection string for psycopg3 / AsyncPostgresSaver.
    """
    db_url = settings.DATABASE_URL or "postgresql://postgres:password@localhost:5432/nextserve"
    # Ensure standard postgresql scheme
    if db_url.startswith("postgresql+psycopg2://") or db_url.startswith("postgresql+asyncpg://"):
        db_url = "postgresql://" + db_url.split("://", 1)[1]
    return db_url


class PostgresMemoryManager:
    """
    Manages the lifecycle of the AsyncPostgresSaver checkpointer
    for thread state persistence across conversational agent workflows.
    """

    def __init__(self, conn_string: Optional[str] = None):
        self.conn_string = conn_string or get_postgres_conn_string()
        self.pool: Optional[AsyncConnectionPool] = None
        self.saver: Optional[AsyncPostgresSaver] = None
        self._fallback_saver: MemorySaver = MemorySaver()
        self._initialized: bool = False

    async def initialize(self) -> AsyncPostgresSaver:
        """
        Initialize database connection pool and run table setup migrations.
        """
        if not HAS_POSTGRES_CHECKPOINTER:
            logger.warning("Using MemorySaver fallback (Postgres saver not installed).")
            return self._fallback_saver

        try:
            # Create connection pool with autocommit for migration / checkpoint handling
            self.pool = AsyncConnectionPool(
                conninfo=self.conn_string,
                max_size=20,
                open=False,
                kwargs={"autocommit": True}
            )
            await self.pool.open()
            self.saver = AsyncPostgresSaver(self.pool)
            # Run table migrations (checkpoints, checkpoint_blobs, checkpoint_writes)
            await self.saver.setup()
            self._initialized = True
            logger.info("AsyncPostgresSaver initialized successfully against PostgreSQL.")
            return self.saver
        except Exception as exc:
            logger.error("Failed to initialize AsyncPostgresSaver: %s. Using MemorySaver fallback.", exc)
            return self._fallback_saver

    async def get_checkpointer(self):
        """
        Retrieve the active checkpointer. If initialization fails, returns MemorySaver fallback.
        """
        if self._initialized and self.saver:
            return self.saver
        return await self.initialize()

    async def close(self):
        """Cleanly close connection pool on shutdown."""
        if self.pool:
            try:
                await self.pool.close()
                self._initialized = False
                logger.info("AsyncPostgresSaver connection pool closed.")
            except Exception as e:
                logger.warning("Error closing connection pool: %s", e)


# Global memory manager instance
postgres_memory_manager = PostgresMemoryManager()


@asynccontextmanager
async def get_postgres_checkpointer(
    conn_string: Optional[str] = None
) -> AsyncGenerator[AsyncPostgresSaver, None]:
    """
    Async context manager to obtain an initialized AsyncPostgresSaver.
    Usage:
        async with get_postgres_checkpointer() as checkpointer:
            compiled_graph = graph_builder.compile(checkpointer=checkpointer)
            await compiled_graph.ainvoke(state, config={"configurable": {"thread_id": "123"}})
    """
    uri = conn_string or get_postgres_conn_string()
    if not HAS_POSTGRES_CHECKPOINTER:
        yield MemorySaver()
        return

    try:
        async with AsyncPostgresSaver.from_conn_string(uri) as saver:
            await saver.setup()
            yield saver
    except Exception as exc:
        logger.error("Postgres connection error in context manager: %s. Falling back to MemorySaver.", exc)
        yield MemorySaver()
