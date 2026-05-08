"""Config flow for Alexa Device Builder."""
from __future__ import annotations

from typing import Any

import yaml
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    ALEXA_SUPPORTED_DOMAINS,
    CONF_ENTITY_NAMES,
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
            self._filter_options = user_input
            return await self.async_step_entity_names()

        domain_options = [
            selector.SelectOptionDict(value=d, label=d)
            for d in ALEXA_SUPPORTED_DOMAINS
        ]

        return self.async_show_form(
            step_id="filter",
            data_schema=vol.Schema(
                {
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

    async def async_step_entity_names(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the entity name overrides step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            names_text = (user_input.get(CONF_ENTITY_NAMES) or "").strip()
            entity_names: dict[str, str] = {}
            if names_text:
                try:
                    parsed = yaml.safe_load(names_text)
                    if parsed is None:
                        entity_names = {}
                    elif isinstance(parsed, dict):
                        entity_names = {str(k): str(v) for k, v in parsed.items()}
                    else:
                        errors[CONF_ENTITY_NAMES] = "invalid_format"
                except yaml.YAMLError:
                    errors[CONF_ENTITY_NAMES] = "invalid_yaml"

            if not errors:
                options: dict[str, Any] = dict(self._filter_options)
                if entity_names:
                    options[CONF_ENTITY_NAMES] = entity_names
                return self.async_create_entry(
                    title="Alexa Device Builder",
                    data={CONF_PACKAGE_PATH: self._package_path},
                    options=options,
                )

        default_yaml = _build_default_names_yaml(
            self.hass, self._filter_options.get("include_entities", []), {}
        )

        return self.async_show_form(
            step_id="entity_names",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_ENTITY_NAMES, default=default_yaml
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            multiline=True,
                            type=selector.TextSelectorType.TEXT,
                        )
                    ),
                }
            ),
            errors=errors,
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

    def __init__(self) -> None:
        """Initialize options flow."""
        self._filter_options: dict[str, Any] = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle options."""
        if user_input is not None:
            self._filter_options = user_input
            return await self.async_step_entity_names()

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

    async def async_step_entity_names(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle entity name overrides."""
        errors: dict[str, str] = {}

        if user_input is not None:
            names_text = (user_input.get(CONF_ENTITY_NAMES) or "").strip()
            entity_names: dict[str, str] = {}
            if names_text:
                try:
                    parsed = yaml.safe_load(names_text)
                    if parsed is None:
                        entity_names = {}
                    elif isinstance(parsed, dict):
                        entity_names = {str(k): str(v) for k, v in parsed.items()}
                    else:
                        errors[CONF_ENTITY_NAMES] = "invalid_format"
                except yaml.YAMLError:
                    errors[CONF_ENTITY_NAMES] = "invalid_yaml"

            if not errors:
                options: dict[str, Any] = dict(self._filter_options)
                if entity_names:
                    options[CONF_ENTITY_NAMES] = entity_names
                return self.async_create_entry(title="", data=options)

        existing_names: dict[str, str] = dict(
            self.config_entry.options.get(CONF_ENTITY_NAMES, {})
        )
        default_yaml = _build_default_names_yaml(
            self.hass,
            self._filter_options.get("include_entities", []),
            existing_names,
        )

        return self.async_show_form(
            step_id="entity_names",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_ENTITY_NAMES, default=default_yaml
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            multiline=True,
                            type=selector.TextSelectorType.TEXT,
                        )
                    ),
                }
            ),
            errors=errors,
        )


def _build_default_names_yaml(
    hass: Any,
    include_entities: list[str],
    existing_names: dict[str, str],
) -> str:
    """Build a YAML string pre-populated with friendly names for include_entities.

    Already-configured overrides are preserved; new entities get their HA friendly
    name as the suggested value.
    """
    names: dict[str, str] = dict(existing_names)
    for entity_id in include_entities:
        if entity_id not in names:
            state = hass.states.get(entity_id)
            if state:
                friendly_name = state.attributes.get("friendly_name") or entity_id
                names[entity_id] = friendly_name
    if not names:
        return ""
    return yaml.dump(names, allow_unicode=True, default_flow_style=False).strip()
