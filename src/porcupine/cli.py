import signal
import click
import pkg_resources
import logging
import random
import string

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
def start(**args):

    cfg.add("mapping", {})
    cfg.add("defaults", {})

    cfg.fromFile(args["config_file"])
    for k, w in args.items():
        if k not in cfg:
            cfg.add(k, w)

    logging.debug(f"Loaded config: {cfg}")

    if cfg.api_key is None:
        cfg.api_key = "".join(random.choice(string.ascii_letters + string.digits) for i in range(48))
        logging.warning(f"No API_KEY given, new one generated: {cfg.api_key}")

    server.run()


def sig_handler(signum, stack):
    if signum in [1, 2, 3, 15]:
        logging.warning("Caught signal %s, exiting.", str(signum))
        server.stop()
    # else:
    # gin_app.logger.warning('Ignoring signal %s.', str(signum))
    return stack


def set_sig_handler(funcname, avoid=["SIG_DFL", "SIGSTOP", "SIGKILL"]):
    for i in [x for x in dir(signal) if x.startswith("SIG") and x not in avoid]:
        try:
            signum = getattr(signal, i)
            signal.signal(signum, funcname)
        except (OSError, RuntimeError, ValueError) as m:  # OSError for Python3, RuntimeError for 2
            logging.warning("Skipping {} {}".format(i, m))
