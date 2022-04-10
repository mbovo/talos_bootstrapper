import logging
from loguru import logger
import urllib3
from .config import cfg


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(level: str = "INFO"):
    urllib3.disable_warnings()
    logging.basicConfig(handlers=[InterceptHandler()], level=level)


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


def parse_mac(mac: str):

    if mac not in cfg.mapping:
        return None

    for i in ["ip", "hostname", "device", "role"]:
        if i not in cfg.mapping[mac]:
            return None

    client_ip = cfg.mapping[mac].ip
    hostname = cfg.mapping[mac].hostname
    device = cfg.mapping[mac].device
    role = cfg.mapping[mac].role

    netmask = cfg.mapping[mac].netmask if "netmask" in cfg.mapping[mac] else cfg.defaults.netmask
    server_ip = cfg.mapping[mac].server_ip if "server_ip" in cfg.mapping[mac] else cfg.defaults.server_ip
    gateway = cfg.mapping[mac].gateway if "gateway" in cfg.mapping[mac] else cfg.defaults.gateway
    dns = cfg.mapping[mac].dns if "dns" in cfg.mapping[mac] else cfg.defaults.dns
    ntp = cfg.mapping[mac].ntp if "ntp" in cfg.mapping[mac] else cfg.defaults.ntp

    kernel = cfg.mapping[mac].kernel if "kernel" in cfg.mapping[mac] else cfg.defaults.kernelcmdline
    initrd = cfg.mapping[mac].initrd if "initrd" in cfg.mapping[mac] else cfg.defaults.initrd
    message = cfg.mapping[mac].message if "message" in cfg.mapping[mac] else cfg.defaults.message
    cmdline = cfg.mapping[mac].cmdline if "cmdline" in cfg.mapping[mac] else cfg.defaults.cmdline

    cmdline += f"ip={client_ip}:{server_ip}:{gateway}:{netmask}:{hostname}:{device}:off:{dns}::{ntp}"
    cmdline += f"talos.config=/v1/cluster/{role}"

    ret = {"kernel": kernel, "initrd": initrd, "message": message, "cmdline": cmdline}

    return ret
