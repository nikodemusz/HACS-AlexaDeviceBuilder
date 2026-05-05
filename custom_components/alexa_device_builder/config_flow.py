"""Config flow for Alexa Device Builder."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    ALEXA_SUPPORTED_DOMAINS,
    CONF_PACKAGE_PATH,
    DEFAULT_PACKAGE_PATH,
    DOMAIN,
)


class AlexaDeviceBuilderConfigFlow(
    config_entries.ConfigFlow, domain=DOMAIN
):
    """Config flow for Alexa Device Builder."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial setup step."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(
                title="Alexa Device Builder",
                data={
                    CONF_PACKAGE_PATH: user_input.get(
                        CONF_PACKAGE_PATH, DEFAULT_PACKAGE_PATH
                    )
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_PACKAGE_PATH, default=DEFAULT_PACKAGE_PATH
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        )
                    ),
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> AlexaDeviceBuilderOptionsFlow:
        """Get options flow."""
        return AlexaDeviceBuilderOptionsFlow(config_entry)


class AlexaDeviceBuilderOptionsFlow(config_entries.OptionsFlow):
    """Options flow for Alexa Device Builder."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        domain_options = [
            selector.SelectOptionDict(value=d, label=d)
            for d in ALEXA_SUPPORTED_DOMAINS
        ]

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "include_entities",
                        default=list(options.get("include_entities", [])),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(multiple=True)
                    ),
                    vol.Optional(
                        "include_domains",
                        default=list(options.get("include_domains", [])),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=domain_options,
                            multiple=True,
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    ),
                    vol.Optional(
                        "exclude_entities",
                        default=list(options.get("exclude_entities", [])),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(multiple=True)
                    ),
                    vol.Optional(
                        "exclude_domains",
                        default=list(options.get("exclude_domains", [])),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=domain_options,
                            multiple=True,
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    ),
                }
            ),
        )
