# Enterprise Console Auth

Mistral Vibe can connect to enterprise Mistral deployments (e.g. Azure-hosted instances) that use the Mistral console for SSO-based authentication. Instead of a long-lived API key, the CLI reads short-lived keys managed by the **Mistral Code VSCode extension** (`mistralai.mistral-code`).

## Prerequisites

1. **Mistral Code VSCode extension** — install `mistralai.mistral-code` from the VS Code marketplace and sign in through your enterprise SSO.
2. **Enterprise console URL** — the hostname of your organisation's Mistral console (e.g. `mistral-console.prd.swce.azure.asml.com`).
3. **Enterprise API URL** — the base URL of the Mistral API endpoint (e.g. `https://mistral-api.prd.swce.azure.asml.com/v1`).

## Configuration

Add a provider and model to `~/.vibe/config.toml`:

```toml
[[providers]]
name = "enterprise"
api_base = "https://mistral-api.example.com/v1"
backend = "mistral"
console_domain = "mistral-console.example.com"
```

| Field | Description |
|-------|-------------|
| `name` | A short identifier for the provider (your choice). |
| `api_base` | The full base URL of the enterprise Mistral API, including `/v1`. |
| `backend` | Use `"mistral"` for the native SDK backend, or `"generic"` for the OpenAI-compatible httpx backend. |
| `console_domain` | The hostname of the enterprise Mistral console. This tells Vibe to read the API key from the VSCode extension instead of an environment variable. |
| `console_config_path` | *(optional)* Override the path to the extension config file. Defaults to `~/.mistralcode/config.json`. |

> **Note:** Do not set `api_key_env_var` — when `console_domain` is present the key is resolved automatically from the extension config.

Then add a model that references the provider:

```toml
[[models]]
name = "devstral-medium-latest"
provider = "enterprise"
alias = "ent"
```

Finally, set the model as active:

```toml
active_model = "ent"
```

## How It Works

When `console_domain` is set on a provider, Vibe reads `~/.mistralcode/config.json` (written by the Mistral Code extension) and extracts the API key whose `consoleDomain` or `apiDomain` matches the configured `console_domain`. The key is re-read on every API call, so when the extension refreshes the key after SSO re-authentication, Vibe picks it up automatically.

## CLI Commands

### Check login status

```bash
vibe --login              # checks the active provider
vibe --login enterprise   # checks a specific provider by name
```

If a valid key is found, Vibe prints a confirmation. If not, it opens the enterprise console in your browser so you can re-authenticate.

### Logout info

```bash
vibe --logout
```

Tokens are managed by the VSCode extension, so `--logout` shows instructions on how to sign out through the extension or clear `~/.mistralcode/config.json`.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| *"Mistral Code VSCode extension config was not found"* | Install `mistralai.mistral-code` in VS Code and sign in. |
| *"No API key found … key may have expired"* | Open the extension or visit the console in your browser to refresh the SSO session. |
| *"Provider does not have console_domain configured"* | Add `console_domain = "…"` to the provider in `config.toml`. |
| API returns 401 Unauthorized | The key has expired. Re-authenticate in the extension, then retry. |
