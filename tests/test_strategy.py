"""
Pruebas Unitarias para el Patrón Strategy y StrategyFactory.
"""

import pytest
from src.whatsapp_bot.patterns.strategy.console_mock_strategy import ConsoleMockDeliveryStrategy
from src.whatsapp_bot.patterns.strategy.delivery_strategy import DeliveryContext
from src.whatsapp_bot.patterns.strategy.direct_url_strategy import DirectUrlDeliveryStrategy
from src.whatsapp_bot.patterns.strategy.search_chat_strategy import SearchChatDeliveryStrategy
from src.whatsapp_bot.patterns.strategy.strategy_factory import StrategyFactory


def test_strategy_factory_instantiation():
    """Valida que la fábrica instancie las estrategias correctas."""
    strategy_direct = StrategyFactory.get_strategy("direct_url")
    assert isinstance(strategy_direct, DirectUrlDeliveryStrategy)
    assert strategy_direct.strategy_name == "direct_url"

    strategy_search = StrategyFactory.get_strategy("search_chat")
    assert isinstance(strategy_search, SearchChatDeliveryStrategy)
    assert strategy_search.strategy_name == "search_chat"

    strategy_mock = StrategyFactory.get_strategy("console_mock")
    assert isinstance(strategy_mock, ConsoleMockDeliveryStrategy)
    assert strategy_mock.strategy_name == "console_mock"


def test_strategy_factory_invalid_name():
    """Valida que una estrategia no registrada genere ValueError con sugerencias."""
    with pytest.raises(ValueError) as excinfo:
        StrategyFactory.get_strategy("estrategia_inexistente")
    assert "Estrategia desconocida" in str(excinfo.value)


def test_delivery_context_execution_and_switching():
    """Valida el patrón Strategy y el cambio dinámico de algoritmo en tiempo de ejecución."""
    mock_strategy = ConsoleMockDeliveryStrategy()
    context = DeliveryContext(strategy=mock_strategy)

    result = context.execute_delivery(
        chat_page=None,
        recipient_phone="584121234567",
        message_content="Tarea finalizada.",
    )
    assert result is True

    # Cambiar de estrategia dinámicamente
    new_strategy = DirectUrlDeliveryStrategy()
    context.strategy = new_strategy
    assert context.strategy.strategy_name == "direct_url"
