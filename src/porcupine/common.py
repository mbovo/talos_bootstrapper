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
    try:
        if mac not in cfg.mapping:
            logging.error(f"Unknown map address {mac}")
            return f"ERROR: Unknown mac address {mac}", 400

        if "dhcp" in cfg.mapping[mac] and cfg.mapping[mac].dhcp is False:
            for i in ["ip", "hostname", "device", "role"]:
                if i not in cfg.mapping[mac]:
                    logging.error(f"field '{i}' not found in mapping for mac {mac}")
                    return f"ERROR: field '{i}' not found in mapping for mac {mac}", 400

        client_ip = cfg.mapping[mac].ip if "ip" in cfg.mapping[mac] else ""
        hostname = cfg.mapping[mac].hostname if "hostname" in cfg.mapping[mac] else ""
        device = cfg.mapping[mac].device if "device" in cfg.mapping[mac] else ""
        role = cfg.mapping[mac].role if "role" in cfg.mapping[mac] else "worker"

        netmask = cfg.mapping[mac].netmask if "netmask" in cfg.mapping[mac] else cfg.defaults.netmask
        server_ip = cfg.mapping[mac].server_ip if "server_ip" in cfg.mapping[mac] else cfg.defaults.server_ip
        gateway = cfg.mapping[mac].gateway if "gateway" in cfg.mapping[mac] else cfg.defaults.gateway
        dns = cfg.mapping[mac].dns if "dns" in cfg.mapping[mac] else cfg.defaults.dns
        ntp = cfg.mapping[mac].ntp if "ntp" in cfg.mapping[mac] else cfg.defaults.ntp

        kernel = cfg.mapping[mac].kernel if "kernel" in cfg.mapping[mac] else cfg.defaults.kernel
        initrd = cfg.mapping[mac].initrd if "initrd" in cfg.mapping[mac] else cfg.defaults.initrd
        message = cfg.mapping[mac].message if "message" in cfg.mapping[mac] else cfg.defaults.message
        cmdline = cfg.mapping[mac].cmdline if "cmdline" in cfg.mapping[mac] else cfg.defaults.cmdline

        cmdline += f" talos.config = /v1/cluster/{role}"
        if not cfg.mapping[mac].dhcp:
            cmdline += f" ip={client_ip}:{server_ip}:{gateway}:{netmask}:{hostname}:{device}:off:{dns}::{ntp}"

        ret = {"kernel": kernel, "initrd": initrd, "message": message, "cmdline": cmdline}
    except Exception as e:
        logging.error(f"Error: {e}")
        return str(e), 400
    return ret, 200
