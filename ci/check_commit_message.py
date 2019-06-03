#!/usr/bin/env python

"""Script to check that a commit message is valid"""

# noqa

import argparse
import os.path
import re
import shutil
import sys
from collections import defaultdict

from colorama import Fore, Style
from git import Repo


def check(message):
    """Ensure the message follow some rules.

    This is based on "Conventional Commits" (https://www.conventionalcommits.org), but with
    added rules for the body

    Rules
    -----
    A commit is split in four parts:
    - A short subject in the first line
    - An empty line
    - A complete description

    The description must be written in restructured text, containing sections, inspired by
    https://www.python.org/dev/peps/pep-0012/#suggested-sections.
    At least these ones are required, in this order:
    - Abstract
    - Motivation
    - Rationale

    - 1st line: subject
      - length is max 72 chars
      - starts with a type, from a specific list
      - a scope can follow the type, surrounded by parentheses
      - after the type (or scope), a colon must be present, followed by a space
      - then a mandatory short subject
    - 2nd line: empty
      - mandatory
      - empty
    - 3rd line, start of first section of RST description

    In the description, we expect to find:
    - 1st line: "Abstract"
    - 2nd line: "======="
    - 3rd line: empty line
    - 4th line: text

    Then the next title must be "Motivation"

    Parameters
    ----------
    message : str
        The git commit message to check

    Yields
    ------
    Tuple[int, str]
        Will yield a tuple for each error, with the line number and the text of the error.

    """

    if not message:
        yield 0, "No message (message is mandatory)"
        return

    types = {
        "build",
        "ci",
        "chore",
        "docs",
        "feat",
        "fix",
        "merge",
        "perf",
        "refactor",
        "revert",
        "style",
        "tests",
    }

    lines = [line.rstrip() for line in message.splitlines()]

    line = lines.pop(0)
    if len(line) > 72:
        yield 0, "Line to long (max 72 characters)"

    parts = re.split(r"[^a-zA-Z]", line, maxsplit=1)
    type_ = parts[0]
    if not type_:
        yield 0, f"Line must start with a type (must be one of {list(types)})"
    else:
        if type_.lower() not in types:
            yield 0, f"`{type_}` is not a valid type (must be one of {list(types)})"
            if type_ != type_.lower():
                yield 0, f"Type `{type_}` must be lowercased"
        else:
            if type_ != type_.lower():
                yield 0, f"Type `{type_}` must be lowercased (use {type_.lower()})"
        if len(parts) == 1 or not parts[1].strip():
            yield 0, f"Type `{type_}` must be followed by en optional scope and a subject (`type(scope): subject`)"
        else:
            rest = line[len(type_) :]
            if rest.startswith(" "):
                yield 0, f"No space expected after the type `{type_}` (must be a scope in parentheses or `: `)"
            rest = rest.lstrip()
            if rest.startswith("("):
                parts = rest.split(")", maxsplit=1)
                scope = parts[0][1:]
                if not scope.strip():
                    yield 0, "Scope is empty (if set, scope is between parentheses after the type"
                if scope.strip() != scope:
                    yield 0, f"Scope `{scope}` must not be surrounded by spaces"
                scope = scope.strip()
                if not re.fullmatch(r"[a-zA-Z]+[\w\-.]+[a-zA-Z]+", scope):
                    yield 0, f"Invalid scope `{scope}` (must start with letter, then letters, `_`, `-`, or `.`, then letter)"
                if len(parts) == 1 or not parts[1].strip():
                    rest = ""
                else:
                    rest = parts[1]

            if not rest or not rest.strip():
                yield 0, "Description is missing (must be after type or scope)"
            else:
                parts = rest.split(":", maxsplit=1)
                if parts[0]:
                    if not parts[0].strip():
                        yield 0, "No space before `:` (type or scope is followed by `: `)"
                    else:
                        yield 0, "Invalid subject separator (subject must be prefixed by `: `)"
                if parts[0].strip():
                    subject = parts[0]
                elif len(parts) == 1 or not parts[1].strip():
                    yield 0, "Description is missing (must be after type or scope)"
                    subject = ""
                else:
                    subject = parts[1]
                if subject:
                    if subject[0] != " ":
                        yield 0, "Description must be preceded by a space (subject must be prefixed by `: `)"
                    else:
                        subject = subject[1:]
                    if subject.strip() != subject:
                        yield 0, "Invalid spaces around subject (required only one space after `:`, and no space at the end)"
                    subject = subject.strip()
                    if len(subject) < 20:
                        yield 0, "Description too short (min 20 characters)"

    if len(lines) < 2:
        yield 1, "Description is missing (must be after a blank line following the first line)"
        return

    sections = {
        name: {
            "found_on_line": None,
            "underline": None,
            "nb_blank_lines_before": 0,
            "nb_blank_lines_after_title": 0,
            "nb_blank_lines_after_underline": 0,
            "has_text": False,
            "order": index,
        }
        for index, name in enumerate(["Abstract", "Motivation", "Rationale"])
    }
    found_sections = []
    current_section = None
    text_before = False
    skip = 0
    for index, line in enumerate(lines):
        if skip:
            skip -= 1
            continue
        num = index + 1
        if line in sections:
            current_section = line
            sections[current_section]["found_on_line"] = num
            found_sections.append(current_section)
            # search for empty lines before title
            if index:
                index_ = index
                while index_:
                    if lines[index_ - 1]:
                        break
                    sections[current_section]["nb_blank_lines_before"] += 1
                    index_ -= 1
            try:
                # search for empty lines after title
                index_ = index
                while True:
                    if lines[index_ + 1 + skip]:
                        break
                    sections[current_section]["nb_blank_lines_after_title"] += 1
                    skip += 1
                # search for underline
                if lines[index + 1 + skip].startswith("="):
                    sections[current_section]["underline"] = lines[
                        index + 1 + skip
                    ] == "=" * len(current_section)
                if sections[current_section]["underline"] is not None:
                    skip += 1
                # search for empty lines after underline
                index_ = index + skip
                while True:
                    if lines[index_ + skip]:
                        break
                    sections[current_section]["nb_blank_lines_after_underline"] += 1
                    skip += 1
            except IndexError:
                pass
            continue

        if line:
            if not current_section:
                text_before = True
            else:
                sections[current_section]["has_text"] = True

    if text_before:
        yield 2, "No text must preceed the first section"

    for name, info in sections.items():
        if not info["found_on_line"]:
            yield 2, f"Description must include the {name} section"

    for index, name in enumerate(found_sections):
        info = sections[name]
        num = info["found_on_line"]
        if info["order"] != index:
            yield num, f"Section {name} must be in position {info['order']+1}"
        if info["nb_blank_lines_before"] != 1:
            yield num - info[
                "nb_blank_lines_before"
            ], f"Section {name} must be preceded with exactly one blank line"
        if info["nb_blank_lines_after_title"]:
            yield num + 1, f"No blank lines expected after title of section {name}"
            num += info["nb_blank_lines_after_title"]
        if info["underline"] is not True:
            yield num + 1, f"Title of section {name} must be underlined with {len(name)} `=`"
        if info["underline"] is not None:
            num += 1
        if info["nb_blank_lines_after_underline"] != 1:
            yield num + 1, f"Underline of title of section {name} must be followed with exactly one blank line"
            num += info["nb_blank_lines_after_underline"]
        if not info["has_text"]:
            yield num, f"Section {name} must contain text"

    for index, line in enumerate(message.splitlines()):
        if line != line.rstrip():
            yield index, f"Remove trailing space(s)"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate a git commit message via a git reference or text.",
        add_help=False,
    )
    parser.add_argument("-h", "--help", help="Show this help and exit.", action="help")
    parser.add_argument(
        "-v", "--verbose", help="Increase output verbosity.", action="store_true"
    )
    parser.add_argument(
        "-t", "--template", help="Show git commit template.", action="store_true"
    )
    parser.add_argument(
        "--check-merge",
        help="If set, will enforce the style for a merge commit. Else merge commits are always valid.",
        action="store_true",
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "-r",
        "--ref",
        metavar="REF",
        type=str,
        nargs="?",
        help="The git reference of the commit to check.",
        default=None,
    )
    group.add_argument(
        "-l",
        "--last",
        help="Use the last commit (equivalent to -r HEAD).",
        action="store_true",
    )
    group.add_argument(
        "path",
        metavar="PATH",
        type=argparse.FileType("r", encoding="UTF-8"),
        nargs="?",
        help="Path to file containing the message to check. Use `-` for stdin.",
        default=None,
    )
    args = parser.parse_args()

    errors = None
    do_check = False
    if args.last or args.ref or args.path:
        do_check = True

        if args.last:
            args.ref = "HEAD"

        if args.ref:
            if args.verbose:
                print(
                    f"Checking from git reference: {Style.BRIGHT}{args.ref}{Style.NORMAL}\n"
                )
            repo = Repo(search_parent_directories=True)
            commit = repo.commit(args.ref)
            if not args.check_merge and len(commit.parents) > 1:
                do_check = False
                if args.verbose:
                    print(
                        f"{Style.BRIGHT}{Fore.GREEN}It's a merge commit, no style enforced{Fore.RESET}{Style.NORMAL}\n"
                    )
            else:
                message = commit.message

        else:
            if args.verbose:
                print(
                    f"Checking from file: {Style.BRIGHT}{args.path.name}{Style.NORMAL}\n"
                )
            with args.path as file:
                message = file.read()

            if not args.check_merge and message and message.startswith("Merge branch "):
                do_check = False
                if args.verbose:
                    print(
                        f"{Style.BRIGHT}{Fore.GREEN}It sounds like a merge commit, so no style enforced{Fore.RESET}{Style.NORMAL}\n"
                    )

        if do_check:
            lines = message.splitlines()
            nb_lines = len(lines)
            errors = defaultdict(list)
            nb_errors = 0
            for line, error in check(message):
                if line >= nb_lines:
                    line = nb_lines - 1
                errors[line].append(error)
                nb_errors += 1
            if nb_errors:
                if args.verbose:
                    print(
                        f"{Style.BRIGHT}{Fore.RED}Message is invalid. "
                        f"Found {nb_errors} error{'(s)' if nb_errors > 1 else ''} "
                        f"for {len(errors)} line{'(s)' if len(errors) > 1 else ''} "
                        f"(on {nb_lines}):{Fore.RESET}{Style.NORMAL}\n",
                        file=sys.stderr,
                    )
            else:
                if args.verbose:
                    print(
                        f"{Style.BRIGHT}{Fore.GREEN}Message is valid:{Fore.RESET}{Style.NORMAL}\n"
                    )

            if args.verbose:
                for line_num, line in enumerate(lines):
                    if line_num in errors:
                        print(
                            f"{Style.BRIGHT}{Fore.RED}✘{Fore.RESET}{Style.NORMAL} {line}",
                            file=sys.stderr,
                        )
                        for error in errors[line_num]:
                            print(
                                f"  -> {Style.BRIGHT}{Fore.RED}{error}{Fore.RESET}{Style.NORMAL}",
                                file=sys.stderr,
                            )
                    else:
                        print(
                            f"{Style.BRIGHT}{Fore.GREEN}✔{Fore.RESET} {Style.NORMAL}{line}",
                            file=sys.stderr,
                        )
            else:
                for line_num, line_errors in errors.items():
                    for error in line_errors:
                        print(f"{line_num}: {error}", file=sys.stderr)

    if args.template:
        if args.ref or args.path:
            print("")
        if args.verbose:
            print(f"{Style.BRIGHT}Git commit message template:{Style.NORMAL}\n")
        else:
            print("Git commit message template:\n")

        with open(
            os.path.join(os.path.dirname(__file__), "..", ".gitmessage"), "r"
        ) as file:
            shutil.copyfileobj(file, sys.stdout)

    exit(1 if errors else 0)
