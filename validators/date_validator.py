

from datetime import datetime


def validate_date(date_value, selected_format):
    """
    Validate date against selected format.

    Returns:
        None if valid
        Error message if invalid
    """

    if not date_value:
        return "Date is missing"

    try:
        datetime.strptime(str(date_value).strip(), selected_format)
        return None
    except ValueError:
        return (
            f"Invalid date format. "
            f"Expected {selected_format}"
        )