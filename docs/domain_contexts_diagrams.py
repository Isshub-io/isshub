#!/usr/bin/env python

"""Make the diagrams of entities for each isshub domain contexts."""

import importlib
import os.path
import pkgutil
import sys
from enum import Enum
from types import ModuleType
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    get_type_hints,
)

import attr


if TYPE_CHECKING:
    from attr import _Fields  # pylint: disable=no-name-in-module

from isshub.domain import contexts
from isshub.domain.utils.entity import BaseEntity


def import_submodules(
    package: Union[str, ModuleType], skip_names: Optional[List[str]] = None
) -> Dict[str, ModuleType]:
    """Import all submodules of a module, recursively, including subpackages.

    Parameters
    ----------
    package : Union[str, ModuleType]
        The package to import recursively
    skip_names : Optional[List[str]]
        A list of names of packages to ignore. For example ``['tests']`` to ignore packages
        named "tests" (and subpackages)

    Returns
    -------
    Dict[str, ModuleType]
        Dict containing all imported packages
    """
    if skip_names is None:
        skip_names = []
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for __, name, is_package in pkgutil.walk_packages(
        path=package.__path__, prefix=package.__name__ + "."  # type: ignore
    ):
        if any(
            name.endswith(f".{skip_name}") or f".{skip_name}." in name
            for skip_name in skip_names
        ):
            continue
        results[name] = importlib.import_module(name)
        if is_package:
            results.update(import_submodules(name, skip_names=skip_names))
    return results


def get_python_path(klass: Type) -> str:
    """Get the full python path of a class.

    Parameters
    ----------
    klass: type
        The class for which we want the python path

    Returns
    -------
    str
        The python path of the class, like "path.to.module.class"

    """
    return f"{klass.__module__}.{klass.__name__}"


def get_dot_identifier(name: str) -> str:
    """Convert a string to be ready to be used as an identifier in a .dot file.

    It actually only handles "python paths", ie the only thing to be replaced is the dot character.

    We replace theses dots by three underscores.

    Parameters
    ----------
    name : str
       The string to convert

    Returns
    -------
    str
       The converted string ready to be used as a dot identifier

    """
    return name.replace(".", "___")


def get_final_subclasses(klass: Type) -> Dict[str, Type]:
    """Get all the subclasses of `klass` that don't have subclasses.

    Parameters
    ----------
    klass : Type
        The subclasses to analyze

    Returns
    -------
    Dict[str, Type]
        A dict with one entry for each "final subclass", with the python paths as keys and the class
        themselves as values.

    """
    if not klass.__subclasses__():
        return {get_python_path(klass): klass}
    result = {}
    for subclass in klass.__subclasses__():
        result.update(get_final_subclasses(subclass))
    return result


NoneType = type(None)
AlignLeft = chr(92) + "l"  # "\l"


def render_enum(enum: Type[Enum]) -> Tuple[str, str]:
    """Render the given `enum` to be incorporated in a dot file.

    Parameters
    ----------
    enum : Type[Enum]
        The enum to render

    Returns
    -------
    str
        The name of the enum as a dot identifier
    str
        The definition of the enum to represent it in the graph

    """
    dot_name = get_dot_identifier(get_python_path(enum))
    enum_parts = "|".join(f"{value.value} {AlignLeft}" for value in enum)
    return (
        dot_name,
        f'{dot_name} [label="<__class__> Enum: {enum.__name__}|{enum_parts}"]',
    )


