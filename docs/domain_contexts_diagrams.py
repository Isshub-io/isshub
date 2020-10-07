#!/usr/bin/env python

"""Make the diagrams of entities for each isshub domain contexts."""

import importlib
import inspect
import os.path
import pkgutil
import re
import sys
from enum import Enum
from types import ModuleType
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    get_type_hints,
)

import attr

from isshub.domain import contexts
from isshub.domain.utils.entity import BaseEntity
from isshub.domain.utils.repository import AbstractRepository


if TYPE_CHECKING:
    from attr import _Fields  # pylint: disable=no-name-in-module

    try:
        from typing import get_args, get_origin  # type: ignore
    except ImportError:
        # pylint: disable=C,W
        # this happen in my python 3.8 virtualenv: it shouldn't but can't figure out the problem
        def get_args(tp: Any) -> Any:  # noqa
            return getattr(tp, "__args__", ())

        def get_origin(tp: Any) -> Any:  # noqa
            return getattr(tp, "__origin__", None)


else:
    from typing import get_args, get_origin


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


def filter_classes_from_module(
    classes: Dict[str, Type], module_name: str
) -> Dict[str, Type]:
    """Restrict the given classes to the one found in the given module.

    Parameters
    ----------
    classes : Dict[str, Type]
        A dict of classes from which to extract the ones to return. Full python path as keys, and
        the classes as values.
    module_name : str
        The python path of the module for which we want the classes

    Returns
    -------
    Dict[str, Type]
        The filtered `classes` (same format as the given `classes` argument)

    """
    prefix = f"{module_name}."
    return {
        class_name: klass
        for class_name, klass in classes.items()
        if class_name.startswith(prefix)
    }


def render_dot_file(output_path: str, name: str, content: str) -> None:
    """Save `content` of a dot file.

    Parameters
    ----------
    output_path : str
        The directory where to store the dot file
    name : str
        The base name (without extension) of the final file
    content : str
        The content to save in the dot file
    """
    dot_path = os.path.join(output_path, f"{name}.dot")
    print(f"Writing diagram {dot_path}")
    with open(dot_path, "w") as file_d:
        file_d.write(content)


def render_dot_record(identifier: str, title: str, lines: Iterable[str]) -> str:
    """Render a record in a dot file.

    Parameters
    ----------
    identifier : str
        The identifier of the record in the dot file
    title : str
        The title of the record. Will be centered.
    lines : Iterable[str]
        The lines of the record. Will be left aligned.

    Returns
    -------
    str
        The line representing the record for the dot file.

    """
    lines_parts = "|".join(f"{line} {AlignLeft}" for line in lines)
    return f'{identifier} [label="{title}|{lines_parts}"]'


def render_dot_link(source: str, dest: str, label: Optional[str]) -> str:
    """Render a link between a `source` and a `dest` in a dot file.

    Parameters
    ----------
    source : str
        The source of the link in the dot file
    dest : str
        The destination of the link in the dot file
    label : Optional[str]
        If set, will be the label of the link.

    Returns
    -------
    str
        The line representing the link for the dot file.

    """
    result = f"{source} -> {dest}"
    if label:
        result += f' [label="{label}"]'
    return result


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
        The definition of the enum to represent it in the diagram

    """
    dot_name = get_dot_identifier(get_python_path(enum))
    return dot_name, render_dot_record(
        dot_name, f"<__class__> Enum: {enum.__name__}", (value.value for value in enum)
    )


def get_optional_type(type_: Any) -> Union[None, Any]:
    """Get the optional type defined in the given `type_`.

    Only works for one of these syntax:

      - ``Optional[TheType]``
      - ``Union[TheType, None'``

    Parameters
    ----------
    type_ : Any
        The type (from from a call to ``get_type_hints``) to analyse

    Returns
    -------
    Union[None, Any]
        Will be ``None`` if the `type_`

    """
    if get_origin(type_) is not Union:
        return None
    args = get_args(type_)
    if len(args) != 2:
        return None
    if NoneType not in args:
        return None
    return [arg for arg in args if arg is not NoneType][0]


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

        if get_origin(field_type) is Union:
            args = get_args(field_type)
            if len(args) != 2:
                raise NotImplementedError(
                    f"{name}.{field_name} : {field_type}"
                    " - Union type with more that two choices is not implemented"
                )
            if NoneType not in args:
                raise NotImplementedError(
                    f"{name}.{field_name} : {field_type}"
                    " - Union type without None is not implemented"
                )
            required = False
            field_type = [arg for arg in args if arg is not NoneType][0]

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


def render_entity_link(
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

    return render_dot_link(
        f"{source_name}:{field_name}", f"{dest_name}:__class__", link_label
    )


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
            links.add(
                render_entity_link(dot_name, field_name, link_to, required, attr_fields)
            )

        fields[field_name] = field_type.__name__
        if not required:
            fields[field_name] = f"{fields[field_name]} (optional)"

    lines[dot_name] = render_dot_record(
        dot_name,
        f"<__class__> Entity: {entity.__name__}",
        (f"<{f_name}> {f_name} : {f_type}" for f_name, f_type in fields.items()),
    )

    return lines, links


def make_domain_context_entities_diagram(
    context_name: str, subclasses: Dict[str, Type[BaseEntity]], output_path: str
) -> None:
    """Make the graph of entities in the given contexts.

    Parameters
    ----------
    context_name : str
        The name of the context, represented by the python path of its module
    subclasses : Dict[str, Type[BaseEntity]]
        All the subclasses of ``BaseEntity`` from which to extract the ones to render.
        Only subclasses present in the given context will be rendered.
    output_path : str
        The path where to save the generated graph

    """
    # restrict the subclasses of ``BaseEntity`` to the ones in the given module name
    context_subclasses = filter_classes_from_module(subclasses, context_name)

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
  label = "Domain context entities [%s]"
  #labelloc = "t"
  rankdir=LR
  node[shape=record]
"""
        % context_name
    )
    for line in tuple(entity_lines.values()) + tuple(links):
        dot_file_content += f"  {line}\n"
    dot_file_content += "}"

    render_dot_file(output_path, f"{context_name}-entities", dot_file_content)


