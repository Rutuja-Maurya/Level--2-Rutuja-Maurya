from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from ..config import DATABASE_URL

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
session_factory = sessionmaker(bind=engine)

# Create scoped session
Session = scoped_session(session_factory)

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close() 