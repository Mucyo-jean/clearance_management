"""Alembic environment.

The database URL is taken from application settings rather than from
alembic.ini, so the credentials live in exactly one place (.env) and
alembic.ini stays safe to commit.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import settings

# Importing the package registers every model on Base.metadata. Without this,
# autogenerate would see an empty metadata and generate a migration that
# drops all the tables.
from app.models import Base  # noqa: F401
import app.models  # noqa: F401

config = context.config

# Deliberately NOT config.set_main_option("sqlalchemy.url", ...).
# alembic.ini is parsed by configparser, which reads "%" as interpolation
# syntax. A URL-encoded password such as "Kirenga%40123" would raise
# "invalid interpolation syntax". The engine is built directly from settings
# in run_migrations_online() instead, so the URL never passes through
# configparser at all.

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Emit SQL to stdout without connecting — useful for review."""
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Connect and apply migrations."""
    connectable = create_engine(settings.DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,            # notice column type changes
            compare_server_default=True,  # notice default changes
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
