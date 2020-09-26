=============================================
IssHub : Your essential Git.Hub.Lab companion
=============================================


Welcome to the repository where `IssHub <https://isshub.io>`_ v2 is developed.

--------
Abstract
--------

IssHub is an "ISSues Hub", where you can manage your issues (and code requests, notifications...) from code hosting platforms like Github and Gitlab, in one place, with a common interface and advanced tools.

This is the repository of the second version, that is developed in a totally different way that the previous one: progressive, clean and in the open.

----------
Motivation
----------

The first version was developed starting on a "Proof of concept" and evolved over several years without a  clear vision on what was the goal, and no proper code architecture.

When `Joachim Jablon <https://github.com/ewjoachim>`_ and I prepared our `talk fo the Djangocon Europe 2019 in Copenhagen, "Maintaining a Django codebase after 10k commits" <https://www.youtube.com/watch?v=_DIlE-yc9ZQ&t=724s>`_, I "saw the light" and wanted to do a little experiment around all we talked about.

In the few months prior to the conference, as a planed sponsor, I worked a lot in IssHub to have it ready, bug-free (ahem) and mainly the biggest new feature since I started to work on this project in 2013: support for Gitlab in addition to Github.

It was a real pain as I encountered all the pain points we tried to solve in our talk

Third parties
    Over 6 years, Django evolved a lot, and a lot of third parties were abandoned. Upgrading was very difficult. Proof: IssHub v1 is still on Python 2.

Code architecture
    The original proof of concept was to simply be able to organize issues with labels. So, as a POC, it was normal to follow Github on how to model things. But Gitlab, does things in a very different way and I had to make it fit the Github model.

    So there was no clear separation (and even no separation at all) between the "domain", and all the rest of the application.

    And finally the logic was everywhere: in the models, in the managers, in the views, in the templates.... Exactly what you want to avoid to maintain - and evolve - a big project.

Tests
    I won't speak about tests in IssHub v1: I gave up on many parts, because of the big bowl of spaghetti I had.

So after our talk, instead of a little experiment about what we learnt in the process, I asked myself: why not starting up IssHub again, but this time doing it properly, and in the open, to force myself to do the things correctly.

And it could also be a good way for others to see what I, as a 43 years old senior developer with half of my life as a paid developer, think is **a** (and not **the**) good way of developing a "big project"


---------
Rationale
---------

The main concepts that are used on this project:

- coding in the open
- developer friendly
- future friendly
- clear separation of concerns

''''''''''''''''''
Coding in the open
''''''''''''''''''

The main reason for the code of IssHub v1 to be "closed source" is because I'm not proud of it. It is really far from everything I try to transmit at work: quality is important, if not the most important.

By doing this in the open, it will force me to do things well.

It will also be for me a good resource to provide when looking for new freelancer missions.

And, I hope, it can become a reference for everything I do elsewhere, from my own pet projects, to other "big projects" I may create in the future, or to simply pick ideas, code snippets, etc. when working for someone else.

And finally, having it in the open allow other people to participate in many ways (reporting bugs is a good start)

'''''''''''''''''''''''''''''
Developer and future friendly
'''''''''''''''''''''''''''''

  “Always code as if the guy who ends up maintaining your code will be a violent psychopath who knows where you live”

  -- John F. Woods

aka: future you

Nobody knows the future. A project started alone after work can become a big company later. Or it can just be you in a few years having to deal with "just a quick fix" made by past you. Or you simply want to have other hands working with you.

In all these cases, you want your code to be clean. You don't want to fight to have great code readability. You don't want to have a fix break totally unrelated things.

For this you want:

- code linting
- tests
- documentation

This will be one on the roots of this new rewrite of IssHub.

''''''''''''''''''''''''''''
Clear separation of concerns
''''''''''''''''''''''''''''

Having concerns separated allow better testing: each part can be unit tested, and the "glue" can be tested in integration mode.

Updates are also easier because each part does one thing and does it well.

