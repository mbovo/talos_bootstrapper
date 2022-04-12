import signal
import click
import pkg_resources
import logging
import uuid

from . import server, common
from .config import cfg

VERSION = pkg_resources.get_distribution("porcupine").version


@click.group()
def main():
    common.setup_logging()
    set_sig_handler(sig_handler)


@main.command(help="Print version and exit")
def version():
    click.echo(f"Porcupine - Talos Linux bootstrapper v{VERSION}")


@main.command(help="Start the daemon")
@click.option(
    "-c",
    "--config",
    "config_file",
    envvar="CONFIGFILE",
    required=False,
    default="config.yaml",
    type=click.Path(exists=False, dir_okay=False, file_okay=True, readable=True, resolve_path=True, allow_dash=False),
    help="Yaml config file (config.yaml)",
)
@click.option("-l", "--listen", "listen_address", envvar="LISTEN_ADDRESS", default="0.0.0.0", help="Listen address (0.0.0.0)")
@click.option("-p", "--port", "listen_port", envvar="LISTEN_PORT", default="5000", help="Listen port (5000)")
@click.option("-e", "--externalurl", "external_url", envvar="EXTERNAL_URL", default=None, help="URL from external standpoint (default: http://IPADDR:PORT)")
def start(**args):

    if not cfg.fromFile(args["config_file"]):
        exit(1)

    if not cfg.settings.listen_address:
        cfg.settings.listen_address = args["listen_address"]
    if not cfg.settings.listen_port:
        cfg.settings.listen_port = args["listen_port"]
    if not cfg.settings.config_file:
        cfg.settings.config_file = args["config_file"]
    if not cfg.settings.external_url:
        cfg.settings.external_url = args["external_url"]

    if cfg.settings.external_url is None:
        cfg.settings.external_url = f"http://{common.get_hostname()}:{cfg.settings.listen_port}"

    if cfg.settings.api_key is None:
        cfg.settings.api_key = str(uuid.uuid4())
        logging.warning(f"No API_KEY given, new one generated: {cfg.settings.api_key}")
        logging.warning("To avoid this message on start add your `api_key: yourstring` to config.yaml file")

    logging.debug(f"Loaded config: {cfg}")

    server.run()


def sig_handler(signum, stack):
    if signum in [1, 2, 3, 15]:
        logging.warning("Caught signal %s, exiting.", str(signum))
        server.stop()
    return stack


def set_sig_handler(funcname, avoid=["SIG_DFL", "SIGSTOP", "SIGKILL"]):
    for i in [x for x in dir(signal) if x.startswith("SIG") and x not in avoid]:
        try:
            signum = getattr(signal, i)
            signal.signal(signum, funcname)
        except (OSError, RuntimeError, ValueError) as m:  # OSError for Python3, RuntimeError for 2
            logging.warning("Skipping {} {}".format(i, m))
