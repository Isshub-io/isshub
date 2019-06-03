"""Test file to check testing tools"""

from pytest_bdd import given, parsers, scenario, then


def test_passing():
    """A test that must pass"""

    assert 1 == 1


@scenario("test_testing.feature", "A bdd test must pass")
def test_bdd():
    pass


@given("a bdd test")
def a_bdd_test():
    return "a bdd test"


@then("it must pass")
def it_must_pass(a_bdd_test):
    assert a_bdd_test == "a bdd test"
