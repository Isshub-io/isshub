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

    Scenario: A Namespace has a description
        Given a Namespace
        Then it must have a field named description

    Scenario: A Namespace description is a string
        Given a Namespace
        Then its description must be a string

    Scenario: A Namespace description can be None
        Given a Namespace
        Then its description can be None

    Scenario: A Namespace has a namespace
        Given a Namespace
        Then it must have a field named namespace

    Scenario: A Namespace namespace is a Namespace
        Given a Namespace
        Then its namespace must be a Namespace

    Scenario: A Namespace namespace can be None
        Given a Namespace
        Then its namespace can be None

    Scenario: A Namespace has a kind
        Given a Namespace
        Then it must have a field named kind

    Scenario: A Namespace kind is a NamespaceKind
        Given a Namespace
        Then its kind must be a NamespaceKind

    Scenario: A Namespace kind cannot be None
        Given a Namespace
        Then its kind cannot be None
