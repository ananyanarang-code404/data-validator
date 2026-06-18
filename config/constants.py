# config/constants.py

DEFAULT_PHONE_RULES = {
    "IN": {
        "length": 10,
        "prefixes": ["6", "7", "8", "9"]
    },
    "US": {
        "length": 10,
        "prefixes": None
    },
    "SG": {
        "length": 8,
        "prefixes": None
    }
}

VALID_PAYMENT_MODES = [
    "UPI",
    "CARD",
    "NETBANKING",
    "COD",
    "WALLET"
]

VALID_PAYMENT_STATUSES = [
    "SUCCESS",
    "FAILED",
    "PENDING"
]

DATE_FORMATS = {
    "YYYY-MM-DD": "%Y-%m-%d",
    "DD/MM/YYYY": "%d/%m/%Y",
    "MM/DD/YYYY": "%m/%d/%Y"
}

CHUNK_SIZE = 10000