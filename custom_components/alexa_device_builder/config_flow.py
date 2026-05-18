"""Config flow for Alexa Device Builder."""
from __future__ import annotations

from collections import deque
from typing import Any

import yaml
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    ALEXA_SUPPORTED_DOMAINS,
    ALEXA_SUPPORTED_LOCALES,
    CONF_ENTITY_NAMES,
    CONF_LOCALE,
    CONF_OPERATION_MODE,
    CONF_PACKAGE_PATH,
    DEFAULT_PACKAGE_PATH,
    DOMAIN,
    MODE_AMAZON_ACCOUNT,
    MODE_HA_YAML,
)


class AlexaDeviceBuilderConfigFlow(
    config_entries.ConfigFlow, domain=DOMAIN
):
    """Config flow for Alexa Device Builder."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self._package_path: str = DEFAULT_PACKAGE_PATH
        self._operation_mode: str = MODE_HA_YAML
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
            self._operation_mode = user_input.get(CONF_OPERATION_MODE, MODE_HA_YAML)
            if self._operation_mode == MODE_AMAZON_ACCOUNT:
                return self.async_abort(reason="amazon_mode_not_ready")
            return await self.async_step_filter()

        operation_mode_options = [
            selector.SelectOptionDict(
                value=MODE_HA_YAML, label="Home Assistant YAML package"
            ),
            selector.SelectOptionDict(
                value=MODE_AMAZON_ACCOUNT,
                label="Amazon account management (Phase 1 preview)",
            ),
        ]

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_OPERATION_MODE,
                        default=MODE_HA_YAML,
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=operation_mode_options,
                            multiple=False,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            custom_value=False,
                        )
                    ),
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
        locale_options = [
            selector.SelectOptionDict(value="", label="(Use Alexa app default)"),
        ] + [
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
                    data={
                        CONF_OPERATION_MODE: self._operation_mode,
                        CONF_PACKAGE_PATH: self._package_path,
                    },
                    options=options,
                )

        default_yaml = _build_default_names_yaml(
            self.hass,
            self._filter_options.get("include_entities", []),
            self._filter_options.get("include_domains", []),
            self._filter_options.get("exclude_entities", []),
            self._filter_options.get("exclude_domains", []),
            {},
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
        locale_options = [
            selector.SelectOptionDict(value="", label="(Use Alexa app default)"),
        ] + [
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
            self._filter_options.get("include_domains", []),
            self._filter_options.get("exclude_entities", []),
            self._filter_options.get("exclude_domains", []),
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
    include_domains: list[str],
    exclude_entities: list[str],
    exclude_domains: list[str],
    existing_names: dict[str, str],
) -> str:
    """Build a YAML string pre-populated with friendly names for exposed entities.

    Already-configured overrides are preserved; new entities get their HA friendly
    name as the suggested value.
    """
    entity_ids = _resolve_exposed_entities(
        hass,
        include_entities,
        include_domains,
        exclude_entities,
        exclude_domains,
    )

    names: dict[str, str] = dict(existing_names)
    for entity_id in sorted(entity_ids):
        if entity_id not in names:
            state = hass.states.get(entity_id)
            if state:
                friendly_name = state.attributes.get("friendly_name") or entity_id
                names[entity_id] = friendly_name
    if not names:
        return ""
    return yaml.dump(
        names, allow_unicode=True, default_flow_style=False, sort_keys=True
    ).strip()


def _resolve_exposed_entities(
    hass: Any,
    include_entities: list[str],
    include_domains: list[str],
    exclude_entities: list[str],
    exclude_domains: list[str],
) -> set[str]:
    """Resolve entities exposed by include/exclude filters for name overrides."""
    include_entities_set = {
        e for e in include_entities if isinstance(e, str) and "." in e
    }
    include_domains_set = {d for d in include_domains if isinstance(d, str) and d}
    exclude_entities_set = {
        e for e in exclude_entities if isinstance(e, str) and "." in e
    }
    exclude_domains_set = {d for d in exclude_domains if isinstance(d, str) and d}

    states = hass.states.async_all()

    if include_entities_set or include_domains_set:
        exposed_entities = set(include_entities_set)
        for state in states:
            if state.domain in include_domains_set:
                exposed_entities.add(state.entity_id)
    else:
        exposed_entities = {state.entity_id for state in states}

    _expand_group_members(hass, exposed_entities)

    exposed_entities -= exclude_entities_set
    return {
        entity_id
        for entity_id in exposed_entities
        if "." in entity_id and entity_id.split(".", 1)[0] not in exclude_domains_set
    }


def _expand_group_members(hass: Any, entity_ids: set[str]) -> None:
    """Expand group entities to also include their members."""
    pending_groups = deque(
        entity_id for entity_id in entity_ids if entity_id.startswith("group.")
    )
    seen_groups: set[str] = set()

    while pending_groups:
        group_entity_id = pending_groups.popleft()
        if group_entity_id in seen_groups:
            continue
        seen_groups.add(group_entity_id)

        group_state = hass.states.get(group_entity_id)
        if not group_state:
            continue

        members = group_state.attributes.get("entity_id")
        if not isinstance(members, list):
            continue

        for member_entity_id in members:
            if not isinstance(member_entity_id, str) or "." not in member_entity_id:
                continue
            if member_entity_id in entity_ids:
                continue
            entity_ids.add(member_entity_id)
            if (
                member_entity_id.startswith("group.")
                and member_entity_id not in seen_groups
            ):
                pending_groups.append(member_entity_id)
