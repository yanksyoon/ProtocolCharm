#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charm the service.

Refer to the following tutorial that will help you
develop a new k8s charm using the Operator Framework:

https://juju.is/docs/sdk/create-a-minimal-kubernetes-charm
"""

import logging
import typing

import ops
from database import DatabaseObserver
from printenv import PrintEnvService

# Log messages can be retrieved using juju debug-log
logger = logging.getLogger(__name__)


class PrintEnvCharm(ops.CharmBase):
    """Charm the service."""

    def __init__(self, *args):
        """Initialize the charm.
        
        Args:
            args: CharmBase arguments.
        """
        super().__init__(*args)

        self.printenv_service = PrintEnvService(self)
        self.database_service = DatabaseObserver(self)
        self.framework.observe(self.on.config_changed, self._on_config_changed)

    def merge_envs(self, envs: typing.Iterable[typing.Dict]) -> typing.Dict[str, str]:
        """Merge all environment variables of sub-services.
        
        Args:
            envs: The environment dictionaries to merge.

        Returns:
            The merged environment variable dictionary.
        """
        merged = {}
        for env in envs:
            merged.update(env.items())
        return merged

    @property
    def printenv_container(self):
        """The main printenv workload container."""
        return self.unit.get_container("printenv")

    def _on_config_changed(self, _: ops.ConfigChangedEvent):
        """Handle changed configuration."""
        log_level = self.model.config["log-level"].lower()
        self.unit.status = ops.MaintenanceStatus("Configuring log level.")
        self.printenv_service.replan(self.merge_envs(({"log_level": log_level},)))
        self.unit.status = ops.ActiveStatus()


if __name__ == "__main__":  # pragma: nocover
    ops.main(PrintEnvCharm)  # type: ignore
