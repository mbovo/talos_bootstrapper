import logging
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from .config import cfg, MacEntry, Defaults, Settings
from .logic import parse_mac

app = FastAPI()
logger = logging.getLogger("webapp")


@app.get("/")
def root():
    return {"health": "ok"}


@app.get("/health")
@app.head("/health")
def health():
    return {"status": "OK"}


@app.get("/v1/boot/{macaddress}")
def bootstrap(macaddress: str):
    try:
        return parse_mac(macaddress)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/v1/cluster/{role}", response_class=PlainTextResponse)
def clusterconfig(role: str):
    data = "this is a big config file"
    return data


@app.get("/config", response_model=Settings)
def get_config(apikey: str):
    if apikey != cfg.settings.api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return cfg.settings


@app.get("/config/defaults", response_model=Defaults)
def get_defaults():
    return cfg.settings.defaults


@app.get("/config/mapping", response_model=Optional[Dict[str, MacEntry]])
def get_mapping():
    return cfg.settings.mapping


@app.post("/config/mapping/{macaddress}")
def set_mapping(macaddress: str, apikey: str, mapping: MacEntry):
    if apikey != cfg.settings.api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")

    cfg.settings.mapping[macaddress] = mapping

    return cfg.settings.mapping[macaddress]
