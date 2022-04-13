import logging
import threading
from pydantic import FilePath
from typing import List, Dict, Optional
from pydantic_yaml import YamlModel
from . import common

# Models


class BootSection(YamlModel):
    kernel: str
    initrd: List[str]
    message: Optional[str]
    cmdline: Optional[str]


class NetworkSection(YamlModel):
    dhcp: bool
    server: Optional[str]
    gateway: Optional[str]
    netmask: Optional[str]
    dns: Optional[str]
    ntp: Optional[str]
    ip: Optional[str]
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
    template_dir: Optional[FilePath]
    defaults: Defaults
    mapping: Optional[Dict[str, MacEntry]]


class BootResponse(YamlModel):
    kernel: str
    initrd: List[str]
    message: Optional[str]
    cmdline: Optional[str]


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
            with open(filename, "w") as c:
                self.__lock.acquire()
                settings: Settings = self.settings.copy()
                settings.config_file = None
                if settings.external_url == common.get_hostname():
                    settings.external_url = None
                c.write(settings.yaml(exclude_none=True, exclude_unset=True))
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
