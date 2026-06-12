"""Smoke tests for Sales CRUD endpoints of the Commercial API."""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch


class TestListSales:
    """GET /api/commercial/sales — List all sales."""

    def test_returns_empty_list(self, client):
        from conftest import FakeCursor
        from conftest import fake_db_context

        fake_cursor = FakeCursor(rows=[])

        with patch("main.get_db_cursor", return_value=fake_db_context(fake_cursor)):
            response = client.get("/api/commercial/sales")

        assert response.status_code == 200
        assert response.json() == []

    def test_returns_single_sale(self, client, fake_sale_row):
        from conftest import FakeCursor
        from conftest import fake_db_context

        fake_cursor = FakeCursor(rows=[fake_sale_row])

        with patch("main.get_db_cursor", return_value=fake_db_context(fake_cursor)):
            response = client.get("/api/commercial/sales")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["product_name"] == "Laptop Dell XPS 15"


class TestCreateSale:
    """POST /api/commercial/sales — Create a new sale."""

    def test_creates_sale_with_inventory_ok(self, client, fake_sale_row):
        from conftest import FakeCursor
        from conftest import fake_db_context

        fake_cursor = FakeCursor(rows=[fake_sale_row])

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "remaining_stock": 95,
            "message": "Reserva exitosa",
        }

        mock_client_context = MagicMock()
        mock_client_context.post = AsyncMock(return_value=mock_response)
        mock_client_context.__aenter__ = AsyncMock(return_value=mock_client_context)
        mock_client_context.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "main.get_db_cursor", return_value=fake_db_context(fake_cursor)
        ), patch("main.httpx.AsyncClient", return_value=mock_client_context):
            payload = {
                "product_name": "Laptop Dell XPS 15",
                "quantity": 5,
                "unit_price": 500.00,
                "customer_name": "Acme Corp",
            }
            response = client.post("/api/commercial/sales", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["product_name"] == "Laptop Dell XPS 15"
        assert data["quantity"] == 5

    def test_creates_sale_when_inventory_fails(self, client, fake_sale_row):
        from conftest import FakeCursor
        from conftest import fake_db_context

        fake_cursor = FakeCursor(rows=[fake_sale_row])

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": False,
            "remaining_stock": 0,
            "message": "Sin stock",
        }

        mock_client_context = MagicMock()
        mock_client_context.__aenter__ = AsyncMock(return_value=mock_client_context)
        mock_client_context.__aexit__ = AsyncMock(return_value=None)
        mock_client_context.post = AsyncMock(return_value=mock_response)

        with patch(
            "main.get_db_cursor", return_value=fake_db_context(fake_cursor)
        ), patch("main.httpx.AsyncClient", return_value=mock_client_context):
            payload = {
                "product_name": "Laptop Dell XPS 15",
                "quantity": 5,
                "unit_price": 500.00,
                "customer_name": "Acme Corp",
            }
            response = client.post("/api/commercial/sales", json=payload)

        assert response.status_code == 201


class TestGetSale:
    """GET /api/commercial/sales/{id} — Get a single sale (not yet implemented)."""

    def test_endpoint_not_implemented_yet(self, client):
        """The GET single-sale endpoint does not exist; only PUT/DELETE use this
        path pattern.  This test documents the gap — returns 405."""
        response = client.get("/api/commercial/sales/1")

        assert response.status_code == 405
        assert response.json()["detail"] == "Method Not Allowed"


class TestDeleteSale:
    """DELETE /api/commercial/sales/{id} — Delete a sale."""

    def test_deletes_existing_sale(self, client, fake_sale_row):
        from conftest import FakeCursor
        from conftest import fake_db_context

        fake_cursor = FakeCursor(rows=[fake_sale_row])

        with patch("main.get_db_cursor", return_value=fake_db_context(fake_cursor)):
            response = client.delete("/api/commercial/sales/1")

        assert response.status_code == 204

    def test_returns_404_when_not_found(self, client):
        from conftest import FakeCursor
        from conftest import fake_db_context

        fake_cursor = FakeCursor(rows=[])

        with patch("main.get_db_cursor", return_value=fake_db_context(fake_cursor)):
            response = client.delete("/api/commercial/sales/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Venta 999 no encontrada"
