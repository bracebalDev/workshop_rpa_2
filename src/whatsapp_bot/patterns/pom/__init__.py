"""Módulo del Patrón Page Object Model (POM)."""

from .base_page import BasePage
from .chat_page import WhatsAppChatPage
from .login_page import WhatsAppLoginPage

__all__ = ["BasePage", "WhatsAppLoginPage", "WhatsAppChatPage"]
