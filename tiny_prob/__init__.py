from tiny_prob.pins import EventProb
from .tiny_prob import TinyProb as TinyProbClass
from typing import Any, TypeVar

T = TypeVar("T")
TINY_PROB_VERSION = "0.0.1"


class __TinyProbSingleton:
    __instance = None
    __config = None

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance
    
    @classmethod
    def set_config(cls, **kwargs):
        cls.__config = kwargs

    def __init__(self):
        self.__tiny_prob = TinyProbClass(**self.__config)

    def __getattr__(self, name):
        return getattr(self.__tiny_prob, name)

    def __setattr__(self, name, value):
        if name == "_TinyProbSingleton__tiny_prob":
            super().__setattr__(name, value)
        else:
            setattr(self.__tiny_prob, name, value)

    def __delattr__(self, name):
        if name == "_TinyProbSingleton__tiny_prob":
            super().__delattr__(name)
        else:
            delattr(self.__tiny_prob, name)

    def __enter__(self):
        return self.__tiny_prob.__enter__()
    
    def __exit__(self, exc_type, exc_value, traceback):
        return self.__tiny_prob.__exit__(exc_type, exc_value, traceback)

def SetConfig(**kwargs) -> None:
    """
    Set the configuration for the TinyProb instance.
    Using this function is optional. If not called, the default configuration will be used.
    NOTE: This function should be called before any other TinyProb function is called.

    Args:
        FIXME: fill this
        open_browser=False
        ask_before_exit=True
        static_root
        template_args
        "debug": True,
        "reloader": False,
        "quiet": True,

    Example:
    ```python
    SetConfig(port=8080, host="localhost", open_browser=False)
    ```
    """
    __TinyProbSingleton.set_config(**kwargs)


def TinyProb() -> TinyProbClass:
    """
    Get the TinyProb instance.
    Please note that this function is returning a singleton instance of TinyProb.

    Example:
    ```python

    @capture_all
    class App:
        ...

    With TinyProb() as tp:
        # webserver is running inside the context manager.
        # Any captured values will be available here.
        app = App()
    ```
    """
    return __TinyProbSingleton.get_instance()  # type: ignore


def __capture_variable(cls: T, name: str, value: Any) -> None:
    getter, setter = TinyProb().add_pin(name, value, cls.__name__)
    setattr(cls, name, property(getter, setter))


def capture_all(cls: T) -> T:
    """
    Capture all the variables of a class.
    How? All variables are replaced with a Pin, and then getter/setter functions are added to the 
    class to access the value of the variable. Any variable not supported by the Pin system will be
    ignored.

    Example:
    ```python
    @capture_all
    class App:
        a: int = 10
        b: str = "Hello"
        c: dict = {"a": 1, "b": 2, "c": 3}
        d: SomeClass = SomeClass()  # will be ignored
    ```
    """
    attributes = list(vars(cls).items())
    for name, value in attributes:
        if name.startswith("__") or callable(value):
            continue
        try:
            __capture_variable(cls, name, value)
        except NotImplementedError:
            print(
                f"[Warning] Variable '{name}' of type '{type(value)}' is not supported for probing."
            )  # FIXME: change this to a log
            continue
    return cls


def capture(*args):
    """
    Capture only the variables passed as arguments, and replace them with Pins. Getter/setter will be
    added to the class to access the value of the variable.

    Example:
    ```python
    @capture("a", "b")
    class App:
        a: int = 10
        b: str = "Hello"
        c: dict = {"a": 1, "b": 2, "c": 3}  # will be ignored
    ```
    """
    def decorator(cls: T) -> T:
        for name in args:
            __capture_variable(cls, name, getattr(cls, name))
        return cls

    return decorator


def capture_primitive(cls: T) -> T:
    """
    Capture all the primitive variables of a class. Primitive variables are int, float, str, bool.

    Example:
    ```python
    @capture_primitive
    class App:
        a: int = 10
        b: str = "Hello"
        c: dict = {"a": 1, "b": 2, "c": 3}  # will be ignored
    ```
    """
    for name, value in vars(cls).items():
        if name.startswith("__") or callable(value):
            continue
        if not isinstance(value, (int, float, str, bool)):
            continue
        try:
            __capture_variable(cls, name, value)
        except NotImplementedError:
            pass
    return cls

def listener(func):
    """
    Add a listener to the function. The function will be called whenever the event is triggered.
    """
    # FIXME: this is currently only working for static functions
    ev = TinyProb().add_event_pin(name=func.__name__, namespace=func.__module__ if func.__module__ != "__main__" else None)
    ev += func
    return ev
    