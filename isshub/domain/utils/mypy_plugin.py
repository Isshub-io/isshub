"""Mypy plugin to declare our own functions to create ``attr`` classes and fields.

Inspired by https://github.com/python/mypy/issues/5406#issuecomment-490547091

"""

# type: ignore

# pylint: disable=no-name-in-module
from mypy.plugin import Plugin
from mypy.plugins.attrs import attr_attrib_makers, attr_class_makers


# pylint: enable=no-name-in-module


attr_class_makers.add("isshub.domain.utils.entity.validated")
attr_attrib_makers.add("isshub.domain.utils.entity.optional_field")
attr_attrib_makers.add("isshub.domain.utils.entity.required_field")


class MypyPlugin(Plugin):
    """Plugin class for mypy.

    Notes
    -----
    Our plugin does nothing but it has to exist so this file gets loaded.
    """


def plugin(version: str):  # pylint: disable=unused-argument
    """Define the plugin to use.

    Parameters
    ----------
    version : str
        The version for which to return a plugin class. Ignored in our case.

    Returns
    -------
    Type[Plugin]
        The plugin class to be used by mypy

    """
    return MypyPlugin
