from flask import Flask, redirect, jsonify, request
from flasgger import Swagger
import logging
from .config import cfg
from .common import parse_mac

web = Flask(__name__)
swagger = Swagger(web)
logger = logging.getLogger("webapp")


@web.route("/")
def root():
    return redirect("/apidocs")


@web.route("/health")
def health():
    """Health endpoint returns 200 if the server is ready to go
    ---
    parameters: {}
    responses:
      200:
        description: A json with the current server status
    """
    ret = {"status": "OK"}
    code = 200
    return ret, code


@web.route("/v1/boot/<string:macaddress>")
def bootstrap(macaddress: str):
    """Bootstrap a node, given a macaddress it returns an object with all information to boot
    ---
    parameters:
      - name: macaddress
        in: path
        type: string
        required: true
    responses:
      200:
        description: Return the info needed to boot
        examples:
          kernel: file:///path/to/kernelfile
          initrd: [file:///path/to/initerd]
          message: Boot message
          cmdline: linux kernel parameters
      400:
        description: Block pxe booting process
    """
    ret, rc = parse_mac(macaddress)
    return jsonify(ret), rc


@web.route("/v1/cluster/<string:role>")
def clusterconfig(role: str):
    """Return the Talos configuration file used to setup a node
    ---
    parameters:
      - name: role
        in: path
        type: string
        required: true
    responses:
      200:
        description: The configuration file
      400:
        description: When role is unknown
    """
    rc = 200
    return "this is a big config file", rc


@web.route("/config")
def get_config():
    """Returns current configuration
    ---
    responses:
      200:
        description: Return the json with current configuration
    """
    m = {k: cfg[k] for k in cfg}
    return m, 200


@web.route("/config/defaults")
def get_defaults():
    """Returns current defaults
    ---
    responses:
      200:
        description: Return the json with current defaults
    """
    return cfg.defaults, 200


@web.route("/config/mapping/", methods=["GET"])
def get_mapping():
    """Returns current mapping mac-address / configuration
    ---
    responses:
      200:
        description: Return the json with current mappings
    """
    return cfg.mapping, 200


@web.route("/config/mapping/<string:macaddress>", methods=["POST"])
def set_mapping(macaddress: str):
    """Add/edit mapping mac-address / configuration
    ---
    responses:
      201:
        description: Configuration saved
      400:
        description: Configuration given is invalid
    """
    data = request.json
    cfg.mapping[macaddress] = data
    return "", 201
