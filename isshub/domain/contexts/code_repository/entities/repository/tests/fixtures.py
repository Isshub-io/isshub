"""Module defining fixtures for the Repository code_repository entity."""


from pytest import fixture

from .factories import RepositoryFactory


@fixture
def repository_factory():
    """Fixture to return the factory to create a ``Repository``.

    Returns
    -------
    Type[RepositoryFactory]
        The ``RepositoryFactory`` class.

    """
    return RepositoryFactory
