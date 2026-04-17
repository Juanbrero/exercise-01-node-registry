"""
Database connection and session management.

Read DATABASE_URL from environment variable.
Create SQLAlchemy engine and session.
Provide a dependency for FastAPI to get a DB session.
"""

# TODO: Implement database connection here
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base

DATABASE_URL = os.getenv("DATABASE_URL")
# create_engine devuelve un objeto Engine que representa la conexión a la base de datos.
engine = create_engine(DATABASE_URL)
# Crea las tablas si aún no existen.
Base.metadata.create_all(bind=engine)
# sessionmaker es una función que devuelve una clase de sesión personalizada. La clase de sesión se utiliza para interactuar con la base de datos.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    # sessionlocal() crea una nueva sesión de base de datos. La sesión se utiliza para realizar operaciones de lectura y escritura en la base de datos.
    db = SessionLocal()
    try:
        # si usara return la sesion se cerraria automaticamente al salir del try,
        # con yield, la sesion se mantiene abierta hasta que el codigo que la consume termine de usarla, y luego se cierra en el finally.
        yield db
    finally:
        db.close()

