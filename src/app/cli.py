import typer
import uvicorn
import logging
from uvicorn.supervisors import Multiprocess, ChangeReload
from core.log import setup_loguru_logging_intercept

app = typer.Typer()

DEFAULT_UVICORN_APP = "app:api"
APP_KEY = "uvicorn_app"
UVICORN_LOGGING_MODULES = ("uvicorn.error", "uvicorn.asgi", "uvicorn.access")


@app.command()
def main(
        ctx: typer.Context,
        uvicorn_app: str = typer.Option(DEFAULT_UVICORN_APP),
        host: str = typer.Option("0.0.0.0"),
        port: int = typer.Option(6006),
        log_level: str = typer.Option("info"),
        timeout_keep_alive: int = typer.Option(300),
        force_exit: bool = False
):
    config = uvicorn.Config(uvicorn_app, host=host, port=port, log_level=log_level,
                            timeout_keep_alive=timeout_keep_alive)
    server = uvicorn.Server(config)
    server.force_exit = force_exit
    setup_loguru_logging_intercept(
        level=logging.getLevelName(config.log_level.upper()),
        modules=UVICORN_LOGGING_MODULES
    )
    supervisor_type = None
    if config.should_reload:
        supervisor_type = ChangeReload
    if config.workers > 1:
        supervisor_type = Multiprocess
    if supervisor_type:
        sock = config.bind_socket()
        supervisor = supervisor_type(config, target=server.run, sockets=[sock])
        supervisor.run()
    else:
        server.run()
