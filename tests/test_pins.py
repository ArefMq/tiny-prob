import pytest
from tiny_prob.pins import NumericPin, BooleanPin, StringPin, EventPin


@pytest.fixture
def numeric_pin():
    return NumericPin(name="test_numeric", namespace="test_ns", value=10)


@pytest.fixture
def boolean_pin():
    return BooleanPin(name="test_boolean", namespace="test_ns", value=True)


@pytest.fixture
def string_pin():
    return StringPin(name="test_string", namespace="test_ns", value="Hello")


def test_numeric_pin(numeric_pin):
    assert numeric_pin.read_value() == 10
    numeric_pin.write_value(20)
    assert numeric_pin.read_value() == 20


def test_boolean_pin(boolean_pin):
    assert boolean_pin.read_value() is True
    boolean_pin.write_value(False)
    assert boolean_pin.read_value() is False


def test_string_pin(string_pin):
    assert string_pin.read_value() == "Hello"
    string_pin.write_value("World")
    assert string_pin.read_value() == "World"


def test_event_pin():
    pin = EventPin(name="test_event", namespace="test_ns")
    assert pin.type == "event"
    assert not pin._readable
    assert not pin._writable
