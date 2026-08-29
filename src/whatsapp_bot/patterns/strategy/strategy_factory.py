"""
Fábrica de Estrategias de Envío (Strategy Factory).

Permite instanciar dinámicamente la estrategia de entrega adecuada
a partir de su identificador textual o nombre de configuración.
"""

from typing import Dict, List, Type

from .console_mock_strategy import ConsoleMockDeliveryStrategy
from .delivery_strategy import MessageDeliveryStrategy
from .direct_url_strategy import DirectUrlDeliveryStrategy
from .search_chat_strategy import SearchChatDeliveryStrategy


class StrategyFactory:
    """Fábrica para instanciación de estrategias de envío."""

    _registry: Dict[str, Type[MessageDeliveryStrategy]] = {
        "direct_url": DirectUrlDeliveryStrategy,
        "search_chat": SearchChatDeliveryStrategy,
        "console_mock": ConsoleMockDeliveryStrategy,
    }

    @classmethod
    def get_strategy(cls, strategy_name: str) -> MessageDeliveryStrategy:
        """
        Retorna una instancia de la estrategia solicitada.

        :param strategy_name: Nombre de la estrategia ('direct_url', 'search_chat', 'console_mock').
        :return: Instancia de MessageDeliveryStrategy.
        :raises ValueError: Si la estrategia especificada no existe en el registro.
        """
        normalized_name = strategy_name.lower().strip()
        strategy_cls = cls._registry.get(normalized_name)
        if not strategy_cls:
            valid_options = ", ".join(cls._registry.keys())
            raise ValueError(
                f"Estrategia desconocida: '{strategy_name}'. "
                f"Las estrategias disponibles son: {valid_options}"
            )
        return strategy_cls()

    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """Retorna la lista de identificadores de estrategias registradas."""
        return list(cls._registry.keys())
