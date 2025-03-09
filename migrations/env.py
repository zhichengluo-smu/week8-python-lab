from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import your SQLAlchemy models
from app.db.db import Base
from app.models.book import Book  # Import Book model
from app.models.review import Review  # Import Review model

# Set up Alembic Config
config = context.config
fileConfig(config.config_file_name)

# Set the target metadata to Base.metadata
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
