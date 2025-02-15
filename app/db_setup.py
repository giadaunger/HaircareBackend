from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.database.models import Base
import os

load_dotenv()

engine = create_engine(os.getenv("DB_URL"), echo=True)

def init_db():
  Base.metadata.create_all(bind=engine)

def get_db():
  with Session(engine, expire_on_commit=False) as session:
    yield session