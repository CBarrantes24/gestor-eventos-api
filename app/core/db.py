from sqlmodel import Session, create_engine
from app.core.config import engine # Importa el engine desde tu archivo de configuración

def get_db():
    """
    Generador de sesión de base de datos.
    Se asegura de que la sesión de base de datos se cierre siempre después de su uso.
    """
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()

# Podrías también querer crear todas las tablas aquí si no lo haces en otro lugar (ej. con Alembic)
# from sqlmodel import SQLModel
# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)
#
# if __name__ == "__main__":
#     # Esto es útil para crear la base de datos y las tablas desde la línea de comandos
#     # directamente si es necesario, aunque usualmente se maneja con migraciones.
#     create_db_and_tables()