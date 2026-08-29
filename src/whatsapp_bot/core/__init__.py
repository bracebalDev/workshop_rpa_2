"""Módulo central y orquestador del Bot RPA."""

from .bot_controller import WhatsAppBotController
from .browser_manager import BrowserManager

__all__ = ["BrowserManager", "WhatsAppBotController"]
