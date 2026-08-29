"""
Pruebas Unitarias para el Builder de Configuración del Bot.
"""

from pathlib import Path
from src.whatsapp_bot.patterns.builder.bot_config_builder import BotConfigBuilder


def test_default_bot_configuration():
    """Valida los valores por defecto del builder de configuración."""
    config = BotConfigBuilder().build()
    assert config.headless is False
    assert config.slow_mo_ms > 0
    assert config.delivery_strategy == "direct_url"
    assert config.dry_run is False


def test_custom_bot_configuration():
    """Valida la personalización completa de la configuración del bot."""
    custom_path = Path("custom/sessions/state.json")
    config = (
        BotConfigBuilder()
        .set_headless(True)
        .set_slow_mo(250)
        .set_session_file(custom_path)
        .set_timeout(10000)
        .set_qr_timeout(60000)
        .set_target_phone("584121234567")
        .set_delivery_strategy("search_chat")
        .set_dry_run(True)
        .build()
    )

    assert config.headless is True
    assert config.slow_mo_ms == 250
    assert config.session_file == custom_path
    assert config.timeout_ms == 10000
    assert config.qr_timeout_ms == 60000
    assert config.target_phone == "584121234567"
    assert config.delivery_strategy == "search_chat"
    assert config.dry_run is True
