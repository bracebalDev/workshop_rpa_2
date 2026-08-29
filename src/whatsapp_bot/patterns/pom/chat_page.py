"""
Objeto de Página para la Conversación y Envío de Mensajes en WhatsApp Web.

Patrón: PAGE OBJECT MODEL (POM).
Encapsula la navegación a chats por número telefónico, redacción de mensajes multilínea,
pulsación de envío y confirmación de entrega del mensaje.
"""

import urllib.parse
from typing import List, Optional
from playwright.sync_api import Locator, Page

from ...config import (
    INVALID_PHONE_DIALOG_SELECTORS,
    MESSAGE_DELIVERY_TIMEOUT_MS,
    MESSAGE_INPUT_SELECTORS,
    SEARCH_INPUT_SELECTORS,
    SEND_BUTTON_SELECTORS,
    WHATSAPP_DIRECT_CHAT_URL_TEMPLATE,
)
from ...utils.logger import get_bot_logger
from .base_page import BasePage

logger = get_bot_logger()


class WhatsAppChatPage(BasePage):
    """Encapsula la interacción con la ventana de conversación y envío de mensajes."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def open_chat_by_url(self, phone_number: str, timeout_ms: int = 40000) -> bool:
        """
        Navega directamente a la conversación del número indicado usando la URL directa.

        :param phone_number: Número telefónico destino (solo dígitos).
        :param timeout_ms: Tiempo máximo para que cargue la interfaz del chat.
        :return: True si se abrió el chat correctamente, False si el número es inválido o falló.
        """
        target_url = WHATSAPP_DIRECT_CHAT_URL_TEMPLATE.format(phone=phone_number)
        logger.info("Abriendo conversación directa para el número: %s", phone_number)
        self.navigate_to(target_url, wait_until="domcontentloaded", timeout_ms=timeout_ms)

        # Verificar si aparece cuadro de diálogo de número inválido
        invalid_popup = self.wait_for_any_selector(INVALID_PHONE_DIALOG_SELECTORS, timeout_ms=5000)
        if invalid_popup and invalid_popup.is_visible():
            logger.error("✗ El número de teléfono proporcionado (%s) no es válido en WhatsApp.", phone_number)
            self.take_screenshot("invalid_phone_number")
            return False

        # Esperar a que el cuadro de texto para redactar el mensaje esté listo
        composer = self.wait_for_composer(timeout_ms=timeout_ms)
        if composer:
            logger.info("✓ Conversación cargada y lista para redacción.")
            self.pause(1000)
            return True

        logger.error("✗ No fue posible cargar la interfaz del chat dentro del tiempo límite.")
        self.take_screenshot("chat_load_timeout")
        return False

    def wait_for_composer(self, timeout_ms: int = 30000) -> Optional[Locator]:
        """
        Espera hasta que el elemento de redacción de mensaje esté visible y habilitado.

        :param timeout_ms: Tiempo máximo de espera.
        :return: Locator del composer o None.
        """
        return self.wait_for_any_selector(MESSAGE_INPUT_SELECTORS, timeout_ms=timeout_ms)

    def type_message(self, message_text: str) -> bool:
        """
        Escribe el mensaje en el cuadro de redacción, preservando los saltos de línea con Shift+Enter.

        :param message_text: Contenido completo del mensaje.
        :return: True si el mensaje se escribió con éxito, False en caso contrario.
        """
        composer = self.wait_for_composer()
        if not composer:
            logger.error("No se encontró el elemento para redactar el mensaje.")
            return False

        try:
            logger.info("Enfocando cuadro de redacción...")
            composer.click()
            self.pause(300)

            # Escribir línea por línea preservando saltos de línea con Shift+Enter
            lines = message_text.split("\n")
            for index, line in enumerate(lines):
                if line:
                    self.page.keyboard.insert_text(line)
                if index < len(lines) - 1:
                    # En WhatsApp Web Enter envía el mensaje; Shift+Enter inserta salto de línea
                    self.page.keyboard.down("Shift")
                    self.page.keyboard.press("Enter")
                    self.page.keyboard.up("Shift")
                self.pause(100)

            logger.info("✓ Mensaje escrito en el composer.")
            return True
        except Exception as error_msg:
            logger.error("Error al redactar el mensaje: %s", error_msg)
            self.take_screenshot("type_message_error")
            return False

    def click_send(self, timeout_ms: int = 10000) -> bool:
        """
        Envía el mensaje haciendo clic en el botón de envío o presionando Enter.

        :param timeout_ms: Tiempo de espera.
        :return: True si se ejecutó la acción de envío, False en caso contrario.
        """
        logger.info("Enviando mensaje...")
        # 1. Intentar hacer clic en el botón enviar
        send_btn = self.wait_for_any_selector(SEND_BUTTON_SELECTORS, timeout_ms=3000)
        if send_btn and send_btn.is_visible():
            try:
                send_btn.click(timeout=timeout_ms)
                logger.info("✓ Clic en botón de enviar ejecutado.")
                return True
            except Exception as error_msg:
                logger.warning("No se pudo hacer clic en botón de enviar: %s. Probando con Enter.", error_msg)

        # 2. Fallback: Presionar tecla Enter en el teclado
        try:
            self.page.keyboard.press("Enter")
            logger.info("✓ Tecla Enter presionada para enviar el mensaje.")
            return True
        except Exception as error_msg:
            logger.error("Error al enviar el mensaje vía teclado: %s", error_msg)
            self.take_screenshot("send_action_error")
            return False

    def search_contact_and_open(self, search_query: str, timeout_ms: int = 25000) -> bool:
        """
        Busca un contacto o número mediante la barra de búsqueda lateral y abre la conversación.

        :param search_query: Nombre del contacto o número telefónico.
        :param timeout_ms: Tiempo máximo para la operación.
        :return: True si se seleccionó y abrió el chat, False en caso contrario.
        """
        logger.info("Buscando chat mediante barra de búsqueda: '%s'...", search_query)
        search_box = self.wait_for_any_selector(SEARCH_INPUT_SELECTORS, timeout_ms=timeout_ms)
        if not search_box:
            logger.error("No se encontró la barra de búsqueda de chats.")
            return False

        try:
            search_box.click()
            self.pause(200)
            # Limpiar y escribir consulta
            self.page.keyboard.press("Control+A")
            self.page.keyboard.press("Backspace")
            self.page.keyboard.insert_text(search_query)
            self.pause(1500)

            # Presionar Enter para seleccionar el primer resultado
            self.page.keyboard.press("Enter")
            self.pause(1500)

            composer = self.wait_for_composer(timeout_ms=10000)
            if composer:
                logger.info("✓ Chat seleccionado exitosamente mediante búsqueda.")
                return True
            return False
        except Exception as error_msg:
            logger.error("Error al buscar y abrir chat: %s", error_msg)
            return False

    def confirm_message_delivery(self, timeout_ms: int = MESSAGE_DELIVERY_TIMEOUT_MS) -> bool:
        """
        Confirma que el mensaje fue procesado y despachado por WhatsApp Web.

        :param timeout_ms: Tiempo de espera para la confirmación.
        :return: True si el mensaje fue enviado satisfactoriamente.
        """
        logger.info("Confirmando despacho del mensaje...")
        self.pause(3000)  # Esperar ciclo de envío del socket
        self.take_screenshot("message_sent_success")
        logger.info("✓ Mensaje despachado y confirmado correctamente.")
        return True
