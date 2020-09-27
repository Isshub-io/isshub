"""Module holding BDD tests for isshub Namespace code_repository entity."""

import pytest
from pytest import mark
from pytest_bdd import given, parsers, scenario, scenarios, then

from isshub.domain.contexts.code_repository.entities.namespace import NamespaceKind
from isshub.domain.utils.testing.validation import (
    FrozenAttributeError,
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


@given("a Namespace", target_fixture="namespace")
def a_namespace(namespace_factory):
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


@then(parsers.parse("its {field_name:w} is mandatory"))
def namespace_field_is_mandatory(namespace_factory, field_name):
    check_field_not_nullable(namespace_factory, field_name)


@then(parsers.parse("its {field_name:w} is optional"))
def namespace_field_is_optional(namespace_factory, field_name):
    check_field_nullable(namespace_factory, field_name)


@scenario("../features/describe.feature", "A Namespace id cannot be changed")
def test_namespace_id_cannot_be_changed():
    pass


@then("its id cannot be changed")
def namespace_id_cannot_be_changed(namespace):
    with pytest.raises(FrozenAttributeError):
        namespace.id = namespace.id + 1


@scenario("../features/describe.feature", "A Namespace cannot be contained in itself")
def test_namespace_namespace_cannot_be_itself():
    pass


@then("its namespace cannot be itself")
def namespace_namespace_cannot_be_itself(namespace):
    namespace.namespace = namespace
    with pytest.raises(ValueError):
        namespace.validate()


@scenario("../features/describe.feature", "A Namespace namespace cannot be in a loop")
def test_namespace_namespace_cannot_be_in_a_loop():
    pass


@given("a second Namespace", target_fixture="namespace2")
def a_second_namespace(namespace_factory):
    return namespace_factory()


@given("a third Namespace", target_fixture="namespace3")
def a_third_namespace(namespace_factory):
    return namespace_factory()


@then("we cannot create a relationships loop with these namespaces")
def namespace_relationships_cannot_create_a_loop(namespace, namespace2, namespace3):
    namespace2.namespace = namespace3
    namespace3.validate()
    namespace2.validate()
    namespace.validate()
    namespace.namespace = namespace2
    namespace3.validate()
    namespace2.validate()
    namespace.validate()
    namespace3.namespace = namespace
    with pytest.raises(ValueError):
        namespace3.validate()
    with pytest.raises(ValueError):
        namespace2.validate()
    with pytest.raises(ValueError):
        namespace.validate()
    namespace3.namespace = None
    namespace3.validate()
    namespace2.validate()
    namespace.validate()
