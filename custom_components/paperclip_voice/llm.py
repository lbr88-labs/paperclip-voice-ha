"""Temporary read-only tool for verifying the selected conversation API."""

from homeassistant.components.llm import LLMTools
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.llm import LLM_API_ASSIST, LLMContext, Tool, ToolInput
from homeassistant.util.json import JsonObjectType


class PaperclipProbeTool(Tool):
    """Return a fixed marker without reaching Paperclip or changing anything."""

    name = "paperclip_voice__probe"
    description = "Check whether the Paperclip voice tool is available to this assistant."

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: ToolInput,
        llm_context: LLMContext,
    ) -> JsonObjectType:
        """Return an unmistakable result for a text conversation test."""
        return {"available": True, "marker": "paperclip-voice-probe-v1"}


@callback
def async_get_tools(
    hass: HomeAssistant, llm_context: LLMContext, api_id: str
) -> LLMTools | None:
    """Contribute only to the built-in Assist LLM API."""
    if api_id != LLM_API_ASSIST:
        return None
    return LLMTools(
        tools=[PaperclipProbeTool()],
        prompt=(
            "When the user asks to test the Paperclip voice tool, call "
            "paperclip_voice__probe and report its marker exactly."
        ),
    )
