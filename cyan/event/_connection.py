from typing import Any, Dict

from cyan.event import Event, EventInfo, Intent


class ReadyEventData:
    _props: Dict[str, Any]

    def __init__(self, props: Dict[str, Any]) -> None:
        self._props = props

    @property
    def session(self) -> str:
        return self._props["session_id"]


class ReadyEvent(Event):
    @staticmethod
    def get_event_info() -> EventInfo:
        return EventInfo("READY", Intent.DEFAULT)

    async def _parse_data(self, data: Any) -> ReadyEventData:
        return ReadyEventData(data)
