from flask import Flask, request, redirect, url_for, jsonify
import logging
import yaml
from .config import cfg

web = Flask(__name__)
logger = logging.getLogger("webapp")


@web.route("/")
def root():
    return redirect(url_for("health"))


@web.route("/health")
def health():
    ret = {"status": "OK"}
    code = 200
    return ret, code


@web.route("/v1/boot/<string:macaddress>")
def bootstrap(macaddress: str):
    rc = 200
    ret = {"kernel": "", "initrd": [""], "message": "", "cmdline": ""}
    ret["cmdline"] += f"ip={client_ip}:{server_ip}:{gateway_ip}:{netmask}:{hostname}:{device}:off:{dns_ip}::{ntp_ip}"
    ret["cmdline"] += f"talos.config={myaddress}/v1/config/"
    return jsonify(ret), rc


@web.route("/v1/config/<string:role>")
def clusterconfig(role: str):
    rc = 200
    return "this is a big config file", rc


@web.route("/defaults")
def defaults():
    return cfg.defaults, 200


@web.route("/mapping")
def mapping():
    return cfg.mapping, 200
