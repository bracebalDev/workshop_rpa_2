"""
Pruebas Unitarias para el Patrón Builder (Constructor de Mensajes).

Valida que el mensaje cumpla estrictamente con las especificaciones académicas
de la Tarea 2 del Taller de RPA.
"""

from src.whatsapp_bot.patterns.builder.message_builder import (
    WhatsAppMessage,
    WhatsAppMessageBuilder,
)


def test_academic_standard_message_format():
    """Valida que el mensaje estándar coincida exactamente con el formato requerido."""
    message = WhatsAppMessageBuilder.create_academic_standard_message()
    expected_text = (
        "Tarea finalizada.\n"
        "Patrones utilizados: Builder, Page Object Model, Strategy."
    )
    assert message.to_text() == expected_text
    assert str(message) == expected_text
    assert message.status == "Tarea finalizada."
    assert "Builder" in message.patterns_used
    assert "Page Object Model" in message.patterns_used
    assert "Strategy" in message.patterns_used


def test_builder_fluent_customization():
    """Valida la interfaz fluida del builder con campos personalizados."""
    builder = WhatsAppMessageBuilder()
    message = (
        builder.set_header("NOTIFICACIÓN RPA")
        .set_status("Proceso completado exitosamente.")
        .add_pattern("Builder")
        .add_pattern("Page Object Model")
        .add_metadata("Asignatura", "Sistemas de Información")
        .set_footer("Universidad de Carabobo")
        .build()
    )

    rendered = message.to_text()
    assert "*NOTIFICACIÓN RPA*" in rendered
    assert "Proceso completado exitosamente." in rendered
    assert "Patrones utilizados: Builder, Page Object Model." in rendered
    assert "• Asignatura: Sistemas de Información" in rendered
    assert "Universidad de Carabobo" in rendered


def test_builder_duplicate_pattern_handling():
    """Verifica que el builder evite patrones duplicados."""
    message = (
        WhatsAppMessageBuilder()
        .add_pattern("Builder")
        .add_pattern("Builder")
        .add_pattern("Strategy")
        .build()
    )
    assert message.patterns_used == ["Builder", "Strategy"]
