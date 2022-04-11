import logging
import yaml
import json
from pydantic import BaseModel, BaseSettings, IPvAnyAddress, IPvAnyNetwork, FilePath
from typing import List, Dict, Optional

# class Config(object):
#     __map: dict()

#     def __init__(self) -> None:
#         self.__map
#         self.lock = threading.Lock()

#     def fromFile(self, filename: str) -> bool:
#         if filename is None:
#             return False
#         try:
#             with open(filename) as c:
#                 validyaml = yaml.safe_load(c)
#                 self.lock.acquire()
#                 self.__map = validyaml
#                 self.lock.release()
#         except (ValueError, TypeError, FileNotFoundError) as e:
#             logging.error(f"exception {e}")
#             return False
#         return True

#     def toFile(self, filename: str) -> bool:
#         if filename is None:
#             return False
#         try:
#             with open(filename) as c:
#                 self.lock.acquire()
#                 m = self.__map
#                 yaml.safe_dump(m, c)
#                 self.lock.release()
#         except (ValueError, TypeError, FileNotFoundError) as e:
#             logging.error(f"error {e}")
#             return False
#         return True

#     def __iter__(self):
#         for p in self.__map:
#             yield p

#     def __str__(self) -> str:
#         return str(self.__map)

#     def __getitem__(self, item):
#         if item not in self.__map:
#             raise KeyError
#         return dot.dotify(self.__map[item])

#     def __getattr__(self, item):
#         if item in self.__map:
#             return self.__map[item]

#     def add(self, item, value):
#         try:
#             self.lock.acquire()
#             self.__map[item] = value
#         except (ValueError, TypeError) as e:
#             logging.error(f"Cannot add {item}={value}:  {e}")
#             return False
#         finally:
#             self.lock.release()


class Defaults(BaseModel):
    kernel: str = ...
    initrd: List[str] = ...
    message: Optional[str]
    cmdline: Optional[str]
    server: Optional[IPvAnyAddress]
    gateway: Optional[IPvAnyAddress]
    netmask: Optional[IPvAnyNetwork]
    dns: Optional[IPvAnyAddress]
    ntp: Optional[IPvAnyAddress]


class MacEntry(BaseModel):
    dhcp: bool
    ip: Optional[IPvAnyAddress]
    hostname: Optional[str]
    device: Optional[str]
    role: Optional[str]


class Settings(BaseSettings):
    api_key: Optional[str]
    listen_address: Optional[str]
    listen_port: Optional[int]
    config_file: Optional[FilePath]
    defaults: Defaults
    mapping: Optional[Dict[str, MacEntry]]

    class Config:
        env_prefix = "porcupine_"


def fromFile(filename: str) -> bool:
    if filename is None:
        return False
    try:
        with open(filename) as c:
            v = yaml.safe_load(c)
            j = json.dumps(v)
            cfg.parse_raw(j)
    except Exception as e:
        logging.error(f"exception {e}")
        return False
    return True


cfg = Settings(defaults=Defaults(kernel="", initrd=[""]), mapping={})  # Config(defaults=Defaults(kernel="",initrd=[""]))
