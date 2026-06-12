import os
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from types import ModuleType
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

COMMERCIAL_API_DIR = os.path.join(os.path.dirname(__file__), "..")
TESTS_DIR = os.path.dirname(__file__)
sys.path.insert(0, COMMERCIAL_API_DIR)
sys.path.insert(0, TESTS_DIR)


def _inject_fake_modules():
    """Inject fake modules so main.py can be imported without real deps."""

    # ── Fake psycopg2 ──────────────────────────────────────────
    if "psycopg2" not in sys.modules:
        _fake = ModuleType("psycopg2")
        _fake.extras = ModuleType("psycopg2.extras")
        _fake.pool = ModuleType("psycopg2.pool")
        _fake.extensions = ModuleType("psycopg2.extensions")
        _fake.OperationalError = Exception
        _fake.extensions.connection = MagicMock
        _fake.extensions.cursor = MagicMock
        _fake.extras.RealDictCursor = MagicMock
        _fake.pool.ThreadedConnectionPool = MagicMock

        sys.modules["psycopg2"] = _fake
        sys.modules["psycopg2.extras"] = _fake.extras
        sys.modules["psycopg2.pool"] = _fake.pool
        sys.modules["psycopg2.extensions"] = _fake.extensions

    # ── Fake prometheus_fastapi_instrumentator ─────────────────
    if "prometheus_fastapi_instrumentator" not in sys.modules:
        _prom = ModuleType("prometheus_fastapi_instrumentator")
        _prom_metrics = ModuleType("prometheus_fastapi_instrumentator.metrics")
        _prom_metrics.Info = MagicMock
        _prom.Instrumentator = MagicMock
        _prom.metrics = _prom_metrics
        sys.modules["prometheus_fastapi_instrumentator"] = _prom
        sys.modules["prometheus_fastapi_instrumentator.metrics"] = _prom_metrics

    # ── Fake pythonjsonlogger ──────────────────────────────────
    if "pythonjsonlogger" not in sys.modules:
        _jsonlog = ModuleType("pythonjsonlogger")
        _jsonlog.jsonlogger = ModuleType("pythonjsonlogger.jsonlogger")
        _jsonlog.jsonlogger.JsonFormatter = MagicMock
        sys.modules["pythonjsonlogger"] = _jsonlog
        sys.modules["pythonjsonlogger.jsonlogger"] = _jsonlog.jsonlogger

    # ── Stub commercial-api/database.py ────────────────────────
    if "database" not in sys.modules:
        _db = ModuleType("database")

        @dataclass
        class _FakeSettings:
            postgres_host: str = "localhost"
            postgres_port: int = 5432
            postgres_user: str = "cicor_user"
            postgres_password: str = "cicor_pass"
            postgres_db: str = "cicor_commercial_db"
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
                    f"application_name=cicor-commercial-api"
                )

        _db.db_settings = _FakeSettings()
        _db.DatabasePool = MagicMock()

        @contextmanager
        def _get_db_cursor():
            yield FakeCursor()

        _db.get_db_cursor = _get_db_cursor
        _db.check_db_health = MagicMock(return_value=True)

        sys.modules["database"] = _db


_inject_fake_modules()


class FakeCursor:
    """Cursor-like object that returns predefined rows and captures queries."""

    def __init__(self, rows=None):
        self._rows = rows or []
        self._index = 0
        self.last_query = None
        self.last_params = None

    def execute(self, query, params=None):
        self.last_query = query
        self.last_params = params

    def fetchall(self):
        return self._rows

    def fetchone(self):
        if self._index < len(self._rows):
            row = self._rows[self._index]
            self._index += 1
            return row
        return None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


@contextmanager
def fake_db_context(cursor):
    yield cursor


@pytest.fixture
def fake_sale_row():
    """A dict-like row matching the sales table schema."""
    from datetime import datetime

    now = datetime(2024, 1, 15, 10, 30, 0)
    return {
        "id": 1,
        "product_name": "Laptop Dell XPS 15",
        "quantity": 5,
        "unit_price": "500.00",
        "total_amount": "2500.00",
        "customer_name": "Acme Corp",
        "sale_date": now,
        "status": "CONFIRMED",
        "created_at": now,
        "updated_at": now,
    }


@pytest.fixture
def mock_db_health():
    """Mock check_db_health to return True for health endpoints."""
    import database

    database.check_db_health.return_value = True
    yield


@pytest.fixture
def client():
    """TestClient for the commercial API."""
    import database
    import main

    database.DatabasePool.init = MagicMock()
    database.DatabasePool.close = MagicMock()
    database.check_db_health.return_value = True

    with TestClient(main.app) as tc:
        yield tc
