# Tests — CICOR ERP v3 APIs

Tests de humo para las APIs del ERP. Cada módulo tiene al menos un test que
valida que la API arranca correctamente y el CRUD básico funciona.

## Estructura

```
tests/
├── __init__.py                    # Package marker
├── conftest.py                    # Fixtures compartidas (TestClient, mocks de BD)
├── test_commercial_health.py      # Health checks del módulo Comercial
└── test_commercial_sales.py       # CRUD de Ventas
```

## Requisitos

Instalar las dependencias de test en el entorno virtual del proyecto:

```bash
pip install pytest pytest-asyncio httpx
```

## Ejecutar

Desde el directorio `v3/`:

```bash
pytest apis/tests/ -v
```

Para ejecutar un archivo específico:

```bash
pytest apis/tests/test_commercial_health.py -v
```

## Cómo agregar tests para otro módulo

1. Copiar `conftest.py` y ajustar el `sys.path` para apuntar al directorio del nuevo módulo.
2. Crear un archivo `test_<modulo>_health.py` con los health checks.
3. Crear un archivo `test_<modulo>_crud.py` con el CRUD mockeado.
4. Usar el patrón de `FakeCursor` y `fake_db_context` para simular la base de datos.

Todos los tests usan `unittest.mock` y no requieren una base de datos real.
