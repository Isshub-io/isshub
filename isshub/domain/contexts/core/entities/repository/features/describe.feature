Feature: Describing a Repository

    Scenario: A Repository has an id
        Given a Repository
        Then it must have a field named id

    Scenario: A Repository id is a positive integer
        Given a Repository
        Then its id must be a positive integer

    Scenario: A Repository id cannot be None
        Given a Repository
        Then its id cannot be None

    Scenario: A Repository has a name
        Given a Repository
        Then it must have a field named name

    Scenario: A Repository name is a string
        Given a Repository
        Then its name must be a string

    Scenario: A Repository name cannot be None
        Given a Repository
        Then its name cannot be None

    Scenario: A Repository has a namespace
        Given a Repository
        Then it must have a field named namespace

    Scenario: A Repository namespace is a string
        Given a Repository
        Then its namespace must be a string

    Scenario: A Repository namespace cannot be None
        Given a Repository
        Then its namespace cannot be None
