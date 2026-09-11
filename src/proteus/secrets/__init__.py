"""Secret substrate / broker package."""

from .broker import (
    PROVIDER_ID,
    SecretBrokerError,
    SecretNotFoundError,
    WindowsCredentialManagerBroker,
    delete_secret,
    describe_secret,
    get_secret,
    put_secret,
    redact,
    secret_uri_to_target,
)

__all__ = [
    "PROVIDER_ID",
    "SecretBrokerError",
    "SecretNotFoundError",
    "WindowsCredentialManagerBroker",
    "put_secret",
    "get_secret",
    "delete_secret",
    "describe_secret",
    "redact",
    "secret_uri_to_target",
]
