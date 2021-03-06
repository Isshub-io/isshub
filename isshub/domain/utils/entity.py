"""Package to handle isshub entities validation.

It is an adapter over the ``attrs`` external dependency.

"""
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)
from uuid import UUID

import attr


_T = TypeVar("_T")

if TYPE_CHECKING:
    from attr.__init__ import Attribute  # isort:skip
else:

    class Attribute(Generic[_T]):
        """Class for typing when not using mypy, for example when using ``get_type_hints``.

        :meta private:
        """


class _InstanceOfSelfValidator(
    attr.validators._InstanceOfValidator  # type: ignore  # pylint: disable=protected-access
):
    """Validator checking that the field holds an instance of its own entity."""

    def __call__(self, inst, attr, value):  # type: ignore  # pylint: disable=redefined-outer-name
        """Validate that the `value` is an instance of the class of `inst`.

        For the parameters, see ``attr.validators._InstanceOfValidator``
        """
        self.type = inst.__class__
        super().__call__(inst, attr, value)


def instance_of_self() -> _InstanceOfSelfValidator:
    """Return a validator checking that the field holds an instance of its own entity.

    Returns
    -------
    _InstanceOfSelfValidator
        The instantiated validator
    """
    return _InstanceOfSelfValidator(type=None)


def optional_field(
    field_type: Union[Type[_T], str], relation_verbose_name: Optional[str] = None
) -> Optional[_T]:
    """Define an optional field of the specified `field_type`.

    Parameters
    ----------
    field_type : Union[type, str]
        The expected type of the field. Use the string "self" to reference the current field's
        entity
    relation_verbose_name : Optional[str]
        A verbose name to describe the relation between the entity linked to the field, and the
        entity pointed by `field_type`

    Returns
    -------
    Any
        An ``attrs`` attribute, with a default value set to ``None``, and a validator checking
        that this field is optional and, if set, of the correct type.

    Raises
    ------
    AssertionError
        If `field_type` is a string and this string is not "self"

    Examples
    --------
    >>> from isshub.domain.utils.entity import optional_field, validated, BaseEntity
    >>>
    >>> @validated()
    ... class MyEntity(BaseEntity):
    ...     my_field: str = optional_field(str)
    >>>
    >>> from isshub.domain.utils.testing.validation import check_field_nullable
    >>> check_field_nullable(MyEntity, 'my_field', my_field='foo')

    """
    metadata = {}
    if relation_verbose_name:
        metadata["relation_verbose_name"] = relation_verbose_name

    assert not isinstance(field_type, str) or field_type == "self"

    return attr.ib(
        default=None,
        validator=attr.validators.optional(
            instance_of_self()
            if isinstance(field_type, str)
            else attr.validators.instance_of(field_type)
        ),
        metadata=metadata,
    )


def required_field(
    field_type: Union[Type[_T], str],
    frozen: bool = False,
    relation_verbose_name: Optional[str] = None,
) -> _T:
    """Define a required field of the specified `field_type`.

    Parameters
    ----------
    field_type : Union[type, str]
        The expected type of the field. Use the string "self" to reference the current field's
        entity
    frozen : bool
        If set to ``False`` (the default), the field can be updated after being set at init time.
        If set to ``True``, the field can be set at init time but cannot be changed later, else a
        ``FrozenAttributeError`` exception will be raised.
    relation_verbose_name : Optional[str]
        A verbose name to describe the relation between the entity linked to the field, and the
        entity pointed by `field_type`

    Returns
    -------
    Any
        An ``attrs`` attribute, and a validator checking that this field is of the correct type.

    Raises
    ------
    AssertionError
        If `field_type` is a string and this string is not "self"

    Examples
    --------
    >>> from isshub.domain.utils.entity import required_field, validated, BaseEntity
    >>>
    >>> @validated()
    ... class MyEntity(BaseEntity):
    ...     my_field: str = required_field(str)
    >>>
    >>> from isshub.domain.utils.testing.validation import check_field_not_nullable
    >>> check_field_not_nullable(MyEntity, 'my_field', my_field='foo')

    """
    metadata = {}
    if relation_verbose_name:
        metadata["relation_verbose_name"] = relation_verbose_name

    assert not isinstance(field_type, str) or field_type == "self"

    kwargs = {
        "validator": instance_of_self()
        if isinstance(field_type, str)
        else attr.validators.instance_of(field_type),
        "metadata": metadata,
    }
    if frozen:
        kwargs["on_setattr"] = attr.setters.frozen

    return attr.ib(**kwargs)  # type: ignore


