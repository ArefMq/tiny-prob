import json
import logging
import os
from time import time
from typing import Any, Callable, TypeVar

from tiny_prob.pins import EventPin, EventProb, Pin4Type, PinBase
from tiny_prob.webserver import WebServer


TINY_PROB_VERSION = "0.0.1"
TINY_PROB_AUTO_RUN = bool(os.environ.get("TINY_PROB_AUTO_RUN", False))


T = TypeVar("T")


class TinyProb(WebServer):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.route("/all_pins", callback=self.__all_pins, method="GET")
        self.route("/pin_value", callback=self.__pin_value, method="POST")
        self.route("/logs", callback=self.__read_logs, method="GET")
        # self.route("/__internal", callback=self.__internal_comm, method="POST")
        self.__pins: dict[str, PinBase] = {}
        self.__logs: list[tuple[float, str]] = []  # [(timestamp, message)}, ...]

    def __all_pins(self) -> str:
        """
        This function returns all the pins in the system along with their meta attributes.
        """
        return json.dumps([val.to_dict() for val in self.__pins.values()])

    def __pin_value(self) -> str:
        """
        Controls the Values of the Pins, both reading and writing.
        This function is called via Post request. In the body of the request,
        the following JSON is expected:
        {
            "write_pins": {"pin_name": "value_to_set", ...},  # Optional
            "read_pins": ["pin_name", ...]  # Optional
        }
        """
        write_pins = self._post_param("write_pins", None)
        read_pins = self._post_param("read_pins", None)
        assert isinstance(write_pins, dict) or write_pins is None, "write_pins must be a dict"+repr(write_pins)
        assert isinstance(read_pins, list) or read_pins is None, "read_pins must be a list"+repr(read_pins)
        res = {}

        print("write_pins:: ", repr(write_pins))
        print("read_pins:: ", repr(read_pins))

        if write_pins is not None:
            for pin_name, value in write_pins.items():
                self.__pins[pin_name].write_value(value)

        if read_pins is not None:
            res["read_pins"] = {
                pin_name: self.__pins[pin_name].read_value() for pin_name in read_pins
            }

        print("res:: ", repr(res))
        return json.dumps(res)

    def __read_logs(self) -> str:
        """
        This function returns all the logs in the system.
        The GET request will have a timestamp parameter (?timestamp=1234567890)
        to get logs after a certain timestamp.
        """
        # FIXME: come up with a better implementation of logs
        timestamp = int(self._get_param("timestamp", 0))
        return json.dumps(
            [{"timestamp": t, "message": m} for t, m in self.__logs if t >= timestamp]
        )

    def append_log(self, message: str, timestamp: float | None = None) -> None:
        """
        Append a log to the system.

        Args:
            message (str): The message to log.
            timestamp (int, optional): The timestamp of the log. Defaults to Now.
        """
        if timestamp is None:
            timestamp = time()
        self.__logs.append((timestamp, message))

    def get_log_handler(self) -> logging.StreamHandler:
        """
        Get a log handler that can be used to append logs to the system.
        """

        class Stream:
            def write(_, message):
                self.append_log(message)
        
        class CustomStreamHandler(logging.StreamHandler):
            terminator = ""

        return CustomStreamHandler(Stream())

    def add_pin(
        self, name: str, var: Any, namespace: str = ""
    ) -> tuple[Callable, Callable]:
        """
        Get a variable (name: var) and add it as a pin to the system.
        Return a setter and a getter function for the pin.
        """
        pin = Pin4Type(name, namespace, var)
        self.__pins[name] = pin

        def setter(_=None, value: Any=None):
            pin.write_value(value)

        def getter(_=None):
            return pin.read_value()

        return getter, setter

    def add_event_pin(self, name: str, namespace: str = "") -> EventPin:
        pin = EventPin(name, namespace=namespace)
        self.__pins[name] = pin
        return pin
    
    def add_debug_prob(self, name: str, namespace: str = "") -> EventProb:
        return EventProb(self.add_event_pin(name, namespace))

    @staticmethod
    def __capture_variable(cls: T, name: str, value: Any) -> None:
        """
        Capture a variable (name: value) of a class (cls) and add it as a pin.
        """
        getter, setter = TinyProb.instance().add_pin(name, value, cls.__name__)
        setattr(cls, name, property(getter, setter))

    @staticmethod
    def capture_all(cls: T) -> T:
        attributes = list(vars(cls).items())
        for name, value in attributes:
            if name.startswith("__") or callable(value):
                continue
            try:
                TinyProb.__capture_variable(cls, name, value)
            except NotImplementedError:
                print(
                    f"[Warning] Variable '{name}' of type '{type(value)}' is not supported for probing."
                )  # FIXME: change this to a log
                continue
        return cls

    @staticmethod
    def capture(*args):
        def decorator(cls: T) -> T:
            for name in args:
                TinyProb.__capture_variable(cls, name, getattr(cls, name))
            return cls

        return decorator

    @staticmethod
    def capture_primitive(cls: T) -> T:
        for name, value in vars(cls).items():
            if name.startswith("__") or callable(value):
                continue
            if not isinstance(value, (int, float, str, bool)):
                continue
            try:
                TinyProb.__capture_variable(cls, name, value)
            except NotImplementedError:
                pass
        return cls

    @staticmethod
    def StaticProb(name: str) -> EventProb:
        return TinyProb.instance().add_event_pin(name)
