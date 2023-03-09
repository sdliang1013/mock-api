# -*- coding: utf-8 -*-

import logging
import sys

from fastapi import FastAPI
from loguru import logger

from core.check_token import CheckTokenMiddleware
from core.config import settings
from core.event import create_start_app_handler, create_stop_app_handler
from plugins import api_router


def get_api() -> FastAPI:
    app = FastAPI(
        title="Mock API",
        version="0.0.1",
        openapi_url=settings.api_path("/api.json"),
    )

    # add middleware
    app.add_middleware(CheckTokenMiddleware,
                       key=settings.key,
                       salt='MockAPI',
                       expired=settings.expire_seconds,
                       header=settings.token_header,
                       prefix=settings.api_base,
                       white_uris=list(map(lambda x: settings.api_path(x), settings.white_uris.split(','))), )
    logger.info("Application Middleware initialized")

    app.add_event_handler("startup", create_start_app_handler(app))
    app.add_event_handler("shutdown", create_stop_app_handler(app))
    logger.info("Application Event Handler initialized")

    # load plugins
    api_router.register(app.router, prefix=settings.api_base)

    logger.info("Application Router initialized")

    logger.info("Application initialized")

    return app


api = get_api()

fmt = logging.Formatter(
    fmt="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)
sh.setFormatter(fmt)
