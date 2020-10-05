Feature: Describing a Namespace

    Scenario: A Namespace has an identifier
        Given a Namespace
        Then it must have a field named identifier

    Scenario: A Namespace identifier is a uuid
        Given a Namespace
        Then its identifier must be a uuid

    Scenario: A Namespace identifier is mandatory
        Given a Namespace
        Then its identifier is mandatory

    Scenario: A Namespace identifier cannot be changed
        Given a Namespace
        Then its identifier cannot be changed

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

    Scenario: A Namespace cannot be contained in itself
        Given a Namespace
        Then its namespace cannot be itself

    Scenario: A Namespace namespace cannot be in a loop
        Given a Namespace
        And a second Namespace
        And a third Namespace
        Then we cannot create a relationships loop with these namespaces
