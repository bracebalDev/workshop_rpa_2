"""
Objeto de Página para Autenticación e Inicio de Sesión en WhatsApp Web.

Patrón: PAGE OBJECT MODEL (POM).
Maneja la verificación del estado de sesión, detección de código QR, espera
del escaneo por parte del usuario y exportación del `storage_state` de Playwright.
"""

from pathlib import Path
from typing import Optional
from playwright.sync_api import BrowserContext, Page

from ...config import (
    MAIN_CHAT_PANE_SELECTORS,
    QR_CONTAINER_SELECTORS,
    QR_SCAN_TIMEOUT_MS,
    WHATSAPP_WEB_BASE_URL,
)
from ...utils.logger import get_bot_logger
from .base_page import BasePage

logger = get_bot_logger()


class WhatsAppLoginPage(BasePage):
    """Encapsula las operaciones y validaciones de la pantalla de inicio y autenticación."""

    def __init__(self, page: Page, context: BrowserContext) -> None:
        super().__init__(page)
        self.context = context

    def open_whatsapp_web(self) -> None:
        """Carga la página principal de WhatsApp Web."""
        logger.info("Accediendo a WhatsApp Web...")
        self.navigate_to(WHATSAPP_WEB_BASE_URL, wait_until="domcontentloaded")

    def is_session_active(self, timeout_ms: int = 15000) -> bool:
        """
        Verifica si el usuario ya cuenta con una sesión activa y cargada.

        :param timeout_ms: Tiempo de espera para detectar el panel de chats.
        :return: True si la sesión está abierta, False en caso contrario.
        """
        logger.info("Verificando si existe una sesión activa...")
        element = self.wait_for_any_selector(MAIN_CHAT_PANE_SELECTORS, timeout_ms=timeout_ms)
        if element:
            logger.info("✓ Sesión activa detectada. Saltando paso de escaneo QR.")
            return True
        return False

    def is_qr_code_displayed(self, timeout_ms: int = 8000) -> bool:
        """
        Verifica si el código QR para vinculación está actualmente visible.

        :param timeout_ms: Tiempo límite de detección.
        :return: True si se visualiza el QR, False de lo contrario.
        """
        element = self.wait_for_any_selector(QR_CONTAINER_SELECTORS, timeout_ms=timeout_ms)
        return element is not None

    def wait_for_authentication(self, timeout_ms: int = QR_SCAN_TIMEOUT_MS) -> bool:
        """
        Espera a que el usuario complete el escaneo del código QR y se cargue el panel principal.

        :param timeout_ms: Tiempo máximo para escanear el QR (default 120 segundos).
        :return: True si el login fue exitoso, False si expiró el tiempo o falló.
        """
        print("\n" + "=" * 60)
        print(" [!] SE REQUIERE ESCANEAR EL CÓDIGO QR EN WHATSAPP WEB")
        print(" Por favor, abra WhatsApp en su teléfono móvil:")
        print(" Ajustes / Dispositivos Vinculados -> Vincular un dispositivo.")
        print(f" Tiempo límite de espera: {timeout_ms // 1000} segundos.")
        print("=" * 60 + "\n")

        logger.info("Esperando inicio de sesión tras escaneo de QR...")
        element = self.wait_for_any_selector(MAIN_CHAT_PANE_SELECTORS, timeout_ms=timeout_ms)

        if element:
            logger.info("✓ Autenticación confirmada exitosamente.")
            self.pause(2000)  # Breve estabilización del DOM tras el login
            return True

        logger.error("✗ Tiempo límite excedido para el escaneo del código QR.")
        self.take_screenshot("login_timeout_error")
        return False

    def save_session_state(self, storage_file_path: Path) -> bool:
        """
        Persiste el estado de almacenamiento (cookies, tokens, local storage) en disco.

        :param storage_file_path: Ruta del archivo JSON donde se guardará el estado.
        :return: True si se guardó exitosamente, False en caso de error.
        """
        try:
            storage_file_path.parent.mkdir(parents=True, exist_ok=True)
            self.context.storage_state(path=str(storage_file_path))
            logger.info(
                "✓ Persistencia de sesión completada. 'storage_state' guardado en: %s",
                storage_file_path,
            )
            return True
        except Exception as error_msg:
            logger.error("Error al guardar el storage_state: %s", error_msg)
            return False
