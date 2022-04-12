import logging
import threading
from pydantic import IPvAnyAddress, IPvAnyNetwork, FilePath
from typing import List, Dict, Optional
from pydantic_yaml import YamlModel

# Models


class BootSection(YamlModel):
    kernel: str
    initrd: List[str]
    message: Optional[str]
    cmdline: Optional[str]


class NetworkSection(YamlModel):
    dhcp: bool
    server: Optional[IPvAnyAddress]
    gateway: Optional[IPvAnyAddress]
    netmask: Optional[IPvAnyNetwork]
    dns: Optional[IPvAnyAddress]
    ntp: Optional[IPvAnyAddress]
    ip: Optional[IPvAnyAddress]
    hostname: Optional[str]
    device: Optional[str]


class Defaults(YamlModel):
    boot: BootSection
    net: NetworkSection
    deny_unknown_clients: bool
    role: str


class MacEntry(YamlModel):
    boot: Optional[BootSection]
    net: Optional[NetworkSection]
    role: Optional[str]


class Settings(YamlModel):
    api_key: Optional[str]
    listen_address: Optional[str]
    listen_port: Optional[int]
    external_url: Optional[str]
    config_file: Optional[FilePath]
    defaults: Defaults
    mapping: Optional[Dict[str, MacEntry]]


# Global config, wraps Settings model


class Config(object):
    settings: Settings
    cache: dict()
    __lock: threading.Lock

    def __init__(self) -> None:
        self.settings: Settings = Settings(
            defaults=Defaults(boot=BootSection(kernel="", initrd=[""]), net=NetworkSection(dhcp=True), deny_unknown_clients=False, role="worker"), mapping={}
        )
        self.cache = dict()
        self.__lock = threading.Lock()

    def fromFile(self, filename: str) -> bool:
        try:
            self.__lock.acquire()
            self.settings = Settings.parse_file(filename, proto="yaml")
        except Exception as e:
            logging.error(f"exception {e}")
            return False
        finally:
            self.__lock.release()
        return True

    def toFile(self, filename: str) -> bool:
        if filename is None:
            return False
        try:
            with open(filename) as c:
                self.__lock.acquire()
                c.write(self.settings.yaml())
        except Exception as e:
            logging.error(f"error {e}")
            return False
        finally:
            self.__lock.release()
        return True

    def __iter__(self):
        yield from self.settings.dict()

    def __str__(self) -> str:
        return self.settings.__str__()

    def __repr__(self) -> str:
        return self.settings.__repr__()


cfg = Config()
