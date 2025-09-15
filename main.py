# main.py

import os

import click
import uvicorn


@click.command()
@click.option(
    "--env",
    type=click.Choice(["local", "dev", "prod"], case_sensitive=False),
    default="local",
    help="Application environment.",
    show_default=True,
)
@click.option(
    "--debug",
    type=click.BOOL,
    is_flag=True,
    default=False,
    help="Enable debug mode.",
    show_default=True,
)
@click.option(
    "--host",
    type=str,
    default="0.0.0.0",
    help="Host to run the application on.",
    show_default=True,
)
@click.option(
    "--port",
    type=int,
    default=8000,
    help="Port to run the application on.",
    show_default=True,
)
def main(env: str, debug: bool, host: str, port: int):
    uvicorn.run(
        app="src.server:app",
        host=host,
        port=port,
        reload=False if env == "prod" else True,
        workers=((os.cpu_count() or 1) * 2 + 1 if env == "prod" else 1),
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
