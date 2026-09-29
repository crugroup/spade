import pytest

from spadeapp.utils.params import parse_user_params


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, {}),
        ("", {}),
        ('{"a": 1}', {"a": 1}),
        ({"a": 1}, {"a": 1}),
    ],
)
def test_valid_params(raw, expected):
    assert parse_user_params(raw) == expected


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ("{not json", "Failed to parse user params as JSON"),
        ("[1, 2]", "User params must be a JSON object"),
        ([1, 2], "User params must be a JSON object"),
        (42, "User params must be a JSON object"),
    ],
)
def test_invalid_params(raw, message):
    with pytest.raises(ValueError, match=message):
        parse_user_params(raw)
