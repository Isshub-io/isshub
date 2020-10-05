"""Module holding BDD tests for isshub repository for code_repository Namespace entity as defined in ``storage.feature``."""
from functools import partial

import pytest
from pytest_bdd import given, scenario, scenarios, then, when

from isshub.domain.contexts.code_repository.repositories.namespace import (
    InMemoryNamespaceRepository,
)

from ....entities.namespace.tests.fixtures import namespace_factory


FEATURE_FILE = "../features/storage.feature"
scenario = partial(scenario, FEATURE_FILE)


@scenario("A new namespace can be saved and retrieved")
def test_add_new_namespace():
    pass


@given("a namespace with a parent namespace", target_fixture="namespace")
def a_namespace_with_parent_namespace(namespace_factory):
    return namespace_factory(namespace=namespace_factory(namespace=None))


@given("a namespace without parent namespace", target_fixture="namespace")
def a_namespace_without_namespace(namespace_factory):
    return namespace_factory(namespace=None)


@given("a namespace storage", target_fixture="namespace_storage")
def a_namespace_storage():
    return InMemoryNamespaceRepository()


@when("the namespace is added to the namespace storage")
def add_namespace(namespace, namespace_storage):
    namespace_storage.add(namespace)


@then("I can retrieve it")
def retrieve_new_from_namespace(namespace, namespace_storage):
    assert namespace_storage.exists(identifier=namespace.identifier)
    from_namespace = namespace_storage.get(identifier=namespace.identifier)
    assert from_namespace == namespace


@scenario("A new namespace cannot be saved if invalid")
def test_add_invalid_namespace():
    pass


@when("the namespace has some invalid content")
def update_namespace_with_invalid_content(namespace):
    namespace.kind = 123


@then("I cannot add it because it's invalid")
def cannot_add_invalid_namespace(namespace, namespace_storage):
    with pytest.raises(TypeError):
        namespace_storage.add(namespace)


@scenario("An existing namespace cannot be added")
def test_add_existing_namespace():
    pass


@then("it's not possible to add it again")
def cannot_add_existing_namespace(namespace, namespace_storage):
    with pytest.raises(namespace_storage.UniquenessError):
        namespace_storage.add(namespace)


@scenario("An existing namespace can be updated")
def test_update_existing_namespace():
    pass


@when("it is updated")
def namespace_is_updated(namespace, namespace_storage):
    namespace.name = "new name"
    namespace_storage.update(namespace)


@then("I can retrieve its updated version")
def retrieve_updated_from_namespace(namespace, namespace_storage):
    from_namespace = namespace_storage.get(identifier=namespace.identifier)
    assert from_namespace.name == "new name"


@scenario("An existing namespace cannot be saved if invalid")
def test_update_invalid_namespace():
    pass


@then("I cannot update it because it's invalid")
def cannot_update_invalid_namespace(namespace, namespace_storage):
    with pytest.raises(TypeError):
        namespace_storage.update(namespace)


@scenario("A non existing namespace cannot be updated")
def test_update_non_existing_namespace():
    pass


@when("the namespace is not added to the namespace storage")
def add_namespace(namespace, namespace_storage):
    pass


@then("I cannot update it because it does not exist")
def cannot_update_non_existing_namespace(namespace, namespace_storage):
    namespace.name = "new name"
    with pytest.raises(namespace_storage.NotFoundError):
        namespace_storage.update(namespace)


@scenario("An existing namespace can be deleted")
def test_delete_namespace():
    pass


@when("it is deleted")
def namespace_is_deleted(namespace, namespace_storage):
    namespace_storage.delete(namespace)


@then("I cannot retrieve it")
def cannot_retrieve_deleted_namespace(namespace, namespace_storage):
    with pytest.raises(namespace_storage.NotFoundError):
        namespace_storage.get(identifier=namespace.identifier)


@scenario("An non existing namespace cannot be deleted")
def test_delete_non_existing_namespace():
    pass


@then("I cannot delete it")
def cannot_delete_non_existing_namespace(namespace, namespace_storage):
    with pytest.raises(namespace_storage.NotFoundError):
        namespace_storage.delete(namespace)


@scenario("All namespaces in same namespace can be retrieved at once")
def test_retrieve_all_namespaces_from_namespace():
    pass


@given("a parent namespace with no namespaces in it", target_fixture="parent_namespace")
def a_parent_namespace(namespace_factory):
    return namespace_factory()


@given("a second namespace, in the parent namespace", target_fixture="namespace1")
def a_namespace_in_a_namespace(namespace_factory, parent_namespace):
    return namespace_factory(namespace=parent_namespace)


@given("a third namespace, in the parent namespace", target_fixture="namespace2")
def an_other_namespace_in_a_namespace(namespace_factory, parent_namespace):
    return namespace_factory(namespace=parent_namespace)


@when("the second namespace is added to the namespace storage")
def add_namespace_in_namespace(namespace1, namespace_storage):
    namespace_storage.add(namespace1)


@when("the third namespace is added to the namespace storage")
def add_other_namespace_in_namespace(namespace2, namespace_storage):
    namespace_storage.add(namespace2)


@then("I can retrieve the second and the third namespaces at once")
def retrieve_namespaces_for_namespace(
    namespace_storage, parent_namespace, namespace1, namespace2
):
    namespaces = set(namespace_storage.for_namespace(parent_namespace))
    assert namespaces == {namespace1, namespace2}


@scenario("No namespaces returned from a parent namespace without namespaces")
def test_retrieve_namespaces_from_empty_namespace():
    pass


@then("I got no namespaces for the parent namespace")
def retrieve_namespaces_for_empty_namespace(namespace_storage, parent_namespace):
    namespaces = set(namespace_storage.for_namespace(parent_namespace))
    assert namespaces == set()