def validated() -> Any:
    """Decorate an entity to handle validation.

    This will let ``attrs`` manage the class, using slots for fields, and forcing attributes to
    be passed as named arguments (this allows to not have to defined all required fields first, then
    optional ones, and resolves problems with inheritance where we can't handle the order)

    Returns
    -------
    type
        The decorated class.

    Examples
    --------
    >>> from isshub.domain.utils.entity import required_field, validated, BaseEntity
    >>>
    >>> @validated()
    ... class MyEntity(BaseEntity):
    ...     my_field: str = required_field(str)
    >>>
    >>> MyEntity.__slots__
    ('my_field',)
    >>>
    >>> instance = MyEntity()
    Traceback (most recent call last):
        ...
    TypeError: __init__() missing 1 required keyword-only argument: 'my_field'
    >>> instance = MyEntity(my_field='foo')
    >>> instance.my_field
    'foo'
    >>> instance.validate()
    >>> instance.my_field = None
    >>> instance.validate()
    Traceback (most recent call last):
        ...
    TypeError: ("'my_field' must be <class 'str'> (got None that is a <class 'NoneType'>)...

    """
    return attr.s(slots=True, kw_only=True, eq=False)


TValidateMethod = TypeVar(
    "TValidateMethod", bound=Callable[[Any, "Attribute[_T]", _T], None]
)


class field_validator:  # pylint: disable=invalid-name
    """Decorate an entity method to make it a validator of the given `field`.

    Notes
    -----
    It's easier to implement as a function but we couldn't make mypy work with it.
    Thanks to https://github.com/python/mypy/issues/1551#issuecomment-253978622

    Parameters
    ----------
    field : Any
        The field to validate.

    Examples
    --------
    >>> from isshub.domain.utils.entity import field_validator, required_field, BaseEntity
    >>>
    >>> @validated()
    ... class MyEntity(BaseEntity):
    ...    my_field: str = required_field(str)
    ...
    ...    @field_validator(my_field)
    ...    def validate_my_field(self, field, value):
    ...        if value != 'foo':
    ...            raise ValueError(f'{self.__class__.__name__}.my_field must be "foo"')
    >>>
    >>> instance = MyEntity(my_field='bar')
    Traceback (most recent call last):
        ...
    ValueError: MyEntity.my_field must be "foo"
    >>> instance = MyEntity(my_field='foo')
    >>> instance.my_field
    'foo'
    >>> instance.my_field = 'bar'
    >>> instance.validate()
    Traceback (most recent call last):
        ...
    ValueError: MyEntity.my_field must be "foo"
    >>> instance.my_field = 'foo'
    >>> instance.validate()
    >>> instance.my_field
    'foo'

    """

    def __init__(self, field: "Attribute[_T]") -> None:
        """Save the given field."""
        self.field = field

    def __call__(self, func: TValidateMethod) -> TValidateMethod:
        """Decorate the given function.

        Parameters
        ----------
        func: Callable
            The validation method to decorate

        Returns
        -------
        Callable
            The decorated method.

        """
        return cast(TValidateMethod, self.field.validator(func))


def validate_instance(instance: Any) -> Any:
    """Validate a whole instance.

    Parameters
    ----------
    instance : Any
        The instance to validate.

    Raises
    ------
    TypeError, ValueError
        If a field in the `instance` is not valid.

    Examples
    --------
    >>> from isshub.domain.utils.entity import required_field, validate_instance, BaseEntity
    >>>
    >>> @validated()
    ... class MyEntity(BaseEntity):
    ...    my_field: str = required_field(str)
    >>>
    >>> instance = MyEntity(my_field='foo')
    >>> validate_instance(instance)
    >>> instance.my_field = None
    >>> validate_instance(instance)
    Traceback (most recent call last):
        ...
    TypeError: ("'my_field' must be <class 'str'> (got None that is a <class 'NoneType'>)...

    """
    attr.validate(instance)


def validate_positive_integer(
    value: Any, none_allowed: bool, display_name: str
) -> None:
    """Validate that the given `value` is a positive integer (``None`` accepted if `none_allowed`).

    Parameters
    ----------
    value : Any
        The value to validate as a positive integer.
    none_allowed : bool
        If ``True``, the value can be ``None``. If ``False``, the value must be a positive integer.
    display_name : str
        The name of the field to display in errors.

    Raises
    ------
    TypeError
        If `value` is not of type ``int``.
    ValueError
        If `value` is not a positive integer (ie > 0), or ``None`` if `none_allowed` is ``True``.

    Examples
    --------
    >>> from isshub.domain.utils.entity import field_validator, required_field, BaseEntity
    >>>
    >>> @validated()
    ... class MyEntity(BaseEntity):
    ...    my_field: int = required_field(int)
    ...
    ...    @field_validator(my_field)
    ...    def validate_my_field(self, field, value):
    ...        validate_positive_integer(
    ...            value=value,
    ...            none_allowed=False,
    ...            display_name=f"{self.__class__.__name__}.my_field",
    ...        )
    >>>
    >>> instance = MyEntity(my_field='foo')
    Traceback (most recent call last):
        ...
    TypeError: ("'my_field' must be <class 'int'> (got 'foo' that is a <class 'str'>)...
    >>> instance = MyEntity(my_field=-2)
    Traceback (most recent call last):
        ...
    ValueError: MyEntity.my_field must be a positive integer
    >>> instance = MyEntity(my_field=0)
    Traceback (most recent call last):
        ...
    ValueError: MyEntity.my_field must be a positive integer
    >>> instance = MyEntity(my_field=1.1)
    Traceback (most recent call last):
        ...
    TypeError: ("'my_field' must be <class 'int'> (got 1.1 that is a <class 'float'>)...
    >>> instance = MyEntity(my_field=1)
    >>> instance.my_field = -2
    >>> instance.validate()
    Traceback (most recent call last):
        ...
    ValueError: MyEntity.my_field must be a positive integer

    """
    if none_allowed and value is None:
        return

    if not isinstance(value, int):
        raise TypeError(f"{display_name} must be a positive integer")
    if value <= 0:
        raise ValueError(f"{display_name} must be a positive integer")


