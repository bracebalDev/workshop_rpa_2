"""
Módulo de Registro de Eventos (Logger).

Proporciona un registro estructurado y formateado para auditoría y trazabilidad
de los procesos de automatización RPA del bot.
"""

import logging
import sys
from typing import Optional


class BotLogger:
    """Configura y encapsula el formateo de logs para el bot RPA."""

    _logger_instance: Optional[logging.Logger] = None

    @classmethod
    def get_logger(cls, name: str = "WhatsAppRPA") -> logging.Logger:
        """
        Retorna una instancia singleton configurada del logger.

        :param name: Nombre del logger.
        :return: Instancia de logging.Logger.
        """
        if cls._logger_instance is None:
            logger = logging.getLogger(name)
            logger.setLevel(logging.INFO)

            if not logger.handlers:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(logging.INFO)

                formatter = logging.Formatter(
                    fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
                console_handler.setFormatter(formatter)
                logger.addHandler(console_handler)

            cls._logger_instance = logger

        return cls._logger_instance


def get_bot_logger(name: str = "WhatsAppRPA") -> logging.Logger:
    """Función de acceso directo para obtener el logger del bot."""
    return BotLogger.get_logger(name)
