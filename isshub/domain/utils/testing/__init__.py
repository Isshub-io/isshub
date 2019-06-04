"""Utils for isshub domain tests."""

try:
    import pytest
except ImportError:
    pass
else:
    pytest.register_assert_rewrite("isshub.domain.utils.testing.validation")
