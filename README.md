# Home Assistant × Paperclip voice prototype

The installed `v0.1.0-probe.2` proved that the selected ChatGPT conversation agent can call a contributed Assist tool. The working tree now contains an **unreleased read-only status draft**. It is not installed on Home Assistant and does not create tasks.

The draft adds `paperclip_company_status`, which reads current open tasks and agent names from the Paperclip API. It returns counts, at most 12 active tasks with assignees and links, and a `truncated` flag when the first 100 results may be incomplete. The token is entered through a masked Home Assistant config flow and stored in `ConfigEntry.data`. The existing empty probe entry can use Home Assistant's reconfigure flow. No token belongs in this repository.

The status draft needs a separately approved scoped Paperclip credential, source review, release, and Home Assistant maintenance window before a live text test. The live text test should ask `conversation.chatgpt` what the company is working on, confirm a `paperclip_company_status` tool call, compare the result against a same-time Paperclip API read, and test an unavailable API response. Task creation and device acceptance follow in separately gated steps.

## Completed text exposure check for the installed probe

1. The custodian installed the reviewed `v0.1.0-probe.2` through HACS in the approved window.
2. The custodian validated configuration, made backup `45c1c996`, restarted Core once, and loaded the empty config entry.
3. The OpenAI conversation entity was `conversation.chatgpt`, with the Assist LLM API selected.
5. The non-actuating text request `Test the Paperclip voice tool and tell me its exact marker` returned `paperclip-voice-probe-v1` from exactly one `paperclip_voice__probe` call. The installation record is [HOM-58](/HOM/issues/HOM-58#document-install-record).

The marker proof cleared the exposure gate. This unreleased draft removes the probe tool and adds read-only status. Task creation still needs its own credential and write-boundary decision.

To roll back, remove the config entry and HACS integration, validate configuration, restart Home Assistant, and confirm the prior conversation entity and API still work. No deployment or restart is authorized by this repository alone.

Home Assistant's [LLM API documentation](https://developers.home-assistant.io/docs/core/llm/) describes contributed tools; its [config flow guidance](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/config-flow/) supports storing connection data in `ConfigEntry.data`.
