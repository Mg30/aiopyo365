import aiohttp
import aiopyo365.config as config
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class AbstractFactory(ABC):
    """Abstract Factotry that provide guidelines
    to DriveItemsFactories implementation class.
    """

    _base_url: str = field(init=False, default=config.BASE_GRAPH_API_V1_URL)

    @abstractmethod
    def create(self, session: aiohttp.ClientSession):
        raise NotImplementedError
