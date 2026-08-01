"""Exceções de domínio da integração de e-mail."""


class EmailDeliveryError(Exception):
    """Falha ao entregar e-mail via o backend configurado."""
