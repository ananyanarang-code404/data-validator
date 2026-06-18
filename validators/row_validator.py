# validators/row_validator.py

from validators.phone_validator import validate_phone
from validators.date_validator import validate_date
from validators.payment_validator import (
    validate_payment_mode,
    validate_payment_status
)


def validate_row(row, phone_rules, date_format):
    errors = []

    # Required fields
    required_fields = [
        "order_id",
        "customer_id",
        "country",
        "phone",
        "order_date",
        "payment_mode",
        "payment_status"
    ]

    for field in required_fields:
        value = row.get(field)

        if value is None or str(value).strip() == "":
            errors.append(f"{field} is required")

    # Stop further validation if critical fields missing
    if errors:
        return errors

    # Phone validation
    phone_error = validate_phone(
        row["phone"],
        row["country"],
        phone_rules
    )

    if phone_error:
        errors.append(phone_error)

    # Date validation
    date_error = validate_date(
        row["order_date"],
        date_format
    )

    if date_error:
        errors.append(date_error)

    # Payment mode validation
    mode_error = validate_payment_mode(
        row["payment_mode"]
    )

    if mode_error:
        errors.append(mode_error)

    # Payment status validation
    status_error = validate_payment_status(
        row["payment_status"]
    )

    if status_error:
        errors.append(status_error)

    return errors