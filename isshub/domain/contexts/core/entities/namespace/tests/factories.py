"""Module defining factories for the Namespace core entity."""

import factory

from isshub.domain.contexts.core.entities.namespace import Namespace


class NamespaceFactory(factory.Factory):
    """Factory for the ``Namespace`` core entity."""

    class Meta:
        """Factory config."""

        model = Namespace

    id = factory.Faker("pyint", min=1)
    name = factory.Faker("pystr", min_chars=2)
