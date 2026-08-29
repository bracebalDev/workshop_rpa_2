"""
Estrategia Concreta de Envío: Enlace Directo (Direct URL Strategy).

Navega directamente a la API Web de WhatsApp mediante el parámetro `phone`,
abrindo de forma directa e inequívoca el chat del destinatario sin depender
del historial de contactos.
"""

from typing import TYPE_CHECKING, Optional

from ...utils.logger import get_bot_logger
from .delivery_strategy import MessageDeliveryStrategy

if TYPE_CHECKING:
    from ..pom.chat_page import WhatsAppChatPage

logger = get_bot_logger()


class DirectUrlDeliveryStrategy(MessageDeliveryStrategy):
    """Estrategia que utiliza la URL de redirección directa de WhatsApp Web."""

    @property
    def strategy_name(self) -> str:
        return "direct_url"

    @property
    def description(self) -> str:
        return "Navegación directa al chat mediante https://web.whatsapp.com/send?phone=<numero>."

    def deliver_message(
        self,
        chat_page: Optional["WhatsAppChatPage"],
        recipient_phone: str,
        message_content: str,
    ) -> bool:
        """
        Ejecuta el flujo de envío navegando a la URL directa.

        :param chat_page: Instancia de WhatsAppChatPage (POM).
        :param recipient_phone: Teléfono sanitizado.
        :param message_content: Contenido del mensaje.
        :return: True si se envió correctamente.
        """
        if not chat_page:
            logger.error("No se proporcionó una instancia válida de WhatsAppChatPage.")
            return False

        logger.info("[Estrategia: Direct URL] Iniciando proceso de envío a: %s", recipient_phone)

        # 1. Abrir chat por URL
        if not chat_page.open_chat_by_url(recipient_phone):
            logger.error("[Estrategia: Direct URL] Fallo al abrir la conversación por URL.")
            return False

        # 2. Redactar el mensaje
        if not chat_page.type_message(message_content):
            logger.error("[Estrategia: Direct URL] Fallo al redactar el mensaje en el composer.")
            return False

        # 3. Hacer clic en enviar
        if not chat_page.click_send():
            logger.error("[Estrategia: Direct URL] Fallo al accionar el botón de envío.")
            return False

        # 4. Confirmar despacho
        return chat_page.confirm_message_delivery()
