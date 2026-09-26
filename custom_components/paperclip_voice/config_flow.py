"""UI setup for a scoped Paperclip connection."""

from urllib.parse import urlsplit

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

DOMAIN = "paperclip_voice"


def _schema():
    return vol.Schema(
        {
            vol.Required("base_url"): str,
            vol.Required("company_id"): str,
            vol.Required("token"): TextSelector(
                TextSelectorConfig(type=TextSelectorType.PASSWORD)
            ),
        }
    )


def _normalize(user_input):
    url = user_input["base_url"].strip().rstrip("/")
    parsed = urlsplit(url)
    if (parsed.scheme not in ("http", "https") or not parsed.netloc
        or parsed.username or parsed.password or parsed.path not in ("", "/")
        or parsed.query or parsed.fragment):
        return None
    if not user_input["company_id"].strip() or not user_input["token"].strip():
        return None
    return {
        "base_url": url,
        "company_id": user_input["company_id"].strip(),
        "token": user_input["token"].strip(),
    }


class PaperclipVoiceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Create or update the credential stored in ConfigEntry.data."""

    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")
        if user_input is not None:
            data = _normalize(user_input)
            if data is not None:
                return self.async_create_entry(title="Paperclip Voice", data=data)
            return self.async_show_form(step_id="user", data_schema=_schema(), errors={"base": "invalid_input"})
        return self.async_show_form(step_id="user", data_schema=_schema())

    async def async_step_reconfigure(self, user_input=None):
        """Upgrade the existing empty probe entry without putting a key in YAML."""
        if user_input is not None:
            data = _normalize(user_input)
            if data is not None:
                return self.async_update_reload_and_abort(
                    self._get_reconfigure_entry(), data_updates=data
                )
            return self.async_show_form(step_id="reconfigure", data_schema=_schema(), errors={"base": "invalid_input"})
        return self.async_show_form(step_id="reconfigure", data_schema=_schema())
