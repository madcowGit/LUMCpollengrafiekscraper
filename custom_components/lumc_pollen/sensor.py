"""Sensor entities for LUMC Pollen integration."""

import base64
import logging
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    ATTR_GRAPH_IMAGE,
    ATTR_GRAPH_URL,
    CONF_BASE_URL,
    CONF_CACHE_TTL,
    CONF_POLLEN_TYPE,
    DEFAULT_BASE_URL,
    DEFAULT_CACHE_TTL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .lumc_client import LUMCPollenClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities from a config entry."""
    base_url = entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL)
    pollen_type = entry.data.get(CONF_POLLEN_TYPE)
    cache_ttl = entry.data.get(CONF_CACHE_TTL, DEFAULT_CACHE_TTL)
    scan_interval = entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)

    client = LUMCPollenClient(base_url=base_url, ttl_seconds=cache_ttl)

    coordinator = LumcPollenDataUpdateCoordinator(
        hass, client, pollen_type, scan_interval
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    entities = [
        LumcPollenTotalSensor(coordinator, entry, pollen_type),
        LumcPollenGraphUrlSensor(coordinator, entry, pollen_type),
        LumcPollenGraphImageSensor(coordinator, entry, pollen_type),
    ]

    async_add_entities(entities)


class LumcPollenDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for LUMC Pollen."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: LUMCPollenClient,
        pollen_type: str,
        scan_interval: int,
    ) -> None:
        """Initialize the coordinator."""
        self.client = client
        self.pollen_type = pollen_type

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from LUMC."""
        try:
            total = await self.hass.async_add_executor_job(
                self.client.get_total, self.pollen_type
            )
            graph_url = await self.hass.async_add_executor_job(
                self.client.get_history_graph_url, self.pollen_type
            )
            graph_png = await self.hass.async_add_executor_job(
                self.client.get_history_graph_png, self.pollen_type
            )
            graph_image = f"data:image/png;base64,{base64.b64encode(graph_png).decode()}"

            return {
                "total": total,
                "graph_url": graph_url,
                "graph_image": graph_image,
            }
        except Exception as err:
            raise UpdateFailed(f"Error fetching data from LUMC: {err}") from err


class LumcPollenBaseSensor(CoordinatorEntity, SensorEntity):
    """Base sensor entity for LUMC Pollen."""

    def __init__(
        self,
        coordinator: LumcPollenDataUpdateCoordinator,
        entry: ConfigEntry,
        pollen_type: str,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entry = entry
        self.pollen_type = pollen_type
        self.sensor_type = sensor_type
        self._attr_unique_id = f"{DOMAIN}_{pollen_type}_{sensor_type}"
        self._attr_name = (
            f"LUMC {pollen_type} {sensor_type.replace('_', ' ').title()}"
        )

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": f"LUMC Pollen - {self.pollen_type}",
            "manufacturer": "LUMC",
            "model": "Pollen Grafiek",
        }


class LumcPollenTotalSensor(LumcPollenBaseSensor):
    """Sensor for pollen total count."""

    def __init__(
        self,
        coordinator: LumcPollenDataUpdateCoordinator,
        entry: ConfigEntry,
        pollen_type: str,
    ) -> None:
        """Initialize the total sensor."""
        super().__init__(coordinator, entry, pollen_type, "total")
        self._attr_native_unit_of_measurement = "µg/m³"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:flower"

    @property
    def native_value(self) -> int | None:
        """Return the state."""
        if self.coordinator.data:
            return self.coordinator.data["total"]
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        if self.coordinator.data:
            attrs[ATTR_GRAPH_URL] = self.coordinator.data["graph_url"]
            attrs[ATTR_GRAPH_IMAGE] = self.coordinator.data["graph_image"]
        return attrs


class LumcPollenGraphUrlSensor(LumcPollenBaseSensor):
    """Sensor for graph URL."""

    def __init__(
        self,
        coordinator: LumcPollenDataUpdateCoordinator,
        entry: ConfigEntry,
        pollen_type: str,
    ) -> None:
        """Initialize the graph URL sensor."""
        super().__init__(coordinator, entry, pollen_type, "graph_url")
        self._attr_icon = "mdi:link"

    @property
    def native_value(self) -> str | None:
        """Return the state."""
        if self.coordinator.data:
            return self.coordinator.data["graph_url"]
        return None


class LumcPollenGraphImageSensor(LumcPollenBaseSensor):
    """Sensor for graph image."""

    def __init__(
        self,
        coordinator: LumcPollenDataUpdateCoordinator,
        entry: ConfigEntry,
        pollen_type: str,
    ) -> None:
        """Initialize the graph image sensor."""
        super().__init__(coordinator, entry, pollen_type, "graph_image")
        self._attr_icon = "mdi:image"

    @property
    def native_value(self) -> str | None:
        """Return the state."""
        if self.coordinator.data:
            return self.coordinator.data["graph_image"]
        return None
