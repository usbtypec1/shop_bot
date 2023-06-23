from users.models import UsersIdentifiers
from users.services import parse_users_identifiers_for_search


def test_parse_users_identifiers_for_search():
    user_identifiers_text = "123\njohn_doe\n456\njane_smith"
    expected_result = UsersIdentifiers(
        user_ids=[123, 456],
        usernames=["john_doe", "jane_smith"],
    )
    assert parse_users_identifiers_for_search(
        user_identifiers_text,
    ) == expected_result


def test_parse_users_identifiers_for_search_empty_text():
    user_identifiers_text = ""
    expected_result = UsersIdentifiers(user_ids=[], usernames=[])
    assert parse_users_identifiers_for_search(
        user_identifiers_text,
    ) == expected_result


def test_parse_users_identifiers_for_search_only_user_ids():
    user_identifiers_text = "123\n456\n789"
    expected_result = UsersIdentifiers(
        user_ids=[123, 456, 789],
        usernames=[],
    )
    assert parse_users_identifiers_for_search(
        user_identifiers_text,
    ) == expected_result


def test_parse_users_identifiers_for_search_only_usernames():
    user_identifiers_text = "john_doe\njane_smith\njimmy"
    expected_result = UsersIdentifiers(
        user_ids=[],
        usernames=["john_doe", "jane_smith", "jimmy"],
    )
    assert parse_users_identifiers_for_search(
        user_identifiers_text,
    ) == expected_result


def test_parse_users_identifiers_for_search_mixed_ids_and_usernames():
    user_identifiers_text = "123\njohn_doe\n456\njane_smith\n789\njimmy"
    expected_result = UsersIdentifiers(
        user_ids=[123, 456, 789],
        usernames=["john_doe", "jane_smith", "jimmy"],
    )
    assert parse_users_identifiers_for_search(
        user_identifiers_text,
    ) == expected_result
