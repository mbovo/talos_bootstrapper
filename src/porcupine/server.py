import asyncio
from asyncio.events import AbstractEventLoop
import threading
import concurrent.futures
import logging
from gevent.pywsgi import WSGIServer

from .webapp import web
from .config import cfg

thread_pool: concurrent.futures.ThreadPoolExecutor
wsgi: WSGIServer
stop_event: threading.Event


def run():
    global thread_pool, stop_event
    logging.info("Starting threads")

    functions = [webapp_run]

    stop_event = threading.Event()
    thread_pool = concurrent.futures.ThreadPoolExecutor()
    future_tasks = {thread_pool.submit(fn): fn for fn in functions}

    for future in concurrent.futures.as_completed(future_tasks):
        future.result()


def stop():
    global thread_pool, stop_event
    logging.info("signalling threads to stop")
    stop_event.set()
    wsgi.stop()
    thread_pool.shutdown(wait=False, cancel_futures=True)


def webapp_run():
    """Run WEB Listener in this thread"""
    global wsgi
    try:
        log = logging.getLogger("webapp")
        wsgi = WSGIServer((cfg.listen_address, int(cfg.listen_port)), web, log=log)
        wsgi.serve_forever()
    except Exception as e:
        logging.error(f"Cannot start web server: {e}")
