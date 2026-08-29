"""
Estrategia Concreta de Envío: Búsqueda en Lista de Chats (Search Chat Strategy).

Utiliza el cuadro de búsqueda lateral de WhatsApp Web para localizar un contacto
o conversación existente antes de proceder a la redacción y despacho del mensaje.
"""

from typing import TYPE_CHECKING, Optional

from ...utils.logger import get_bot_logger
from .delivery_strategy import MessageDeliveryStrategy

if TYPE_CHECKING:
    from ..pom.chat_page import WhatsAppChatPage

logger = get_bot_logger()


class SearchChatDeliveryStrategy(MessageDeliveryStrategy):
    """Estrategia que busca el chat destinatario en la barra de búsqueda de WhatsApp Web."""

    @property
    def strategy_name(self) -> str:
        return "search_chat"

    @property
    def description(self) -> str:
        return "Búsqueda interactiva del contacto en la barra de búsqueda lateral de chats."

    def deliver_message(
        self,
        chat_page: Optional["WhatsAppChatPage"],
        recipient_phone: str,
        message_content: str,
    ) -> bool:
        """
        Ejecuta el flujo de envío buscando el chat en la interfaz.

        :param chat_page: Instancia de WhatsAppChatPage (POM).
        :param recipient_phone: Teléfono o nombre del contacto.
        :param message_content: Contenido del mensaje.
        :return: True si se envió correctamente.
        """
        if not chat_page:
            logger.error("No se proporcionó una instancia válida de WhatsAppChatPage.")
            return False

        logger.info("[Estrategia: Search Chat] Buscando contacto '%s'...", recipient_phone)

        # 1. Buscar y abrir chat
        if not chat_page.search_contact_and_open(recipient_phone):
            logger.error("[Estrategia: Search Chat] No se pudo encontrar o abrir el chat.")
            return False

        # 2. Redactar el mensaje
        if not chat_page.type_message(message_content):
            logger.error("[Estrategia: Search Chat] Fallo al redactar el mensaje en el composer.")
            return False

        # 3. Hacer clic en enviar
        if not chat_page.click_send():
            logger.error("[Estrategia: Search Chat] Fallo al presionar el botón de envío.")
            return False

        # 4. Confirmar despacho
        return chat_page.confirm_message_delivery()
