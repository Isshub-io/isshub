#!/usr/bin/env python

# Set env `GIT_TO_SPHINX_UPDATE_BRANCHES` to other than empty string to update the remote branches
# Careful: in dev environment it will reset all your local branches if they diverged from the
# remove ones

import os
import re
import shutil
import sys
import tempfile
from collections import defaultdict
from contextlib import contextmanager
from functools import partial

import rstcheck
from cached_property import cached_property
from git.objects.util import from_timestamp
from pydriller import RepositoryMining as RepositoryMiningBase
from pydriller.domain.commit import ModificationType
from pydriller.git_repository import GitRepository as GitRepositoryBase


DOC_DIRNAME = "git"
SOURCE_DIRNAME = "source"
DIRNAME = os.path.dirname(__file__)
BASEPATH = os.path.join(DIRNAME, DOC_DIRNAME)
SOURCE_BASE_PATH = os.path.join(DIRNAME, SOURCE_DIRNAME)

REMOVED = " (removed)"

GIT_ENVIRON = {
    "GIT_COMMITTER_NAME": "git-to-sphinx",
    "GIT_COMMITTER_EMAIL": "git-to-sphinx@example.com",
    "GIT_AUTHOR_NAME": "git-to-sphinx",
    "GIT_AUTHOR_EMAIL": "git-to-sphinx@example.com",
}


@contextmanager
def override_environ(**env):
    original_env = {key: os.getenv(key) for key in env}
    os.environ.update(env)
    try:
        yield
    finally:
        for key, value in original_env.items():
            if value is None:
                del os.environ[key]
            else:
                os.environ[key] = value


def slugify(text):
    text = text.lower()
    for c in slugify.to_underscore:
        text = text.replace(c, "_")
    text = slugify.re_W.sub("", text).replace("_", " ")
    return slugify.re_s.sub(" ", text).strip().replace(" ", "-")


slugify.to_underscore = [" ", "-", ".", "/"]
slugify.re_W = re.compile(r"\W")
slugify.re_s = re.compile(r"\s+")


def escape_path(path):
    if path.endswith(".rst"):
        path += "_"
    return path


def escape_subject(text):
    for what, how in escape_subject.replacements:
        text = text.replace(what, how)
    return text


escape_subject.replacements = [("*", r"\*"), ("_", r"\_")]


def path_in_tree(path, tree, allow_root=True):
    if allow_root and (not path or path == "/"):
        return True
    return path in tree


MODIFICATION_TYPES = {
    "ADD": "Added",
    "COPY": "Copied",
    "RENAME": "Renamed",
    "DELETE": "Deleted",
    "MODIFY": "Modified",
    "UNKNOWN": "Unknown",
}


class GitRepository(GitRepositoryBase):
    @cached_property
    def git(self):
        return super().git

    def _discover_main_branch(self, repo):
        if repo.head.is_detached:
            for branch in repo.branches:
                if branch.commit.hexsha == repo.head.commit.hexsha:
                    self._conf.set_value("main_branch", branch.name)
        else:
            super()._discover_main_branch(repo)

    @cached_property
    def repo(self):
        return super().repo

    def get_list_tags(self):
        for tag in sorted(
            self.repo.tags,
            key=lambda t: t.commit.committed_datetime,
            reverse=True,
        ):
            yield tag

    def get_list_branches(self):
        for branch in sorted(
            self.repo.branches,
            key=lambda t: t.commit.committed_datetime,
            reverse=True,
        ):
            yield branch

    def get_list_tree(self, node, parent_path=""):
        for child in node:
            path = os.path.join(parent_path, child.name)
            yield (child, path)
            if child.type == "tree":
                yield from self.get_list_tree(child, path)

    def get_flat_tree(self):
        yield from self.get_list_tree(self.get_head()._c_object.tree)


