# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Database observer module."""
import typing

import ops
from charms.data_platform_libs.v0.data_interfaces import (
    DatabaseCreatedEvent,
    DatabaseEndpointsChangedEvent,
    DatabaseRequires,
)

from protocol import CharmProtocol


class DatabaseObserver(ops.Object):
    """The database observer."""

    def __init__(self, charm: CharmProtocol):
        """Initialize the Database Observer.
        
        Args:
            charm: The main charm.
        """
        super().__init__(typing.cast(ops.CharmBase, charm), "database_service")
        self.charm = charm
        self.database = DatabaseRequires(
            charm, relation_name="database", database_name=self.charm.app.name
        )

        charm.framework.observe(self.database.on.database_created, self._on_database_created)
        charm.framework.observe(
            self.database.on.endpoints_changed, self._on_database_endpoints_changed
        )

    @property
    def pebble_env(self) -> typing.Dict[str, str]:
        """The database environment variables for pebble."""
        relation = self.model.get_relation("database")
        if not relation:
            return {"database": "false"}
        return {
            "database": "true",
            "db_user": relation.data[relation.app].get("username"),
            "db_password": relation.data[relation.app].get("password"),
            "db_endpoints": relation.data[relation.app].get("endpoints"),
        }

    def _on_database_created(self, _: DatabaseCreatedEvent):
        """Handle database created event."""
        envs = self.charm.merge_envs((self.charm.printenv_service.pebble_env, self.pebble_env))
        self.charm.unit.status = ops.MaintenanceStatus("Database created.")
        self.charm.printenv_service.replan(envs)
        self.charm.unit.status = ops.ActiveStatus()

    def _on_database_endpoints_changed(self, _: DatabaseEndpointsChangedEvent):
        """Handle database endpoints changed event."""
        envs = self.charm.merge_envs((self.charm.printenv_service.pebble_env, self.pebble_env))
        self.charm.unit.status = ops.MaintenanceStatus("Database endpoints changed.")
        self.charm.printenv_service.replan(envs)
        self.charm.unit.status = ops.ActiveStatus()
