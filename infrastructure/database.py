from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.database_model import Base

engine = create_engine("sqlite:///./cinema.db")
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(engine)
