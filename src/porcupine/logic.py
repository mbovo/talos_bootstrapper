import logging
from .config import cfg


def parse_mac(mac: str):

    # defaults
    ret = {k: v for k, v in cfg.settings.defaults.boot.dict().items() if k in ["kernel", "initrd", "message", "cmdline"]}
    net = {k: v for k, v in cfg.settings.defaults.net.dict().items() if k not in ["dhcp"]}
    use_dhcp = cfg.settings.defaults.net.dhcp
    net_cmdline = ""
    role = cfg.settings.defaults.role

    if cfg.settings.defaults.deny_unknown_clients and mac not in cfg.settings.mapping:
        logging.warning(f"Unknown mac address {mac}, blocking boot process")
        raise Exception(f"mac address not found {mac}")

    if mac in cfg.settings.mapping:
        mapping = cfg.settings.mapping[mac]

        # override boot defaults with parameters from mapping
        if mapping.boot is not None:
            for k, v in mapping.boot.dict().items():
                if v is not None:
                    ret[k] = v

        # override net defaults with paramenters from mapping
        if mapping.net is not None:
            for k, v in mapping.net.dict().items():
                if v is not None and k not in ["dhcp"]:
                    net[k] = v
        # override dhcp with parameters from mapping
        if mapping.net.dhcp is not None:
            use_dhcp = mapping.net.dhcp

        # override role with paramters from mapping
        if mapping.role is not None:
            role = mapping.role

    # enable net cmdline if required (dhcp=false)
    if not use_dhcp:
        ip = net["ip"] if "ip" in net else ""
        server = net["server"] if "server" in net else ""
        gateway = net["gateway"] if "gateway" in net else ""
        netmask = net["netmask"] if "netmask" in net else ""
        hostname = net["hostname"] if "hostname" in net else ""
        device = net["device"] if "device" in net else ""
        dns = net["dns"] if "dns" in net else ""
        ntp = net["ntp"] if "ntp" in net else ""
        net_cmdline = f" ip={ip}:{server}:{gateway}:{netmask}:{hostname}:{device}:off:{dns}::{ntp}"

    # add extra_cmdline
    extra_cmdline = f" talos.config={cfg.settings.external_url}/v1/cluster/{role}"

    ret["cmdline"] = f"{ret['cmdline']}{net_cmdline}{extra_cmdline}"

    logging.info(ret)

    return ret
    # try:
    #     if mac not in cfg.mapping:
    #         logging.error(f"Unknown map address {mac}")
    #         return f"ERROR: Unknown mac address {mac}", 400

    #     if "dhcp" in cfg.mapping[mac] and cfg.mapping[mac].dhcp is False:
    #         for i in ["ip", "hostname", "device", "role"]:
    #             if i not in cfg.mapping[mac]:
    #                 logging.error(f"field '{i}' not found in mapping for mac {mac}")
    #                 return f"ERROR: field '{i}' not found in mapping for mac {mac}", 400

    #     client_ip = cfg.mapping[mac].ip if "ip" in cfg.mapping[mac] else ""
    #     hostname = cfg.mapping[mac].hostname if "hostname" in cfg.mapping[mac] else ""
    #     device = cfg.mapping[mac].device if "device" in cfg.mapping[mac] else ""
    #     role = cfg.mapping[mac].role if "role" in cfg.mapping[mac] else "worker"

    #     netmask = cfg.mapping[mac].netmask if "netmask" in cfg.mapping[mac] else cfg.defaults.netmask
    #     server_ip = cfg.mapping[mac].server_ip if "server_ip" in cfg.mapping[mac] else cfg.defaults.server_ip
    #     gateway = cfg.mapping[mac].gateway if "gateway" in cfg.mapping[mac] else cfg.defaults.gateway
    #     dns = cfg.mapping[mac].dns if "dns" in cfg.mapping[mac] else cfg.defaults.dns
    #     ntp = cfg.mapping[mac].ntp if "ntp" in cfg.mapping[mac] else cfg.defaults.ntp

    #     kernel = cfg.mapping[mac].kernel if "kernel" in cfg.mapping[mac] else cfg.defaults.kernel
    #     initrd = cfg.mapping[mac].initrd if "initrd" in cfg.mapping[mac] else cfg.defaults.initrd
    #     message = cfg.mapping[mac].message if "message" in cfg.mapping[mac] else cfg.defaults.message
    #     cmdline = cfg.mapping[mac].cmdline if "cmdline" in cfg.mapping[mac] else cfg.defaults.cmdline

    #     cmdline += f" talos.config = /v1/cluster/{role}"
    #     if not cfg.mapping[mac].dhcp:
    #         cmdline += f" ip={client_ip}:{server_ip}:{gateway}:{netmask}:{hostname}:{device}:off:{dns}::{ntp}"

    #     ret = {"kernel": kernel, "initrd": initrd, "message": message, "cmdline": cmdline}
    # except Exception as e:
    #     logging.error(f"Error: {e}")
    #     return str(e), 400
    # return ret, 200