class RepositoryMining(RepositoryMiningBase):
    def get_git_repo(self):
        path_repo = self._conf.get("path_to_repos")[0]

        if self._is_remote(path_repo):
            path_repo = self._clone_remote_repo(self._clone_folder(), path_repo)

        git_repo = GitRepository(path_repo)

        # we need to fetch all branches:
        repo = git_repo.repo

        if os.environ.get("GIT_TO_SPHINX_UPDATE_BRANCHES"):
            # get remote branches not fetched yet
            existing_branches = {
                branch.name: branch.commit.hexsha for branch in repo.branches
            }
            remote_branches = {}
            for ref_info in repo.remote("origin").fetch():
                local_ref_name = ref_info.name.split("/", 1)[1]
                if ref_info.commit.hexsha != existing_branches.get(local_ref_name):
                    remote_branches[local_ref_name] = ref_info.name

            if remote_branches:
                # save the current head
                head_detached = repo.head.is_detached
                if head_detached:
                    current_ref = repo.head.commit
                else:
                    current_ref = repo.head.ref

                # stash existing updates if needed
                with override_environ(**GIT_ENVIRON):
                    stashed = "No local changes to save" not in repo.git.stash(
                        "save", "-u"
                    )

                # fetch remote branches not fetched yet
                for local_branch_name, remote_branch_name in remote_branches.items():
                    repo.git.checkout("-B", local_branch_name, remote_branch_name)

                # restore previous head
                if head_detached:
                    repo.git.checkout(current_ref.hexsha)
                else:
                    current_ref.checkout()

                # and restore previous updates
                if stashed:
                    with override_environ(**GIT_ENVIRON):
                        repo.git.stash("pop")

        # get the branch from the head now that we are sure we have all branches
        git_repo._discover_main_branch(repo)

        return git_repo

    def __init__(self, path_to_repo):
        super().__init__(path_to_repo=path_to_repo, order="reverse")

        if not isinstance(self._conf.get("path_to_repo"), str):
            raise Exception("The path to the repo has to be of type 'string'")

        self.git_repo = self.get_git_repo()

    def traverse_tags(self):
        for tag in self.git_repo.get_list_tags():
            yield tag

    def traverse_branches(self):
        for branch in self.git_repo.get_list_branches():
            yield branch

    def traverse_commits(self, revision=None):
        for commit in self.git_repo.get_list_commits(rev=revision, reverse=False):
            yield commit

    def traverse_tree(self):
        yield from self.git_repo.get_flat_tree()


BRANCH_TEMPLATE = """\
:doc:`{name} </{doc_dirname}/branches/{slug}>`{active}
  {commit}
"""

TAG_TEMPLATE = """\
:doc:`{name} </{doc_dirname}/tags/{slug}>`
  {message}
"""

BRANCH_TEMPLATE_SHORT = """\
:doc:`{name} </{doc_dirname}/branches/{slug}>` {head}
"""

TAG_TEMPLATE_SHORT = """\
:doc:`{name} </{doc_dirname}/tags/{slug}>` {head}
"""

COMMIT_TEMPLATE = """\
**{subject}** :doc:`[{short_hexsha}] </{doc_dirname}/commits/{hexsha}>` — *{at}*
"""

INDEX_PAGE_TEMPLATE = """\
Git repository
==============

.. toctree::

   Content <content/index>
   branches/index
   tags/index
   commits/index

"""

BRANCHES_PAGE_TEMPLATE = """\
========
Branches
========

.. toctree::
   :hidden:

{branch_links}

{branches}
"""

BRANCH_TOCTREE_LINK_TEMPLATE = """\
{name} {active} </{doc_dirname}/branches/{slug}>
"""

TAGS_PAGE_TEMPLATE = """\
====
Tags
====

.. toctree::
   :hidden:

{tag_links}

{tags}
"""

TAG_TOCTREE_LINK_TEMPLATE = """\
{name} </{doc_dirname}/tags/{slug}>
"""

COMMITS_PAGE_TEMPLATE = """\
=======
Commits
=======

.. toctree::
   :glob:
   :hidden:

   *

.. note::

   To see commits, pick a :doc:`branch </{doc_dirname}/branches/index>`
"""

