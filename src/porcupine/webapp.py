import logging
from .config import cfg
from .common import parse_mac
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

# from pydantic import BaseModel

web = FastAPI()
logger = logging.getLogger("webapp")


@web.get("/")
def root():
    return {"health": "ok"}


@web.get("/health")
@web.head("/health")
def health():
    return {"status": "OK"}


@web.get("/v1/boot/{macaddress}")
def bootstrap(macaddress: str):
    ret, _ = parse_mac(macaddress)
    return ret


@web.get("/v1/cluster/{role}", response_class=PlainTextResponse)
def clusterconfig(role: str):
    data = "this is a big config file"
    return data


@web.get("/config")
def get_config():
    m = {k: cfg[k] for k in cfg}
    return m


@web.get("/config/defaults")
def get_defaults():
    return cfg.defaults, 200


@web.get("/config/mapping")
def get_mapping():
    return cfg.mapping, 200


# class Mappings(BaseModel):


@web.post("/config/mapping/{macaddress}")
def set_mapping(macaddress: str):
    pass
    # cfg.mapping[macaddress] = data
    # return "", 201
