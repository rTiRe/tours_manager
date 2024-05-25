"""Filters for work with data in templates."""

from typing import Any

from django import template

register = template.Library()


def check_isinstance(
    expected_types: list[type] | tuple[type],
    any_object: Any,
    object_literal: str,
) -> None:
    """Check any object instance of expected types.

    Args:
        expected_types: list[type] | tuple[type] - types that an object must match.
        any_object: Any - object for check.
        object_literal: str - object (variable) name. For error massage.

    Raises:
        TypeError: if any_object does not match the expected_types.
    """
    expected_types = tuple(expected_types)
    if not isinstance(any_object, expected_types):
        expected_types = ', '.join([expected_type.__name__ for expected_type in expected_types])
        object_type_name = type(any_object).__name__
        error_text = f'`{object_literal}` type must be {expected_types}. Not {object_type_name}.'
        raise TypeError(error_text)


@register.filter
def get_item(
    dictionary: dict,
    key: str | int | float | tuple | frozenset,
) -> Any | None:
    """Get item from dictionary by key.

    Args:
        dictionary: dict - dictionary with data.
        key: str | int | float | tuple | frozenset - dictionary key for get data.

    Returns:
        Any: dictionary data if key exists.
        None: dictionary data if key not exists.
    """
    expected_types = (dict)
    check_isinstance(expected_types, dictionary, 'dictionary')
    expected_types = (str, int, float, tuple, frozenset)
    check_isinstance(expected_types, key, 'key')
    return dictionary.get(key)


@register.filter
def to_int(any_object: str | float | bool) -> int:
    """Convert object to int.

    Args:
        any_object: Any - object for convert to int.

    Returns:
        int: converted object.
    """
    expected_types = (str, float, bool)
    check_isinstance(expected_types, any_object, 'any_object')
    return int(any_object)


@register.filter
def get_avg(any_data: list | dict) -> float | int:
    """Get average from list or dict values.

    Args:
        any_data: list | dict - list or dict with values.

    Returns:
        float | int: _description_
    """
    expected_types = (list, dict)
    check_isinstance(expected_types, any_data, 'any_data')
    if isinstance(any_data, dict):
        any_data = list(any_data.values())
    any_data = list(filter(lambda number: number != 0, any_data))
    if any_data:
        return sum(any_data) / len(any_data)
    return 0
