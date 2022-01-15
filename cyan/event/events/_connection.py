from typing import Any
from cyan.event import Event, EventType, Intent


class ReadyEvent(Event):
    @staticmethod
    def get_event_type():
        return EventType("READY", Intent.DEFAULT)

    def _parse_data(self, data: Any) -> Any:
        return ReadyEventData(data)


class ReadyEventData:
    _props: dict[str, Any]

    def __init__(self, props: dict[str, Any]):
        self._props = props

    @property
    def session(self) -> str:
        return self._props["session_id"]
