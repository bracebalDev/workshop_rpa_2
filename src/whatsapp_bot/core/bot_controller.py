"""
Controlador Orquestador del Bot de WhatsApp RPA.

Coordina la interacción entre el Gestor de Credenciales, el Navegador,
los Objetos de Página (POM), el Constructor de Mensajes (Builder) y las
Estrategias de Envío (Strategy).
"""

from typing import Optional

from ..patterns.builder.bot_config_builder import BotConfiguration
from ..patterns.builder.message_builder import WhatsAppMessage, WhatsAppMessageBuilder
from ..patterns.pom.chat_page import WhatsAppChatPage
from ..patterns.pom.login_page import WhatsAppLoginPage
from ..patterns.strategy.console_mock_strategy import ConsoleMockDeliveryStrategy
from ..patterns.strategy.delivery_strategy import DeliveryContext
from ..patterns.strategy.strategy_factory import StrategyFactory
from ..security.credentials_manager import CredentialManager
from ..utils.logger import get_bot_logger
from .browser_manager import BrowserManager

logger = get_bot_logger()


class WhatsAppBotController:
    """Orquestador principal del flujo de automatización RPA."""

    def __init__(
        self,
        config: BotConfiguration,
        credentials_manager: Optional[CredentialManager] = None,
    ) -> None:
        self.config = config
        self.credentials_manager = credentials_manager or CredentialManager()

    def run(self, custom_message: Optional[WhatsAppMessage] = None) -> bool:
        """
        Ejecuta el ciclo de vida completo del bot de WhatsApp.

        :param custom_message: Mensaje opcional construido con Builder.
                               Si no se proporciona, se construye el estándar académico.
        :return: True si la ejecución finalizó exitosamente, False en caso de error.
        """
        logger.info("=== INICIANDO EJECUCION DEL BOT RPA DE WHATSAPP ===")

        # 1. Obtener o solicitar número telefónico destinatario
        recipient_phone = self.config.target_phone or self.credentials_manager.ensure_target_phone()
        if not recipient_phone:
            logger.error("No se pudo obtener un número de teléfono destinatario válido.")
            return False

        # 2. Construir mensaje mediante el Patrón Builder
        message_to_send = custom_message or WhatsAppMessageBuilder.create_academic_standard_message()
        rendered_text = message_to_send.to_text()

        logger.info("Contenido del mensaje a despachar:\n%s", rendered_text)

        # 3. Resolver e instanciar Estrategia de Envío
        if self.config.dry_run:
            strategy = ConsoleMockDeliveryStrategy()
        else:
            strategy = StrategyFactory.get_strategy(self.config.delivery_strategy)

        delivery_context = DeliveryContext(strategy=strategy)

        # 4. Manejo de Modo Simulación / Dry-Run
        if self.config.dry_run or strategy.strategy_name == "console_mock":
            logger.info("Ejecutando en modo de prueba / simulacion.")
            return delivery_context.execute_delivery(
                chat_page=None,
                recipient_phone=recipient_phone,
                message_content=rendered_text,
            )

        # 5. Ejecución en Navegador Real con Playwright
        browser_manager = BrowserManager(
            headless=self.config.headless,
            slow_mo_ms=self.config.slow_mo_ms,
            session_file=self.config.session_file,
        )

        try:
            page = browser_manager.initialize()
            context = browser_manager.context

            # Paso 5.1: Gestionar Autenticación (Page Object: LoginPage)
            login_page = WhatsAppLoginPage(page=page, context=context)
            login_page.open_whatsapp_web()

            if not login_page.is_session_active(timeout_ms=12000):
                logger.info("Sesión no autenticada. Iniciando flujo de vinculación por QR.")
                is_logged_in = login_page.wait_for_authentication(
                    timeout_ms=self.config.qr_timeout_ms
                )
                if not is_logged_in:
                    logger.error("Error: No se completó la autenticación en WhatsApp Web.")
                    return False

                # Guardar sesión inmediatamente tras el primer login
                login_page.save_session_state(self.config.session_file)

            # Paso 5.2: Despachar Mensaje según la Estrategia Seleccionada (Page Object: ChatPage)
            chat_page = WhatsAppChatPage(page=page)
            delivery_result = delivery_context.execute_delivery(
                chat_page=chat_page,
                recipient_phone=recipient_phone,
                message_content=rendered_text,
            )

            if delivery_result:
                logger.info("[EXITO] Tarea finalizada y mensaje despachado correctamente.")
                # Refrescar persistencia de sesión
                browser_manager.save_storage_state()
                return True
            else:
                logger.error("[FALLO] No se pudo completar la entrega del mensaje.")
                return False

        except Exception as error_msg:
            logger.exception("Excepción no controlada durante la ejecución del bot: %s", error_msg)
            return False
        finally:
            browser_manager.close()
            logger.info("=== FIN DE LA EJECUCION DEL BOT RPA ===")
