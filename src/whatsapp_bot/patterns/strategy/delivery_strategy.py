"""
Definición del Patrón de Diseño de Comportamiento: STRATEGY.

Permite definir una familia de algoritmos para el envío de mensajes, encapsular
cada uno de ellos y hacerlos intercambiables según el contexto operativo del bot RPA.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..pom.chat_page import WhatsAppChatPage


class MessageDeliveryStrategy(ABC):
    """
    Interfaz abstracta de la estrategia de envío de mensajes.
    """

    @abstractmethod
    def deliver_message(
        self,
        chat_page: Optional["WhatsAppChatPage"],
        recipient_phone: str,
        message_content: str,
    ) -> bool:
        """
        Ejecuta el algoritmo de entrega del mensaje.

        :param chat_page: Instancia de WhatsAppChatPage (POM) para interactuar con la UI.
        :param recipient_phone: Número de teléfono destinatario.
        :param message_content: Contenido textual del mensaje a enviar.
        :return: True si el envío fue exitoso, False en caso de error.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Retorna el nombre identificativo de la estrategia."""
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str:
        """Retorna una descripción del funcionamiento de la estrategia."""
        raise NotImplementedError


class DeliveryContext:
    """
    Contexto que utiliza una estrategia concreta para realizar el despacho del mensaje.
    """

    def __init__(self, strategy: MessageDeliveryStrategy) -> None:
        self._strategy = strategy

    @property
    def strategy(self) -> MessageDeliveryStrategy:
        """Estrategia actual configurada."""
        return self._strategy

    @strategy.setter
    def strategy(self, new_strategy: MessageDeliveryStrategy) -> None:
        """Permite cambiar la estrategia de envío en tiempo de ejecución."""
        self._strategy = new_strategy

    def execute_delivery(
        self,
        chat_page: Optional["WhatsAppChatPage"],
        recipient_phone: str,
        message_content: str,
    ) -> bool:
        """
        Delega la ejecución del envío a la estrategia actualmente configurada.

        :param chat_page: Page Object del chat.
        :param recipient_phone: Teléfono destinatario.
        :param message_content: Texto del mensaje.
        :return: Resultado booleano de la entrega.
        """
        return self._strategy.deliver_message(
            chat_page=chat_page,
            recipient_phone=recipient_phone,
            message_content=message_content,
        )
