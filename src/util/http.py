# coding: utf-8
import ssl
from typing import Union

from httpx import AsyncClient, HTTPStatusError, Response, TimeoutException

try:
    from urllib.error import HTTPError
    import urllib.parse as urlparse
except ImportError:
    from urllib2 import HTTPError
    import urlparse

try:
    ssl._create_default_https_context = ssl._create_stdlib_context
except:
    pass


class HttpClient(object):
    """
    A thin wrapper for making HTTP calls to the salt-api rest_cherrpy REST
    interface

    api = HttpClient('https://localhost:8000')
    api.req_json({'a': 'local', 'b': '*', 'c': 'test.ping'})

    """

    def __init__(self,
                 uri,
                 ssl_verify=False,
                 proxies: dict = {},
                 headers: dict = {}, ):
        """
        Initialize the class with the URL of the API

        :param uri: Host or IP address of the salt-api URL;
            include the port number

        :param ssl_verify: SSL certificates

        :raises SaltApiException: if the uri is misformed
        
        """
        split = urlparse.urlsplit(uri)
        if split.scheme not in ['http', 'https']:
            raise NotImplementedError(message="URL missing HTTP(s) protocol: {0}".format(uri))

        self.uri = uri
        self.ssl_verify = ssl_verify
        self.proxies = proxies
        self.header_default = headers
        self.stream_resp = []
        self.timeout_default = 15
        self.client = self.get_client()

    def get_client(self) -> AsyncClient:
        return AsyncClient(verify=self.ssl_verify, proxies=self.proxies)

    async def req_stream(self, path, timeout=120, headers: dict = {}):
        """
        A thin wrapper to get a response from saltstack api.
        The body of the response will not be downloaded immediately.
        Make sure to close the connection after use.
        api = HttpClient('http://ipaddress/api/')
        resp_lines = api.req_stream('/events')
        async for line in resp_lines:
            print(line)

        :param path: The path to the salt api resource

        :return: :class:`Response <Response>` object

        :rtype: requests.Response
        """

        async with self.client.stream(method='GET', url=self._construct_url(path),
                                      headers=self.__get_headers__(headers), timeout=timeout) as resp:
            resp.raise_for_status()
            self.stream_resp.append(resp)
            async for line in resp.aiter_lines():
                yield line

    async def req_get(self, path, timeout=None, headers: dict = {}) -> dict:
        """
        A thin wrapper from get http method of saltstack api
        api = HttpClient('http://ipaddress/api/',auth={'salt','salt','pam'})
        print(await api.req_get('/keys'))
        """
        if not timeout:
            timeout = self.timeout_default

        resp = await self.client.get(url=self._construct_url(path), headers=self.__get_headers__(headers),
                                     timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    async def req_post(self, path: str, data=None, timeout=None, headers: dict = {},
                       **kwargs) -> Response:
        if not timeout:
            timeout = self.timeout_default

        resp = await self.client.post(url=self._construct_url(path),
                                      headers=self.__get_headers__(headers),
                                      json=data,
                                      timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    async def req_json(self, path, data=None, timeout=None, headers: dict = {}, **kwargs) -> dict:
        """
        A thin wrapper around urllib2 to send requests and return the response
        api = HttpClient('http://ipaddress/api/',auth={'salt','salt','pam'})
        print(await api.req_json('/keys'))

        If the current instance contains an authentication token it will be
        attached to the request as a custom header.

        :rtype: dictionary

        """
        req_headers = {
            'Content-Type': 'application/json',
        }
        req_headers.update(headers)
        if not timeout:
            timeout = self.timeout_default

        return await self.req_post(path=path, data=data, timeout=timeout, headers=req_headers)

    async def close_stream(self):
        for resp in self.stream_resp:
            await resp.aclose()

    @classmethod
    def to_http_error(cls, err: Union[TimeoutException, HTTPStatusError]):
        status_code = 500
        if isinstance(err, TimeoutException):
            status_code = 408
        elif isinstance(err, HTTPStatusError):
            status_code = err.response.status_code
        return HTTPError(url=err.request.url,
                         code=status_code,
                         msg="%s" % err, hdrs=None, fp=None)

    @classmethod
    def is_timeout(cls, err: HTTPError):
        return err.code in [408, 502, 504]

    def _construct_url(self, path):
        """
        Construct the url to salt-api for the given path

        Args:
            path: the path to the salt-api resource

        api = HttpClient('https://localhost:8000/')
        api._construct_url('/login')
        'https://localhost:8000/login'
        """

        relative_path = path.lstrip('/')
        return urlparse.urljoin(self.uri, relative_path)

    def __get_headers__(self, headers: dict):
        req_headers = {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        }
        req_headers.update(self.header_default)
        req_headers.update(headers)
        return req_headers
