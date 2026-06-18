from config.constants import (
    VALID_PAYMENT_MODES,
    VALID_PAYMENT_STATUSES
)


def validate_payment_mode(mode):
    if not mode:
        return "Payment mode is missing"

    if str(mode).upper() not in VALID_PAYMENT_MODES:
        return (
            f"Invalid payment mode: {mode}"
        )

    return None


def validate_payment_status(status):
    if not status:
        return "Payment status is missing"

    if str(status).upper() not in VALID_PAYMENT_STATUSES:
        return (
            f"Invalid payment status: {status}"
        )

    return None