def validate_uuid(value: Any, none_allowed: bool, display_name: str) -> None:
    """Validate that the given `value` is a uuid (version 4) (``None`` accepted if `none_allowed`).

    Parameters
    ----------
    value : Any
        The value to validate as a uuid.
    none_allowed : bool
        If ``True``, the value can be ``None``. If ``False``, the value must be a uuid.
    display_name : str
        The name of the field to display in errors.

    Raises
    ------
    TypeError
        If `value` is not of type ``UUID`` version 4 .

    Examples
    --------
    >>> from uuid import UUID
    >>> from isshub.domain.utils.entity import field_validator, required_field, BaseEntity
    >>>
    >>> @validated()
    ... class MyEntity(BaseEntity):
    ...    my_field: UUID = required_field(UUID)
    ...
    ...    @field_validator(my_field)
    ...    def validate_my_field(self, field, value):
    ...        validate_uuid(
    ...            value=value,
    ...            none_allowed=False,
    ...            display_name=f"{self.__class__.__name__}.my_field",
    ...        )
    >>>
    >>> instance = MyEntity(my_field='foo')
    Traceback (most recent call last):
        ...
    TypeError: ("'my_field' must be <class 'uuid.UUID'> (got 'foo' that is a <class 'str'>)...
    >>> instance = MyEntity(my_field='7298d61a-f08f-4f83-b75e-934e786eb43d')
    Traceback (most recent call last):
        ...
    TypeError: ("'my_field' must be <class 'uuid.UUID'> (got '7298d61a-f08f-4f83-b75e-934e786eb43d' that is a <class 'str'>)...
    >>> instance = MyEntity(my_field=UUID('19f49bc8-06e5-11eb-8465-bf44725d7bd3'))
    Traceback (most recent call last):
        ...
    TypeError: MyEntity.my_field must be a UUID version 4
    >>> instance = MyEntity(my_field=UUID('7298d61a-f08f-4f83-b75e-934e786eb43d'))
    >>> instance.my_field = UUID('19f49bc8-06e5-11eb-8465-bf44725d7bd3')
    >>> instance.validate()
    Traceback (most recent call last):
        ...
    TypeError: MyEntity.my_field must be a UUID version 4

    """
    if none_allowed and value is None:
        return

    if not isinstance(value, UUID) or value.version != 4:
        raise TypeError(f"{display_name} must be a UUID version 4")


@validated()
class BaseEntity:
    """A base entity without any field, that is able to validate itself."""

    def validate(self) -> None:
        """Validate all fields of the current instance.

        Raises
        ------
        TypeError, ValueError
            If a field is not valid.

        """
        validate_instance(self)


@validated()
class BaseEntityWithIdentifier(BaseEntity):
    """A base entity with an :obj:`~BaseEntityWithIdentifier.identifier`, that is able to validate itself.

    Attributes
    ----------
    identifier : UUID
        The identifier of the instance. Validated to be a UUID version 4.

    """

    identifier: UUID = required_field(UUID, frozen=True)

    @field_validator(identifier)
    def validate_id_is_uuid(  # noqa  # pylint: disable=unused-argument
        self, field: "Attribute[_T]", value: _T
    ) -> None:
        """Validate that the :obj:`BaseEntityWithIdentifier.identifier` field is a uuid.

        Parameters
        ----------
        field : Any
            The field to validate.
        value : Any
            The value to validate for the `field`.

        """
        validate_uuid(
            value=value,
            none_allowed=False,
            display_name=f"{self.__class__.__name__}.identifier",
        )

    def __hash__(self) -> int:
        """Compute the hash of the entity for python internal hashing.

        The hash is purely based on the entity's identifier, ie two different with the same
        identifier will share the same hash. And as it's the same for ``__eq__`` method, two
        different instances of the same entity class with the same identifier will always have the
        same hash.

        Returns
        -------
        int
            The hash for the entity

        """
        return hash(self.identifier)

    def __eq__(self, other: Any) -> bool:
        """Check if the `other` object is the same as the current entity.

        Parameters
        ----------
        other : Any
            The object to compare with the actual entity.

        Returns
        -------
        bool
            ``True`` if the given `other` object is an instance of the same class as the current
            entity, with the same identifier.

        """
        return self.__class__ is other.__class__ and self.identifier == other.identifier
