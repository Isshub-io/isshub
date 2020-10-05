"""Package defining bases for domain repositories."""

import abc
from inspect import isabstract
from typing import Any, Generic, Optional, Set, Type, TypeVar
from uuid import UUID

from isshub.domain.utils.entity import BaseEntityWithIdentifier


Entity = TypeVar("Entity", bound=BaseEntityWithIdentifier)


class RepositoryException(Exception):
    """Exception raised in a repository context.

    Attributes
    ----------
    repository: Optional[Type[AbstractRepository]]
        An optional repository attached to the exception or the exception class.

    """

    repository: Optional[Type["AbstractRepository"]] = None

    def __init__(
        self,
        message: str,
        repository: Optional[Type["AbstractRepository"]] = None,
    ) -> None:
        """Create the exception with a repository and formatted message.

        Parameters
        ----------
        message : str
            The message of the exception. Will be prefixed by the name of the repository and its
            entity class.
        repository : Optional[Type[AbstractRepository]]
            The repository (class) having raised the exception. To get the related entity class, use
            ``the_exception.repository.entity_class``.
        """
        if repository:
            self.repository = repository
        if self.repository is not None:
            entity_name = ""
            if self.repository.entity_class is not None:
                entity_name = f"[{self.repository.entity_class.__name__}]"
            message = f"{self.repository.__name__}{entity_name}: {message}"
        super().__init__(message)


class UniquenessError(RepositoryException):
    """Exception raised when an entity is added/updated that already exists."""


class NotFoundError(RepositoryException):
    """Exception raised when an entity couldn't be found in its repository."""


class AbstractRepository(abc.ABC, Generic[Entity]):
    """Base of all repositories.

    Attributes
    ----------
    entity_class : Optional[Type[Entity]]
        The entity class the repository is designed for. Passed as a named argument while defining
        the class.
    NotFoundError : Type["NotFoundError"]
        Local version of the :obj:`NotFoundError` exception, bound to the current repository.
    UniquenessError : Type["UniquenessError"]
        Local version of the :obj:`UniquenessError` exception, bound to the current repository.

    """

    entity_class: Optional[Type[Entity]] = None
    NotFoundError: Type[NotFoundError]
    UniquenessError: Type[UniquenessError]

    def __init_subclass__(
        cls,
        abstract: bool = False,
        entity_class: Optional[Type[Entity]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the subclass for the given `entity_class`, if the subclass is not abstract.

        Parameters
        ----------
        abstract : bool
            If ``False``, the default, the `entity_class` is mandatory, else it's ignored.
        entity_class : Optional[Type[Entity]]
            The entity class the repository is designed for.
        kwargs : Any
            Other arguments passed to ``super().__init_subclass__``

        Raises
        ------
        TypeError
            If the class is a concrete subclass and `entity_class` is not given or not present on
            one of its parent classes.

        """
        super().__init_subclass__(**kwargs)  # type: ignore
        if entity_class is None:
            for klass in cls.mro():
                if issubclass(klass, AbstractRepository) and klass.entity_class:
                    entity_class = klass.entity_class
                    break
        if entity_class is None:
            if not (isabstract(cls) or abstract):
                raise TypeError(
                    f"`entity_class` is required for non abstract repository {cls}"
                )
        else:
            cls.entity_class = entity_class
        cls.NotFoundError = type("NotFoundError", (NotFoundError,), {"repository": cls})
        cls.UniquenessError = type(
            "UniquenessError", (UniquenessError,), {"repository": cls}
        )

    def exists(self, identifier: UUID) -> bool:
        """Tell if an entity with the given identifier exists in the repository.

        Parameters
        ----------
        identifier : UUID
            The UUID to check for in the repository

        Returns
        -------
        bool
            ``True`` if an entity with the given UUID exists. ``False`` otherwise.

        """

    @abc.abstractmethod
    def add(self, entity: Entity) -> Entity:
        """Add the given `entity` in the repository.

        Parameters
        ----------
        entity : Entity
            The entity to add to the repository

        Returns
        -------
        Entity
            The added entity

        """

    @abc.abstractmethod
    def get(self, identifier: UUID) -> Entity:
        """Get an entity by its `identifier`.

        Parameters
        ----------
        identifier : UUID
            The identifier of the wanted entity

        Returns
        -------
        Entity
            The wanted entity

        Raises
        ------
        self.NotFoundError
            If no entity was found with the given `identifier`

        """

    @abc.abstractmethod
    def update(self, entity: Entity) -> Entity:
        """Update the given entity in the repository.

        Parameters
        ----------
        entity : Entity
            The entity to updated in the repository. It must already exist.

        Returns
        -------
        Entity
            The updated entity

        Raises
        ------
        self.NotFoundError
            If no entity was found matching the given one

        """

    @abc.abstractmethod
    def delete(self, entity: Entity) -> None:
        """Delete the given `entity` from the repository.

        For the parameters, see :obj:`AbstractRepository.delete`.

        Raises
        ------
        self.NotFoundError
            If no entity was found matching the given one

        """


class AbstractInMemoryRepository(AbstractRepository[Entity], abstract=True):
    """Repository to handle entities in memory.

    Notes
    -----
    The class is created with ``abstract=True`` because as all methods from the :obj:`AbstractRepository`
    are defined, it is not viewed as abstract by ``inspect.isabstract``.

    """

    def __init__(self) -> None:
        """Initialize the repository with an empty collection (a set)."""
        self._collection: Set[Entity] = set()
        super().__init__()

    def exists(self, identifier: UUID) -> bool:
        """Tell if an entity with the given identifier exists in the repository.

        For the parameters, see :obj:`AbstractRepository.exists`.

        Returns
        -------
        bool
            ``True`` if an entity with the given UUID exists. ``False`` otherwise.

        """
        return any(
            entity for entity in self._collection if entity.identifier == identifier
        )

    def add(self, entity: Entity) -> Entity:
        """Add the given `entity` in the repository.

        For the parameters, see :obj:`AbstractRepository.add`.

        Notes
        -----
        The `entity` will be validated before being saved.

        Returns
        -------
        Entity
            The added entity

        Raises
        ------
        self.UniquenessError
            If an entity with the same identifier as the given one already exists.

        """
        entity.validate()

        if self.exists(entity.identifier):
            raise self.UniquenessError(
                f"One already exists with identifier={entity.identifier}"
            )

        self._collection.add(entity)
        return entity

    def get(self, identifier: UUID) -> Entity:
        """Get an entity by its `identifier`.

        For the parameters, see :obj:`AbstractRepository.get`.

        Returns
        -------
        Entity
            The wanted entity

        Raises
        ------
        self.NotFoundError
            If no entity was found with the given `identifier`

        """
        try:
            return [
                entity for entity in self._collection if entity.identifier == identifier
            ][0]
        except IndexError as exception:
            raise self.NotFoundError(
                f"Unable to find one with identifier={identifier}"
            ) from exception

    def update(self, entity: Entity) -> Entity:
        """Update the given entity in the repository.

        For the parameters, see :obj:`AbstractRepository.update`.

        Notes
        -----
        The `entity` will be validated before being saved.

        Returns
        -------
        Entity
            The updated entity

        Raises
        ------
        self.NotFoundError
            If no entity was found matching the given one

        """
        entity.validate()
        self.delete(entity)
        return self.add(entity)

    def delete(self, entity: Entity) -> None:
        """Delete the given `entity` from the repository.

        For the parameters, see :obj:`AbstractRepository.delete`.

        Raises
        ------
        self.NotFoundError
            If no entity was found matching the given one

        """
        entity = self.get(entity.identifier)
        self._collection.remove(entity)
