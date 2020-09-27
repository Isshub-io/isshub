"""Package defining the ``Namespace`` entity."""

import enum
from typing import Any, Optional

from isshub.domain.utils.entity import (
    BaseModelWithId,
    field_validator,
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
    """A namespace can contain namespaces and repositories.

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
    description : Optional[str]
        The description of the namespace.

    """

    name: str = required_field(str)  # type: ignore
    namespace = None
    kind: NamespaceKind = required_field(NamespaceKind)  # type: ignore
    description: str = optional_field(str)  # type: ignore


@validated()  # type: ignore
class Namespace(_Namespace):
    """A namespace can contain namespaces and repositories.

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
    description : Optional[str]
        The description of the namespace.

    """

    namespace: Optional[_Namespace] = optional_field(_Namespace)  # type: ignore

    @field_validator(namespace)  # type: ignore
    def validate_namespace_is_not_in_a_loop(  # noqa  # pylint: disable=unused-argument
        self, field: Any, value: Any
    ) -> None:
        """Validate that the ``namespace`` field is not in a loop.

        Being in a loop means that one of the descendants is the parent of one of the ascendants.

        Parameters
        ----------
        field : Any
            The field to validate. Passed via the ``@field_validator`` decorator.
        value : Any
            The value to validate for the `field`.

        Raises
        ------
        ValueError
            If the given namespace (`value`) is in a loop

        """
        if not value:
            return

        parent = value
        while parent := parent.namespace:
            if parent == value:
                raise ValueError(
                    f"{self.__class__.__name__}.namespace cannot be in a loop"
                )
