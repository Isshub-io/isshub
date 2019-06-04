"""Package defining the ``Namespace`` entity."""

from typing import Optional

from isshub.domain.utils.entity import (
    BaseModelWithId,
    optional_field,
    required_field,
    validated,
)


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

    """

    name: str = required_field(str)  # type: ignore
    namespace = None


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

    """

    namespace: Optional[_Namespace] = optional_field(_Namespace)  # type: ignore
