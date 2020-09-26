Feature: Describing a Namespace

    Scenario: A Namespace has an id
        Given a Namespace
        Then it must have a field named id

    Scenario: A Namespace id is a positive integer
        Given a Namespace
        Then its id must be a positive integer

    Scenario: A Namespace id is mandatory
        Given a Namespace
        Then its id is mandatory

    Scenario: A Namespace has a name
        Given a Namespace
        Then it must have a field named name

    Scenario: A Namespace name is a string
        Given a Namespace
        Then its name must be a string

    Scenario: A Namespace name is mandatory
        Given a Namespace
        Then its name is mandatory

    Scenario: A Namespace has a description
        Given a Namespace
        Then it must have a field named description

    Scenario: A Namespace description is a string
        Given a Namespace
        Then its description must be a string

    Scenario: A Namespace description is optional
        Given a Namespace
        Then its description is optional

    Scenario: A Namespace has a namespace
        Given a Namespace
        Then it must have a field named namespace

    Scenario: A Namespace namespace is a Namespace
        Given a Namespace
        Then its namespace must be a Namespace

    Scenario: A Namespace namespace is optional
        Given a Namespace
        Then its namespace is optional

    Scenario: A Namespace has a kind
        Given a Namespace
        Then it must have a field named kind

    Scenario: A Namespace kind is a NamespaceKind
        Given a Namespace
        Then its kind must be a NamespaceKind

    Scenario: A Namespace kind is mandatory
        Given a Namespace
        Then its kind is mandatory
