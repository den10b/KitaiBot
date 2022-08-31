from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, registry
# from pydantic import PostgresDsn
#
# SQLALCHEMY_DATABASE_URI = PostgresDsn.build(
#     scheme="public",
#     user="postgres",
#     password="1234",
#     host="localhost",
#     path="postgres",
# )
# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost/postgres"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()


# mapper_registry = registry()

Base = declarative_base()
# MetaData = mapper_registry.metadata
