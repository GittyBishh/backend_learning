from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Connection URL for PostgreSQL using Psycopg 3 driver
SQLALCHEMY_DATABASE_URL = 'postgresql+psycopg://postgres:mypasspostgres@localhost/fastapi_learning'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Modern SQLAlchemy 2.0 Base class definition
class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()