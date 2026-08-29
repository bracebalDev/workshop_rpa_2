"""
Pruebas Unitarias para el Orquestador WhatsAppBotController.
"""

from unittest.mock import MagicMock
from src.whatsapp_bot.core.bot_controller import WhatsAppBotController
from src.whatsapp_bot.patterns.builder.bot_config_builder import BotConfigBuilder
from src.whatsapp_bot.patterns.builder.message_builder import WhatsAppMessageBuilder


def test_bot_controller_dry_run_execution():
    """Valida la ejecución del controlador en modo dry-run / simulación."""
    config = (
        BotConfigBuilder()
        .set_dry_run(True)
        .set_target_phone("584121234567")
        .set_delivery_strategy("console_mock")
        .build()
    )

    mock_cred_mgr = MagicMock()
    mock_cred_mgr.ensure_target_phone.return_value = "584121234567"

    controller = WhatsAppBotController(
        config=config,
        credentials_manager=mock_cred_mgr,
    )

    message = WhatsAppMessageBuilder.create_academic_standard_message()
    result = controller.run(custom_message=message)

    assert result is True
