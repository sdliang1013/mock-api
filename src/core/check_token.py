import re

from core.config import settings
from starlette.datastructures import URL, QueryParams
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from util import security


class CheckTokenMiddleware:
    def __init__(self,
                 app: ASGIApp,
                 key: str,
                 salt: str,
                 expired: int = 0,
                 prefix: str = '/',
                 white_uris: list = [],
                 header: str = None, ):
        """

        :param app:
        :param key: 密钥
        :param salt: 盐
        :param expired: 过期时长
        :param prefix: 匹配path前缀
        :param white_uris: 白名单
        :param header: 头部token(优先匹配header, 再取url参数token)
        """
        self.app = app
        self.key = key
        self.salt = salt
        self.expired = expired
        self.prefix = prefix
        self.header = header
        self.re_uris = list(map(lambda x: re.compile(x), white_uris))

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # 调试模式
        if settings.debugger:
            await self.app(scope, receive, send)
            return
        # schema (必须和URL判断分开, 否则报Block错误)
        if scope["type"] not in ("http", "https"):
            await self.app(scope, receive, send)
            return
        # path
        url = URL(scope=scope)
        if self.check_white_uri(path=url.path) or not url.path.startswith(self.prefix):
            await self.app(scope, receive, send)
            return
        token = None
        # header
        if self.header:
            request = Request(scope)
            token = request.headers.get(self.header)
        # url
        if not token:
            params = QueryParams(url.query)
            token = params.get('token', None)
        # no token
        if not token:
            response = PlainTextResponse('Token Not Found', status_code=403)
            await response(scope, receive, send)
            return
        # check token
        token_in = security.check_token(key=self.key, salt=self.salt, token=token,
                                        expired=self.expired, tolerance=settings.tolerance_seconds)
        if not token_in:
            response = PlainTextResponse('Token Is Invalid', status_code=401)
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)

    def check_white_uri(self, path: str):
        for re_uri in self.re_uris:
            if re_uri.fullmatch(path):
                return True
        return False
