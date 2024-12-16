import os.path

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, '..', 'data', 'profiles.db')}"

engine = create_engine(DATABASE_URL, echo=True)

Base = declarative_base()


class Profile(Base):
    __tablename__ = "profiles"

    user_id = Column(Integer, primary_key=True)
    city = Column(String(100), nullable=False)
    name = Column(String(50), nullable=False)
    gender = Column(String(10), nullable=False)
    age = Column(Integer, nullable=False)
    budget = Column(Integer, nullable=False)
    media = Column(String, nullable=False)


SessionLocal = sessionmaker(bind=engine)


def init_db():
    os.makedirs(os.path.join(BASE_DIR, '..', 'data'), exist_ok=True)
    Base.metadata.create_all(engine)