COMMIT_PAGE_TEMPLATE = """\
{subject_line}
{subject}
{subject_line}

.. contents::
   :depth: 1
   :local:
   :backlinks: top

{description}

----
Info
----

Hash
  {commit_hexsha}

Date
  {commit_at}

Parents
{parents}

Children
{children}

Branches
{branches}

Tags
{tags}

-------
Changes
-------

.. contents::
   :depth: 1
   :local:
   :backlinks: top

{modifications}

"""

LINK_TO_SOURCE_TEMPLATE = """\
:doc:`View documentation </{source_dirname}/{python_path}>`
"""

FILE_PAGE_TEMPLATE = """\
{title_line}
{title}
{title_line}

.. contents::
   :depth: 1
   :local:
   :backlinks: top

----
Info
----

Parent directory
    :doc:`{dirname}{parent_old} </{doc_dirname}/content/{escaped_dirname}index>`

Last update
   :ref:`{last_type} — {last_updated_at} <{path}-{last_commit_hash}>`
{new_path}
{old_path}

-----------
Last source
-----------
{documentation}
{source_code}

-------
Changes
-------

.. contents::
   :depth: 1
   :local:
   :backlinks: top

{modifications}

"""

DIR_PAGE_TEMPLATE = """\
{title_line}
{title}
{title_line}

.. toctree::
   :hidden:

{entry_links}

{parent_directory}

Content
{entries}
"""

DIR_ENTRY_FILE_TEMPLATE = """\
- :doc:`{name}{old} </{doc_dirname}/content/{escaped_path}>`
"""

DIR_ENTRY_DIR_TEMPLATE = """\
- :doc:`{name}/{old} </{doc_dirname}/content/{escaped_path}/index>`
"""

DIR_TOCTREE_FILE_TEMPLATE = """\
{name}{old} </{doc_dirname}/content/{escaped_path}>
"""

DIR_TOCTREE_DIR_TEMPLATE = """\
{name}/{old} </{doc_dirname}/content/{escaped_path}/index>
"""

DESCRIPTION_TEMPLATE = """\

-----------
Description
-----------

.. include:: {description_path}
{kind}
"""

MODIFICATION_FOR_PATH_IN_COMMIT_TEMPLATE = """\
{path}
{path_line}

.. note::

   :doc:`View last source and history </{doc_dirname}/content/{escaped_path}>`

Type
  {type}
{old_path}
Stats
  +{added} -{removed}

{diff}
"""

MODIFICATION_FOR_COMMIT_IN_PATH_TEMPLATE = """\

.. _{current_path}-{commit_hash}:

{commit_subject}
{commit_subject_line}

Commit
  Hash
    :doc:`{commit_hash} </{doc_dirname}/commits/{commit_hash}>`
  Date
    {commit_at}

Type
  {type}
{old_path}
{new_path}
Stats
  +{added} -{removed}

{diff}
"""

MODIFICATION_DIFF_TEMPLATE = """\

.. code-block:: diff

{diff}
"""

SOURCE_CODE_TEMPLATE = """\

.. code-block::
   :linenos:

{source_code}
"""


BRANCH_PAGE_TEMPLATE = """\
{name_line}
{name}
{name_line}
{active}

{commits}
"""

BRANCH_IS_ACTIVE_TEMPLATE = """\

.. NOTE::
   This is the active branch
"""

TAG_PAGE_TEMPLATE = """\
{name_line}
{name}
{name_line}

{message}

{commits}
"""


OTHER_PATH_TEMPLATE = """\
{keyword} path
  :doc:`{path} </{doc_dirname}/content/{escaped_path}>`
"""


