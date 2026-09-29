from unittest.mock import Mock, call

import pytest
import rules

from spadeapp.users.tests.factories import UserFactory
from spadeapp.utils.permissions import SpadePermissionManager
from spadeapp.variables.models import Variable


@pytest.fixture
def permission_manager():
    """Fixture to create a SpadePermissionManager instance for testing."""
    return SpadePermissionManager()


@pytest.fixture
def mock_default_rule():
    """Fixture to create a mock default rule."""
    mock = Mock()
    mock.test.return_value = False
    return mock


def test_initialization(permission_manager):
    """Test that SpadePermissionManager initializes with an empty rules dictionary."""
    assert permission_manager.rules == {}, "Expected rules to be an empty dictionary upon initialization."


def test_add_rule(permission_manager):
    """Test adding a rule to the SpadePermissionManager."""
    mock_rule = Mock()
    mock_rule.test.return_value = True
    permission_manager.add_rule("test_rule", mock_rule)
    assert "test_rule" in permission_manager.rules, "Rule name 'test_rule' should be in the rules dictionary."
    assert permission_manager.rules["test_rule"] == mock_rule, (
        "The rule associated with 'test_rule' should be mock_rule."
    )


def test_test_rule_existing(permission_manager):
    """Test testing an existing rule."""
    mock_rule = Mock()
    mock_rule.test.return_value = True
    permission_manager.add_rule("test_rule", mock_rule)
    result = permission_manager.test_rule("test_rule")
    mock_rule.assert_has_calls([call.test()])
    assert result, "test_rule should return True for 'test_rule'."


def test_test_rule_non_existing(permission_manager, mock_default_rule):
    """Test testing a non-existing rule uses the default rule."""
    permission_manager.default_rule = mock_default_rule
    assert "non_existing_rule" not in permission_manager.rules, (
        "Rule name 'non_existing_rule' should not be in the rules dictionary."
    )
    result = permission_manager.test_rule("non_existing_rule")
    mock_default_rule.assert_has_calls([call.test()])
    assert not result, "test_rule should return False for a non-existing rule, using the default rule."


def test_test_rule_existing_deny(permission_manager):
    """Test testing an existing rule that denies access."""
    mock_rule_deny = Mock()
    mock_rule_deny.test.return_value = False
    permission_manager.add_rule("deny_rule", mock_rule_deny)
    result = permission_manager.test_rule("deny_rule")
    mock_rule_deny.assert_has_calls([call.test()])
    assert not result, "test_rule should return False for 'deny_rule'."


def test_test_rule_with_argument(permission_manager):
    """Test testing a rule with an additional argument."""
    mock_rule_with_arg = Mock()
    mock_rule_with_arg.test.return_value = True
    permission_manager.add_rule("rule_with_arg", mock_rule_with_arg)
    mock_arg = Mock()
    result = permission_manager.test_rule("rule_with_arg", mock_arg)
    mock_rule_with_arg.assert_has_calls([call.test(mock_arg)])
    assert result, "test_rule should return True for 'rule_with_arg' when passed mock_arg."


class TestFilterVisible:
    @pytest.fixture
    def variables(self, db):
        return [Variable.objects.create(name=name, value="v") for name in ("keep", "hidden")]

    @pytest.fixture
    def active_user(self, db):
        user = UserFactory()
        # Explicitly demoted so ACCOUNT_FIRST_USER_ADMIN cannot promote it.
        user.is_superuser = False
        user.save()
        return user

    def test_inactive_user_sees_nothing(self, permission_manager, variables, active_user):
        active_user.is_active = False
        assert (
            list(permission_manager.filter_visible("variables.view_variable", active_user, Variable.objects.all()))
            == []
        )

    def test_superuser_sees_everything_despite_deny(self, permission_manager, variables):
        permission_manager.add_rule("variables.view_variable", rules.always_deny)
        superuser = UserFactory(is_superuser=True)
        assert permission_manager.filter_visible(
            "variables.view_variable", superuser, Variable.objects.all()
        ).count() == len(variables)

    def test_allow_all_rule_needs_no_queries(
        self, permission_manager, variables, active_user, django_assert_num_queries
    ):
        queryset = Variable.objects.all()
        with django_assert_num_queries(0):
            result = permission_manager.filter_visible("variables.view_variable", active_user, queryset)
        assert result is queryset

    def test_deny_all_rule(self, permission_manager, variables, active_user):
        permission_manager.add_rule("variables.view_variable", rules.always_deny)
        assert not permission_manager.filter_visible("variables.view_variable", active_user, Variable.objects.all())

    def test_custom_rule_tested_per_object(self, permission_manager, variables, active_user):
        permission_manager.add_rule("variables.view_variable", rules.predicate(lambda user, obj: obj.name != "hidden"))
        visible = permission_manager.filter_visible("variables.view_variable", active_user, Variable.objects.all())
        assert [variable.name for variable in visible] == ["keep"]
