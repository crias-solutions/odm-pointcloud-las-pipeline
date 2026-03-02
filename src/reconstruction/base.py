import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ReconstructionStrategy(ABC):
    @abstractmethod
    def run(self, dataset_path: str) -> None:
        pass
