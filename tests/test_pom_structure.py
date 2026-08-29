"""
Pruebas Unitarias para la Estructura e Interfaz del Patrón Page Object Model (POM).
"""

from unittest.mock import MagicMock
from src.whatsapp_bot.patterns.pom.base_page import BasePage
from src.whatsapp_bot.patterns.pom.chat_page import WhatsAppChatPage
from src.whatsapp_bot.patterns.pom.login_page import WhatsAppLoginPage


def test_base_page_delegation():
    """Valida que BasePage delegue operaciones a Playwright Page."""
    mock_page = MagicMock()
    base_page = BasePage(page=mock_page)

    base_page.navigate_to("https://web.whatsapp.com")
    mock_page.goto.assert_called_once_with(
        "https://web.whatsapp.com", wait_until="domcontentloaded", timeout=45000
    )


def test_login_page_detection_mock():
    """Valida la detección de sesión y QR en WhatsAppLoginPage."""
    mock_page = MagicMock()
    mock_context = MagicMock()
    mock_locator = MagicMock()
    mock_locator.wait_for.return_value = None

    mock_page.locator.return_value.first = mock_locator

    login_page = WhatsAppLoginPage(page=mock_page, context=mock_context)
    assert login_page.is_session_active(timeout_ms=1000) is True


def test_chat_page_type_message_mock():
    """Valida el envío de texto multilínea preservando saltos de línea."""
    mock_page = MagicMock()
    mock_composer = MagicMock()
    mock_composer.is_visible.return_value = True

    mock_page.locator.return_value.first = mock_composer

    chat_page = WhatsAppChatPage(page=mock_page)
    multiline_text = "Tarea finalizada.\nPatrones utilizados: Builder, POM, Strategy."
    success = chat_page.type_message(multiline_text)

    assert success is True
    assert mock_page.keyboard.insert_text.call_count == 2
    mock_page.keyboard.down.assert_called_with("Shift")
    mock_page.keyboard.press.assert_called_with("Enter")
    mock_page.keyboard.up.assert_called_with("Shift")
