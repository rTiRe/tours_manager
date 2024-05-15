"""Database setup."""

from types import MethodType
from typing import Any

from django.db import connections
from django.db.backends.base.base import BaseDatabaseWrapper
from django.test.runner import DiscoverRunner


def prepare_db(self):
    """Create database schema.

    Args:
        self: type - class object.

    """
    self.connect()
    self.connection.cursor().execute('CREATE SCHEMA IF NOT EXISTS tours_data;')


class PostgresSchemaRunner(DiscoverRunner):
    """Run table schema."""

    def setup_databases(self, **kwargs: Any) -> list[tuple[BaseDatabaseWrapper, str, bool]]:
        """Pre-setup database for work.

        Args:
            kwargs: Any - key word arguments.

        Returns:
            list[tuple[BaseDatabaseWrapper, str, bool]]: setupped database.
        """
        for conn_name in connections:
            connection = connections[conn_name]
            connection.prepare_database = MethodType(prepare_db, connection)
        return super().setup_databases(**kwargs)
