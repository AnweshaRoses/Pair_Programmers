from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool

from app.db.base import Base
from app.models.room import Room  # ensure model is imported
from app.core.config import settings

import os
from dotenv import load_dotenv

load_dotenv()

# Alembic Config
config = context.config

# Interpret logging from alembic.ini
fileConfig(config.config_file_name)

# Metadata used for autogenerate
target_metadata = Base.metadata


database_url = (
    settings.DATABASE_URL
    or os.getenv("DATABASE_URL")
    or config.get_main_option("sqlalchemy.url")
)


if "+asyncpg" in database_url:
    database_url = database_url.replace("+asyncpg", "")

config.set_main_option("sqlalchemy.url", database_url)


# OFFLINE MIGRATIONS

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ONLINE MIGRATIONS

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# RUN

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