The first thing we do is to do `Domain Driven Development <https://en.wikipedia.org/wiki/Domain-driven_design>`_: instead of mixing everything everywhere, domain logic will be apart from the rest. Considering Django as a third party app and not the center of the project, like it's very often the case.

On the "domain", we'll delimit some "bounded context, for example the data we manage from the repositories, the local interaction between logged in users and these data, payment/subscriptions...

So the domain will be a layer of our architecture. But it's not enough to make an application.

We'll need a layer to handle the persistence, one to manage the synchronization between us and the remote sources (Github, Gitlab...), another to display things to the user.

The domain is in the middle of all of these layers. It means that sync and front layers only handle data from the domain, not from the django ORM, which is only used as the persistence layer.

We then won't be able to use some powerful features of Django, ie all the parts that link the orm to the rest of Django: no `ModelForm`, no `UpdateView`... but we can still use `Form` and `ModelFormMixin`, using our domain to pass data to Django, as "pure python objects", validate the data...

It's a hard choice to make but for me, the separation of concerns, for a project of this size, is more important than the benefits of using Django as the ruler of everything.


--------------
Specifications
--------------

This part will evolve a lot during the development but there are still some things I know for sure.

'''''
Tools
'''''

All tools are incorporated in a `Makefile`, so it's easier to run commands. Tools listed below all have at least one `make` command to run them.

.. note::

   Run `make help` to list the available commands (the first one to run in a fresh python virtual environment being `make dev`)


Linting
=======

To enforce coding style in python, we'll use:

`black <https://black.readthedocs.io/en/stable/>`_
  Black is the "uncompromising code formatter"

  Used with default configuration.

  To check::

    make check-black

  To apply::

    make black


`isort <https://isort.readthedocs.io/>`_
  isort is a Python utility / library to sort imports alphabetically, and automatically separated into sections

  Used with special configuration.

  To check::

    make check-isort

  To apply::

    make isort

But we still use lint checkers:

`pylint <https://docs.pylint.org/>`_
  Pylint is a tool that checks for errors in Python code, tries to enforce a coding standard and looks for code smells.

  With some code specifically ignored, and also with this plugin:

  `pylint.extensions.docparams <http://pylint.pycqa.org/en/stable/technical_reference/extensions.html#parameter-documentation-checker>`_
    If you document the parameters of your functions, methods and constructors and their types systematically in your code this optional component might be useful for you.

    Using configuration to enforce complete docstrings, using NumPy style.

  To run `pylint`::

    make pylint

`flake8 <http://flake8.pycqa.org>`_
  Flake8: Your Tool For Style Guide Enforcement

  A wrapper around `PyFlakes <https://pypi.org/project/pyflakes/>`_, `pycodestyle <https://pypi.org/project/pycodestyle/>`_ (formerly called pep8), `McCabe <https://pypi.org/project/mccabe/>`_.

  With these plugins;

  `flake8-bugbear <https://pypi.org/project/flake8-bugbear/>`_
    A plugin for Flake8 finding likely bugs and design problems in your program

  `flake8-comprehensions <https://pypi.org/project/flake8-comprehensions/>`_
    A flake8 plugin that helps you write better list/set/dict comprehensions.

  `flake8-docstrings <https://pypi.org/project/flake8-docstrings/>`_
    A simple module that adds an extension for the fantastic `pydocstyle <http://www.pydocstyle.org>`_ tool to flake8.

  To run `flake8`::

    make flake8

Yes, it's a lot. My IDE is configured to run isort + black on every save. So pylint and flake8 should report very few things, and when they does, it will mainly be about code badly written.

Other related `make` commands:

- Run isort and black::

    make pretty

- Run all lint checkers (isort, black, pylint, flake8 and mypy)::

    make lint

Documentation
=============

For code documentation, I enforce docstrings in all modules, classes, and functions/methods, using `NumPy style documentation <https://numpydoc.readthedocs.io>`_, using python typing "types" to define the types of parameters and return values.

The checks are enforced by `flake8-docstrings`_ for basic docstring presentation, and by `pylint.extensions.docparams`_ for content.

