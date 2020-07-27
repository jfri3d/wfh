import pytest

from wfh.display.exceptions import InvalidConnection
from wfh.display.helpers import get_today, build_today


def test_invalid_connection():
    with pytest.raises(InvalidConnection):
        get_today(host="http://localhost")


def test_build_empty_today():
    data = build_today({})
    assert len(data) == 1
    assert "now" in data


def test_build_invalid_today():
    with pytest.raises(ValueError):
        mock = {"login": ["2020-02"]}
        build_today(mock)


def test_build_valid_today():
    mock = {"login": ["2020-01-01 00:00:00"]}
    data = build_today(mock)
    assert "login" in data

    mock = {"login": ["2020-01-01 00:00:00", "2020-01-01 00:00:01"]}
    data = build_today(mock)
    assert "login" in data
    assert len(data["login"]) == 2
