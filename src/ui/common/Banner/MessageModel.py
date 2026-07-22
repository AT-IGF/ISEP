from dataclasses import dataclass


@dataclass
class MessageModel:
    obj: object
    text: str
    is_visible: bool