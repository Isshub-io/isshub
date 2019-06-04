"""Module defining fixtures for the Namespace core entity."""


from typing import Type

from pytest import fixture

from isshub.domain.contexts.core.entities.namespace import Namespace

from .factories import NamespaceFactory


@fixture  # type: ignore
def namespace_factory() -> Type[NamespaceFactory]:
    """Fixture to return the factory to create a ``Namespace``.

    Returns
    -------
    Type[NamespaceFactory]
        The ``NamespaceFactory`` class.

    """
    return NamespaceFactory


@fixture  # type: ignore
def namespace() -> Namespace:
    """Fixture to return a ``Namespace``.

    Returns
    -------
    Namespace
        The created ``Namespace``

    """
    return NamespaceFactory()
