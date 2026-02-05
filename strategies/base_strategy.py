from abc import ABC, abstractmethod
from typing import Optional


class BaseStrategy(ABC):
    def __init__(self, config: dict):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.priority = config.get('priority', 999)

    @abstractmethod
    def generate_prompt(self) -> Optional[str]:
        pass

    def is_enabled(self) -> bool:
        return self.enabled
