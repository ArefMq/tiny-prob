from abc import ABC
import json
from dataclasses import dataclass, field, KW_ONLY
from typing import Any, Callable
from threading import Lock


# type of pins:
# - numeric
# - boolean
# - string
# - list[pin]
# - enum
# ~~~~~ Hard Ones ~~~~~
# - np_image
# - drawing canvas (one way from python to web)
# - event (one way from web to python)


@dataclass
class PinBase(ABC):
    name: str
    value: Any | None = None
    html: str | None = None
    topic_html: str | None = None
    _: KW_ONLY
    type: str
    _readable: bool = True
    _writable: bool = True
    _thread_lock: Lock = field(default_factory=Lock)

    def compile_html(self) -> str:
        value_html = self.html
        if value_html is None:
            value_html = f'<input type="text" class="value" value="{self.value}">'
        
        topic_html = self.topic_html
        if topic_html is None:
            topic_html = f'<span class="title">{self.name}</span>'
        
        return {'topic': topic_html, 'value': value_html}

    def to_dict(self) -> str:
        return {
            "name": self.name,
            "value": self.value,
            "type": self.type,
            "html_template": self.compile_html(),
            "readable": self._readable,
            "writable": self._writable,
        }
    
    def write_value(self, value: Any) -> None:
        with self._thread_lock:
            self.value = value
    
    def read_value(self) -> Any:
        with self._thread_lock:
            return self.value


@dataclass
class NumericPin(PinBase):
    type: str = "numeric"
    value: int | float | None = None
    html: str | None = None

    def compile_html(self) -> str:
        res = super().compile_html()
        res["value"] = res["value"].replace("type=\"text\"", "type=\"number\"")
        return res


@dataclass
class BooleanPin(PinBase):
    type: str = "boolean"
    value: bool | None = None
    html: str | None = None

    def compile_html(self) -> str:
        res = super().compile_html()
        res["value"] = res["value"].replace("type=\"text\"", "type=\"checkbox\"")
        return res


@dataclass
class StringPin(PinBase):
    type: str = "string"
    value: str | None = None
    html: str | None = None


@dataclass
class ListPin(PinBase):
    type: str = "list"
    # TODO: investigate list of pins, or potentially dict of pins
    value: list[str] | None = None
    html: str | None = None

    def compile_html(self) -> str:
        res = super().compile_html()
        res["value"] = res["value"].replace("type=\"text\"", "type=\"list\"")
        return res


@dataclass
class EnumPin(PinBase):
    type: str = "enum"
    value: str | None = None
    html: str | None = None

    def compile_html(self) -> str:
        res = super().compile_html()
        res["value"] = res["value"].replace("type=\"text\"", "type=\"enum\"")
        return res

@dataclass
class ImagePin(PinBase):
    type: str = "image"
    value: str | None = None
    html: str | None = None
    _writable: bool = False

    def write_value(self, value: Any) -> None:
        raise NotImplementedError("Image pins can not be written.")

    def compile_html(self) -> str:
        res = super().compile_html()
        res["value"] = res["value"].replace("type=\"text\"", "type=\"image\"")
        return res
    
@dataclass
class EventPin(PinBase):
    type: str = "event"
    callbacks: list[Callable] = field(default_factory=list)
    html: str | None = None
    _readable: bool = False

    def __post_init__(self):
        assert self.value is None, "Event pins can not have a values."

    def compile_html(self) -> str:
        return super().compile_html().replace("type=\"text\"", "type=\"event\"")
    
    def add_callback(self, callback: Callable) -> None:
        self.callbacks.append(callback)
    
    def __iadd__(self, callback: Callable) -> "EventPin":
        self.add_callback(callback)
        return self
    
    def write_value(self, value: Any) -> None:
        for callback in self.callbacks:
            callback(value)
    
    def read_value(self) -> Any:
        raise NotImplementedError("Event pins can not be read.")
    

def Pin4Type(name: str, variable: Any) -> PinBase:
    if isinstance(variable, (int, float)):
        return NumericPin(name, variable)
    if isinstance(variable, bool):
        return BooleanPin(name, variable)
    if isinstance(variable, str):
        return StringPin(name, variable)
    if isinstance(variable, list):
        return ListPin(name, variable)
    raise NotImplementedError(f"Type {type(variable)} not supported.")