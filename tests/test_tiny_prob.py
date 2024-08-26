import pytest
from tiny_prob import TinyProb, SetConfig


def test_singleton_instance():
    instance1 = TinyProb()
    instance2 = TinyProb()
    assert instance1 is instance2


def test_config_setter():
    SetConfig(open_browser=True)
    instance = TinyProb()
    assert (
        instance._TinyProbSingleton__tiny_prob._WebServer__open_browser_on_start is True
    )


@pytest.fixture
def tiny_prob():
    tp = TinyProb()
    yield tp
    tp.stop_server()


def test_all_pins(tiny_prob):
    tiny_prob.add_pin("test_pin", 42)
    response = tiny_prob._TinyProb__all_pins()
    assert "test_pin" in response


def test_pin_value_write_read(tiny_prob):
    tiny_prob.add_pin("test_pin", 42)
    tiny_prob._TinyProb__pin_value = {
        "write_pins": {"test_pin": 10},
        "read_pins": ["test_pin"],
    }
    response = tiny_prob._TinyProb__pin_value()
    assert "test_pin" in response
    assert '"10"' in response


def test_append_log(tiny_prob):
    tiny_prob.append_log("Test log")
    logs = tiny_prob._TinyProb__logs
    assert len(logs) > 0
    assert logs[-1][1] == "Test log"


def test_get_log_handler(tiny_prob):
    handler = tiny_prob.get_log_handler()
    assert handler is not None
