"""Módulo del Patrón Strategy."""

from .console_mock_strategy import ConsoleMockDeliveryStrategy
from .delivery_strategy import DeliveryContext, MessageDeliveryStrategy
from .direct_url_strategy import DirectUrlDeliveryStrategy
from .search_chat_strategy import SearchChatDeliveryStrategy
from .strategy_factory import StrategyFactory

__all__ = [
    "MessageDeliveryStrategy",
    "DeliveryContext",
    "DirectUrlDeliveryStrategy",
    "SearchChatDeliveryStrategy",
    "ConsoleMockDeliveryStrategy",
    "StrategyFactory",
]
