from dataclasses import dataclass


@dataclass
class DirectMessageSubject:
    guild: str
    channel: str
