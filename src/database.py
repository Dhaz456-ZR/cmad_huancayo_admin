from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:1234@localhost:3306/cmac_huancayo_db")

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()