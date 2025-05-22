import os
from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost:5432/events")
engine = create_engine(DATABASE_URL, echo=True)

# JWT Configuration
SECRET_KEY = "G3EST9ON3N5T05.89FE_1S3CT3103N"  # Cambia esto por una clave segura
ALGORITHM = "HS256"