"""
Punto de Entrada Principal (CLI) del Bot de WhatsApp RPA.

Taller de RPA — Asignación 2
Universidad de Carabobo — Sistemas de Información
Automatización de WhatsApp Web con Playwright y Patrones de Diseño (Builder, POM, Strategy).
"""

import argparse
import sys
from pathlib import Path

# Configurar encoding UTF-8 en consola de Windows si está disponible
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.whatsapp_bot.config import STORAGE_STATE_FILE
from src.whatsapp_bot.core.bot_controller import WhatsAppBotController
from src.whatsapp_bot.patterns.builder.bot_config_builder import BotConfigBuilder
from src.whatsapp_bot.patterns.builder.message_builder import (
    WhatsAppMessage,
    WhatsAppMessageBuilder,
)
from src.whatsapp_bot.security.credentials_manager import CredentialManager
from src.whatsapp_bot.utils.logger import get_bot_logger

logger = get_bot_logger()


def print_academic_banner() -> None:
    """Muestra el encabezado institucional y descriptivo de la práctica."""
    banner = """
========================================================================
    UNIVERSIDAD DE CARABOBO - FACULTAD DE CIENCIAS Y TECNOLOGIA
             SISTEMAS DE INFORMACION - TALLER DE RPA
             ASIGNACION 2: BOT DE WHATSAPP CON PLAYWRIGHT
========================================================================
 Patrones de Diseno:
   * Builder: Construccion fluida y desacoplada del mensaje
   * Page Object Model (POM): Abstraccion e interaccion de UI web
   * Strategy: Intercambio dinamico de algoritmos de entrega
 Persistencia de Sesion:
   * Playwright storage_state (evita re-escaneo de codigo QR)
 Seguridad y Credenciales:
   * Keyring (almacenamiento en el gestor seguro del SO)
========================================================================
"""
    print(banner)


def parse_arguments() -> argparse.Namespace:
    """Configura y procesa los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Bot RPA de WhatsApp Web con Playwright y Patrones de Diseno.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Opciones de Credenciales y Teléfono
    phone_group = parser.add_argument_group("Gestion de Telefono y Credenciales (Keyring)")
    phone_group.add_argument(
        "-p",
        "--phone",
        type=str,
        help="Numero telefonico destinatario (con codigo de pais, ej: 584121234567).",
    )
    phone_group.add_argument(
        "--save-phone",
        type=str,
        metavar="NUMERO",
        help="Guarda permanentemente el numero destinatario en Keyring y finaliza.",
    )
    phone_group.add_argument(
        "--show-phone",
        action="store_true",
        help="Consulta y muestra el numero actualmente almacenado en Keyring.",
    )
    phone_group.add_argument(
        "--delete-phone",
        action="store_true",
        help="Elimina el numero telefonico configurado en Keyring.",
    )

    # Opciones de Ejecución del Bot
    execution_group = parser.add_argument_group("Opciones de Ejecucion y Navegador")
    execution_group.add_argument(
        "--headless",
        action="store_true",
        help="Ejecuta el navegador en modo headless (oculto).",
    )
    execution_group.add_argument(
        "-s",
        "--strategy",
        type=str,
        default="direct_url",
        choices=["direct_url", "search_chat", "console_mock"],
        help="Estrategia de envio a emplear (por defecto: direct_url).",
    )
    execution_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Modo simulacion academica: ejecuta el flujo sin abrir navegador ni enviar mensajes reales.",
    )
    execution_group.add_argument(
        "--session-file",
        type=str,
        default=str(STORAGE_STATE_FILE),
        help=f"Ruta personalizada para el archivo de sesion (por defecto: {STORAGE_STATE_FILE}).",
    )

    # Opciones de Mensaje
    message_group = parser.add_argument_group("Opciones de Contenido del Mensaje")
    message_group.add_argument(
        "-m",
        "--custom-msg",
        type=str,
        help="Mensaje personalizado opcional (si no se especifica, se envia el formato de Tarea 2).",
    )

    return parser.parse_args()


def handle_credential_actions(args: argparse.Namespace, cred_manager: CredentialManager) -> bool:
    """
    Procesa acciones directas sobre Keyring (--save-phone, --show-phone, --delete-phone).

    :return: True si se procesó una acción y el programa debe terminar.
    """
    if args.save_phone:
        sanitized = cred_manager.set_target_phone(args.save_phone)
        print(f"[OK] Numero {sanitized} guardado exitosamente en Keyring.")
        return True

    if args.show_phone:
        stored = cred_manager.get_target_phone()
        if stored:
            print(f"[OK] Numero configurado en Keyring: +{stored}")
        else:
            print("[INFO] No hay ningun numero configurado en Keyring actualmente.")
        return True

    if args.delete_phone:
        if cred_manager.delete_target_phone():
            print("[OK] Numero eliminado exitosamente de Keyring.")
        else:
            print("[INFO] No se encontro ningun numero para eliminar en Keyring.")
        return True

    return False


def main() -> int:
    """Función principal de ejecución."""
    print_academic_banner()
    args = parse_arguments()
    cred_manager = CredentialManager()

    # Procesar acciones de mantenimiento de credenciales si fueron solicitadas
    if handle_credential_actions(args, cred_manager):
        return 0

    # 1. Configurar el bot mediante el Patrón Builder
    session_path = Path(args.session_file)
    config = (
        BotConfigBuilder()
        .set_headless(args.headless)
        .set_session_file(session_path)
        .set_target_phone(args.phone)
        .set_delivery_strategy(args.strategy)
        .set_dry_run(args.dry_run)
        .build()
    )

    # 2. Construir el mensaje mediante el Patrón Builder
    if args.custom_msg:
        message = (
            WhatsAppMessageBuilder()
            .set_status(args.custom_msg)
            .set_patterns(["Builder", "Page Object Model", "Strategy"])
            .build()
        )
    else:
        # Mensaje estándar requerido por la asignación
        message = WhatsAppMessageBuilder.create_academic_standard_message()

    # 3. Instanciar el orquestador y ejecutar
    controller = WhatsAppBotController(
        config=config,
        credentials_manager=cred_manager,
    )

    success = controller.run(custom_message=message)

    if success:
        print("\n=======================================================")
        print(" [OK] PROCESO RPA COMPLETADO EXITOSAMENTE")
        print("=======================================================\n")
        return 0
    else:
        print("\n=======================================================")
        print(" [ERROR] LA AUTOMATIZACION NO PUDO FINALIZAR")
        print("=======================================================\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
