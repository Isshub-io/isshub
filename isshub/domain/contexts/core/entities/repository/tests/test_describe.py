"""Module holding BDD tests for isshub Repository core entity."""

from pytest_bdd import given, parsers, scenarios, then

from .fixtures import repository_factory


scenarios("../features/describe.feature")


@given("a Repository")
def repository(repository_factory):
    return repository_factory()


@then(parsers.parse("it must have a field named {field_name:w}"))
def repository_has_field(repository, field_name):
    assert hasattr(repository, field_name)
