"""Package defining the repository for the :obj:`.Repository` entity."""

import abc
from typing import Iterable

from .....utils.repository import AbstractInMemoryRepository, AbstractRepository
from ...entities import Namespace, Repository


class AbstractRepositoryRepository(
    AbstractRepository[Repository], entity_class=Repository
):
    """Base repository for the :obj:`.Repository` entity."""

    @abc.abstractmethod
    def for_namespace(self, namespace: Namespace) -> Iterable[Repository]:
        """Iterate on repositories found in the given `namespace`.

        Parameters
        ----------
        namespace : Namespace
            The namespace for which we want to find the repositories

        Returns
        -------
        Iterable[Repository]
            An iterable of the repositories found in the `namespace`

        """


class InMemoryRepositoryRepository(
    AbstractInMemoryRepository, AbstractRepositoryRepository
):
    """Repository to handle :obj:`.Repository` entities in memory."""

    def add(self, entity: Repository) -> Repository:
        """Add the given Repository `entity` in the repository.

        For the parameters, see :obj:`AbstractRepository.add`.

        Returns
        -------
        Repository
            The added Repository

        Raises
        ------
        self.UniquenessError
            - If a repository with the same identifier as the given one already exists.
            - If a repository with the same name and namespace as the given one already exists.

        """
        if any(
            repository
            for repository in self.for_namespace(entity.namespace)
            if repository.name == entity.name
        ):
            raise self.UniquenessError(
                f"One already exists with name={entity.name} and namespace={entity.namespace}"
            )
        return super().add(entity)

    def for_namespace(self, namespace: Namespace) -> Iterable[Repository]:
        """Iterate on repositories found in the given `namespace`.

        For the parameters, see :obj:`AbstractRepositoryRepository.for_namespace`

        Returns
        -------
        Iterable[Repository]
            An iterable of the repositories found in the `namespace`

        """
        return (entity for entity in self._collection if entity.namespace == namespace)