@scenario(
    "A namespace cannot be added if another exists with same name in same parent namespace"
)
def test_name_and_namespace_uniqueness_at_create_time():
    pass


@given(
    "a second namespace with same name in the same parent namespace",
    target_fixture="namespace1",
)
def an_other_namespace_with_same_name_and_namespace(namespace_factory, namespace):
    return namespace_factory(name=namespace.name, namespace=namespace.namespace)


@then("I cannot add the second one")
def namespace_cannot_be_added(namespace_storage, namespace1):
    with pytest.raises(namespace_storage.UniquenessError):
        namespace_storage.add(namespace1)


@scenario(
    "A namespace cannot be added if another exists with same name both without parent namespace"
)
def test_name_and_no_namespace_uniqueness_at_create_time():
    pass


@given(
    "a second namespace with same name and without parent namespace",
    target_fixture="namespace1",
)
def an_other_namespace_with_same_name_and_namespace(namespace_factory, namespace):
    return namespace_factory(name=namespace.name, namespace=None)


@scenario(
    "A namespace cannot be updated if another exists with same new name in same parent namespace"
)
def test_namespace_cannot_be_updated_if_same_new_name_in_same_namespace():
    pass


@given("a second namespace in the same parent namespace", target_fixture="namespace1")
def an_other_namespace_with_same_namespace(namespace_factory, namespace):
    return namespace_factory(namespace=namespace.namespace)


@when("the second namespace name is set as for the first one")
def update_other_namespace_name_as_first_one(namespace, namespace1):
    namespace1.name = namespace.name


@then("I cannot update the second one")
def other_namespace_cannot_be_updated(namespace_storage, namespace1):
    with pytest.raises(namespace_storage.UniquenessError):
        namespace_storage.update(namespace1)


@scenario(
    "A namespace cannot be updated if another exists with same new name both without parent namespace"
)
def test_namespace_cannot_be_updated_if_same_new_name_no_namespace():
    pass


@given("a second namespace without parent namespace", target_fixture="namespace1")
def an_other_namespace_without_namespace(namespace_factory):
    return namespace_factory(namespace=None)


@scenario(
    "A namespace cannot be updated if another exists with same name in new same parent namespace"
)
def test_namespace_cannot_be_updated_if_same_name_in_new_same_namespace():
    pass


@given("a second namespace with the same name", target_fixture="namespace1")
def an_other_namespace_with_same_name(namespace_factory, namespace):
    return namespace_factory(name=namespace.name)


@when("the second namespace parent namespace is set as for the first one")
def update_other_namespace_namespace_as_first_one(namespace, namespace1):
    namespace1.namespace = namespace.namespace


@scenario(
    "A namespace cannot be updated if another exists with same name now both without namespace"
)
def test_namespace_cannot_be_updated_if_same_name_without_namespace():
    pass


@given(
    "a second namespace with the same name and a parent namespace",
    target_fixture="namespace1",
)
def an_other_namespace_with_same_name_and_a_namespace(namespace_factory, namespace):
    return namespace_factory(name=namespace.name, namespace=namespace_factory())


@when("the second namespace parent namespace is cleared")
def clear_other_namespace_namspesace(namespace1):
    namespace1.namespace = None


@scenario("A namespace can be moved from one parent namespace to another")
def test_move_namespace_from_namespace():
    pass


@given(
    "a second parent namespace with no namespaces in it",
    target_fixture="parent_namespace1",
)
def another_parent_namespace(namespace_factory):
    return namespace_factory()


@when("the namespace is set in the parent namespace")
@when("the namespace is set in the first parent namespace")
def set_namespace_namespace(namespace_storage, namespace, parent_namespace):
    namespace.namespace = parent_namespace
    namespace_storage.update(namespace)


@when("I change its namespace")
def update_namespace(namespace_storage, namespace, parent_namespace1):
    namespace.namespace = parent_namespace1
    namespace_storage.update(namespace)


@then("the namespace is no longer available in the original parent namespace")
def namespace_not_in_namespace(namespace_storage, namespace, parent_namespace):
    assert namespace not in namespace_storage.for_namespace(parent_namespace)


@then("the namespace is available in the new parent namespace")
def namespace_not_in_namespace(namespace_storage, namespace, parent_namespace1):
    assert namespace in namespace_storage.for_namespace(parent_namespace1)


@scenario("A namespace without parent namespace can be moved to one")
def test_move_namespace_to_namespace():
    pass


@then("the namespace is no longer available when fetching namespaces without parents")
def namespace_not_in_namespace(namespace_storage, namespace):
    assert namespace not in namespace_storage.for_namespace(None)


@then("the namespace is available in the parent namespace")
def namespace_not_in_namespace(namespace_storage, namespace, parent_namespace):
    assert namespace in namespace_storage.for_namespace(parent_namespace)


@scenario("A namespace with a parent namespace can have its parent namespace cleared")
def test_clear_parent_namespace():
    pass


@when("the namespace parent namespace is cleared")
def clear_other_namespace_namspesace(namespace):
    namespace.namespace = None


@then("the namespace is no longer available in the parent namespace")
def namespace_not_in_namespace(namespace_storage, namespace, parent_namespace):
    assert namespace not in namespace_storage.for_namespace(parent_namespace)


@then("the namespace is available when fetching namespaces without parents")
def namespace_not_in_namespace(namespace_storage, namespace):
    assert namespace in namespace_storage.for_namespace(None)


# To make pytest-bdd fail if some scenarios are not all implemented. KEEP AT THE END
scenarios(FEATURE_FILE)
