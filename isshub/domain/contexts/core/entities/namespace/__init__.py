"""Package defining the ``Namespace`` entity."""

import enum
from typing import Optional

from isshub.domain.utils.entity import (
    BaseModelWithId,
    optional_field,
    required_field,
    validated,
)


class NamespaceKind(enum.Enum):
    """All the available kinds of namespace."""

    ORGANIZATION = "Organization"
    TEAM = "Team"
    GROUP = "Group"


@validated()  # type: ignore
class _Namespace(BaseModelWithId):
    """A namespace can contain namespace and repositories.

    Notes
    -----
    This is a base class, used by `Namespace` to be able to have a self-reference for the type
    of the `namespace` field.

    Attributes
    ----------
    id : int
        The unique identifier of the namespace
    name : str
        The name of the namespace. Unique in its parent namespace.
    namespace : Optional[Namespace]
        Where the namespace can be found.
    kind : NamespaceKind
        The kind of namespace.

    """

    name: str = required_field(str)  # type: ignore
    namespace = None
    kind: NamespaceKind = required_field(NamespaceKind)  # type: ignore


@validated()  # type: ignore
class Namespace(_Namespace):
    """A namespace can contain namespace and repositories.

    Attributes
    ----------
    id : int
        The unique identifier of the namespace
    name : str
        The name of the namespace. Unique in its parent namespace.
    namespace : Optional[str]
        Where the namespace can be found.
    kind : NamespaceKind
        The kind of namespace.

    """

    namespace: Optional[_Namespace] = optional_field(_Namespace)  # type: ignore
