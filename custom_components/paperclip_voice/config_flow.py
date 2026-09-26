"""UI activation for the read-only Paperclip voice probe."""

from homeassistant import config_entries

DOMAIN = "paperclip_voice"


class PaperclipVoiceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Create one credential-free probe config entry."""

    async def async_step_user(self, user_input=None):
        """Confirm activation through the Home Assistant UI."""
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if user_input is not None:
            return self.async_create_entry(title="Paperclip Voice Probe", data={})

        return self.async_show_form(step_id="user")
