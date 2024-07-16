from unittest.mock import Mock, call

import pytest

from spadeapp.utils.permissions import SpadePermissionManager


@pytest.fixture
def permission_manager():
    """Fixture to create a SpadePermissionManager instance for testing."""
    return SpadePermissionManager()


@pytest.fixture
def mock_default_rule():
    """Fixture to create a mock default rule."""
    return Mock(return_value=False)


def test_initialization(permission_manager):
    """Test that SpadePermissionManager initializes with an empty rules dictionary."""
    assert permission_manager.rules == {}, "Expected rules to be an empty dictionary upon initialization."


def test_add_rule(permission_manager):
    """Test adding a rule to the SpadePermissionManager."""
    mock_rule = Mock(return_value=True)
    permission_manager.add_rule("test_rule", mock_rule)
    assert "test_rule" in permission_manager.rules, "Rule name 'test_rule' should be in the rules dictionary."
    assert (
        permission_manager.rules["test_rule"] == mock_rule
    ), "The rule associated with 'test_rule' should be mock_rule."


def test_test_rule_existing(permission_manager):
    """Test testing an existing rule."""
    mock_rule = Mock(return_value=True)
    permission_manager.add_rule("test_rule", mock_rule)
    result = permission_manager.test_rule("test_rule")
    mock_rule.assert_has_calls([call.test()])
    assert result, "test_rule should return True for 'test_rule'."


def test_test_rule_non_existing(permission_manager, mock_default_rule):
    """Test testing a non-existing rule uses the default rule."""
    permission_manager.default_rule = mock_default_rule
    assert (
        "non_existing_rule" not in permission_manager.rules
    ), "Rule name 'non_existing_rule' should not be in the rules dictionary."
    result = permission_manager.test_rule("non_existing_rule")
    mock_default_rule.assert_has_calls([call.test()])
    assert not result, "test_rule should return False for a non-existing rule, using the default rule."


def test_test_rule_existing_deny(permission_manager):
    """Test testing an existing rule that denies access."""
    mock_rule_deny = Mock(return_value=False)
    permission_manager.add_rule("deny_rule", mock_rule_deny)
    result = permission_manager.test_rule("deny_rule")
    mock_rule_deny.assert_has_calls([call.test()])
    assert not result, "test_rule should return False for 'deny_rule'."


def test_test_rule_with_argument(permission_manager):
    """Test testing a rule with an additional argument."""
    mock_rule_with_arg = Mock(return_value=True)
    permission_manager.add_rule("rule_with_arg", mock_rule_with_arg)
    mock_arg = Mock()
    result = permission_manager.test_rule("rule_with_arg", mock_arg)
    mock_rule_with_arg.assert_has_calls([call.test(mock_arg)])
    assert result, "test_rule should return True for 'rule_with_arg' when passed mock_arg."
