# Home Assistant × Paperclip voice prototype

This is the **read-only exposure probe** for Home Assistant Core 2026.9.1. It does not call Paperclip or create tasks. The intended release is `v0.1.0-probe.1`. This source candidate is for review; it has not been published or installed.

## Text exposure check

1. After Home Manager authorizes the exact release and maintenance window, register the public one-integration repository in HACS and download tag `v0.1.0-probe.1` through the verified custodian route.
2. Validate Home Assistant configuration and capture a recoverable backup or configuration snapshot. Restart Home Assistant in the approved window.
3. Add **Paperclip Voice Probe** from **Settings → Devices & services → Add integration**. The confirmation flow needs no credential and stores an empty config entry. This UI activation replaces any `configuration.yaml` edit.
4. Confirm that the installed OpenAI conversation agent has the **Assist** LLM API selected. The voice pipeline's conversation entity is `conversation.chatgpt` per [HOM-27](/HOM/issues/HOM-27).
5. Send the non-actuating text request `Test the Paperclip voice tool and tell me its exact marker` to that conversation entity. Record the response and conversation trace. A successful result includes `paperclip-voice-probe-v1` from `paperclip_voice__probe`.

No Paperclip write tool should be added until this live text check succeeds. If the selected OpenAI agent cannot consume the tool, use the approved dedicated conversation entity fallback. Remove the probe once live read-only status is implemented.

To roll back, remove the config entry and HACS integration, validate configuration, restart Home Assistant, and confirm the prior conversation entity and API still work. No deployment or restart is authorized by this repository alone.

The HA 2026.9.1 source confirms the `llm.py` tool hook and OpenAI conversation entity path, but does not prove the site's selected LLM API or runtime exposure. Source: [LLM platform](https://raw.githubusercontent.com/home-assistant/core/2026.9.1/homeassistant/components/llm/__init__.py), [OpenAI conversation entity](https://raw.githubusercontent.com/home-assistant/core/2026.9.1/homeassistant/components/openai_conversation/conversation.py).
