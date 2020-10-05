"""Module holding BDD tests for isshub repository for code_repository Repository entity as defined in ``storage.feature``."""
from functools import partial

import pytest
from pytest_bdd import given, scenario, scenarios, then, when

from isshub.domain.contexts.code_repository.repositories.repository import (
    InMemoryRepositoryRepository,
)

from ....entities.namespace.tests.fixtures import namespace_factory
from ....entities.repository.tests.fixtures import repository_factory


FEATURE_FILE = "../features/storage.feature"
scenario = partial(scenario, FEATURE_FILE)


@scenario("A new repository can be saved and retrieved")
def test_add_new_repository():
    pass


@given("a repository", target_fixture="repository")
def a_repository(repository_factory):
    return repository_factory()


@given("a repository storage", target_fixture="repository_storage")
def a_repository_storage():
    return InMemoryRepositoryRepository()


@when("the repository is added to the repository storage")
def add_repository(repository, repository_storage):
    repository_storage.add(repository)


@then("I can retrieve it")
def retrieve_new_from_repository(repository, repository_storage):
    assert repository_storage.exists(identifier=repository.identifier)
    from_repository = repository_storage.get(identifier=repository.identifier)
    assert from_repository == repository


@scenario("A new repository cannot be saved if invalid")
def test_add_invalid_repository():
    pass


@when("the repository has some invalid content")
def update_repository_with_invalid_content(repository):
    repository.name = None


@then("I cannot add it because it's invalid")
def cannot_add_invalid_repository(repository, repository_storage):
    with pytest.raises(TypeError):
        repository_storage.add(repository)


@scenario("An existing repository cannot be added")
def test_add_existing_repository():
    pass


@then("it's not possible to add it again")
def cannot_add_existing_repository(repository, repository_storage):
    with pytest.raises(repository_storage.UniquenessError):
        repository_storage.add(repository)


@scenario("An existing repository can be updated")
def test_update_existing_repository():
    pass


@when("it is updated")
def repository_is_updated(repository, repository_storage):
    repository.name = "new name"
    repository_storage.update(repository)


@then("I can retrieve its updated version")
def retrieve_updated_from_repository(repository, repository_storage):
    from_repository = repository_storage.get(identifier=repository.identifier)
    assert from_repository.name == "new name"


@scenario("An existing repository cannot be saved if invalid")
def test_update_invalid_repository():
    pass


@then("I cannot update it because it's invalid")
def cannot_update_invalid_repository(repository, repository_storage):
    with pytest.raises(TypeError):
        repository_storage.update(repository)


@scenario("A non existing repository cannot be updated")
def test_update_non_existing_repository():
    pass


@when("the repository is not added to the repository storage")
def add_repository(repository, repository_storage):
    pass


@then("I cannot update it because it does not exist")
def cannot_update_non_existing_repository(repository, repository_storage):
    repository.name = "new name"
    with pytest.raises(repository_storage.NotFoundError):
        repository_storage.update(repository)


@scenario("An existing repository can be deleted")
def test_delete_repository():
    pass


@when("it is deleted")
def repository_is_deleted(repository, repository_storage):
    repository_storage.delete(repository)


@then("I cannot retrieve it")
def cannot_retrieve_deleted_repository(repository, repository_storage):
    with pytest.raises(repository_storage.NotFoundError):
        repository_storage.get(identifier=repository.identifier)


@scenario("An non existing repository cannot be deleted")
def test_delete_non_existing_repository():
    pass


@then("I cannot delete it")
def cannot_delete_non_existing_repository(repository, repository_storage):
    with pytest.raises(repository_storage.NotFoundError):
        repository_storage.delete(repository)


@scenario("All repositories in same namespace can be retrieved at once")
def test_retrieve_all_repositories_from_namespace():
    pass


@given("a namespace with no repositories in it", target_fixture="namespace")
def a_namespace(namespace_factory):
    return namespace_factory()


