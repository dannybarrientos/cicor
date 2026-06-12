"""
CICOR ERP - HR API (Recursos Humanos)
Módulo de conexión a PostgreSQL usando pool de conexiones psycopg2.
"""

import logging
import os
from contextlib import contextmanager

import psycopg2
import psycopg2.pool

logger = logging.getLogger(__name__)

# ── Pool de conexiones (singleton) ────────────────────────────────────────────
_pool: psycopg2.pool.SimpleConnectionPool | None = None


# # #def get_pool() -> psycopg2.pool.SimpleConnectionPool:
# # #    """Inicializa y retorna el pool de conexiones (lazy init)."""
# # #    global _pool
# # #    if _pool is None:
# # #        _pool = psycopg2.pool.SimpleConnectionPool(
# # #            minconn=1,
# # #            maxconn=10,
# # #            host=os.getenv("POSTGRES_HOST", "localhost"),
# # #            port=int(os.getenv("POSTGRES_PORT", "5432")),
# # #            user=os.getenv("POSTGRES_USER", "cicor_user"),
# # #            password=os.getenv("POSTGRES_PASSWORD", "cicor_pass"),
# # #            dbname=os.getenv("POSTGRES_DB", "cicor_hr_db"),
# # #        )
# # #        logger.info(
# # #            "Pool de conexiones inicializado",
# # #            extra={
# # #                "host": os.getenv("POSTGRES_HOST"),
# # #                "db":   os.getenv("POSTGRES_DB"),
# # #                "min_conn": 1,
# # #                "max_conn": 10,
# # #            },
# # #        )
# # #    return _pool

def get_pool() -> psycopg2.pool.SimpleConnectionPool:
    """Inicializa y retorna el pool de conexiones (lazy init)."""
    global _pool
    if _pool is None:
        # ← VALIDACIÓN: asegúrate que POSTGRES_DB existe
        db_name = os.getenv("POSTGRES_DB")
        if not db_name:
            raise ValueError(
                "ERROR: Variable de entorno 'POSTGRES_DB' no definida. "
                "Asegúrate de que está en tu docker-compose.yml o .env"
            )

        _pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            user=os.getenv("POSTGRES_USER", "cicor_user"),
            password=os.getenv("POSTGRES_PASSWORD", "cicor_pass"),
            dbname=db_name,  # ← Usa la variable validada
        )
        logger.info(
            "Pool de conexiones inicializado",
            extra={
                "host": os.getenv("POSTGRES_HOST"),
                "db":   db_name,
                "user": os.getenv("POSTGRES_USER"),
                "min_conn": 1,
                "max_conn": 10,
            },
        )
    return _pool


@contextmanager
def get_db():
    """
    Context manager que entrega una conexión del pool.
    - Hace commit si no hay excepciones.
    - Hace rollback y re-lanza si hay alguna excepción.
    - Siempre devuelve la conexión al pool al finalizar.
    """
    pool = get_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


def check_db_connection() -> bool:
    """
    Verifica que la base de datos esté accesible.
    Usada por el readiness probe del health check.
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(
            "Fallo de conexión a la base de datos",
            extra={"error": str(e)},
        )
        return False
