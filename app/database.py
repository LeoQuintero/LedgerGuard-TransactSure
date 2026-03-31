import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

DATABASE_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
# El engine es el motor — es el objeto central que administra todas las conexiones a PostgreSQL. 
# pool_pre_ping=True verifica que la conexión sigue viva antes de usarla.

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#Una Session es como una conversación abierta con la BD. Cada operación (INSERT, SELECT, UPDATE) ocurre dentro de una sesión. 
# SessionLocal es la fábrica que crea esas conversaciones.

class Base(DeclarativeBase):
    pass