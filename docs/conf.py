# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#


import os
import subprocess
import sys
from glob import glob

from sphinx.ext import apidoc


# for apidoc
sys.path.insert(0, os.path.abspath("../isshub"))

# default env var to be used by the doc builder, for example readthedocs
# os.environ.setdefault("XXX", "yyy")


# -- Project information -----------------------------------------------------

project = "IssHub"
copyright = '2019, Stéphane "Twidi" Angel'
author = 'Stéphane "Twidi" Angel'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.graphviz",
    "sphinx_autodoc_typehints",
    "sphinxprettysearchresults",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "apidoc_templates"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

html_theme_options = {
    "navigation_depth": -1,
    "collapse_navigation": True,
    "sticky_navigation": True,
    "includehidden": True,
    "titles_only": False,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "isshubdoc"

# -- Extension configuration -------------------------------------------------

html_use_old_search_snippets = True

# -- Run apidoc when building the documentation-------------------------------

napoleon_use_ivar = True
add_module_names = False


def run_apidoc(_):
    """Run apidoc on the project and store source doc in ``source`` dir."""

    current_dir = os.path.dirname(__file__)

    output_path = os.path.join(current_dir, "source")
    source_path = os.path.normpath(os.path.join(current_dir, "..", "isshub"))
    exclude_paths = [
        os.path.join(source_path, exclude_path) for exclude_path in ["*/tests/*"]
    ]
    apidoc.main(
        [
            "--force",
            "--module-first",
            "--separate",
            "-d",  # maxdepth
            "6",
            "--doc-project",
            "Python packages",
            "--templatedir",
            os.path.join(current_dir, "apidoc_templates"),
            "--output-dir",
            output_path,
            source_path,
        ]
        + exclude_paths
    )


def run_gherkindoc(_):
    """Run gherkindoc on the project and store bdd doc in ``bdd`` dir."""

    current_dir = os.path.dirname(__file__)

    output_path = os.path.join(current_dir, "bdd")
    source_path = os.path.normpath(os.path.join(current_dir, "..", "isshub"))
    subprocess.run(
        [
            "sphinx-gherkindoc",
            source_path,
            output_path,
            "--toc-name",
            "index",
            "--maxtocdepth",
            "5",
        ]
    )

    # add the diagrams
    subprocess.run(
        [
            os.path.join(current_dir, "domain_contexts_diagrams.py"),
            output_path,
        ]
    )

    # incorporate the diagrams in each contexts doc
    for file in glob(os.path.join(output_path, "*-entities.dot")):
        base_name = os.path.basename(file)[:-13]
        rst_file = os.path.join(output_path, f"{base_name}-toc.rst")
        with open(rst_file, "r") as file_d:
            rst_lines = file_d.readlines()
        rst_lines.insert(3, f".. graphviz:: {base_name}-entities.dot\n\n")
        with open(rst_file, "w") as file_d:
            file_d.write("".join(rst_lines))


def run_git_to_sphinx(_):
    """Add git content into doc"""

    update_remote_branches_env_var = "GIT_TO_SPHINX_UPDATE_BRANCHES"
    update_remote_branches = os.environ.get(update_remote_branches_env_var)
    if os.environ.get("READTHEDOCS"):
        os.environ[update_remote_branches_env_var] = "TRUE"

    try:
        current_dir = os.path.dirname(__file__)
        subprocess.run(
            [
                os.path.join(current_dir, "git_to_sphinx.py"),
                os.path.normpath(os.path.join(current_dir, "..")),
                os.path.normpath(os.path.join(current_dir, "source")),
            ]
        )
    finally:
        if not update_remote_branches and os.environ.get(
            update_remote_branches_env_var
        ):
            del os.environ[update_remote_branches_env_var]


def setup(app):
    # Run apidoc
    app.connect("builder-inited", run_apidoc)
    app.connect("builder-inited", run_gherkindoc)
    app.connect("builder-inited", run_git_to_sphinx)
    # Add custom css/js for rtd template
    app.add_css_file("css/custom.css")
    app.add_css_file("css/gherkin.css")
    app.add_js_file("js/custom.js")
