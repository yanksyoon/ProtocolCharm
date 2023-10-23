# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Printenv module for printenv service."""

import typing

import ops
from protocol import CharmProtocol


class PrintEnvService(ops.Object):
    """The printenv pebble service."""

    def __init__(self, charm: CharmProtocol):
        """Initialize the PrintEnvService.

        Args:
            charm: The main charm.
        """
        super().__init__(typing.cast(ops.CharmBase, charm), "printenv_service")
        self.charm = charm

        charm.framework.observe(charm.on["printenv"].pebble_ready, self._on_printenv_pebble_ready)

    def _on_printenv_pebble_ready(self, _: ops.PebbleReadyEvent):
        """Start the service on pebble ready."""
        self.charm.unit.status = ops.MaintenanceStatus("Initializing service.")
        envs = self.charm.merge_envs((self.pebble_env, self.charm.database_service.pebble_env))
        self.replan(envs)
        self.charm.unit.status = ops.ActiveStatus()

    def _create_pebble_layer(self, env: typing.Dict[str, str]) -> ops.pebble.LayerDict:
        """Return a dictionary representing a Pebble layer.
        
        Args:
            env: environment variables for printenv.

        Returns:
            The pebble layer definition.
        """
        return {
            "summary": "printenv layer",
            "description": "pebble config layer for printenv",
            "services": {
                "printenv": {
                    "override": "replace",
                    "summary": "printenv",
                    "command": "npx micro -p 8080",
                    "startup": "enabled",
                    "environment": env,
                }
            },
        }

    @property
    def pebble_env(self) -> typing.Dict[str, str]:
        """Printenv service environment variables for pebble.
        
        Returns:
            The pebble environment for printenv service.
        """
        return {"initialized": "true"}

    def replan(self, env: typing.Dict[str, str]) -> None:
        """Replan the printenv service through pebble.
        
        Args:
            env: the environment variables for printenv pebble layer.
        """
        layer = self._create_pebble_layer(env)
        self.charm.printenv_container.add_layer("printenv", layer, combine=True)
        self.charm.printenv_container.replan()
