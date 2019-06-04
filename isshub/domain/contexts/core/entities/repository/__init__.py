"""Package defining the ``Repository`` entity."""

from isshub.domain.utils.entity import BaseModelWithId, required_field, validated


@validated()  # type: ignore
class Repository(BaseModelWithId):
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

    name: str = required_field(str)  # type: ignore
    namespace: str = required_field(str)  # type: ignore
