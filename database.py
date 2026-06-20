from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from urllib.parse import quote_plus
from sqlalchemy import create_engine


DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_mycgN3qsTO9f@ep-plain-thunder-at7jyw40-pooler.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()