import logging
import yaml
import threading
from supermutes import dot


class Config(object):
    __map: dict()

    def __init__(self) -> None:
        self.__map = dot.dotify({})
        self.lock = threading.Lock()

    def fromFile(self, filename: str) -> bool:
        if filename is None:
            return False
        try:
            with open(filename) as c:
                validyaml = yaml.safe_load(c)
                self.lock.acquire()
                m = dot.dotify(validyaml)
                if m:
                    self.__map = m
                self.lock.release()
        except (ValueError, TypeError, FileNotFoundError) as e:
            logging.error(f"exception {e}")
            return False
        return True

    def toFile(self, filename: str) -> bool:
        if filename is None:
            return False
        try:
            with open(filename) as c:
                self.lock.acquire()
                m = self.__map
                yaml.safe_dump(m, c)
                self.lock.release()
        except (ValueError, TypeError, FileNotFoundError) as e:
            logging.error(f"error {e}")
            return False
        return True

    def __iter__(self):
        for p in self.__map:
            yield p

    def __str__(self) -> str:
        return str(self.__map)

    def __getitem__(self, item):
        if item not in self.__map:
            raise KeyError
        return dot.dotify(self.__map[item])

    def __getattr__(self, item):
        if item in self.__map:
            return self.__map[item]

    def add(self, item, value):
        try:
            self.lock.acquire()
            self.__map[item] = value
        except (ValueError, TypeError) as e:
            logging.error(f"Cannot add {item}={value}:  {e}")
            return False
        finally:
            self.lock.release()


cfg = dot.dotify(Config())
