import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

dirname = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(dirname, '..')))

from osm_validator.app import build_application  # isort:skip  # noqa
from osm_validator.settings import DATABASE  # isort:skip  # noqa

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from models import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None
loop = asyncio.get_event_loop()
app = loop.run_until_complete(build_application())
target_metadata = app.db.Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
config.set_main_option('sqlalchemy.url', "postgresql://{}:{}@{}/{}".format(
    DATABASE['user'],
    DATABASE['password'],
    DATABASE['host'],
    DATABASE['database']))


def exclude_tables_from_config(config):
    tables = config.get('tables', [])
    if tables:
        tables = tables.split(',')
    return tables


exclude_tables = exclude_tables_from_config(config.get_section('alembic:exclude'))


def include_object(object, name, type_, reflected, compare_to):
    return name not in exclude_tables


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=config.get_main_option('sqlalchemy.url'),
        target_metadata=target_metadata,
        include_object=include_object,
        literal_binds=True,
        transaction_per_migration=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            transaction_per_migration=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
