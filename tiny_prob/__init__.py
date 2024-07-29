import json
import os
from typing import Any, Callable

from tiny_prob.pins import PinBase
from tiny_prob.webserver import WebServer


TINY_PROB_VERSION = "0.0.1"
TINY_PROB_AUTO_RUN = bool(os.environ.get("TINY_PROB_AUTO_RUN", False))
DEFAULT_BOTTLE_LOCAL_URL = "http://127.0.0.1:8080/"


class TinyProb(WebServer):
    __instance = None

    def __init__(self) -> None:
        super().__init__()
        self.route("/all_pins", callback=self.__all_pins, method="GET")
        self.route("/pin_value", callback=self.__pin_value, method="POST")
        self.route("/logs", callback=self.__logs, method="GET")
        self.__pins: dict[str, PinBase] = {}
        self.__logs: dict[int, tuple[int, str]] = {}  # {timestamp: (level, message)}

    # FIXME - This is not working
    # def __new__(cls) -> "TINY_PROB":
    #     if not cls.__instance:
    #         cls.__instance =
    #     return cls.__instance

    @staticmethod
    def instance() -> "TinyProb":
        if not TinyProb.__instance:
            TinyProb.__instance = TinyProb()
        return TinyProb.__instance

    @staticmethod
    def start(blocking: bool = False, open_browser: bool = False) -> None:
        self = TinyProb.instance()
        if blocking:
            self.run(debug=True)
        else:
            self.run_non_blocking()

        if open_browser:
            TinyProb.OpenBrowser()

    @staticmethod
    def OpenBrowser(url: str = DEFAULT_BOTTLE_LOCAL_URL) -> None:
        import webbrowser

        webbrowser.open(url, new=0, autoraise=True)

    @staticmethod
    def stop(timeout: int | None = None) -> None:
        self = TinyProb.instance()
        self.stop_server(timeout=timeout)

    def __all_pins(self) -> str:
        """
        This function returns all the pins in the system along with their meta attributes.
        """
        return json.dumps([val.to_dict() for val in self.__pins.values()])

    def __pin_value(self) -> str:
        """
        This function is post, and can set/get the value of a pin.
        In the body of the request, the following JSON is expected:
        {
            "write_pins": {"pin_name": "value_to_set", ...},  # Optional
            "read_pins": ["pin_name", ...]  # Optional
        }
        """
        data = json.loads(self.request.body.read().decode())
        res = {}

        if "write_pins" in data:
            for pin_name, value in data["write_pins"].items():
                self.__pins[pin_name].write_value(value)

        if "read_pins" in data:
            res["read_pins"] = {
                pin_name: self.__pins[pin_name].read_value()
                for pin_name in data["read_pins"]
            }

        return json.dumps(res)

    def __logs(self) -> str:
        """
        This function returns all the logs in the system.
        The GET request will have a url parameter (?level=1) to filter logs by level,
        and also a timestamp parameter (?timestamp=1234567890) to get logs after a
        certain timestamp.
        """
        # FIXME: come up with a better implementation of logs
        level = int(self.request.query.get("level", 0))
        timestamp = int(self.request.query.get("timestamp", 0))
        return json.dumps(
            {
                timestamp: log
                for timestamp, log in self.__logs.items()
                if log[0] >= level and timestamp > timestamp
            }
        )

    def add_pin(self, name: str, var: Any) -> tuple[Callable, Callable]:
        """
        Get a variable (name: var) and add it as a pin to the system.
        Return a setter and a getter function for the pin.
        """
        pin = Pin4Type(name, var)
        self.__pins[name] = pin

        def setter(_, value: Any):
            pin.write_value(value)

        def getter(_):
            return pin.read_value()

        return getter, setter

    @staticmethod
    def capture_all(cls):
        attributes = list(vars(cls).items())
        for name, value in attributes:
            if name.startswith("__") or callable(value):
                continue
            try:
                getter, setter = TinyProb.instance().add_pin(name, value)
            except NotImplementedError:
                print(
                    f"[Warning] Variable '{name}' of type '{type(value)}' is not supported for probing."
                )  # FIXME: change this to a log
                continue
            setattr(cls, name, property(getter, setter))

        return cls