def format_date(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S %z")


def split_commit_message(message):
    parts = message.split("\n", 1)
    return [parts[0].strip(), parts[1].strip() if len(parts) > 1 else ""]


def short_hexsha(hexsha):
    return str(hexsha)[:8]


def indent(text, prefix):
    return "\n".join(prefix + line for line in text.splitlines())


def render_tag(tag):
    try:
        message = escape_subject(split_commit_message(tag.tag.message)[0])
    except AttributeError:
        message = "(no message)"

    return TAG_TEMPLATE.format(
        name=tag.name,
        slug=slugify(tag.name),
        commit=render_commit(tag.commit),
        doc_dirname=DOC_DIRNAME,
        message="**{message}**  — *{at}*".format(
            message=message or "",
            at=format_date(
                from_timestamp(tag.tag.tagged_date, tag.tag.tagger_tz_offset)
            )
            if hasattr(tag.tag, "tagged_date")
            else "(no date)",
        ),
    )


def render_branch(branch, active_branch_name):
    return BRANCH_TEMPLATE.format(
        name=branch.name,
        slug=slugify(branch.name),
        commit=render_commit(branch.commit),
        doc_dirname=DOC_DIRNAME,
        active=" [ACTIVE BRANCH]" if branch.name == active_branch_name else "",
    )


def render_branch_short(name, is_head):
    if (name, is_head) not in render_branch_short.cache:
        render_branch_short.cache[(name, is_head)] = BRANCH_TEMPLATE_SHORT.format(
            name=name,
            slug=slugify(name),
            doc_dirname=DOC_DIRNAME,
            head=" (head)" if is_head else "",
        )
    return render_branch_short.cache[(name, is_head)]


render_branch_short.cache = {}


def render_tag_short(name, is_head):
    if (name, is_head) not in render_tag_short.cache:
        render_tag_short.cache[(name, is_head)] = TAG_TEMPLATE_SHORT.format(
            name=name,
            slug=slugify(name),
            doc_dirname=DOC_DIRNAME,
            head=" (head)" if is_head else "",
        )
    return render_tag_short.cache[(name, is_head)]


render_tag_short.cache = {}


def render_commit(commit):
    if commit.hexsha not in render_commit.cache:
        render_commit.cache[commit.hexsha] = COMMIT_TEMPLATE.format(
            at=format_date(commit.committed_datetime),
            subject=escape_subject(split_commit_message(commit.message)[0]),
            hexsha=commit.hexsha,
            short_hexsha=short_hexsha(commit.hexsha),
            doc_dirname=DOC_DIRNAME,
        )
    return render_commit.cache[commit.hexsha]


render_commit.cache = {}


def render_index_pages(repo):
    return {"index.rst": INDEX_PAGE_TEMPLATE.format(doc_dirname=DOC_DIRNAME)}


def render_branches_pages(branches, active_branch_name):
    rendered_branches = []
    branch_links = []
    for branch in branches:
        rendered_branches.append(render_branch(branch, active_branch_name).strip())
        branch_links.append(
            BRANCH_TOCTREE_LINK_TEMPLATE.format(
                doc_dirname=DOC_DIRNAME,
                name=branch.name,
                slug=slugify(branch.name),
                active=" [ACTIVE]" if branch.name == active_branch_name else "",
            ).strip()
        )
    return {
        "branches/index.rst": BRANCHES_PAGE_TEMPLATE.format(
            branches="\n\n".join(rendered_branches),
            branch_links=indent("\n".join(branch_links), "   "),
        )
    }


def render_tags_pages(tags):
    rendered_tags = []
    tag_links = []
    for tag in tags:
        rendered_tags.append(render_tag(tag).strip())
        tag_links.append(
            TAG_TOCTREE_LINK_TEMPLATE.format(
                doc_dirname=DOC_DIRNAME, name=tag.name, slug=slugify(tag.name)
            ).strip()
        )
    return {
        "tags/index.rst": TAGS_PAGE_TEMPLATE.format(
            tags="\n\n".join(rendered_tags),
            tag_links=indent("\n".join(tag_links), "   "),
        )
    }


def render_commits_pages(repo):
    return {"commits/index.rst": COMMITS_PAGE_TEMPLATE.format(doc_dirname=DOC_DIRNAME)}


def render_branch_pages(branch, commits, active_branch_name):
    commits = "\n".join(render_commit(commit).strip() for commit in commits)
    return {
        f"branches/{slugify(branch.name)}.rst": BRANCH_PAGE_TEMPLATE.format(
            name=branch.name,
            name_line="=" * len(branch.name),
            commits=indent(commits, "- "),
            active=BRANCH_IS_ACTIVE_TEMPLATE
            if branch.name == active_branch_name
            else "",
        )
    }


def render_tag_pages(tag, commits):
    commits = "\n".join(render_commit(commit).strip() for commit in commits)
    try:
        message = tag.tag.message.strip()
    except AttributeError:
        message = "(no message)"
    return {
        f"tags/{slugify(tag.name)}.rst": TAG_PAGE_TEMPLATE.format(
            name=tag.name,
            name_line="=" * len(tag.name),
            commits=indent(commits, "- "),
            message=("::\n\n" + indent(message, "   ")) if message else "",
        )
    }


def render_commit_pages(commit, children, branches, tags):
    subject, description = split_commit_message(commit.msg)
    subject = escape_subject(subject)
    parents = "\n".join(
        render_commit(parent).strip() for parent in commit._c_object.parents
    )
    children = "\n".join(render_commit(child._c_object).strip() for child in children)
    branches = "\n".join(
        render_branch_short(branch.name, commit.hash == branch.commit.hexsha).strip()
        for branch in branches
    )
    tags = " • ".join(
        render_tag_short(tag.name, commit.hash == tag.commit.hexsha).strip()
        for tag in tags
    )
    modifications = "\n\n".join(
        render_modification_for_path_in_commit(modification).strip()
        for modification in commit.modifications
    )
    return {
        f"commits/{commit.hash}.rst": COMMIT_PAGE_TEMPLATE.format(
            subject=subject,
            subject_line="=" * len(subject),
            description=render_commit_description(commit, description),
            commit_hexsha=commit.hash,
            commit_at=format_date(commit.committer_date),
            parents=indent(parents, "  - ") if parents else "  (No parents)",
            children=indent(children, "  - ") if children else "  (No children)",
            branches=indent(branches, "  - ") if branches else "  (No branches)",
            tags=indent(tags, "  ") if tags else "  (No tags)",
            modifications=modifications,
        ),
        f"commits/descriptions/{commit.hash}": description,
    }


def find_last_source_code(path, change, changes_by_file):
    commit, modification, parent_change = change
    if modification.source_code or modification.added or modification.removed:
        return modification.source_code
    if parent_change:
        return find_last_source_code(path, parent_change, changes_by_file)
    if (
        modification.change_type == ModificationType.RENAME
        and modification.old_path
        and modification.old_path != modification.new_path
    ):
        return find_last_source_code(
            modification.old_path,
            changes_by_file[modification.old_path][0],
            changes_by_file,
        )
    return None


def render_file_pages(path, changes_by_file, current_tree):
    last_change = changes_by_file[path][0]
    changes = [change for change in changes_by_file[path] if not change[0].merge]
    modifications = "\n\n".join(
        "\n"
        + render_modification_for_commit_in_path(modification, commit, path).strip()
        for commit, modification, *__ in changes
    )
    last_commit, last_modification = changes[0][:2]
    first_commit, first_modification = changes[-1][:2]
    basename = os.path.basename(path)
    dirname = os.path.dirname(path)
    suffixed_dirname = dirname + "/"
    title = basename
    if not path_in_tree(path, current_tree):
        title += REMOVED
    source_code = last_change[1].source_code or find_last_source_code(
        path, last_change, changes_by_file
    )
    documentation = ""
    if path.endswith(".py"):
        parts = path[:-3].split("/")
        if parts[-1] == "__init__":
            parts.pop()
        python_path = ".".join(parts)
        if os.path.exists(os.path.join(SOURCE_BASE_PATH, python_path + ".rst")):
            documentation = LINK_TO_SOURCE_TEMPLATE.format(
                python_path=python_path, source_dirname=SOURCE_DIRNAME
            )

    return {
        f"content/{escape_path(path)}.rst": FILE_PAGE_TEMPLATE.format(
            path=path,
            title=title,
            title_line="=" * len(title),
            dirname=suffixed_dirname,
            escaped_dirname=escape_path(suffixed_dirname),
            modifications=modifications,
            source_code=SOURCE_CODE_TEMPLATE.format(
                source_code=indent(source_code, "   ")
            )
            if source_code
            else "(No source code)",
            last_type=MODIFICATION_TYPES[last_modification.change_type.name],
            last_updated_at=format_date(last_commit.committer_date),
            last_commit_hash=last_commit.hash,
            doc_dirname=DOC_DIRNAME,
            old_path=render_old_path(
                first_modification.old_path, DOC_DIRNAME, keyword="Previous"
            )
            if first_modification.old_path and first_modification.old_path != path
            else "",
            new_path=render_new_path(last_modification.new_path, DOC_DIRNAME)
            if last_modification.new_path and last_modification.new_path != path
            else "",
            documentation=documentation,
            parent_old="" if path_in_tree(dirname, current_tree) else REMOVED,
        )
    }


def render_dir_pages(path, entries, current_tree):
    is_removed = not path_in_tree(path, current_tree)
    rendered_entries = []
    entry_links = []
    for entry, is_dir in sorted(
        entries, key=lambda entry: (not entry[1], entry[0].lower())
    ):
        rendered_entry = render_dir_entry(entry, is_dir, path, current_tree, is_removed)
        if rendered_entry:
            rendered_entries.append(rendered_entry.strip())

        entry_path = os.path.join(path, entry)
        entry_links.append(
            (DIR_TOCTREE_DIR_TEMPLATE if is_dir else DIR_TOCTREE_FILE_TEMPLATE)
            .format(
                doc_dirname=DOC_DIRNAME,
                name=entry,
                escaped_path=escape_path(entry_path),
                old="" if path_in_tree(entry_path, current_tree) else REMOVED,
            )
            .strip()
        )
    basename = os.path.basename(path)
    title = (basename + "/") if basename else "`/`"
    if is_removed:
        title += REMOVED
    dirname = os.path.dirname(path)
    suffixed_dirname = dirname + "/"
    return {
        f"content/{escape_path(path)}/index.rst": DIR_PAGE_TEMPLATE.format(
            title=title,
            title_line="=" * len(title),
            parent_directory="Parent directory\n  :doc:`{dirname}{old} </{doc_dirname}/content/{escaped_dirname}index>`".format(
                dirname=suffixed_dirname,
                escaped_dirname=escape_path(suffixed_dirname),
                doc_dirname=DOC_DIRNAME,
                old="" if path_in_tree(dirname, current_tree) else REMOVED,
            )
            if path
            else "",
            entries=indent("\n".join(rendered_entries), "  "),
            entry_links=indent("\n".join(entry_links), "   "),
        )
    }


def render_dir_entry(name, is_dir, parent_dir, current_tree, include_removed):
    path = os.path.join(parent_dir, name)
    is_removed = not path_in_tree(path, current_tree)
    if is_removed and not include_removed:
        return None
    return (DIR_ENTRY_DIR_TEMPLATE if is_dir else DIR_ENTRY_FILE_TEMPLATE).format(
        name=name,
        escaped_path=escape_path(path),
        doc_dirname=DOC_DIRNAME,
        old=REMOVED if is_removed else "",
    )


def render_commit_description(commit, description):
    if not description:
        return ""

    kind = ""
    if list(
        rstcheck.check(
            description, f"/{DOC_DIRNAME}/commits/descriptions/{commit.hash}"
        )
    ):
        kind = "   :literal:\n"

    return DESCRIPTION_TEMPLATE.format(
        description_path=f"descriptions/{commit.hash}", kind=kind
    )


def get_modification_paths(modification):
    path = modification.new_path or modification.old_path
    old_path = (
        modification.old_path
        if modification.new_path is not None
        and modification.old_path is not None
        and modification.new_path != modification.old_path
        else None
    )
    return path, old_path


def _render_changed_path(path, dirname, keyword):
    return (
        OTHER_PATH_TEMPLATE.format(
            doc_dirname=dirname,
            path=path,
            keyword=keyword,
            escaped_path=escape_path(path),
        )
        if path
        else ""
    )


render_old_path = partial(_render_changed_path, keyword="Old")
render_new_path = partial(_render_changed_path, keyword="New")


def render_modification_for_path_in_commit(modification):
    path, old_path = get_modification_paths(modification)
    return MODIFICATION_FOR_PATH_IN_COMMIT_TEMPLATE.format(
        path=path,
        path_line="=" * len(path),
        escaped_path=escape_path(path),
        type=MODIFICATION_TYPES[modification.change_type.name],
        old_path=render_old_path(old_path, DOC_DIRNAME),
        added=modification.added or 0,
        removed=modification.removed or 0,
        diff=MODIFICATION_DIFF_TEMPLATE.format(diff=indent(modification.diff, "   "))
        if modification.diff
        else "",
        doc_dirname=DOC_DIRNAME,
    )


def render_modification_for_commit_in_path(modification, commit, current_path):
    path, old_path = get_modification_paths(modification)
    subject = escape_subject(split_commit_message(commit.msg)[0])
    return MODIFICATION_FOR_COMMIT_IN_PATH_TEMPLATE.format(
        current_path=current_path,
        commit_subject=subject,
        commit_subject_line="=" * len(subject),
        commit_hash=commit.hash,
        commit_at=format_date(commit.committer_date),
        type=MODIFICATION_TYPES[modification.change_type.name],
        old_path=render_old_path(old_path, DOC_DIRNAME)
        if old_path and old_path != current_path
        else "",
        new_path=render_new_path(path, DOC_DIRNAME) if path != current_path else "",
        added=modification.added or 0,
        removed=modification.removed or 0,
        diff=MODIFICATION_DIFF_TEMPLATE.format(diff=indent(modification.diff, "   "))
        if modification.diff
        else "",
        doc_dirname=DOC_DIRNAME,
    )


def render_to_file(content, name, basepath=BASEPATH):
    path = os.path.join(basepath, name)
    dir = os.path.dirname(path)
    if dir not in render_to_file.dirs_ok:
        os.makedirs(dir, exist_ok=True)
        render_to_file.dirs_ok.add(dir)
    with open(path, "w") as fd:
        fd.write(content)


render_to_file.dirs_ok = set()


def render_to_files(rendered_pages, basepath=BASEPATH):
    for page_name, content in rendered_pages.items():
        if content:
            render_to_file(content, page_name, basepath)


def render(location, basepath=BASEPATH, clean=True):
    if clean:
        shutil.rmtree(BASEPATH, ignore_errors=True)

    print(f"\nGit to Sphinx: {location}...\n")

    print("Reading repository...", end="")
    repo = RepositoryMining(location)
    print("\rReading repository [ok]")

    print("Rendering indexes:")
    print("  - branches...", end="")
    branches = list(repo.traverse_branches())
    render_to_files(
        render_branches_pages(branches, repo.git_repo._conf.get("main_branch")),
        basepath=basepath,
    )
    print("\r  - branches [ok]")
    print("  - tags...", end="")
    tags = list(repo.traverse_tags())
    render_to_files(render_tags_pages(tags), basepath=basepath)
    print("\r  - tags [ok]")
    print("  - commits...", end="")
    render_to_files(render_commits_pages(repo), basepath=basepath)
    print("\r  - commits [ok]")
    print("  - main...", end="")
    render_to_files(render_index_pages(repo), basepath=basepath)
    print("\r  - main [ok]")

    print("Rendering branches:")
    commits_branches = defaultdict(list)
    for branch in branches:
        print(f"  - {branch.name}...", end="")
        commits = [branch.commit] + list(branch.commit.iter_parents())
        render_to_files(
            render_branch_pages(
                branch, commits, repo.git_repo._conf.get("main_branch")
            ),
            basepath=basepath,
        )
        for commit in commits:
            commits_branches[commit.hexsha].append(branch)
        print(f"\r  - {branch.name} [ok]")

    print("Rendering tags:")
    commits_tags = defaultdict(list)
    for tag in tags:
        print(f"  - {tag.name}...", end="")
        commits = [tag.commit] + list(tag.commit.iter_parents())
        render_to_files(render_tag_pages(tag, commits=commits), basepath=basepath)
        for commit in commits:
            commits_tags[commit.hexsha].append(tag)
        print(f"\r  - {tag.name} [ok]")

    print("Building commits trees...", end="")
    children = defaultdict(list)
    revisions = branches + tags
    nb_revisions = len(revisions)
    commits = {}
    for index, revision in enumerate(revisions, 1):
        print(f"\rBuilding commits trees [{index}/{nb_revisions}]", end="")
        rev_commits = list(repo.traverse_commits(revision=revision.name))
        for commit in rev_commits:
            if commit.hash in commits:
                break
            commits[commit.hash] = commit
            for parent_hash in commit.parents:
                if commit.hash in children[parent_hash]:
                    continue
                children[parent_hash].append(commit.hash)
    print("")

    print("Rendering commits...", end="")
    changes_by_file = defaultdict(list)
    nb_commits = len(commits)
    for index, (__, commit) in enumerate(commits.items(), 1):
        print(f"\rRendering commits [{index}/{nb_commits}]", end="")
        if (commit.hash not in commits_branches) and (commit.hash not in commits_tags):
            # ignore commits not in branches or tags: they won't be rendered anywhere
            continue
        render_to_files(
            render_commit_pages(
                commit,
                children=[commits[hash] for hash in children[commit.hash]],
                branches=commits_branches.get(commit.hash) or [],
                tags=commits_tags.get(commit.hash) or [],
            ),
            basepath=basepath,
        )
        for modification in commit.modifications:
            if modification.new_path:
                changes_by_file[modification.new_path].append(
                    [commit, modification, None]
                )
            if modification.old_path and modification.old_path != modification.new_path:
                changes_by_file[modification.old_path].append(
                    [commit, modification, None]
                )

    # link changes to their parent
    for path, changes in changes_by_file.items():
        for index, change in enumerate(changes[:-1]):
            change[2] = changes[index + 1]

    print("")

    print("Building content tree...", end="")
    current_tree = {path: node for node, path in repo.traverse_tree()}
    print("\rBuilding content tree [ok]")

    print("Rendering files...", end="")
    nb_files = len(changes_by_file)
    dirs = defaultdict(set)
    for index, path in enumerate(sorted(changes_by_file), 1):
        print(f"\rRendering files [{index}/{nb_files}]", end="")

        current, is_dir = path, False
        while True:
            dirname, basename = os.path.dirname(current), os.path.basename(current)
            dirs[dirname].add((basename, is_dir))
            if dirname:
                current = dirname
                is_dir = True
            else:
                break

        render_to_files(
            render_file_pages(path, changes_by_file, current_tree), basepath=basepath
        )
    print("")

    print("Rendering dirs...", end="")
    nb_dirs = len(dirs)
    for index, dir in enumerate(sorted(dirs), 1):
        print(f"\rRendering dirs [{index}/{nb_dirs}]", end="")
        render_to_files(
            render_dir_pages(dir, dirs[dir], current_tree), basepath=basepath
        )

    print(f"\n\nGit to Sphinx: {location} [ok]\n")


if __name__ == "__main__":
    assert len(sys.argv) > 1 and sys.argv[1], "Missing location"
    render(sys.argv[1])
