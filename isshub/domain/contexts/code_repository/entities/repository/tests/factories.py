"""Module defining factories for the Repository code_repository entity."""

import factory

from isshub.domain.contexts.code_repository.entities.repository import Repository

from ...namespace.tests.factories import NamespaceFactory


class RepositoryFactory(factory.Factory):
    """Factory for the ``Repository`` code_repository entity."""

    class Meta:
        """Factory config."""

        model = Repository

    id = factory.Faker("pyint", min_value=1)
    name = factory.Faker("pystr", min_chars=2)
    namespace = factory.SubFactory(NamespaceFactory)
