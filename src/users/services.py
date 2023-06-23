from users.models import UsersIdentifiers

__all__ = (
    'parse_users_identifiers_for_search',
)


def parse_users_identifiers_for_search(
        user_identifiers_text: str,
) -> UsersIdentifiers:
    """
    Parses the user identifiers from the given text for searching.

    The user identifiers can be provided as a string, where each line represents
    either a user ID or a username. The function splits the input text into
    lines and extracts the user IDs and usernames separately.

    Args:
        user_identifiers_text: The text containing user identifiers, where each
            line represents a user ID or a username.

    Returns:
        Instance of UsersIdentifiers with the extracted user IDs and usernames.

    Example:
        >>> parse_users_identifiers_for_search("123\\njohn_doe\\n456\\njane")
        UsersIdentifiers(user_ids=[123, 456], usernames=['john_doe', 'jane'])
    """
    user_identifiers = user_identifiers_text.splitlines()
    user_ids: list[int] = []
    usernames: list[str] = []
    for user_identifier in user_identifiers:
        if user_identifier.isdigit():
            user_ids.append(int(user_identifier))
        else:
            usernames.append(user_identifier)
    return UsersIdentifiers(
        user_ids=user_ids,
        usernames=usernames,
    )
