"""Configuration flow for LUMC Pollen Grafiek integration."""

import logging
from typing import Any, Dict

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback

from .const import CONF_BASE_URL, CONF_POLLEN_TYPE, CONF_TTL, DEFAULT_BASE_URL, DEFAULT_TTL, DOMAIN
from .lumc_client import LUMCPollenClient, PollenNotFound

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
        vol.Required(CONF_POLLEN_TYPE): str,
        vol.Required(CONF_TTL, default=DEFAULT_TTL): int,
    }
)


class LUMCPollenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LUMC Pollen Grafiek."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input: Dict[str, Any] | None = None):
        """Handle the initial step."""
        if user_input is not None:
            # Validate the pollen type
            base_url = user_input[CONF_BASE_URL]
            pollen_type = user_input[CONF_POLLEN_TYPE]

            try:
                client = LUMCPollenClient(base_url=base_url)
                available_types = client.list_names()

                # Case-insensitive match
                if pollen_type.lower() not in [t.lower() for t in available_types]:
                    return self.async_show_form(
                        step_id="user",
                        data_schema=DATA_SCHEMA,
                        errors={"base": "invalid_pollen_type"},
                        description_placeholders={
                            "available_types": ", ".join(available_types)
                        },
                    )
            except Exception as e:
                _LOGGER.error("Error validating pollen type: %s", e)
                return self.async_show_form(
                    step_id="user",
                    data_schema=DATA_SCHEMA,
                    errors={"base": "cannot_connect"},
                )

            # Create unique ID based on pollen type
            await self.async_set_unique_id(f"{pollen_type.lower()}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"LUMC Pollen - {pollen_type}",
                data=user_input,
            )

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Get the options flow for this integration."""
        return LUMCPollenOptionsFlow(config_entry)


class LUMCPollenOptionsFlow(config_entries.OptionsFlow):
    """Options flow for LUMC Pollen Grafiek integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Dict[str, Any] | None = None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
                vol.Required(
                    CONF_TTL, default=self.config_entry.options.get(CONF_TTL, DEFAULT_TTL)
                ): int,
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