re_optional = re.compile(r"(?:typing\.)?Union\[(.*), NoneType]")
re_literal = re.compile(r"(?:typing\.)?Literal\[(.*?)]")


def render_repository(  # pylint: disable=too-many-locals
    name: str, repository: Type[AbstractRepository], context: str
) -> str:
    """Render the content of the dot file for the given `repository`.

    Parameters
    ----------
    name : str
        The name of the `repository`
    repository : Type[AbstractRepository]
        The repository to render
    context : str
        The name of the context  containing the `repository`

    Returns
    -------
    str
        The content of the dot file for the diagram of the given `repository`

    """
    members = {
        name: value
        for name, value in inspect.getmembers(repository)
        if not name.startswith("_")
    }
    methods = {
        name: value for name, value in members.items() if inspect.isfunction(value)
    }
    entity_class = members["entity_class"]

    re_context = re.compile(context + r".(?:\w+\.)*(\w+)")

    def optimize_annotation(type_: Any) -> str:  # pylint: disable=W
        if isinstance(type_, type):
            return type_.__name__
        result = str(type_)
        for regexp, replacement in (
            (re_context, r"\1"),
            (re_literal, r"\1"),
            (re_optional, r"Optional[\1]"),
        ):
            result = regexp.sub(replacement, result)
        return result.replace("~Entity", entity_class.__name__).replace("typing.", "")

    methods_lines = []
    for method_name, method in methods.items():
        signature = inspect.signature(method)
        params = []
        for param_name, param in signature.parameters.items():
            if param_name == "self":
                continue
            params.append(
                "".join(
                    (
                        param_name,
                        ""
                        if not param.annotation or param.annotation is param.empty
                        else ": %s" % optimize_annotation(param.annotation),
                        "" if param.default is param.empty else " = %s" % param.default,
                    )
                )
            )
        methods_lines.append(
            f"{method_name}(%s)%s"
            % (
                ", ".join(params),
                ""
                if not signature.return_annotation
                or signature.return_annotation is signature.empty
                else " → %s" % optimize_annotation(signature.return_annotation),
            )
        )

    return render_dot_record(
        get_dot_identifier(get_python_path(repository)),
        f"{repository.__name__} (for {entity_class.__name__} entity)",
        methods_lines,
    )


def make_domain_context_repositories_diagram(
    context_name: str, subclasses: Dict[str, Type[AbstractRepository]], output_path: str
) -> None:
    """Make the graph of entities in the given contexts.

    Parameters
    ----------
    context_name : str
        The name of the context, represented by the python path of its module
    subclasses : Dict[str, Type[AbstractRepository]]
        All the subclasses of ``AbstractRepository`` from which to extract the ones to render.
        Only subclasses present in the given context will be rendered.
    output_path : str
        The path where to save the generated graph

    """
    # restrict the subclasses of ``AbstractRepository`` to the ones in the given module name
    context_subclasses = filter_classes_from_module(subclasses, context_name)
    rendered_repositories = [
        render_repository(subclass_name, subclass, context_name)
        for subclass_name, subclass in context_subclasses.items()
    ]

    # compose the content of the dot file
    dot_file_content = (
        """\
digraph domain_context_repositories {
  label = "Domain context repositories [%s]"
  #labelloc = "t"
  rankdir=LR
  node[shape=record]
"""
        % context_name
    )
    for line in rendered_repositories:
        dot_file_content += f"  {line}\n"
    dot_file_content += "}"

    render_dot_file(output_path, f"{context_name}-repositories", dot_file_content)


def make_domain_contexts_diagrams(output_path: str) -> None:
    """Make the diagrams of entities for each domain contexts.

    Parameters
    ----------
    output_path : str
        The path where to save the generated diagrams

    """
    # we need to import all python files (except tests) to be sure we have access to all python code
    import_submodules(contexts, skip_names=["tests"])

    entities = get_final_subclasses(BaseEntity)
    repositories = get_final_subclasses(AbstractRepository)

    # we render each context independently, assuming that each one is directly at the root of
    # the ``contexts`` package
    for module in pkgutil.iter_modules(
        path=contexts.__path__, prefix=contexts.__name__ + "."  # type: ignore
    ):
        make_domain_context_entities_diagram(module.name, entities, output_path)
        make_domain_context_repositories_diagram(module.name, repositories, output_path)


if __name__ == "__main__":
    assert len(sys.argv) > 1 and sys.argv[1], "Missing output directory"
    make_domain_contexts_diagrams(sys.argv[1])
