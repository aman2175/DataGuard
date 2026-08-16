from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

engine= create_engine(settings.database_url,pool_pre_ping=True,)

SessionLocal=sessionmaker(bind=engine, autoflush=True, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db=SessionLocal()
    try:
        yield db# this will return the database session object yield is a generator function
    finally:
        db.close()


