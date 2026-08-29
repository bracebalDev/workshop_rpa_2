"""
Pruebas Unitarias para el Gestor de Credenciales con Keyring.
"""

import pytest
from src.whatsapp_bot.security.credentials_manager import CredentialManager


def test_sanitize_phone_number():
    """Valida la limpieza y formateo de números telefónicos internacionales."""
    assert CredentialManager.sanitize_phone_number("+58 412-123.4567") == "584121234567"
    assert CredentialManager.sanitize_phone_number("(58) 412 1234567") == "584121234567"
    assert CredentialManager.sanitize_phone_number("  +1 (800) 555-0199  ") == "18005550199"
    assert CredentialManager.sanitize_phone_number("") == ""


def test_invalid_phone_number_raises_error():
    """Valida que números demasiado cortos o inválidos generen ValueError."""
    cred_mgr = CredentialManager()
    with pytest.raises(ValueError):
        cred_mgr.set_target_phone("123")


def test_keyring_storage_and_retrieval(monkeypatch):
    """Valida el almacenamiento y recuperación en Keyring simulado."""
    storage = {}

    def mock_set_password(service, key, value):
        storage[(service, key)] = value

    def mock_get_password(service, key):
        return storage.get((service, key))

    def mock_delete_password(service, key):
        if (service, key) in storage:
            del storage[(service, key)]

    monkeypatch.setattr("keyring.set_password", mock_set_password)
    monkeypatch.setattr("keyring.get_password", mock_get_password)
    monkeypatch.setattr("keyring.delete_password", mock_delete_password)

    cred_mgr = CredentialManager(service_name="test_service", phone_key="test_key")

    assert cred_mgr.get_target_phone() is None
    assert cred_mgr.is_phone_configured() is False

    saved = cred_mgr.set_target_phone("+58 412 9998877")
    assert saved == "584129998877"
    assert cred_mgr.get_target_phone() == "584129998877"
    assert cred_mgr.is_phone_configured() is True

    deleted = cred_mgr.delete_target_phone()
    assert deleted is True
    assert cred_mgr.get_target_phone() is None