def validate_entity(
    name: str,
    entity: Type[BaseEntity],
    context: str,
    linkable_entities: Dict[str, Type[BaseEntity]],
) -> Dict[str, Tuple[Any, bool]]:
    """Validate that we can handle the given entity and its fields.

    We only handle fields defined with a "type hint", restricted to:
    - the ones with a direct type
    - the ones defined as ``Optional`` (which is, in fact, a ``Union`` with the type and
      ``NoneType``)

    The direct type, if in the ``isshub`` namespace, must be in the given `context` (in the given
    `linkable_entities`.

    Parameters
    ----------
    name : str
        The name of the `entity`
    entity : Type[BaseEntity]
        The entity to validate
    context : str
        The name of the context, ie the name of the module containing the `entity` and the
        `linkable_entities`
    linkable_entities : Dict[str, Type[BaseEntity]]
        A dict containing all the entities the `entity` to validate can link to, with their full python
        path as keys, and the entities themselves as values

    Returns
    -------
    Dict[str, Tuple[Any, bool]]
        A dict with an entry for each field. Each field has its name as key, and, as value, a tuple
        with the final type and if the field is required or not.

    Raises
    ------
    NotImplementedError
        If the type is a ``Union`` of more than two types or with one not being ``NoneType``
    TypeError
        If the type is an object in the ``isshub`` namespace that is not in the given
        `linkable_entities` (except for enums, actually)

    """
    types = get_type_hints(entity)
    fields = {}
    for field_name, field_type in types.items():
        required = True

        if getattr(field_type, "__origin__", None) is Union:
            if len(field_type.__args__) != 2:
                raise NotImplementedError(
                    f"{name}.{field_name} : {field_type}"
                    " - Union type with more that two choices is not implemented"
                )
            if NoneType not in field_type.__args__:
                raise NotImplementedError(
                    f"{name}.{field_name} : {field_type}"
                    " - Union type without None is not implemented"
                )
            required = False
            field_type = [arg for arg in field_type.__args__ if arg is not NoneType][0]

        if field_type.__module__.startswith("isshub") and not issubclass(
            field_type, Enum
        ):
            if get_python_path(field_type) not in linkable_entities:
                raise TypeError(
                    f"{name}.{field_name} : {field_type}"
                    f" - It's not a valid entity in context {context}"
                )

        fields[field_name] = (field_type, required)

    return fields


def render_link(
    source_name: str,
    field_name: str,
    dest_name: str,
    required: bool,
    attr_fields: "_Fields",
) -> str:
    """Render a link between the field of an entity to another class.

    Parameters
    ----------
    source_name : str
        The dot identifier of the source class. The source class is expected to be an entity class
    field_name : str
        The field in the source class that is linked to the dest class
    dest_name : str
        The dot identifier of the dest class.
    required : bool
        If the link is mandatory or optional
    attr_fields : NamedTuple
        A named tuple containing all fields as viewed by the ``attr`` module, to access the metadata
        of such fields, to get the ``relation_verbose_name`` metadata. Without such a medata, the
        link will be simply labelled "0..1" or "1" (depending on the `required` attribute), else
        this verbose name will be used.

    Returns
    -------
    str
        The string to be used in the dot file to represent the link.

    """
    try:
        link_label = (
            f'{getattr(attr_fields, field_name).metadata["relation_verbose_name"]}'
        )
    except Exception:  # pylint: disable=broad-except
        link_label = "(" + ("1" if required else "0..1") + ")"

    return f'{source_name}:{field_name} -> {dest_name}:__class__ [label="{link_label}"]'


