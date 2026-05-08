"""Config flow for Alexa Device Builder."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    ALEXA_SUPPORTED_DOMAINS,
    ALEXA_SUPPORTED_LOCALES,
    CONF_LOCALE,
    CONF_PACKAGE_PATH,
    DEFAULT_PACKAGE_PATH,
    DOMAIN,
)


class AlexaDeviceBuilderConfigFlow(
    config_entries.ConfigFlow, domain=DOMAIN
):
    """Config flow for Alexa Device Builder."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self._package_path: str = DEFAULT_PACKAGE_PATH
        self._filter_options: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial setup step."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            self._package_path = user_input.get(
                CONF_PACKAGE_PATH, DEFAULT_PACKAGE_PATH
            )
            return await self.async_step_filter()

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

    async def async_step_filter(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the filter criteria setup step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Alexa Device Builder",
                data={CONF_PACKAGE_PATH: self._package_path},
                options=user_input,
            )

        domain_options = [
            selector.SelectOptionDict(value=d, label=d)
            for d in ALEXA_SUPPORTED_DOMAINS
        ]
        locale_options = [
            selector.SelectOptionDict(value=loc, label=loc)
            for loc in ALEXA_SUPPORTED_LOCALES
        ]

        return self.async_show_form(
            step_id="filter",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_LOCALE, default=""
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=locale_options,
                            multiple=False,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            custom_value=False,
                        )
                    ),
                    vol.Optional(
                        "include_entities", default=[]
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(multiple=True)
                    ),
                    vol.Optional(
                        "include_domains", default=[]
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=domain_options,
                            multiple=True,
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    ),
                    vol.Optional(
                        "exclude_entities", default=[]
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(multiple=True)
                    ),
                    vol.Optional(
                        "exclude_domains", default=[]
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

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> AlexaDeviceBuilderOptionsFlow:
        """Get options flow."""
        return AlexaDeviceBuilderOptionsFlow()


class AlexaDeviceBuilderOptionsFlow(config_entries.OptionsFlow):
    """Options flow for Alexa Device Builder."""

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
        locale_options = [
            selector.SelectOptionDict(value=loc, label=loc)
            for loc in ALEXA_SUPPORTED_LOCALES
        ]

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_LOCALE,
                        default=options.get(CONF_LOCALE, ""),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=locale_options,
                            multiple=False,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            custom_value=False,
                        )
                    ),
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
