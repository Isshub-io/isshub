Feature: Describing a Namespace

    Scenario: A Namespace has an id
        Given a Namespace
        Then it must have a field named id

    Scenario: A Namespace id is a positive integer
        Given a Namespace
        Then its id must be a positive integer

    Scenario: A Namespace id cannot be None
        Given a Namespace
        Then its id cannot be None

    Scenario: A Namespace has a name
        Given a Namespace
        Then it must have a field named name

    Scenario: A Namespace name is a string
        Given a Namespace
        Then its name must be a string

    Scenario: A Namespace name cannot be None
        Given a Namespace
        Then its name cannot be None

    Scenario: A Namespace has a namespace
        Given a Namespace
        Then it must have a field named namespace

    Scenario: A Namespace namespace is a Namespace
        Given a Namespace
        Then its namespace must be a Namespace

    Scenario: A Namespace namespace can be None
        Given a Namespace
        Then its namespace can be None
