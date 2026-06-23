import os

import dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

ENV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
)
env = dotenv.dotenv_values(ENV_PATH)

db_type = env.get("DATABASE_TYPE") or os.environ.get("DATABASE_TYPE", "sqlite")
db_name = env.get("DATABASE_NAME") or os.environ.get("DATABASE_NAME", "openwa")
db_host = env.get("DATABASE_HOST") or os.environ.get("DATABASE_HOST", "postgres")
db_port = env.get("DATABASE_PORT") or os.environ.get("DATABASE_PORT", "5432")
db_user = env.get("DATABASE_USERNAME") or os.environ.get("DATABASE_USERNAME", "openwa")
db_pass = env.get("DATABASE_PASSWORD") or os.environ.get("DATABASE_PASSWORD", "openwa")

if db_type == "postgres":
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    )
    connect_args = {}
else:
    # Ensure SQLite saves to the data folder appropriately
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(base_dir) == "app":
        # In Docker, we are at /app, and volume is /app/data
        data_dir = os.path.join(base_dir, "data")
    else:
        # Locally, we are at /api-gateway, and data is at /data
        data_dir = os.path.join(base_dir, "..", "data")

    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.abspath(os.path.join(data_dir, f"{db_name}.db"))
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