def render_entity(
    name: str,
    entity: Type[BaseEntity],
    context: str,
    linkable_entities: Dict[str, Type[BaseEntity]],
) -> Tuple[Dict[str, str], Set[str]]:
    """Render the given `entity` to be incorporated in a dot file, with links.

    Parameters
    ----------
    name : str
        The name of the `entity`
    entity : Type[BaseEntity]
        The entity to render
    context : str
        The name of the context, ie the name of the module containing the `entity` and the
        `linkable_entities`
    linkable_entities : Dict[str, Type[BaseEntity]]
        A dict containing all the entities the `entity` to validate can link to, with their full python
        path as keys, and the entities themselves as values

    Returns
    -------
    Dict[str, str]
        Lines representing the entities (or enums) to render in the graph.
        The keys are the dot identifier of the entity (or enum), and the values are the line to put
        in the dot file to render them.
        There is at least one entry, the rendered `entity`, but there can be more entries, if the
        `entity` is linked to some enums (we use a dict to let the caller to deduplicate enums with
        the same identifiers if called from many entities)
    Set[str]
        Lines representing the links between the `entity` and other entities or enums.

    """
    lines = {}
    links = set()

    dot_name = get_dot_identifier(name)
    attr_fields = attr.fields(entity)
    fields = {}

    for field_name, (field_type, required) in validate_entity(
        name, entity, context, linkable_entities
    ).items():

        link_to = None

        if issubclass(field_type, Enum):
            link_to, enum_line = render_enum(field_type)
            lines[link_to] = enum_line
        elif field_type.__module__.startswith("isshub"):
            link_to = get_dot_identifier(get_python_path(field_type))

        if link_to:
            links.add(render_link(dot_name, field_name, link_to, required, attr_fields))

        fields[field_name] = field_type.__name__
        if not required:
            fields[field_name] = f"{fields[field_name]} (optional)"

    fields_parts = "|".join(
        f"<{f_name}> {f_name} : {f_type} {AlignLeft}"
        for f_name, f_type in fields.items()
    )
    lines[
        dot_name
    ] = f'{dot_name} [label="<__class__> Entity: {entity.__name__}|{fields_parts}"]'

    return lines, links


def make_domain_context_graph(
    context_name: str, subclasses: Dict[str, Type[BaseEntity]], output_path: str
) -> None:
    """Make the graph of entities in the given contexts.

    Parameters
    ----------
    context_name : str
        The name of the context, represented by the python path of its module
    subclasses : Dict[str, Type[BaseEntity]]
        All the subclasses of ``BaseEntity`` from which to extract the modules to render.
        Only subclasses present in the given context will be rendered.
    output_path : str
        The path where to save the generated graph

    """
    # restrict the subclasses of ``BaseEntity`` to the ones in the given module name
    context_subclasses = {
        subclass_name: subclass
        for subclass_name, subclass in subclasses.items()
        if subclass_name.startswith(context_name + ".")
    }

    # render entities and all links between them
    entity_lines, links = {}, set()
    for subclass_name, subclass in context_subclasses.items():
        subclass_lines, subclass_links = render_entity(
            subclass_name,
            subclass,
            context_name,
            context_subclasses,
        )
        entity_lines.update(subclass_lines)
        links.update(subclass_links)

    # compose the content of the dot file
    dot_file_content = (
        """\
digraph domain_context_entities {
  label = "Domain context [%s]"
  #labelloc = "t"
  rankdir=LR
  node[shape=record]
"""
        % context_name
    )
    for line in tuple(entity_lines.values()) + tuple(links):
        dot_file_content += f"  {line}\n"
    dot_file_content += "}"

    dot_path = os.path.join(output_path, f"{context_name}-entities.dot")
    print(f"Writing graph for domain context {context_name} in {dot_path}")
    with open(dot_path, "w") as file_d:
        file_d.write(dot_file_content)


def make_domain_contexts_diagrams(output_path: str) -> None:
    """Make the diagrams of entities for each domain contexts.

    Parameters
    ----------
    output_path : str
        The path where to save the generated diagrams

    """
    # we need to import all python files (except tests) to find all subclasses of ``BaseEntity``
    import_submodules(contexts, skip_names=["tests"])
    subclasses = get_final_subclasses(BaseEntity)

    # we render each context independently, assuming that each one is directly at the root of
    # the ``contexts`` package
    for module in pkgutil.iter_modules(
        path=contexts.__path__, prefix=contexts.__name__ + "."  # type: ignore
    ):
        make_domain_context_graph(module.name, subclasses, output_path)


if __name__ == "__main__":
    assert len(sys.argv) > 1 and sys.argv[1], "Missing output directory"
    make_domain_contexts_diagrams(sys.argv[1])
