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

Linting
=======

Documentation
=============

We need to document the install process and how to run the application, how to participate and use all the tools, how things works, from a developer point of view and from a user point of view, etc, etc.

All of this will be done via `sphinx <http://www.sphinx-doc.org>`_ and the documentation will be hosted on `ReadTheDocs <https://readthedocs.org>`_.

To build the documentation locally, simply run::

  make docs


The documentation will be available at `<https://isshub.readthedocs.io>`_ and will contain everything, including the current document and the documented source code.

Testing
=======

For tests I won't use unittest (and so not the Django test subclasses), but `pytest <https://docs.pytest.org/>`_

And I want to do things a little bit differently that we are used too.

I *may* use TDD (`Test-Driven Development <https://en.wikipedia.org/wiki/Test-driven_development>`_), but it's not sure yet, as I'm really not used to it. Will see.

Git
===

''''''
Coding
''''''

Domain
======

Fetching
========

Frontend
========

