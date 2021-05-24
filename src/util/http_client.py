import logging
import requests
from requests.compat import urljoin     # type: ignore
import time
import typing

from src import constant
from src import exception


def retry_request(func: typing.Callable) -> typing.Callable:
    def inner(self, method: str, endpoint: str, data: typing.Dict = None) -> typing.Dict:  # type: ignore
        connection_attempts = 0

        while connection_attempts <= self.max_retries:
            try:
                response = func(self, method, endpoint, data)
            except (requests.exceptions.HTTPError, requests.exceptions.TooManyRedirects) as e:
                self.logger.error(e)
                raise exception.HttpClientException("Please check your config file.") from None
            except (
                    requests.exceptions.Timeout,
                    requests.exceptions.ConnectTimeout,
                    requests.exceptions.ConnectionError
            ) as e:
                self.logger.error(e)
            except requests.exceptions.RequestException as e:
                self.logger.error(e)
                raise exception.HttpClientException(e) from None
            else:
                return response

            connection_attempts += 1
            time.sleep(self.sleep_between_reconnects)
            self.logger.info(f"Connection attempt: {connection_attempts}")

        raise exception.HttpClientException(f"Request failed after {connection_attempts} retries.")
    return inner


class HttpClient:
    def __init__(self, base_url: str, auth_token: str, max_connection_retries: int, timeout: int, sleep: int):
        self.base_url = base_url
        self.auth_token = auth_token
        self.max_retries = max_connection_retries
        self.timeout = timeout
        self.sleep_between_reconnects = sleep
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = requests.session()
        self.set_session_headers()

    def set_session_headers(self) -> None:
        self.session.headers.update({"Authorization": self.auth_token})
        self.logger.debug(f"Session headers set to: {self.auth_token}")

    @retry_request
    def _send_request(self, method: str, endpoint: str, data: typing.Dict = None) -> typing.Dict:
        url = urljoin(self.base_url, endpoint)
        self.logger.info(f"Requesting url: {url}")

        response = self.session.request(method, url, timeout=self.timeout, data=data)
        self.logger.debug(f"Response: {response.text}")

        response.raise_for_status()
        return response.json()

    def get_balance(self) -> typing.Dict:
        return self._send_request("GET", constant.APIEndpoint.balance)

    def get_instruments(self) -> typing.Dict:
        return self._send_request("GET", constant.APIEndpoint.instruments)

    def send_order(self, data: typing.Dict) -> typing.Dict:
        return self._send_request("POST", constant.APIEndpoint.order, data)

    def send_request_for_quote(self, data: typing.Dict) -> typing.Dict:
        return self._send_request("POST", constant.APIEndpoint.rfq, data)
