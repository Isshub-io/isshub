"""Module holding BDD tests for isshub Repository code_repository entity."""
from functools import partial
from uuid import uuid4

import pytest
from pytest import mark
from pytest_bdd import given, parsers, scenario, scenarios, then

from isshub.domain.utils.testing.validation import (
    FrozenAttributeError,
    check_field,
    check_field_not_nullable,
    check_field_value,
    string_only,
    uuid4_only,
)

from ...namespace.tests.fixtures import namespace
from .fixtures import repository_factory


FEATURE_FILE = "../features/describe.feature"
scenario = partial(scenario, FEATURE_FILE)


@mark.parametrize(["value", "exception"], uuid4_only)
@scenario("A repository identifier is a uuid")
def test_repository_identifier_is_a_uuid(value, exception):
    pass


@mark.parametrize(["value", "exception"], string_only)
@scenario("A repository name is a string")
def test_repository_name_is_a_string(value, exception):
    pass


@mark.parametrize(
    ["value", "exception"],
    [(pytest.lazy_fixture("namespace"), None), ("foo", TypeError), (1, TypeError)],
)
@scenario("A repository namespace is a Namespace")
def test_repository_namespace_is_a_namespace(value, exception):
    pass


@given("a repository", target_fixture="repository")
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


@scenario("A repository identifier cannot be changed")
def test_repository_identifier_cannot_be_changed():
    pass


@then("its identifier cannot be changed")
def repository_identifier_cannot_be_changed(repository):
    with pytest.raises(FrozenAttributeError):
        repository.identifier = uuid4()


# To make pytest-bdd fail if some scenarios are not implemented. KEEP AT THE END
scenarios(FEATURE_FILE)
