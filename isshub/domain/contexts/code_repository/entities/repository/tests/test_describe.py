"""Module holding BDD tests for isshub Repository code_repository entity."""

import pytest
from pytest import mark
from pytest_bdd import given, parsers, scenario, scenarios, then

from isshub.domain.utils.testing.validation import (
    FrozenAttributeError,
    check_field,
    check_field_not_nullable,
    check_field_value,
    positive_integer_only,
    string_only,
)

from ...namespace.tests.fixtures import namespace
from .fixtures import repository_factory


@mark.parametrize(["value", "exception"], positive_integer_only)
@scenario("../features/describe.feature", "A Repository id is a positive integer")
def test_repository_id_is_a_positive_integer(value, exception):
    pass


@mark.parametrize(["value", "exception"], string_only)
@scenario("../features/describe.feature", "A Repository name is a string")
def test_repository_name_is_a_string(value, exception):
    pass


@mark.parametrize(
    ["value", "exception"],
    [(pytest.lazy_fixture("namespace"), None), ("foo", TypeError), (1, TypeError)],
)
@scenario("../features/describe.feature", "A Repository namespace is a Namespace")
def test_repository_namespace_is_a_namespace(value, exception):
    pass


scenarios("../features/describe.feature")


@given("a Repository", target_fixture="repository")
def a_repository(repository_factory):
    return repository_factory()


@then(parsers.parse("it must have a field named {field_name:w}"))
def repository_has_field(repository, field_name):
    check_field(repository, field_name)


@then(parsers.parse("its {field_name:w} must be a {field_type}"))
def repository_field_is_of_a_certain_type(
    repository_factory,
    field_name,
    field_type,
    # next args are for parametrize
    value,
    exception,
):
    check_field_value(repository_factory, field_name, value, exception)


@then(parsers.parse("its {field_name:w} is mandatory"))
def repository_field_is_mandatory(repository_factory, field_name):
    check_field_not_nullable(repository_factory, field_name)


@scenario("../features/describe.feature", "A Repository id cannot be changed")
def test_repository_id_cannot_be_changed():
    pass


@then("its id cannot be changed")
def repository_id_cannot_be_changed(repository):
    with pytest.raises(FrozenAttributeError):
        repository.id = repository.id + 1
