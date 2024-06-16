"""Module with functions for work with erros."""


def convert_errors(errors: dict) -> dict:
    """Convert errors into readable dict.

    Args:
        errors: dict - raw dict with errors

    Returns:
        dict: readable dict with errors.
    """
    readable_dict = {}
    for field_name, field_errors in errors.items():
        for error in field_errors:
            error = str(error)
            if error.startswith("['") and error.endswith("']"):
                error = error[2:-2]
                readable_dict[field_name] = error
    return readable_dict
