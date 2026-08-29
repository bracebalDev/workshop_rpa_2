"""
Estrategia Concreta de Envío: Simulación / Pruebas (Console Mock Strategy).

Simula el despacho del mensaje imprimiéndolo en consola y validando la lógica
de negocio sin interactuar con un navegador real ni con los servidores de WhatsApp.
Ideal para pruebas unitarias, testing de integración y demostraciones académicas.
"""

from typing import TYPE_CHECKING, Optional

from ...utils.logger import get_bot_logger
from .delivery_strategy import MessageDeliveryStrategy

if TYPE_CHECKING:
    from ..pom.chat_page import WhatsAppChatPage

logger = get_bot_logger()


class ConsoleMockDeliveryStrategy(MessageDeliveryStrategy):
    """Estrategia de simulación para pruebas académicas y validación de arquitectura."""

    @property
    def strategy_name(self) -> str:
        return "console_mock"

    @property
    def description(self) -> str:
        return "Simulación en consola para pruebas sin apertura de navegador ni conexión web."

    def deliver_message(
        self,
        chat_page: Optional["WhatsAppChatPage"],
        recipient_phone: str,
        message_content: str,
    ) -> bool:
        """
        Simula la entrega del mensaje imprimiendo el resultado con formato estructurado.

        :param chat_page: Ignorado en modo mock.
        :param recipient_phone: Teléfono destinatario.
        :param message_content: Contenido del mensaje.
        :return: Siempre True en modo de simulación exitosa.
        """
        logger.info("[Estrategia: Console Mock] Ejecutando simulación de entrega...")
        print("\n" + "=" * 60)
        print(f" [SIMULACIÓN RPA] Mensaje despachado a: +{recipient_phone}")
        print("-" * 60)
        print(message_content)
        print("=" * 60 + "\n")
        logger.info("✓ [Console Mock] Mensaje simulado exitosamente.")
        return True
