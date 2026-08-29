"""
Implementación del Patrón Builder para la Configuración de Ejecución del Bot.

Permite construir y validar configuraciones de ejecución del bot (Headless, Timeouts, Rutas, etc.)
de forma declarativa y segura.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ...config import (
    DEFAULT_TIMEOUT_MS,
    QR_SCAN_TIMEOUT_MS,
    SLOW_MO_MS,
    STORAGE_STATE_FILE,
)


@dataclass
class BotConfiguration:
    """Configuración de ejecución inmutable del bot."""

    headless: bool
    slow_mo_ms: int
    session_file: Path
    timeout_ms: int
    qr_timeout_ms: int
    target_phone: Optional[str]
    delivery_strategy: str
    dry_run: bool


class BotConfigBuilder:
    """Builder para ensamblar la configuración del bot."""

    def __init__(self) -> None:
        self._headless: bool = False
        self._slow_mo_ms: int = SLOW_MO_MS
        self._session_file: Path = STORAGE_STATE_FILE
        self._timeout_ms: int = DEFAULT_TIMEOUT_MS
        self._qr_timeout_ms: int = QR_SCAN_TIMEOUT_MS
        self._target_phone: Optional[str] = None
        self._delivery_strategy: str = "direct_url"
        self._dry_run: bool = False

    def set_headless(self, headless: bool) -> "BotConfigBuilder":
        """Establece el modo de ejecución del navegador (con o sin interfaz gráfica)."""
        self._headless = headless
        return self

    def set_slow_mo(self, slow_mo_ms: int) -> "BotConfigBuilder":
        """Configura el retardo intencional entre acciones (slow motion)."""
        self._slow_mo_ms = max(0, slow_mo_ms)
        return self

    def set_session_file(self, session_path: Path) -> "BotConfigBuilder":
        """Define la ruta del archivo de persistencia de sesión."""
        self._session_file = session_path
        return self

    def set_timeout(self, timeout_ms: int) -> "BotConfigBuilder":
        """Configura el timeout general para operaciones de red y DOM."""
        self._timeout_ms = timeout_ms
        return self

    def set_qr_timeout(self, qr_timeout_ms: int) -> "BotConfigBuilder":
        """Configura el timeout para el escaneo del código QR."""
        self._qr_timeout_ms = qr_timeout_ms
        return self

    def set_target_phone(self, phone: Optional[str]) -> "BotConfigBuilder":
        """Establece el número de teléfono del destinatario."""
        self._target_phone = phone
        return self

    def set_delivery_strategy(self, strategy_name: str) -> "BotConfigBuilder":
        """Establece el nombre de la estrategia de envío a utilizar."""
        self._delivery_strategy = strategy_name.lower()
        return self

    def set_dry_run(self, dry_run: bool) -> "BotConfigBuilder":
        """Habilita o deshabilita el modo de prueba (sin envío real)."""
        self._dry_run = dry_run
        return self

    def build(self) -> BotConfiguration:
        """Construye y valida el objeto de configuración."""
        return BotConfiguration(
            headless=self._headless,
            slow_mo_ms=self._slow_mo_ms,
            session_file=self._session_file,
            timeout_ms=self._timeout_ms,
            qr_timeout_ms=self._qr_timeout_ms,
            target_phone=self._target_phone,
            delivery_strategy=self._delivery_strategy,
            dry_run=self._dry_run,
        )
