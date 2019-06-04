"""Module holding BDD tests for isshub Repository core entity."""

import pytest
from pytest import mark
from pytest_bdd import given, parsers, scenario, scenarios, then

from isshub.domain.utils.testing.validation import positive_integer_only, string_only

from .fixtures import repository_factory


@mark.parametrize(["value", "exception"], positive_integer_only)
@scenario("../features/describe.feature", "A Repository id is a positive integer")
def test_repository_id_is_a_positive_integer(value, exception):
    pass


@mark.parametrize(["value", "exception"], string_only)
@scenario("../features/describe.feature", "A Repository name is a string")
def test_repository_name_is_a_string(value, exception):
    pass


@mark.parametrize(["value", "exception"], string_only)
@scenario("../features/describe.feature", "A Repository namespace is a string")
def test_repository_namespace_is_a_string(value, exception):
    pass


scenarios("../features/describe.feature")


@given("a Repository")
def repository(repository_factory):
    return repository_factory()


@then(parsers.parse("it must have a field named {field_name:w}"))
def repository_has_field(repository, field_name):
    assert hasattr(repository, field_name)


@then(parsers.parse("its {field_name:w} must be a {field_type}"))
def repository_field_is_of_a_certain_type(
    repository_factory,
    field_name,
    field_type,
    # next args are for parametrize
    value,
    exception,
):
    # `field_type` is ignored: the type must be managed via parametrize at the
    # scenario level, passing values to test and the exception that must be raised
    # in case of failure, or `None` if the value is valid
    if exception:
        # When creating an instance
        with pytest.raises(exception):
            repository_factory(**{field_name: value})
        # When updating the value
        repository = repository_factory()
        setattr(repository, field_name, value)
        with pytest.raises(exception):
            repository.validate()
    else:
        # When creating an instance
        repository_factory(**{field_name: value})
        # When updating the value
        repository = repository_factory()
        setattr(repository, field_name, value)
        repository.validate()


@then(parsers.parse("its {field_name:w} cannot be none"))
def repository_field_cannot_be_none(repository_factory, field_name):
    # When creating an instance
    with pytest.raises(TypeError):
        repository_factory(**{field_name: None})
    # When updating the value
    repository = repository_factory()
    repository.id = None
    with pytest.raises(TypeError):
        repository.validate()
