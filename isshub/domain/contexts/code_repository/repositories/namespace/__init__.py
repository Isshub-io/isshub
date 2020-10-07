"""Package defining the repository for the :obj:`.Namespace` entity."""

import abc
from typing import Iterable, Literal, Union  # type: ignore

from .....utils.repository import AbstractInMemoryRepository, AbstractRepository
from ...entities import Namespace


class AbstractNamespaceRepository(
    AbstractRepository[Namespace], entity_class=Namespace
):
    """Base repository for the :obj:`.Namespace` entity."""

    @abc.abstractmethod
    def for_namespace(
        self, namespace: Union[Namespace, Literal[None]]
    ) -> Iterable[Namespace]:
        """Iterate on namespaces found in the given `namespace`, or with no namespace if ``None``.

        Parameters
        ----------
        namespace : Union[Namespace, None]
            The namespace for which we want to find the namespaces.
            If ``None``, will look for namespaces having no parent namespace.

        Returns
        -------
        Iterable[Namespace]
            An iterable of the namespaces found in the `namespace` (or that have no namespace if
            `namespace` is ``None``)

        """


class InMemoryNamespaceRepository(
    AbstractInMemoryRepository, AbstractNamespaceRepository
):
    """Repository to handle :obj:`.Namespace` entities in memory."""

    def add(self, entity: Namespace) -> Namespace:
        """Add the given Namespace `entity` in the repository.

        For the parameters, see :obj:`AbstractRepository.add`.

        Returns
        -------
        Namespace
            The added Namespace

        Raises
        ------
        self.UniquenessError
            - If a namespace with the same identifier as the given one already exists.
            - If a namespace with the same name and parent namespace (including no namespace) as
              the given one already exists.

        """
        if any(
            namespace
            for namespace in self.for_namespace(entity.namespace)
            if namespace.name == entity.name
        ):
            raise self.UniquenessError(
                f"One already exists with name={entity.name} and namespace={entity.namespace}"
            )
        return super().add(entity)

    def for_namespace(
        self, namespace: Union[Namespace, Literal[None]]
    ) -> Iterable[Namespace]:
        """Iterate on namespaces found in the given `namespace`, or with no namespace if ``None``.

        For the parameters, see :obj:`AbstractNamespaceRepository.for_namespace`

        Returns
        -------
        Iterable[Namespace]
            An iterable of the namespaces found in the `namespace`

        """
        return (entity for entity in self._collection if entity.namespace == namespace)
