"""
Módulo de Configuración y Constantes del Bot RPA.

Define URLs, rutas de almacenamiento de sesiones, claves de seguridad para
keyring, tiempos de espera (timeouts) y selectores DOM resilientes para WhatsApp Web.
"""

from pathlib import Path
from typing import Final, List

# --- Rutas de Archivos y Directorios ---
BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent.parent
SESSIONS_DIR: Final[Path] = BASE_DIR / "sessions"
STORAGE_STATE_FILE: Final[Path] = SESSIONS_DIR / "storage_state.json"
SCREENSHOTS_DIR: Final[Path] = BASE_DIR / "screenshots"

# --- URLs de WhatsApp Web ---
WHATSAPP_WEB_BASE_URL: Final[str] = "https://web.whatsapp.com"
WHATSAPP_SEND_URL_TEMPLATE: Final[str] = "https://web.whatsapp.com/send?phone={phone}&text={text}"
WHATSAPP_DIRECT_CHAT_URL_TEMPLATE: Final[str] = "https://web.whatsapp.com/send?phone={phone}"

# --- Configuración del Gestor de Credenciales (Keyring) ---
KEYRING_SERVICE_NAME: Final[str] = "whatsapp_rpa_workshop"
KEYRING_PHONE_KEY: Final[str] = "target_recipient_phone"
ENV_PHONE_KEY: Final[str] = "WHATSAPP_TARGET_PHONE"

# --- Tiempos de Espera (Timeouts en milisegundos) ---
DEFAULT_TIMEOUT_MS: Final[int] = 45000
QR_SCAN_TIMEOUT_MS: Final[int] = 120000
ELEMENT_WAIT_TIMEOUT_MS: Final[int] = 30000
MESSAGE_DELIVERY_TIMEOUT_MS: Final[int] = 25000
SLOW_MO_MS: Final[int] = 100

# --- Selectores Resilientes para WhatsApp Web ---

# Selectores para identificar la presencia del código QR (Pantalla de Login)
QR_CONTAINER_SELECTORS: Final[List[str]] = [
    "canvas[aria-label*='Scan']",
    "canvas[aria-label*='QR']",
    "canvas[aria-label*='código QR']",
    "canvas[aria-label*='código']",
    "div[data-ref] canvas",
    "div[data-testid='qrcode']",
    "canvas",
]

# Selectores para verificar que la sesión está autenticada (Panel principal cargado)
MAIN_CHAT_PANE_SELECTORS: Final[List[str]] = [
    "div[id='pane-side']",
    "div[data-testid='chat-list']",
    "header[data-testid='chatlist-header']",
    "div[role='textbox'][data-tab='3']",
    "#pane-side",
]

# Selectores del cuadro de texto para redactar mensajes (Message Composer)
MESSAGE_INPUT_SELECTORS: Final[List[str]] = [
    "footer div[contenteditable='true'][role='textbox']",
    "div[contenteditable='true'][data-tab='10']",
    "div[contenteditable='true'][role='textbox']",
    "div[title='Escribe un mensaje']",
    "div[title='Escribe un mensaje aquí']",
    "div[title='Type a message']",
    "footer div[contenteditable='true']",
    "div[data-testid='conversation-compose-box-input']",
]

# Selectores del botón de enviar mensaje
SEND_BUTTON_SELECTORS: Final[List[str]] = [
    "button[data-testid='compose-btn-send']",
    "button[aria-label='Enviar']",
    "button[aria-label='Send']",
    "span[data-icon='send']",
    "button:has(span[data-icon='send'])",
]

# Selectores del campo de búsqueda de chats/contactos
SEARCH_INPUT_SELECTORS: Final[List[str]] = [
    "div[contenteditable='true'][data-tab='3']",
    "div[title='Cuadro de texto de búsqueda']",
    "div[title='Search input box']",
    "div[data-testid='chat-list-search']",
]

# Selectores de alerta de número de teléfono inválido o no registrado
INVALID_PHONE_DIALOG_SELECTORS: Final[List[str]] = [
    "div[data-testid='popup-contents']",
    "div[role='dialog']",
]
