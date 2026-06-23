import logging
import os
import time
from collections import OrderedDict
from urllib.parse import urlparse

import requests

from .query_params import QueryParams

try:
    import http.client as http_client
except ImportError:
    import httplib as http_client

try:
    import urllib3

    urllib3.disable_warnings()
except ImportError:
    pass


class MCAPIError(Exception):
    def __init__(self, message, response):
        super(MCAPIError, self).__init__(message)
        self.response = response


def merge_dicts(dict1, dict2):
    merged = dict1.copy()
    merged.update(dict2)
    return merged


def set_paging_params(params, starting_page, page_size):
    if starting_page is not None:
        params["page[number]"] = starting_page

    if page_size is not None:
        params["page[size]"] = page_size

    return params


def origin(url):
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


class ClientBase:
    """
    Shared HTTP/auth/rate-limit behavior for the Materials Commons REST API client.
    """

    def __init__(self, apikey, base_url="https://materialscommons.org/api", raise_exception=True):
        self.apikey = apikey
        self.base_url = base_url
        self.log = False
        self.raise_exception = raise_exception
        self.headers = {
            "Authorization": "Bearer " + self.apikey,
            "Accept": "application/json",
        }
        self.rate_limit = 0
        self.rate_limit_remaining = 0
        self.rate_limit_reset = None
        self.retry_after = None
        self.r = None
        self._throttle_s = 0.0

        tls_cert = os.getenv("MC_VERIFY_TLS_CERT")
        if tls_cert is None or tls_cert.lower() == "false" or tls_cert.lower() == "no":
            self._verify_tls_cert = False
        else:
            self._verify_tls_cert = True

    @staticmethod
    def get_apikey(email, password, base_url="https://materialscommons.org/api"):
        url = base_url + "/get_apitoken"
        form = {"email": email, "password": password}
        r = requests.post(url, json=form, verify=False)
        r.raise_for_status()
        return r.json()["data"]["api_token"]

    @classmethod
    def login(cls, email, password, base_url="https://materialscommons.org/api"):
        apikey = cls.get_apikey(email, password, base_url)
        return cls(apikey, base_url)

    @staticmethod
    def set_debug_on():
        http_client.HTTPConnection.debuglevel = 1
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    @staticmethod
    def set_debug_off():
        http_client.HTTPConnection.debuglevel = 0
        logging.disable()
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.disabled = True
        requests_log.propagate = False

    def _decode_response(self, data, decoder):
        if data is None:
            return None
        if decoder is None:
            return data
        return decoder(data)

    def _throttle(self):
        if self._throttle_s < 0:
            self._throttle_s = 0.0
        if self._throttle_s:
            time.sleep(self._throttle_s)

    def _get(self, urlpart, params=None, other_params=None, decoder=None):
        self._throttle()
        url = self.base_url + urlpart
        if self.log:
            print("GET:", url)
        params = params or {}
        other_params = other_params or {}
        params_to_use = merge_dicts(QueryParams.to_query_args(params), other_params)
        r = requests.get(url, params=params_to_use, verify=self._verify_tls_cert, headers=self.headers)
        return self._decode_response(self._handle_with_json(r), decoder)

    def _get_no_value(self, urlpart):
        self._throttle()
        url = self.base_url + urlpart
        if self.log:
            print("GET:", url)
        r = requests.get(url, verify=self._verify_tls_cert, headers=self.headers)
        return self._handle(r)

    def _post(self, urlpart, data=None, params=None, decoder=None):
        self._throttle()
        url = self.base_url + urlpart
        if self.log:
            print("POST:", url)
        data = OrderedDict(data or {})
        r = requests.post(url, json=data, verify=self._verify_tls_cert, headers=self.headers, params=params)
        return self._decode_response(self._handle_with_json(r), decoder)

    def _put(self, urlpart, data=None, decoder=None):
        self._throttle()
        url = self.base_url + urlpart
        if self.log:
            print("PUT:", url)
        data = OrderedDict(data or {})
        r = requests.put(url, json=data, verify=self._verify_tls_cert, headers=self.headers)
        return self._decode_response(self._handle_with_json(r), decoder)

    def _delete(self, urlpart, params=None):
        self._throttle()
        url = self.base_url + urlpart
        if self.log:
            print("DELETE:", url)
        r = requests.delete(url, verify=self._verify_tls_cert, params=params, headers=self.headers)
        self._handle(r)

    def _download(self, urlpart, to):
        self._throttle()
        url = self.base_url + urlpart
        with requests.get(url, stream=True, verify=self._verify_tls_cert, headers=self.headers) as r:
            self._handle(r)
            with open(to, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

    def _upload_to_path(self, urlpart, file_path, dest_path):
        self._throttle()
        url = self.base_url + urlpart
        form = {'path': dest_path}
        with open(file_path, 'rb') as f:
            files = {'file': f}
            r = requests.post(url, files=files, verify=self._verify_tls_cert, headers=self.headers, data=form)
            return self._handle_with_json(r)

    def _upload(self, urlpart, file_path):
        self._throttle()
        url = self.base_url + urlpart
        with open(file_path, 'rb') as f:
            files = [('files[]', f)]
            r = requests.post(url, verify=self._verify_tls_cert, headers=self.headers, files=files)
            return self._handle_with_json(r)

    def _upload_raw(self, urlpart, f):
        self._throttle()
        url = self.base_url + urlpart
        files = [('files[]', f)]
        r = requests.post(url, verify=self._verify_tls_cert, headers=self.headers, files=files)
        return self._handle_with_json(r)

    def _handle(self, r):
        self.r = r
        self._update_rate_limits_from_request(r)
        try:
            r.raise_for_status()
            return True
        except requests.HTTPError as e:
            if not self.raise_exception:
                return False
            raise MCAPIError(str(e), e.response)

    def _handle_with_json(self, r):
        if not self._handle(r):
            return None
        if r.headers.get("content-type") == "application/json":
            result = r.json()
            if "data" in result:
                return result["data"]
            return result
        return None

    def _update_rate_limits_from_request(self, r):
        self.rate_limit = int(r.headers.get("x-ratelimit-limit", self.rate_limit))
        self.rate_limit_remaining = int(r.headers.get("x-ratelimit-remaining", self.rate_limit_remaining))
        self.rate_limit_reset = r.headers.get("x-ratelimit-reset", None)
        self.retry_after = r.headers.get("retry-after", None)

        if self.rate_limit_remaining < 10:
            self._throttle_s = 60.0 / (self.rate_limit_remaining - 1.0)
        else:
            self._throttle_s = 0.0