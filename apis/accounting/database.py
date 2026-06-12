# ============================================================
# CICOR ERP - Accounting API | database.py
# Descripción: Pool de conexiones PostgreSQL con psycopg2.
#              Gestiona el ciclo de vida de la conexión y
#              expone un context manager para uso seguro
#              en cada endpoint de FastAPI.
# ============================================================

import logging
import time
from contextlib import contextmanager
from typing import Generator

import psycopg2
import psycopg2.extras
import psycopg2.pool
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


# ── Configuración ─────────────────────────────────────────────
class DatabaseSettings(BaseSettings):
    """Lee las variables de entorno del Secret de Kubernetes
    (o del .env en desarrollo local)."""

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "cicor_user"
    postgres_password: str = "cicor_pass"
    postgres_db: str = "cicor_accounting_db"

    db_pool_min_conn: int = 1
    db_pool_max_conn: int = 10

    @property
    def dsn(self) -> str:
        return (
            f"host={self.postgres_host} "
            f"port={self.postgres_port} "
            f"dbname={self.postgres_db} "
            f"user={self.postgres_user} "
            f"password={self.postgres_password} "
            f"connect_timeout=10 "
            f"application_name=cicor-accounting-api"
        )

    class Config:
        env_file = ".env"
        case_sensitive = False


db_settings = DatabaseSettings()


# ── Pool de conexiones ────────────────────────────────────────
class DatabasePool:
    _pool: psycopg2.pool.ThreadedConnectionPool | None = None

    @classmethod
    def init(cls, retries: int = 5, delay: int = 3) -> None:
        for attempt in range(1, retries + 1):
            try:
                cls._pool = psycopg2.pool.ThreadedConnectionPool(
                    minconn=db_settings.db_pool_min_conn,
                    maxconn=db_settings.db_pool_max_conn,
                    dsn=db_settings.dsn,
                )
                logger.info(
                    "DB pool inicializado",
                    extra={
                        "host": db_settings.postgres_host,
                        "db": db_settings.postgres_db,
                        "min_conn": db_settings.db_pool_min_conn,
                        "max_conn": db_settings.db_pool_max_conn,
                    },
                )
                return
            except psycopg2.OperationalError as exc:
                logger.warning(
                    f"Intento {attempt}/{retries} fallido conectando a BD: {exc}"
                )
                if attempt < retries:
                    time.sleep(delay)
                else:
                    raise RuntimeError(
                        f"No se pudo conectar a PostgreSQL tras {retries} intentos"
                    ) from exc

    @classmethod
    def close(cls) -> None:
        if cls._pool:
            cls._pool.closeall()
            cls._pool = None
            logger.info("DB pool cerrado")

    @classmethod
    def get_connection(cls) -> psycopg2.extensions.connection:
        if cls._pool is None:
            raise RuntimeError("El pool de BD no está inicializado")
        return cls._pool.getconn()

    @classmethod
    def release_connection(cls, conn: psycopg2.extensions.connection) -> None:
        if cls._pool:
            cls._pool.putconn(conn)


# ── Context manager para uso en endpoints ────────────────────
@contextmanager
def get_db_cursor() -> Generator[psycopg2.extensions.cursor, None, None]:
    """Proporciona un cursor dentro de una transacción con
    commit automático y rollback en caso de error."""
    conn = DatabasePool.get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            yield cursor
        conn.commit()
    except Exception as exc:
        conn.rollback()
        logger.error(f"Error en transacción BD, rollback ejecutado: {exc}")
        raise
    finally:
        DatabasePool.release_connection(conn)


# ── Health check de BD ────────────────────────────────────────
def check_db_health() -> bool:
    """Verifica que la BD esté disponible.
    Usado por los endpoints /health/ready y /health/startup."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except Exception as exc:
        logger.error(f"Health check BD fallido: {exc}")
        return False
