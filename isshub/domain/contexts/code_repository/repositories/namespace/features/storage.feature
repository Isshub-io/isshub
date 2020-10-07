Feature: Storing namespaces

    Background: Given a namespace and a namespace storage
        Given a namespace with a parent namespace
        And a namespace storage

    Scenario: A new namespace can be saved and retrieved
        When the namespace is added to the namespace storage
        Then I can retrieve it

    Scenario: A new namespace cannot be saved if invalid
        When the namespace has some invalid content
        Then I cannot add it because it's invalid

    Scenario: An existing namespace cannot be added
        When the namespace is added to the namespace storage
        Then it's not possible to add it again

    Scenario: An existing namespace can be updated
        When the namespace is added to the namespace storage
        And it is updated
        Then I can retrieve its updated version

    Scenario: An existing namespace cannot be saved if invalid
        When the namespace has some invalid content
        Then I cannot update it because it's invalid

    Scenario: A non existing namespace cannot be updated
        When the namespace is not added to the namespace storage
        Then I cannot update it because it does not exist

    Scenario: An existing namespace can be deleted
        When the namespace is added to the namespace storage
        And it is deleted
        Then I cannot retrieve it

    Scenario: An non existing namespace cannot be deleted
        When the namespace is not added to the namespace storage
        Then I cannot delete it

    Scenario: All namespaces in same namespace can be retrieved at once
        Given a parent namespace with no namespaces in it
        And a second namespace, in the parent namespace
        And a third namespace, in the parent namespace
        When the namespace is added to the namespace storage
        And the second namespace is added to the namespace storage
        And the third namespace is added to the namespace storage
        Then I can retrieve the second and the third namespaces at once

    Scenario: No namespaces returned from a parent namespace without namespaces
        Given a parent namespace with no namespaces in it
        Then I got no namespaces for the parent namespace

    Scenario: A namespace cannot be added if another exists with same name in same parent namespace
        Given a second namespace with same name in the same parent namespace
        When the namespace is added to the namespace storage
        Then I cannot add the second one

    Scenario: A namespace cannot be added if another exists with same name both without parent namespace
        Given a namespace without parent namespace
        And a second namespace with same name and without parent namespace
        When the namespace is added to the namespace storage
        Then I cannot add the second one

    Scenario: A namespace cannot be updated if another exists with same new name in same parent namespace
        Given a second namespace in the same parent namespace
        When the namespace is added to the namespace storage
        And the second namespace is added to the namespace storage
        And the second namespace name is set as for the first one
        Then I cannot update the second one

    Scenario: A namespace cannot be updated if another exists with same new name both without parent namespace
        Given a namespace without parent namespace
        And a second namespace without parent namespace
        When the namespace is added to the namespace storage
        And the second namespace is added to the namespace storage
        And the second namespace name is set as for the first one
        Then I cannot update the second one

    Scenario: A namespace cannot be updated if another exists with same name in new same parent namespace
        Given a second namespace with the same name
        When the namespace is added to the namespace storage
        And the second namespace is added to the namespace storage
        And the second namespace parent namespace is set as for the first one
        Then I cannot update the second one

    Scenario: A namespace cannot be updated if another exists with same name now both without namespace
        Given a namespace without parent namespace
        And a second namespace with the same name and a parent namespace
        When the namespace is added to the namespace storage
        And the second namespace is added to the namespace storage
        And the second namespace parent namespace is cleared
        Then I cannot update the second one

    Scenario: A namespace can be moved from one parent namespace to another
        Given a parent namespace with no namespaces in it
        And a second parent namespace with no namespaces in it
        When the namespace is added to the namespace storage
        And the namespace is set in the first parent namespace
        And I change its namespace
        Then the namespace is no longer available in the original parent namespace
        And the namespace is available in the new parent namespace

    Scenario: A namespace without parent namespace can be moved to one
        Given a namespace without parent namespace
        And a parent namespace with no namespaces in it
        When the namespace is added to the namespace storage
        And the namespace is set in the first parent namespace
        Then the namespace is no longer available when fetching namespaces without parents
        And the namespace is available in the parent namespace

    Scenario: A namespace with a parent namespace can have its parent namespace cleared
        Given a namespace without parent namespace
        And a parent namespace with no namespaces in it
        When the namespace is added to the namespace storage
        And the namespace is set in the parent namespace
        And the namespace parent namespace is cleared
        Then the namespace is no longer available in the parent namespace
        And the namespace is available when fetching namespaces without parents
