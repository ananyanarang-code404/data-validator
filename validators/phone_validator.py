# validators/phone_validator.py

import re


def validate_phone(phone, country, phone_rules):
    """
    Validates phone number based on country-specific rules.

    Returns:
        None if valid
        Error message string if invalid
    """

    if not phone:
        return "Phone number is missing"

    phone = str(phone).strip()

    if not re.fullmatch(r"\d+", phone):
        return "Phone number must contain only digits"

    country_rule = phone_rules.get(country)

    if not country_rule:
        return f"Unsupported country: {country}"

    required_length = country_rule.get("length")

    if len(phone) != required_length:
        return (
            f"Phone number must be {required_length} digits "
            f"for country {country}"
        )

    allowed_prefixes = country_rule.get("prefixes")

    if allowed_prefixes:
        if phone[0] not in allowed_prefixes:
            return (
                f"Phone number must start with "
                f"{', '.join(allowed_prefixes)}"
            )

    return None