@given("a second repository, in the namespace", target_fixture="repository1")
def a_repository_in_a_namespace(repository_factory, namespace):
    return repository_factory(namespace=namespace)


@given("a third repository, in the namespace", target_fixture="repository2")
def an_other_repository_in_a_namespace(repository_factory, namespace):
    return repository_factory(namespace=namespace)


@when("the second repository is added to the repository storage")
def add_repository_in_namespace(repository1, repository_storage):
    repository_storage.add(repository1)


@when("the third repository is added to the repository storage")
def add_other_repository_in_namespace(repository2, repository_storage):
    repository_storage.add(repository2)


@then("I can retrieve the second and the third repositories at once")
def retrieve_repositories_for_namespace(
    repository_storage, namespace, repository1, repository2
):
    repositories = set(repository_storage.for_namespace(namespace))
    assert repositories == {repository1, repository2}


@scenario("No repositories returned from a namespace without repositories")
def test_retrieve_repositories_from_empty_namespace():
    pass


@then("I got no repositories for the namespace")
def retrieve_repositories_for_empty_namespace(repository_storage, namespace):
    repositories = set(repository_storage.for_namespace(namespace))
    assert repositories == set()


@scenario(
    "A repository cannot be added if another exists with same name in same namespace"
)
def test_name_and_namespace_uniqueness_at_create_time():
    pass


@given(
    "a second repository with same name in the same namespace",
    target_fixture="repository1",
)
def an_other_repository_with_same_name_and_namespace(repository_factory, repository):
    return repository_factory(name=repository.name, namespace=repository.namespace)


@then("I cannot add the second one")
def repository_cannot_be_added_if_same_name_and_namespace(
    repository_storage, repository1
):
    with pytest.raises(repository_storage.UniquenessError):
        repository_storage.add(repository1)


@scenario(
    "A repository cannot be updated if another exists with same new name in same namespace"
)
def test_repository_cannot_be_updated_if_same_new_name_in_same_namespace():
    pass


@given("a second repository in the same namespace", target_fixture="repository1")
def an_other_repository_with_same_namespace(repository_factory, repository):
    return repository_factory(namespace=repository.namespace)


@when("the second repository name is set as for the first one")
def update_other_repository_name_as_first_one(repository, repository1):
    repository1.name = repository.name


@then("I cannot update the second one")
def other_repository_cannot_be_updated(repository_storage, repository1):
    with pytest.raises(repository_storage.UniquenessError):
        repository_storage.update(repository1)


@scenario(
    "A repository cannot be updated if another exists with same name in new same namespace"
)
def test_repository_cannot_be_updated_if_same_name_in_new_same_namespace():
    pass


@given("a second repository with the same name", target_fixture="repository1")
def an_other_repository_with_same_name(repository_factory, repository):
    return repository_factory(name=repository.name)


@when("the second repository namespace is set as for the first one")
def update_other_repository_namespace_as_first_one(repository, repository1):
    repository1.namespace = repository.namespace


@scenario("A repository can be moved from one namespace to another")
def test_move_repository_from_namespace():
    pass


@given("a second namespace with no repositories in it", target_fixture="namespace1")
def another_namespace(namespace_factory):
    return namespace_factory()


@when("the repository is set in the first namespace")
def set_repository_namespace(repository_storage, repository, namespace):
    repository.namespace = namespace
    repository_storage.update(repository)


@when("I change its namespace")
def update_namespace(repository_storage, repository, namespace1):
    repository.namespace = namespace1
    repository_storage.update(repository)


@then("the repository is no longer available in the original namespace")
def repository_not_in_namespace(repository_storage, repository, namespace):
    assert repository not in repository_storage.for_namespace(namespace)


@then("the repository is available in the new namespace")
def repository_not_in_namespace(repository_storage, repository, namespace1):
    assert repository in repository_storage.for_namespace(namespace1)


# To make pytest-bdd fail if some scenarios are not all implemented. KEEP AT THE END
scenarios(FEATURE_FILE)
