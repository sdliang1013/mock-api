from typing import Callable

from fastapi import FastAPI
from loguru import logger

from core.starter import AgentStarter


class SchedulerStarter(AgentStarter):
    def __init__(self):
        logger.info("init SchedulerStarter")
        ...

    async def start(self):
        logger.info("start SchedulerStarter")
        ...

    async def stop(self):
        logger.info("stop SchedulerStarter")
        ...


scheduler_starter = SchedulerStarter()


def create_start_app_handler(app: FastAPI) -> Callable:
    async def start_app() -> None:
        await scheduler_starter.start()

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        await scheduler_starter.stop()

    return stop_app
