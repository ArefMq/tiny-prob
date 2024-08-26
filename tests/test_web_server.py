import time
import pytest
from threading import Thread
from bottle import HTTPResponse
from tiny_prob.webserver import WebServer


@pytest.fixture
def webserver():
    server = WebServer()
    yield server
    server.stop_server()


def test_static_route(webserver):
    response = webserver.static("logo.png")
    assert isinstance(response, HTTPResponse)
    assert response.status_code == 200


def test_index_route(webserver):
    response = webserver.index()
    assert isinstance(response, str)
    assert "<title>TinyProb</title>" in response


def test_run_non_blocking(webserver):
    webserver.run_non_blocking(
        host="localhost",
        port=8081,
        quiet=True,
        open_browser=False,
    )
    assert isinstance(webserver._WebServer__app_thread, Thread)
    webserver.stop_server()


def test_start_stop_server(webserver):
    webserver.start(blocking=False)
    assert webserver._WebServer__server is not None
    time.sleep(1)
    webserver.stop_server()
    assert webserver._WebServer__app_thread is None
