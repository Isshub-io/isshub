Feature: Describing a repository

    Scenario: A repository has an identifier
        Given a repository
        Then it must have a field named identifier

    Scenario: A repository identifier is a uuid
        Given a repository
        Then its identifier must be a uuid

    Scenario: A repository identifier is mandatory
        Given a repository
        Then its identifier is mandatory

    Scenario: A repository identifier cannot be changed
        Given a repository
        Then its identifier cannot be changed

    Scenario: A repository has a name
        Given a repository
        Then it must have a field named name

    Scenario: A repository name is a string
        Given a repository
        Then its name must be a string

    Scenario: A repository name is mandatory
        Given a repository
        Then its name is mandatory

    Scenario: A repository has a namespace
        Given a repository
        Then it must have a field named namespace

    Scenario: A repository namespace is a Namespace
        Given a repository
        Then its namespace must be a Namespace

    Scenario: A repository namespace is mandatory
        Given a repository
        Then its namespace is mandatory
