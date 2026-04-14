from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class PostResult:
    post_id: str
    url: str
    platform: str

class BasePublisher(ABC):
    name: str = ""

    @abstractmethod
    def post(self, content, topic_slug: str) -> PostResult:
        ...
