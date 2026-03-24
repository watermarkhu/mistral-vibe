"""Read API keys from the Mistral Code VSCode extension's config.

Enterprise Mistral deployments (e.g. Azure-hosted) issue short-lived API keys
through the Mistral console after SSO login.  The Mistral Code VSCode extension
(`mistralai.mistral-code`, a Continue fork) stores these keys in
``~/.mistralcode/config.json``.

This module reads that file and extracts the active API key for a given console
domain, allowing Vibe CLI to piggyback on the extension's authenticated session.
When the key is stale, the user is directed to the console to re-authenticate
(or to refresh via the extension).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import webbrowser

from vibe.core.logger import logger

_DEFAULT_CONFIG_FILE = Path.home() / ".mistralcode" / "config.json"


class ConsoleAuthError(Exception):
    pass


def _read_config(config_path: Path | None = None) -> dict[str, Any]:
    """Read and parse the extension config file."""
    path = config_path or _DEFAULT_CONFIG_FILE
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text("utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Failed to read %s: %s", path, e)
        return {}


def get_api_key_for_domain(
    console_domain: str, *, config_path: Path | None = None
) -> str | None:
    """Return the API key from the extension config matching *console_domain*.

    The extension stores keys in two places inside ``config.json``:
    - ``models[*].apiKey`` (used for chat models)
    - ``tabAutocompleteModel.apiKey`` (used for autocomplete)

    We match against ``consoleDomain`` or ``apiDomain`` and return the first
    non-empty ``apiKey`` found.
    """
    data = _read_config(config_path)
    if not data:
        return None

    # Check if this config belongs to the right console domain
    config_console = str(data.get("consoleDomain", ""))
    config_api = str(data.get("apiDomain", ""))

    # Match against either the console domain or the API domain
    domain_lower = console_domain.lower()
    if not (
        config_console.lower() == domain_lower or config_api.lower() == domain_lower
    ):
        return None

    # Try models array first (chat models have the most relevant key)
    models = data.get("models")
    if isinstance(models, list):
        for model in models:
            if isinstance(model, dict) and (key := model.get("apiKey")):
                return str(key)

    # Fall back to tabAutocompleteModel
    tab_model = data.get("tabAutocompleteModel")
    if isinstance(tab_model, dict) and (key := tab_model.get("apiKey")):
        return str(key)

    # Fall back to top-level mistralCodeUserAPIKey
    if user_key := data.get("mistralCodeUserAPIKey"):
        return str(user_key)

    return None


def get_api_base_for_domain(
    console_domain: str, *, config_path: Path | None = None
) -> str | None:
    """Return the API base URL from the extension config matching *console_domain*."""
    data = _read_config(config_path)
    if not data:
        return None

    config_console = str(data.get("consoleDomain", ""))
    config_api = str(data.get("apiDomain", ""))
    domain_lower = console_domain.lower()

    if not (
        config_console.lower() == domain_lower or config_api.lower() == domain_lower
    ):
        return None

    # Derive api_base from apiDomain
    if config_api:
        return f"https://{config_api}/v1"

    # Try from models array
    models = data.get("models")
    if isinstance(models, list):
        for model in models:
            if isinstance(model, dict) and (base := model.get("apiBase")):
                return str(base)

    return None


def open_console_login(console_domain: str) -> None:
    """Open the enterprise console in the user's browser for SSO login."""
    url = f"https://{console_domain}"
    webbrowser.open(url)


def has_extension_config(config_path: Path | None = None) -> bool:
    """Return True if the mistral-code extension config file exists."""
    return (config_path or _DEFAULT_CONFIG_FILE).is_file()
