"""
Gestor del Ciclo de Vida del Navegador Playwright.

Encapsula el inicio de Chromium, la configuración del contexto de navegación,
la inyección del estado de persistencia (`storage_state.json`) y el cierre ordenado.
"""

from pathlib import Path
from typing import Optional
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from ..config import STORAGE_STATE_FILE
from ..utils.logger import get_bot_logger

logger = get_bot_logger()

# User-Agent estándar de Chrome de escritorio para asegurar compatibilidad con WhatsApp Web
DESKTOP_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
)


class BrowserManager:
    """Administrador de instancias y contextos de navegador Playwright."""

    def __init__(
        self,
        headless: bool = False,
        slow_mo_ms: int = 100,
        session_file: Path = STORAGE_STATE_FILE,
    ) -> None:
        self.headless = headless
        self.slow_mo_ms = slow_mo_ms
        self.session_file = Path(session_file)

        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    @property
    def page(self) -> Page:
        """Página activa del navegador."""
        if not self._page:
            raise RuntimeError("El navegador no ha sido inicializado. Llame a initialize() primero.")
        return self._page

    @property
    def context(self) -> BrowserContext:
        """Contexto activo del navegador."""
        if not self._context:
            raise RuntimeError("El contexto de navegación no está disponible.")
        return self._context

    def initialize(self) -> Page:
        """
        Inicializa Playwright, lanza Chromium y configura el contexto cargando
        la sesión guardada si existe.

        :return: Instancia de Page lista para interactuar.
        """
        logger.info("Iniciando motor de automatización Playwright...")
        self._playwright = sync_playwright().start()

        # Argumentos de Chromium para optimizar rendimiento y estabilidad
        chromium_args = [
            "--disable-blink-features=AutomationControlled",
            "--start-maximized",
            "--no-sandbox",
            "--disable-setuid-sandbox",
        ]

        logger.info("Lanzando Chromium (Headless: %s, SlowMo: %sms)...", self.headless, self.slow_mo_ms)
        self._browser = self._playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo_ms,
            args=chromium_args,
        )

        context_options = {
            "user_agent": DESKTOP_USER_AGENT,
            "viewport": {"width": 1280, "height": 800},
            "locale": "es-ES",
            "timezone_id": "America/Caracas",
        }

        # Verificación y carga de persistencia de sesión previa
        if self.session_file.exists() and self.session_file.stat().st_size > 0:
            logger.info("Cargando sesión persistida desde: %s", self.session_file)
            context_options["storage_state"] = str(self.session_file)
        else:
            logger.info("No se encontró sesión previa guardada. Se requerirá autenticación inicial.")

        self._context = self._browser.new_context(**context_options)
        self._page = self._context.new_page()

        return self._page

    def save_storage_state(self, target_path: Optional[Path] = None) -> bool:
        """
        Guarda el estado actual del contexto (cookies, tokens y storage) en el archivo indicado.

        :param target_path: Ruta destino opcional (por defecto self.session_file).
        :return: True si se guardó exitosamente.
        """
        file_to_save = target_path or self.session_file
        if not self._context:
            logger.warning("No hay un contexto activo para exportar storage_state.")
            return False

        try:
            file_to_save.parent.mkdir(parents=True, exist_ok=True)
            self._context.storage_state(path=str(file_to_save))
            logger.info("Estado de sesión guardado exitosamente en: %s", file_to_save)
            return True
        except Exception as error_msg:
            logger.error("Error al guardar storage_state: %s", error_msg)
            return False

    def close(self) -> None:
        """Cierra de manera ordenada la página, contexto, navegador y proceso de Playwright."""
        logger.info("Cerrando recursos del navegador...")
        try:
            if self._context:
                self.save_storage_state()
            if self._page:
                self._page.close()
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
            logger.info("Recursos de Playwright liberados correctamente.")
        except Exception as error_msg:
            logger.warning("Excepción durante el cierre de recursos: %s", error_msg)

    def __enter__(self) -> Page:
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
