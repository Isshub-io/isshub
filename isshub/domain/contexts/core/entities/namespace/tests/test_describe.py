"""Module holding BDD tests for isshub Namespace core entity."""

import pytest
from pytest import mark
from pytest_bdd import given, parsers, scenario, scenarios, then

from isshub.domain.contexts.core.entities.namespace import NamespaceKind
from isshub.domain.utils.testing.validation import (
    check_field,
    check_field_not_nullable,
    check_field_nullable,
    check_field_value,
    positive_integer_only,
    string_only,
)

from .fixtures import namespace, namespace_factory


@mark.parametrize(["value", "exception"], positive_integer_only)
@scenario("../features/describe.feature", "A Namespace id is a positive integer")
def test_namespace_id_is_a_positive_integer(value, exception):
    pass


@mark.parametrize(["value", "exception"], string_only)
@scenario("../features/describe.feature", "A Namespace name is a string")
def test_namespace_name_is_a_string(value, exception):
    pass


@mark.parametrize(
    ["value", "exception"],
    [(pytest.lazy_fixture("namespace"), None), ("foo", TypeError), (1, TypeError)],
)
@scenario("../features/describe.feature", "A Namespace namespace is a Namespace")
def test_namespace_namespace_is_a_namespace(value, exception):
    pass


@mark.parametrize(
    ["value", "exception"],
    [(NamespaceKind.GROUP, None), ("foo", TypeError), (1, TypeError)],
)
@scenario("../features/describe.feature", "A Namespace kind is a NamespaceKind")
def test_namespace_kind_is_a_namespacekind(value, exception):
    pass


@mark.parametrize(["value", "exception"], string_only)
@scenario("../features/describe.feature", "A Namespace description is a string")
def test_namespace_description_is_a_string(value, exception):
    pass


scenarios("../features/describe.feature")


@given("a Namespace")
def namespace(namespace_factory):
    return namespace_factory()


@then(parsers.parse("it must have a field named {field_name:w}"))
def namespace_has_field(namespace, field_name):
    check_field(namespace, field_name)


@then(parsers.parse("its {field_name:w} must be a {field_type}"))
def namespace_field_is_of_a_certain_type(
    namespace_factory,
    field_name,
    field_type,
    # next args are for parametrize
    value,
    exception,
):
    check_field_value(namespace_factory, field_name, value, exception)


@then(parsers.parse("its {field_name:w} cannot be none"))
def namespace_field_cannot_be_none(namespace_factory, field_name):
    check_field_not_nullable(namespace_factory, field_name)


@then(parsers.parse("its {field_name:w} can be none"))
def namespace_field_can_be_none(namespace_factory, field_name):
    check_field_nullable(namespace_factory, field_name)
