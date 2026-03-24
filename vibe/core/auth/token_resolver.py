"""Resolve bearer tokens for API providers.

Centralises the logic that both ``MistralBackend`` and ``GenericBackend`` use to
obtain an ``api_key`` / bearer token:

1. If the provider has ``console_domain`` set, read the API key from the
   Mistral Code VSCode extension config (``~/.mistralcode/config.json``).
2. Otherwise fall back to the classic ``os.getenv(provider.api_key_env_var)``.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from vibe.core.auth.console_auth import get_api_key_for_domain

if TYPE_CHECKING:
    from vibe.core.config import ProviderConfig


def resolve_api_key_sync(provider: ProviderConfig) -> str | None:
    """Return a bearer token for *provider* (synchronous)."""
    if provider.uses_console_auth:
        return get_api_key_for_domain(
            provider.console_domain, config_path=provider.resolved_console_config_path
        )
    if provider.api_key_env_var:
        return os.getenv(provider.api_key_env_var)
    return None


async def resolve_api_key(provider: ProviderConfig) -> str | None:
    """Async version — preferred inside running event loops.

    Console auth is a simple file read, so no actual awaiting is needed,
    but we keep the interface async for consistency with the backends.
    """
    return resolve_api_key_sync(provider)
