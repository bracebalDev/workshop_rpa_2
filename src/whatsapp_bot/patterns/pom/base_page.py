"""
Página Base del Patrón Page Object Model (POM).

Encapsula la interacción directa con la API de Playwright, proveyendo métodos
robustos para resolver selectores dinámicos, tolerar cambios en la UI, capturar
evidencias visuales y manejar tiempos de espera.
"""

from pathlib import Path
from typing import List, Optional
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError

from ...config import SCREENSHOTS_DIR
from ...utils.logger import get_bot_logger

logger = get_bot_logger()


class BasePage:
    """Clase base para todos los objetos de página (Page Objects)."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def navigate_to(self, url: str, wait_until: str = "domcontentloaded", timeout_ms: int = 45000) -> None:
        """
        Navega hacia una URL específica con manejo de excepciones.

        :param url: URL de destino.
        :param wait_until: Condición de carga ("load", "domcontentloaded", "networkidle").
        :param timeout_ms: Tiempo límite de navegación.
        """
        logger.info("Navegando a: %s", url)
        self.page.goto(url, wait_until=wait_until, timeout=timeout_ms)

    def find_first_visible_selector(self, selectors: List[str], timeout_ms: int = 5000) -> Optional[str]:
        """
        Prueba una lista de selectores alternativos y retorna el primero que esté visible en el DOM.

        :param selectors: Lista de selectores CSS o XPath alternativos.
        :param timeout_ms: Tiempo máximo para evaluar cada selector.
        :return: El primer selector visible encontrado o None.
        """
        for selector in selectors:
            try:
                locator = self.page.locator(selector).first
                if locator.is_visible(timeout=timeout_ms):
                    return selector
            except Exception:
                continue
        return None

    def wait_for_any_selector(self, selectors: List[str], timeout_ms: int = 30000) -> Optional[Locator]:
        """
        Espera hasta que al menos uno de los selectores provistos esté visible en la página.

        :param selectors: Lista de selectores a monitorear.
        :param timeout_ms: Tiempo máximo total de espera.
        :return: Locator del primer elemento visible o None si expira el tiempo.
        """
        combined_selector = ", ".join(selectors)
        try:
            locator = self.page.locator(combined_selector).first
            locator.wait_for(state="visible", timeout=timeout_ms)
            return locator
        except PlaywrightTimeoutError:
            # Fallback iterativo en caso de problemas con selectores combinados
            for selector in selectors:
                try:
                    loc = self.page.locator(selector).first
                    if loc.is_visible(timeout=1000):
                        return loc
                except Exception:
                    continue
            return None

    def safe_click(self, selectors: List[str], timeout_ms: int = 10000) -> bool:
        """
        Intenta hacer clic en el primer selector disponible de una lista de alternativas.

        :param selectors: Selectores candidatos.
        :param timeout_ms: Tiempo de espera para la acción.
        :return: True si se logró hacer clic, False en caso contrario.
        """
        locator = self.wait_for_any_selector(selectors, timeout_ms=timeout_ms)
        if locator:
            try:
                locator.click(timeout=timeout_ms)
                return True
            except Exception as error_msg:
                logger.warning("Fallo al hacer clic en elemento: %s", error_msg)
        return False

    def take_screenshot(self, name_prefix: str = "bot_evidence") -> Optional[Path]:
        """
        Captura una captura de pantalla del estado actual de la página con fines de auditoría/debug.

        :param name_prefix: Prefijo del nombre del archivo de captura.
        :return: Ruta del archivo generado o None si falló.
        """
        try:
            SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
            file_path = SCREENSHOTS_DIR / f"{name_prefix}.png"
            self.page.screenshot(path=str(file_path), full_page=False)
            logger.info("Evidencia visual guardada en: %s", file_path)
            return file_path
        except Exception as error_msg:
            logger.warning("No se pudo capturar la pantalla: %s", error_msg)
            return None

    def pause(self, milliseconds: int) -> None:
        """Pausa la ejecución de la página durante el tiempo especificado en milisegundos."""
        self.page.wait_for_timeout(milliseconds)
