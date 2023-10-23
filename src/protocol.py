# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""The charm protocol to provide reduced coupling between services."""

import typing
from abc import abstractmethod, abstractproperty

import ops

if typing.TYPE_CHECKING:
    from database import DatabaseObserver
    from printenv import PrintEnvService


class CharmInterface(typing.Protocol):
    """The interface that defines the components of a charm with complex relations."""

    # Commonly used variables can also be defined here to reduce code duplication.
    @abstractproperty
    def printenv_container(self) -> ops.Container:
        """Workload container for PrintEnv."""
        pass

    # Helper methods can come here if necessary.
    @abstractmethod
    def merge_envs(self, envs: typing.Iterable[typing.Dict]) -> typing.Dict[str, str]:
        """Merge all environment variables.

        Args:
            envs: Environment variables to merge.
        """
        pass

    # Different services can be composed here for accessibility.
    @abstractproperty
    def printenv_service(self) -> "PrintEnvService":
        """Printenv workload service."""
        pass

    @abstractproperty
    def database_service(self) -> "DatabaseObserver":
        """Database observer service."""
        pass


CharmProtocol = typing.Union[CharmInterface, ops.CharmBase]
