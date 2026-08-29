"""
Módulo de Gestión Segura de Credenciales y Parámetros Sensibles.

Utiliza la librería `keyring` para almacenar y recuperar de forma segura en el
gestor de credenciales del sistema operativo (Windows Credential Manager / macOS Keychain / Secret Service)
el número de teléfono destinatario del bot de WhatsApp.
"""

import os
import re
from typing import Optional
import keyring

from ..config import ENV_PHONE_KEY, KEYRING_PHONE_KEY, KEYRING_SERVICE_NAME
from ..utils.logger import get_bot_logger

logger = get_bot_logger()


class CredentialManager:
    """
    Gestor de almacenamiento y consulta de parámetros confidenciales con keyring.

    Proporciona métodos mnemotécnicos para guardar, consultar y validar
    el número telefónico del destinatario de las notificaciones RPA.
    """

    def __init__(
        self,
        service_name: str = KEYRING_SERVICE_NAME,
        phone_key: str = KEYRING_PHONE_KEY,
    ) -> None:
        self.service_name = service_name
        self.phone_key = phone_key

    @staticmethod
    def sanitize_phone_number(raw_phone_number: str) -> str:
        """
        Limpia y estandariza el formato del número telefónico.

        Elimina espacios, guiones, paréntesis y signos '+' para dejar sólo
        dígitos numéricos en formato internacional (e.g. 584121234567).

        :param raw_phone_number: Cadena con el número ingresado.
        :return: Cadena numérica sanitizada.
        """
        if not raw_phone_number:
            return ""
        # Remueve todo caracter que no sea dígito
        sanitized = re.sub(r"[^\d]", "", raw_phone_number)
        return sanitized

    def get_target_phone(self) -> Optional[str]:
        """
        Recupera el número de teléfono desde keyring o variables de entorno.

        :return: Número telefónico si existe, None en caso contrario.
        """
        # 1. Intentar obtener desde Keyring del Sistema Operativo
        try:
            stored_phone = keyring.get_password(self.service_name, self.phone_key)
            if stored_phone:
                sanitized = self.sanitize_phone_number(stored_phone)
                if sanitized:
                    logger.info("Número destinatario recuperado con éxito desde Keyring.")
                    return sanitized
        except Exception as error_msg:
            logger.warning(
                "No fue posible acceder a Keyring (%s). Verificando variables de entorno...",
                error_msg,
            )

        # 2. Respaldo a variable de entorno
        env_phone = os.getenv(ENV_PHONE_KEY)
        if env_phone:
            sanitized_env = self.sanitize_phone_number(env_phone)
            if sanitized_env:
                logger.info(
                    "Número destinatario recuperado desde la variable de entorno %s.",
                    ENV_PHONE_KEY,
                )
                return sanitized_env

        return None

    def set_target_phone(self, raw_phone_number: str) -> str:
        """
        Valida, sanitiza y almacena de forma segura el número en Keyring.

        :param raw_phone_number: Número de teléfono a guardar.
        :return: Número sanitizado guardado.
        :raises ValueError: Si el número no cumple con un formato válido.
        """
        sanitized_phone = self.sanitize_phone_number(raw_phone_number)
        if not sanitized_phone or len(sanitized_phone) < 7:
            raise ValueError(
                f"El número telefónico '{raw_phone_number}' no es válido. "
                "Debe contener código de país y dígitos válidos (mínimo 7 dígitos)."
            )

        try:
            keyring.set_password(self.service_name, self.phone_key, sanitized_phone)
            logger.info(
                "Número destinatario (%s) almacenado de forma segura en Keyring.",
                sanitized_phone,
            )
            return sanitized_phone
        except Exception as error_msg:
            logger.error("Error al persistir el número en Keyring: %s", error_msg)
            raise

    def delete_target_phone(self) -> bool:
        """
        Elimina el número telefónico configurado en Keyring.

        :return: True si se eliminó con éxito, False en caso de fallo.
        """
        try:
            keyring.delete_password(self.service_name, self.phone_key)
            logger.info("Número destinatario eliminado de Keyring.")
            return True
        except Exception as error_msg:
            logger.warning("No se pudo eliminar el número de Keyring: %s", error_msg)
            return False

    def is_phone_configured(self) -> bool:
        """Indica si existe un número de teléfono actualmente configurado."""
        return self.get_target_phone() is not None

    def ensure_target_phone(self, interactive_prompt: bool = True) -> str:
        """
        Asegura la disponibilidad de un número telefónico. Si no existe y el modo
        interactivo está activo, solicita el ingreso por consola y lo guarda.

        :param interactive_prompt: Si es True, permite solicitar al usuario el número.
        :return: Número telefónico configurado.
        :raises RuntimeError: Si no hay número y no está habilitado el modo interactivo.
        """
        existing_phone = self.get_target_phone()
        if existing_phone:
            return existing_phone

        if not interactive_prompt:
            raise RuntimeError(
                "No hay un número telefónico configurado en Keyring ni en variables de entorno."
            )

        print("\n=======================================================")
        print(" CONFIGURACIÓN INICIAL DE NÚMERO DESTINATARIO (KEYRING)")
        print("=======================================================")
        print("No se encontró un número guardado en el gestor de credenciales.")
        print("Por favor, ingrese el número con código de país (ej. 584121234567):")

        while True:
            try:
                user_input = input(">> Número de teléfono: ").strip()
                sanitized = self.sanitize_phone_number(user_input)
                if sanitized and len(sanitized) >= 7:
                    self.set_target_phone(sanitized)
                    print(f"[✓] Número {sanitized} guardado exitosamente en Keyring.\n")
                    return sanitized
                print("[!] Número inválido. Ingrese solo números con código de país.")
            except (KeyboardInterrupt, EOFError):
                print("\nOperación cancelada por el usuario.")
                raise SystemExit(1)
