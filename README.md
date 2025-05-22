# eventos-api

Este proyecto es un backend en FastAPI siguiendo Clean Architecture, con SQLModel, PostgreSQL, Alembic, Poetry y Pytest.

## Resumen de lo realizado

1. **Inicialización y dependencias**
   - Se creó el proyecto con Poetry y se instalaron FastAPI, SQLModel, SQLAlchemy, psycopg2, Alembic, python-dotenv y pytest.

2. **Estructura Clean Architecture**
   - Se crearon carpetas para separar responsabilidades: `api`, `core`, `models`, `repositories`, `services`, `schemas`, `tests`.

3. **Modelado y migraciones**
   - Se definieron modelos con SQLModel y se generaron migraciones con Alembic para reflejar los cambios en la base de datos PostgreSQL.

4. **CRUD de ejemplo y de eventos**
   - Se implementó un CRUD completo para eventos, con separación de lógica en repositorio, servicio y API.

5. **Pruebas unitarias**
   - Se crearon tests con pytest para cada operación del CRUD.

6. **Documentación automática**
   - FastAPI expone la documentación Swagger/OpenAPI en `/docs`.

## Diagrama de carpetas y responsabilidades

```
app/
  ├── api/           # Endpoints y routers (FastAPI)
  │     ├── event.py
  │     └── example.py
  ├── core/          # Configuración y utilidades
  │     └── config.py
  ├── models/        # Modelos de dominio y ORM (SQLModel)
  │     ├── event.py
  │     └── example.py
  ├── repositories/  # Acceso a datos (CRUD, consultas)
  │     ├── event_repository.py
  │     └── example_repository.py
  ├── services/      # Lógica de negocio
  │     ├── event_service.py
  │     └── example_service.py
  ├── schemas/       # Esquemas Pydantic (entrada/salida)
  │     ├── event.py
  │     └── example.py
  └── main.py        # Punto de entrada FastAPI
alembic/             # Migraciones de base de datos
  ├── env.py
  ├── versions/
  │     └── <migraciones>.py
  └── ...
tests/               # Pruebas unitarias
  └── test_event_service.py
.env                  # Variables de entorno
pyproject.toml        # Configuración Poetry
README.md             # Documentación del proyecto
```

- **api/**: Define los endpoints HTTP y routers de FastAPI.
- **core/**: Configuración global (DB, settings, etc).
- **models/**: Modelos ORM que representan las tablas.
- **repositories/**: Acceso a datos y lógica CRUD.
- **services/**: Lógica de negocio y orquestación.
- **schemas/**: Esquemas Pydantic para validación y serialización.
- **main.py**: Instancia FastAPI e incluye routers.
- **alembic/**: Migraciones de base de datos.
- **tests/**: Pruebas unitarias con pytest.
- **.env**: Variables de entorno (DB, etc).
- **pyproject.toml**: Dependencias y configuración Poetry.

---