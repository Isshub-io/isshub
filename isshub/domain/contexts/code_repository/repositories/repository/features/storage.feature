Feature: Storing repositories

    Background: Given a repository and a repository storage
        Given a repository
        And a repository storage

    Scenario: A new repository can be saved and retrieved
        When the repository is added to the repository storage
        Then I can retrieve it

    Scenario: A new repository cannot be saved if invalid
        When the repository has some invalid content
        Then I cannot add it because it's invalid

    Scenario: An existing repository cannot be added
        When the repository is added to the repository storage
        Then it's not possible to add it again

    Scenario: An existing repository can be updated
        When the repository is added to the repository storage
        And it is updated
        Then I can retrieve its updated version

    Scenario: An existing repository cannot be saved if invalid
        When the repository has some invalid content
        Then I cannot update it because it's invalid

    Scenario: A non existing repository cannot be updated
        When the repository is not added to the repository storage
        Then I cannot update it because it does not exist

    Scenario: An existing repository can be deleted
        When the repository is added to the repository storage
        And it is deleted
        Then I cannot retrieve it

    Scenario: An non existing repository cannot be deleted
        When the repository is not added to the repository storage
        Then I cannot delete it

    Scenario: All repositories in same namespace can be retrieved at once
        Given a namespace with no repositories in it
        And a second repository, in the namespace
        And a third repository, in the namespace
        When the repository is added to the repository storage
        And the second repository is added to the repository storage
        And the third repository is added to the repository storage
        Then I can retrieve the second and the third repositories at once

    Scenario: No repositories returned from a namespace without repositories
        Given a namespace with no repositories in it
        Then I got no repositories for the namespace

    Scenario: A repository cannot be added if another exists with same name in same namespace
        Given a second repository with same name in the same namespace
        When the repository is added to the repository storage
        Then I cannot add the second one

    Scenario: A repository cannot be updated if another exists with same new name in same namespace
        Given a second repository in the same namespace
        When the repository is added to the repository storage
        And the second repository is added to the repository storage
        And the second repository name is set as for the first one
        Then I cannot update the second one

    Scenario: A repository cannot be updated if another exists with same name in new same namespace
        Given a second repository with the same name
        When the repository is added to the repository storage
        And the second repository is added to the repository storage
        And the second repository namespace is set as for the first one
        Then I cannot update the second one

    Scenario: A repository can be moved from one namespace to another
        Given a namespace with no repositories in it
        And a second namespace with no repositories in it
        When the repository is added to the repository storage
        And the repository is set in the first namespace
        And I change its namespace
        Then the repository is no longer available in the original namespace
        And the repository is available in the new namespace
