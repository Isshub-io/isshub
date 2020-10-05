Feature: Describing a namespace

    Scenario: A namespace has an identifier
        Given a namespace
        Then it must have a field named identifier

    Scenario: A namespace identifier is a uuid
        Given a namespace
        Then its identifier must be a uuid

    Scenario: A namespace identifier is mandatory
        Given a namespace
        Then its identifier is mandatory

    Scenario: A namespace identifier cannot be changed
        Given a namespace
        Then its identifier cannot be changed

    Scenario: A namespace has a name
        Given a namespace
        Then it must have a field named name

    Scenario: A namespace name is a string
        Given a namespace
        Then its name must be a string

    Scenario: A namespace name is mandatory
        Given a namespace
        Then its name is mandatory

    Scenario: A namespace has a description
        Given a namespace
        Then it must have a field named description

    Scenario: A namespace description is a string
        Given a namespace
        Then its description must be a string

    Scenario: A namespace description is optional
        Given a namespace
        Then its description is optional

    Scenario: A namespace has a namespace
        Given a namespace
        Then it must have a field named namespace

    Scenario: A namespace namespace is a namespace
        Given a namespace
        Then its namespace must be a namespace

    Scenario: A namespace namespace is optional
        Given a namespace
        Then its namespace is optional

    Scenario: A namespace has a kind
        Given a namespace
        Then it must have a field named kind

    Scenario: A namespace kind is a NamespaceKind
        Given a namespace
        Then its kind must be a NamespaceKind

    Scenario: A namespace kind is mandatory
        Given a namespace
        Then its kind is mandatory

    Scenario: A namespace cannot be contained in itself
        Given a namespace
        Then its namespace cannot be itself

    Scenario: A namespace namespace cannot be in a loop
        Given a namespace
        And a second namespace
        And a third namespace
        Then we cannot create a relationships loop with these namespaces
