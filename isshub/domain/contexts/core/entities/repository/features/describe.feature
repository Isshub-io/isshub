Feature: Describing a Repository

    Scenario: A Repository has an id
        Given a Repository
        Then it must have a field named id

    Scenario: A Repository has a name
        Given a Repository
        Then it must have a field named name

    Scenario: A Repository has a namespace
        Given a Repository
        Then it must have a field named namespace
