from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol
import requests
import json
import re

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_POLLEN_TYPE,
    CONF_CACHE_TTL,
    DEFAULT_POLLEN_TYPE,
    DEFAULT_CACHE_TTL,
)

_LOGGER = logging.getLogger(__name__)

POLLEN_API = "https://sec.lumc.nl/pollenwebextern/pollenwebservice.asmx/GetPollenData"


def _fetch_pollen_types() -> list[str]:
    """Fetch available pollen types from LUMC API."""
    try:
        resp = requests.post(
            POLLEN_API,
            headers={"Content-Type": "application/json; charset=utf-8"},
            json={},
            timeout=10,
        )
        resp.raise_for_status()

        # Extract JSON inside XML <string>...</string>
        match = re.search(r">{(.*)}<", resp.text)
        if not match:
            _LOGGER.error("LUMC API returned unexpected format")
            return []

        data = json.loads("{" + match.group(1) + "}")
        return [p.get("Name") for p in data.get("d", [])]

    except Exception as err:
        _LOGGER.error("Error fetching pollen types: %s", err)
        return []


class LumcPollenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        pollen_types = await self.hass.async_add_executor_job(_fetch_pollen_types)

        if not pollen_types:
            errors["base"] = "cannot_fetch_pollen_types"
            pollen_types = ["Alnus", "Betula", "Poaceae"]

        if user_input is not None:
            if user_input[CONF_POLLEN_TYPE] not in pollen_types:
                errors["base"] = "invalid_pollen_type"
            else:
                return self.async_create_entry(
                    title=f"LUMC Pollen - {user_input[CONF_POLLEN_TYPE]}",
                    data=user_input,
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_POLLEN_TYPE, default=DEFAULT_POLLEN_TYPE): vol.In(
                    pollen_types
                ),
                vol.Required(CONF_CACHE_TTL, default=DEFAULT_CACHE_TTL): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
