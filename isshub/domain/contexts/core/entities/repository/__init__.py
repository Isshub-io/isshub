"""Package defining the ``Repository`` entity."""

from dataclasses import dataclass


@dataclass
class Repository:
    """A repository holds code, issues, code requests...

    Attributes
    ----------
    id : int
        The unique identifier of the repository
    name : str
        The name of the repository. Unique in its namespace.
    namespace : str
        Where the repository can be found.

    """

    __slots__ = ["id", "name", "namespace"]

    id: int
    name: str
    namespace: str
