Feature: Describing a Repository

    Scenario: A Repository has an identifier
        Given a Repository
        Then it must have a field named identifier

    Scenario: A Repository identifier is a uuid
        Given a Repository
        Then its identifier must be a uuid

    Scenario: A Repository identifier is mandatory
        Given a Repository
        Then its identifier is mandatory

    Scenario: A Repository identifier cannot be changed
        Given a Repository
        Then its identifier cannot be changed

    Scenario: A Repository has a name
        Given a Repository
        Then it must have a field named name

    Scenario: A Repository name is a string
        Given a Repository
        Then its name must be a string

    Scenario: A Repository name is mandatory
        Given a Repository
        Then its name is mandatory

    Scenario: A Repository has a namespace
        Given a Repository
        Then it must have a field named namespace

    Scenario: A Repository namespace is a Namespace
        Given a Repository
        Then its namespace must be a Namespace

    Scenario: A Repository namespace is mandatory
        Given a Repository
        Then its namespace is mandatory
