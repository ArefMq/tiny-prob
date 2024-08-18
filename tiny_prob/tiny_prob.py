import json
import logging
from time import time
from typing import Any, Callable

from tiny_prob.pins import EventPin, EventProb, Pin4Type, PinBase
from tiny_prob.webserver import WebServer


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
