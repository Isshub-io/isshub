"""Validation helpers for BDD tests for isshub entity models."""

from typing import Any, List, Optional, Tuple, Type


ValuesValidation = List[Tuple[Any, Optional[Type[Exception]]]]

integer_only: ValuesValidation = [
    ("foo", TypeError),
    (-123, ValueError),
    (-1.5, TypeError),
    (-1, ValueError),
    (-0.001, TypeError),
    (0.001, TypeError),
    (1, None),
    (1.5, TypeError),
    (123, None),
]

no_zero: ValuesValidation = [(0, ValueError)]

positive_integer_only: ValuesValidation = integer_only + no_zero

string_only: ValuesValidation = [("foo", None), (1, TypeError), (-0.1, TypeError)]
