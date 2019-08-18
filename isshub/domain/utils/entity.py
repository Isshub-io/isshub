"""Package to handle isshub entities validation.

It is an adapter over the ``attrs`` external dependency.

"""

# type: ignore

import attr


def optional_field(field_type):
    """Define an optional field of the specified `field_type`.

    Parameters
    ----------
    field_type : type
        The expected type of the field when not ``None``.

    Returns
    -------
    Any
        An ``attrs`` attribute, with a default value set to ``None``, and a validator checking
        that this field is optional and, if set, of the correct type.

    """
    return attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(field_type)),
    )


def required_field(field_type):
    """Define a required field of the specified `field_type`.

    Parameters
    ----------
    field_type : type
        The expected type of the field..

    Returns
    -------
    Any
        An ``attrs`` attribute, and a validator checking that this field is of the correct type.

    """
    return attr.ib(validator=attr.validators.instance_of(field_type))


def validated():
    """Decorate an entity to handle validation.

    This will let ``attrs`` manage the class, using slots for fields.

    Returns
    -------
    type
        The decorated class.

    """
    return attr.s(slots=True)


def field_validator(field):
    """Decorate an entity method to make it a validator of the given `field`.

    Parameters
    ----------
    field : Any
        The field to validate.

    Returns
    -------
    Callable
        The decorated method.

    """
    return field.validator


def validate_instance(instance):
    """Validate a whole instance.

    Parameters
    ----------
    instance : Any
        The instance to validate.

    Raises
    ------
    TypeError, ValueError
        If a field in the `instance` is not valid.

    """
    attr.validate(instance)


def validate_positive_integer(value, none_allowed, display_name):
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

    """
    if none_allowed and value is None:
        return

    if not isinstance(value, int):
        raise TypeError(f"{display_name} must be a positive integer")
    if value <= 0:
        raise ValueError(f"{display_name} must be a positive integer")


@validated()
class BaseModel:
    """A base model without any field, that is able to validate itself."""

    def validate(self) -> None:
        """Validate all fields of the current instance.

        Raises
        ------
        TypeError, ValueError
            If a field is not valid.

        """
        validate_instance(self)


@validated()
class BaseModelWithId(BaseModel):
    """A base model with an ``id``, that is able to validate itself.

    Attributes
    ----------
    id : int
        The identifier of the instance. Validated to be a positive integer.

    """

    id: int = required_field(int)

    @field_validator(id)
    def validate_id_is_positive_integer(  # noqa  # pylint: disable=unused-argument
        self, field, value
    ):
        """Validate that the ``id`` field is a positive integer.

        Parameters
        ----------
        field : Any
            The field to validate. Passed via the ``@field_validator`` decorator.
        value : Any
            The value to validate for the `field`.

        """
        validate_positive_integer(
            value=value,
            none_allowed=False,
            display_name=f"{self.__class__.__name__}.id",
        )
