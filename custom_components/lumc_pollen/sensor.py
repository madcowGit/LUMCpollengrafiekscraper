from __future__ import annotations

import logging
from datetime import datetime, timedelta
import requests
import json
import re

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_POLLEN_TYPE,
    CONF_CACHE_TTL,
)

_LOGGER = logging.getLogger(__name__)

POLLEN_API = "https://sec.lumc.nl/pollenwebextern/pollenwebservice.asmx/GetPollenData"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    config = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            LumcPollenSensor(
                entry_id=entry.entry_id,
                pollen_type=config[CONF_POLLEN_TYPE],
                cache_ttl=config[CONF_CACHE_TTL],
            )
        ],
        True,
    )


class LumcPollenSensor(SensorEntity):
    _attr_icon = "mdi:flower-pollen"

    def __init__(self, entry_id: str, pollen_type: str, cache_ttl: int) -> None:
        self._entry_id = entry_id
        self._pollen_type = pollen_type
        self._cache_ttl = timedelta(seconds=cache_ttl)
        self._last_update: datetime | None = None
        self._state: float | None = None

        self._attr_unique_id = f"{entry_id}_{pollen_type.lower()}"
        self._attr_name = f"LUMC {pollen_type}"

    @property
    def native_value(self) -> float | None:
        return self._state

    async def async_update(self) -> None:
        now = datetime.utcnow()

        if self._last_update and now - self._last_update < self._cache_ttl:
            return

        _LOGGER.debug("[LUMC Pollen] Fetching pollen JSON…")

        try:
            resp = await self.hass.async_add_executor_job(
                requests.post,
                POLLEN_API,
                {
                    "headers": {"Content-Type": "application/json; charset=utf-8"},
                    "json": {},
                    "timeout": 10,
                },
            )
        except Exception as err:
            _LOGGER.error("[LUMC Pollen] Request failed: %s", err)
            return

        # Extract JSON inside XML <string>...</string>
        match = re.search(r">{(.*)}<", resp.text)
        if not match:
            _LOGGER.error("[LUMC Pollen] Unexpected API format")
            return

        try:
            data = json.loads("{" + match.group(1) + "}")
        except Exception as err:
            _LOGGER.error("[LUMC Pollen] JSON parse error: %s", err)
            return

        pollen_list = data.get("d", [])
        _LOGGER.debug("[LUMC Pollen] Available pollen types: %s",
                      [p.get("Name") for p in pollen_list])

        for item in pollen_list:
            if item.get("Name").lower() == self._pollen_type.lower():
                value = item.get("Value")
                _LOGGER.debug("[LUMC Pollen] %s = %s", self._pollen_type, value)
                self._state = value
                self._last_update = now
                return

        _LOGGER.warning("[LUMC Pollen] Pollen type '%s' not found", self._pollen_type)