I'll try to use `python typing <https://docs.python.org/3/library/typing.html>`_ while avoiding making things too much complicated. So expect some `# type: ignore` comments here and there, notably on decorators.

The types will be checked by `mypy <https://mypy.readthedocs.io/>`_.

So, code documentation is important (take that, Django). But it is clearly not enough.

We need to document the install process and how to run the application, how to participate and use all the tools, how things works, from a developer point of view and from a user point of view, etc, etc.

All of this will be done via `sphinx <http://www.sphinx-doc.org>`_ and the documentation will be hosted on `ReadTheDocs <https://readthedocs.org>`_.

To build the documentation locally, simply run::

  make docs

The documentation will be available at `<https://isshub.readthedocs.io>`_ and will contain everything, including the current document, the documented source code, and every commit.

**Every commit?**

Yes, as will see later in this document, each commit will have a detailed description about the why and the how things are done, so in my opinion, it's like documentation about the process of development. This will be done via `PyDriller <https://pydriller.readthedocs.io>`_.

Testing
=======

For tests I won't use unittest (and so not the Django test subclasses), but `pytest <https://docs.pytest.org/>`_

And I want to do things a little bit differently that we are used too.

I *may* use TDD (`Test-Driven Development <https://en.wikipedia.org/wiki/Test-driven_development>`_), but it's not sure yet, as I'm really not used to it. Will see.

But...

See this `tweet from Cory House <https://mobile.twitter.com/housecor/status/1124308540162805761>`_:

  Test descriptions should ideally include:
    1. The name of the system under test
    2. The scenario under test
    3. The expected result

  Why?
    1. It makes the test easier to understand (remember, tests are docs too)
    2. It makes the test easier to fix when it fails

  -- @housecor 2019-05-03

How to do this?

Generally a test function is written this way:

.. code-block:: python

  def test_concat():
      assert concat('foo', 'bar') == 'foobar'

We can give it a bette name:

.. code-block:: python

  def test_concat_should_concat_two_strings():
      assert concat('foo', 'bar') == 'foobar'

And add a docstring:

.. code-block:: python

  def test_concat_should_concat_two_strings():
      """The ``concat`` function should concat the two given strings."""
      assert concat('foo', 'bar') == 'foobar'

We still don't respect what's said in the tweet.

And also there is no formalism.

What if we can say something like:

  Given the strings "foo" and "bar", when I pass them to the concat function, then it should return "foobar".

So let's use it:

.. code-block:: python

  def test_concat_should_concat_two_strings():
      """Given the strings "foo" and "bar", when I pass them to the concat function, then it should return "foobar"."""
      assert concat('foo', 'bar') == 'foobar'

It's better.

If this test sounds familiar to you, its normal: it's `Gherkin language <https://cucumber.io/docs/gherkin/reference/>`_ and used in BDD (`Behavior-driven development <https://en.wikipedia.org/wiki/Behavior-driven_development>`_)

BDD is generally used for functional tests. But I want to test if it can be applied at other levels: unit tests and integration tests.

So let's use `pytest-bdd <https://github.com/pytest-dev/pytest-bdd>`_ to write this test.

First, the Gherkin, in a file `concat-function.feature`:

.. code-block:: gherkin

  Feature: concat function

    Scenario: Concatenating two strings
      Given a string "foo"
      And a string "bar"
      When I pass them to the concat function
      Then I should get "foobar" in retun

Then the test:

.. code-block:: python

  from pytest_bdd import scenario, given, when, then

  @scenario('concat-function.feature', 'Concatenating two strings')
  def test_concat():
      pass

  @given('a string "foo"')
  def string_foo():
      return 'foo'

  @given('a string "bar"')
  def string_bar():
      return 'bar'

  @when('I pass them to the concat function')
  def concat_foo_and_bar(string_foo, string_bar):
      return concat(string_foo)

  @then('I should get "foobar" in return')
  def result_should_be_foobar(concat_foo_and_bar):
      assert concat_foo_and_bar == 'foobar'

