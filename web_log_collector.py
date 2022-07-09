#!/usr/bin/env python

from logging import Logger, getLogger
from asyncio import run as asyncio_run
from typing import NoReturn, Type
from logging.handlers import TimedRotatingFileHandler
from logging import INFO, StreamHandler

from fastapi import FastAPI
from ecs_tools_py import make_log_handler
from uvicorn import run as uvicorn_run

from web_log_collector.cli import WebLogCollectorArgumentParser
from web_log_collector.api import API_ROUTER

LOG: Logger = getLogger(__name__)


async def main() -> NoReturn:
    args: Type[WebLogCollectorArgumentParser.Namespace] = WebLogCollectorArgumentParser().parse_args()

    provider_name = 'Web Log Collector'

    if args.log_directory:
        log_handler = make_log_handler(
            base_class=TimedRotatingFileHandler,
            provider_name=provider_name
        )(filename=(args.log_directory / 'web_log_collector.log'), when='D')
    else:
        log_handler = StreamHandler()

    LOG.addHandler(hdlr=log_handler)
    LOG.setLevel(level=INFO)

    from web_log_collector.api import LOG as API_LOG

    API_LOG.addHandler(hdlr=log_handler)
    API_LOG.setLevel(level=INFO)

    app = FastAPI()
    app.include_router(API_ROUTER)

    uvicorn_run(app=app, host=args.host, port=args.port)

if __name__ == '__main__':
    asyncio_run(main())

