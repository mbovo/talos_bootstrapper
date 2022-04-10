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
