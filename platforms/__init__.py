from typing import Dict, Type
from marketing_bot.platforms.base import BasePublisher

PLATFORM_REGISTRY: Dict[str, Type[BasePublisher]] = {}

def register(cls: Type[BasePublisher]) -> Type[BasePublisher]:
    if not cls.name:
        raise ValueError(f"{cls.__name__} must set .name")
    PLATFORM_REGISTRY[cls.name] = cls
    return cls
