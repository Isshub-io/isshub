"""Package defining the :obj:`Repository` entity."""

from isshub.domain.contexts.code_repository.entities.namespace import Namespace
from isshub.domain.utils.entity import (
    BaseEntityWithIdentifier,
    required_field,
    validated,
)


@validated()
class Repository(BaseEntityWithIdentifier):
    """A repository holds code, issues, code requests...

    Attributes
    ----------
    identifier : UUID
        The unique identifier of the repository
    name : str
        The name of the repository. Unique in its namespace.
    namespace : Namespace
        Where the repository can be found.

    """

    name: str = required_field(str)
    namespace: Namespace = required_field(Namespace, relation_verbose_name="belongs to")
