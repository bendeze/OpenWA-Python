import os

import dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

ENV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
)
env = dotenv.dotenv_values(ENV_PATH)

db_type = env.get("DATABASE_TYPE", "sqlite")
db_name = env.get("DATABASE_NAME", "openwa")
db_host = env.get("DATABASE_HOST", "postgres")
db_port = env.get("DATABASE_PORT", "5432")
db_user = env.get("DATABASE_USERNAME", "openwa")
db_pass = env.get("DATABASE_PASSWORD", "openwa")

if db_type == "postgres":
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    )
    connect_args = {}
else:
    # Always force SQLite to save into the data folder at the root of the project
    db_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "data", f"{db_name}.db"
        )
    )
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
    connect_args = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
