"""Module defining factories for the Namespace code_repository entity."""

import factory

from faker_enum import EnumProvider

from isshub.domain.contexts.code_repository.entities.namespace import (
    Namespace,
    NamespaceKind,
)


factory.Faker.add_provider(EnumProvider)


class NamespaceFactory(factory.Factory):
    """Factory for the ``Namespace`` code_repository entity."""

    class Meta:
        """Factory config."""

        model = Namespace

    identifier = factory.Faker("uuid4", cast_to=None)
    name = factory.Faker("pystr", min_chars=2)
    kind = factory.Faker("enum", enum_cls=NamespaceKind)
