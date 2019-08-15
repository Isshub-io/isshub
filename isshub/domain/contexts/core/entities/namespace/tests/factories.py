"""Module defining factories for the Namespace core entity."""

import factory

from faker_enum import EnumProvider

from isshub.domain.contexts.core.entities.namespace import Namespace, NamespaceKind


factory.Faker.add_provider(EnumProvider)


class NamespaceFactory(factory.Factory):
    """Factory for the ``Namespace`` core entity."""

    class Meta:
        """Factory config."""

        model = Namespace

    id = factory.Faker("pyint", min_value=1)
    name = factory.Faker("pystr", min_chars=2)
    kind = factory.Faker("enum", enum_cls=NamespaceKind)
