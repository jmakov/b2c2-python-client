class ConfigFile:
    AUTH_TOKEN = "auth_token"
    LOG_LEVEL = "log_level"
    BASE_URL = "base_url"
    MAX_CONNECTION_RETRIES = "max_connection_retries"
    CONNECTION_TIMEOUT = "connection_timeout_seconds"
    SLEEP_BETWEEN_RECONNECTS = "wait_seconds_between_connection_retries"


# TODO: move log to /var/log/b2c2-python-client/log.txt and config to /etc/b2c2-python-client/config.yaml
class Path:
    LOG = "log/log.txt"
    CONFIG = "config.yaml"


class APIEndpoint:
    balance = "balance"
    instruments = "instruments"
    order = "order"
    rfq = "request_for_quote"
    MIN_ORDER_VALID_SECONDS = 10


class Instruments:
    supported_fiat_currencies = ["USD", "EUR", "GBP"]
    MAX_DIGITS_FIAT = 4
    MAX_DIGITS_CRYPTO = 2
