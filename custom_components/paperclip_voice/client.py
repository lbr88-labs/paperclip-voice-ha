"""Small, read-only Paperclip client for spoken company status."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from urllib.parse import quote

from aiohttp import ClientError, ClientResponseError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

PAPERCLIP_ORIGIN = "https://paperclip.nyvej.it"
ISSUE_PAGE_LIMIT = 100


class PaperclipError(Exception):
    """A safe error to report to the conversation agent."""


@dataclass(frozen=True)
class PaperclipConfig:
    base_url: str
    company_id: str
    token: str


async def _get_json(hass, config: PaperclipConfig, path: str):
    if config.base_url != PAPERCLIP_ORIGIN:
        raise PaperclipError("Paperclip connection settings are invalid.")
    session = async_get_clientsession(hass)
    url = f"{PAPERCLIP_ORIGIN}/api/{path.lstrip('/')}"
    try:
        async with asyncio.timeout(10):
            async with session.get(
                url, headers={"Authorization": f"Bearer {config.token}"},
                allow_redirects=False,
            ) as response:
                if 300 <= response.status < 400:
                    raise PaperclipError("Paperclip could not provide a current status. Please try again later.")
                response.raise_for_status()
                return await response.json()
    except ClientResponseError as err:
        if err.status in (401, 403):
            raise PaperclipError("Paperclip access is unavailable. Ask the integration owner to check its credential.") from err
        raise PaperclipError("Paperclip could not provide a current status. Please try again later.") from err
    except (ClientError, TimeoutError, ValueError) as err:
        raise PaperclipError("Paperclip could not provide a current status. Please try again later.") from err


async def company_status(hass, config: PaperclipConfig) -> dict:
    """Return a bounded snapshot with current issue and assignee context."""
    company = quote(config.company_id, safe="")
    issues = await _get_json(
        hass, config,
        f"companies/{company}/issues?status=todo,in_progress,blocked,in_review&limit={ISSUE_PAGE_LIMIT}",
    )
    agents = await _get_json(hass, config, f"companies/{company}/agents")
    return summarize_status(issues, agents, PAPERCLIP_ORIGIN)


def summarize_status(issues: object, agents: object, base_url: str) -> dict:
    """Reduce the API response to a small, spoken-answer-friendly result."""
    if not isinstance(issues, list) or not isinstance(agents, list):
        raise PaperclipError("Paperclip returned an unexpected status response.")

    names = {
        agent.get("id"): str(agent.get("name") or "unknown")[:80]
        for agent in agents if isinstance(agent, dict)
    }
    counts = {status: 0 for status in ("todo", "in_progress", "blocked", "in_review")}
    active = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        status = issue.get("status")
        if status not in counts:
            continue
        counts[status] += 1
        if status == "in_progress":
            identifier = issue.get("identifier", "")
            prefix = identifier.split("-", 1)[0] if "-" in identifier else ""
            active.append({
                "title": str(issue.get("title") or "Untitled task")[:160],
                "assignee": names.get(issue.get("assigneeAgentId")) or "unassigned",
                "status": status,
                "link": f"{base_url.rstrip('/')}/{prefix}/issues/{identifier}" if prefix else None,
            })
    active.sort(key=lambda item: (item["assignee"], item["title"]))
    return {
        "first_page_counts": counts,
        "working_now": active[:12],
        "shown": min(len(active), 12),
        "first_page_working_now": len(active),
        "first_page_limit": ISSUE_PAGE_LIMIT,
        "more_pages_possible": len(issues) >= ISSUE_PAGE_LIMIT,
    }