It can seems cumbersome, but we can:
 - use the great power of pytest fixtures
 - parametrize the strings
 - use the parametrize feature of pytest to run a scenario for different inputs

I won't go further here on how to make this code less cumbersome and more reusable, but as all my tests will be written this way, you'll see a lot of examples.

Among the benefits:
 - the "features", ie the tests (in Gherkin) are readable/writeable by everyone
 - we can write our "features" in advance: we have the specifications and documentation
 - we have a formal way of describing what we test and how we do it.
 - every part does one thing so easy to correct if needed

The main (and only one, in my opinion) inconvenient is that tests may be longer to write. But we cannot have some advantages without losing something, and for me it's something I can live with.

And you'll be surprised to see this "BDD" thing used in very unusual case. An example?

.. code-block:: gherkin

  Feature: Describing a Repository

    Scenario: A Repository has a name
        Given a Repository
        Then it must have a field named name

    Scenario: A Repository name is a string
        Given a Repository
        Then its name must be a string

    Scenario: A Repository name cannot be None
        Given a Repository
        Then its name cannot be None

Yes, things like that :)

Git
===

Commits are as much important as code. They hold the whole history of the project and commits can be used to know why things were done a certain way.

So I want my commits to be very descriptive. So I'll follow a specification, based on `conventional commits <https://www.conventionalcommits.org>`_, at least for the title of the commit. Please refer to this documentation to know more about the syntax. The accepted types are:

- build
- ci
- chore
- docs
- feat
- fix
- perf
- refactor
- revert
- style
- tests

The description will be written in restructured text (like all the documentation in this project), with 3 mandatory sections:

Abstract
  A short description of the issue being addressed.

Motivation
  Describe why particular design decisions were made.

Rationale
  Describe why particular design decisions were made.

This is heavily inspired by the `PEP suggested sections <https://www.python.org/dev/peps/pep-0012/#suggested-sections>`_, and other sections can be added from the list in pep 0012, but the three ones above are mandatory, in this order.

This will also be checked by the CI for every commits.

The repository provides a template in `.gitmessage` to use for new commits. To instruct git to use it, run::

    git config commit.template .gitmessage


To check if the last commit is valid, you can run::

    make check-commit

If you want to validate an other commit message than the last one, check `ci/check_commit_message.py -h`

The commits are so important to me that they will be available in the "Internals" part of the documentation in a easily browsable way.

Another important thing is that, in my opinion, the state of the project after every commit must be a valid state: tests must pass. It is absolutely necessary when you want to find the source of a bug via `git-bisect`.

This will be validated by the CI that will run all the CI jobs for all the commits, via the `ci/check-every-commit.sh` script.

Also, I'm a fan of `git-flow <https://nvie.com/posts/a-successful-git-branching-model/>`_ and it (the `avh edition <https://github.com/petervanderdoes/gitflow-avh>`_) will be used in this project, but adding the username in the branch name (easier to filter on if many users), so for example my own development branches will be prefixed by `features/twidi/`. (If branches from other people in pull requests do not follow this pattern, it will be done on my side)

Continuous integration
======================

All of these tools will be run via continuous integration, on `CircleCi <https://circleci.com/>`_.

One status will be posted on Github for each job for every pull requests.  In addition, every commit will also have a status, via the `check-every-commit` job.

To access the list of jobs: https://circleci.com/gh/Isshub-io/isshub


''''''
Coding
''''''

Domain
======

As said previously, I'll use Domain Driven Development, at least some parts, not sure yet.

The first step is to have a `isshub.domain` package.

It will contain some sub-packages:

contexts
--------

Bounded contexts are used to separate groups of things that work together but independent of other contexts.

The contexts hold some entities, objects that have a distinct identity.

The contexts are:

code_repository
'''''''''''''''

The `code_repository` context will hold things around repositories, issues, code requests...

Its entities are:

Repository
    Repositories are the central entity of the whole isshub project. Everything is tied to them, at one level or another.
Namespace
    A namespace is a place where repositories or other namespaces are stored.

Fetching
========

Frontend
========

