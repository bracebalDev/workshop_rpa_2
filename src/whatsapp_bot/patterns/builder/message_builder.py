"""
Implementación del Patrón de Diseño Creacional: BUILDER.

Permite construir mensajes estructurados y enriquecidos para WhatsApp
de manera fluida, desacoplando la representación del mensaje de su construcción.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class WhatsAppMessage:
    """
    Representación del producto final construido por WhatsAppMessageBuilder.
    """

    status: str
    patterns_used: List[str] = field(default_factory=list)
    header: Optional[str] = None
    footer: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)
    include_timestamp: bool = False

    def to_text(self) -> str:
        """
        Renderiza el mensaje completo en formato de texto para WhatsApp.

        :return: Cadena de texto formateada para el envío.
        """
        lines: List[str] = []

        if self.header:
            lines.append(f"*{self.header}*")
            lines.append("")

        # Estado principal (e.g. "Tarea finalizada.")
        lines.append(self.status)

        # Patrones de diseño implementados
        if self.patterns_used:
            patterns_str = ", ".join(self.patterns_used)
            lines.append(f"Patrones utilizados: {patterns_str}.")

        # Metadatos adicionales opcionales
        if self.metadata:
            lines.append("")
            for key, value in self.metadata.items():
                lines.append(f"• {key}: {value}")

        # Fecha y hora opcional
        if self.include_timestamp:
            now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            lines.append(f"_Generado el: {now_str}_")

        if self.footer:
            lines.append("")
            lines.append(self.footer)

        return "\n".join(lines).strip()

    def __str__(self) -> str:
        return self.to_text()


class WhatsAppMessageBuilder:
    """
    Builder concreto para componer mensajes de WhatsApp.

    Proporciona una interfaz fluida (Fluent Interface) para configurar
    cada sección del mensaje.
    """

    def __init__(self) -> None:
        self._status: str = "Tarea finalizada."
        self._patterns_used: List[str] = []
        self._header: Optional[str] = None
        self._footer: Optional[str] = None
        self._metadata: Dict[str, str] = {}
        self._include_timestamp: bool = False

    def set_status(self, status: str) -> "WhatsAppMessageBuilder":
        """Establece el estado o mensaje principal."""
        self._status = status
        return self

    def add_pattern(self, pattern_name: str) -> "WhatsAppMessageBuilder":
        """Agrega un patrón de diseño a la lista de patrones utilizados."""
        if pattern_name and pattern_name not in self._patterns_used:
            self._patterns_used.append(pattern_name)
        return self

    def set_patterns(self, patterns: List[str]) -> "WhatsAppMessageBuilder":
        """Establece la lista completa de patrones utilizados."""
        self._patterns_used = list(patterns)
        return self

    def set_header(self, header: str) -> "WhatsAppMessageBuilder":
        """Define un encabezado para el mensaje."""
        self._header = header
        return self

    def set_footer(self, footer: str) -> "WhatsAppMessageBuilder":
        """Define un pie de mensaje."""
        self._footer = footer
        return self

    def add_metadata(self, key: str, value: str) -> "WhatsAppMessageBuilder":
        """Agrega un par clave-valor informativo al mensaje."""
        self._metadata[key] = value
        return self

    def with_timestamp(self, include: bool = True) -> "WhatsAppMessageBuilder":
        """Configura si se debe incluir marca de tiempo."""
        self._include_timestamp = include
        return self

    def build(self) -> WhatsAppMessage:
        """
        Construye y retorna el objeto WhatsAppMessage final.

        :return: Instancia inmutable o estructurada de WhatsAppMessage.
        """
        return WhatsAppMessage(
            status=self._status,
            patterns_used=list(self._patterns_used),
            header=self._header,
            footer=self._footer,
            metadata=dict(self._metadata),
            include_timestamp=self._include_timestamp,
        )

    @classmethod
    def create_academic_standard_message(cls) -> WhatsAppMessage:
        """
        Método de fábrica de conveniencia que crea el mensaje estándar
        requerido para la Asignación 2 del Taller de RPA.

        Formato resultante:
        Tarea finalizada.
        Patrones utilizados: Builder, Page Object Model, Strategy.
        """
        return (
            cls()
            .set_status("Tarea finalizada.")
            .set_patterns(["Builder", "Page Object Model", "Strategy"])
            .build()
        )
