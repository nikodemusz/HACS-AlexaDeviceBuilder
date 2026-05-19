"""REST API views for Alexa Device Builder panel."""
from __future__ import annotations

import logging
from typing import Any

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant

from .const import (
    CONF_AMAZON_REGION,
    CONF_OPERATION_MODE,
    DEFAULT_AMAZON_REGION,
    DOMAIN,
    MODE_AMAZON_ACCOUNT,
)

_LOGGER = logging.getLogger(__name__)


def _get_amazon_entry(hass: HomeAssistant) -> Any | None:
    """Return the Amazon-mode config entry, or None."""
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data.get(CONF_OPERATION_MODE) == MODE_AMAZON_ACCOUNT:
            return entry
    return None


class AlexaDeviceListView(HomeAssistantView):
    """Return the list of Alexa appliances from Alexa Media Player."""

    url = "/api/alexa_device_builder/devices"
    name = "api:alexa_device_builder:devices"

    async def get(self, request: web.Request) -> web.Response:
        """Handle GET – return device list."""
        hass: HomeAssistant = request.app["hass"]
        entry = _get_amazon_entry(hass)
        if entry is None:
            return self.json({"error": "no_amazon_entry", "devices": []})

        amazon_region = str(
            entry.options.get(
                CONF_AMAZON_REGION,
                entry.data.get(CONF_AMAZON_REGION, DEFAULT_AMAZON_REGION),
            )
        ).strip()

        from . import (  # pylint: disable=import-outside-toplevel
            _get_alexa_api_class,
            _resolve_alexa_media_login,
        )

        alexa_api = _get_alexa_api_class()
        if alexa_api is None:
            return self.json({"error": "alexa_media_unavailable", "devices": []})

        login_obj = _resolve_alexa_media_login(hass, amazon_region)
        if login_obj is None:
            return self.json({"error": "not_logged_in", "devices": []})

        try:
            network_details = await alexa_api.get_network_details(login_obj)
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.warning("Panel API: could not load Alexa devices: %s", err)
            return self.json({"error": "fetch_failed", "devices": []})

        devices: list[dict[str, Any]] = []
        if isinstance(network_details, list):
            for raw in network_details:
                if not isinstance(raw, dict):
                    continue
                appliance_id = str(raw.get("applianceId") or "").strip()
                if not appliance_id:
                    continue
                devices.append(
                    {
                        "applianceId": appliance_id,
                        "entityId": str(raw.get("entityId") or "").strip(),
                        "friendlyName": str(raw.get("friendlyName") or "").strip(),
                        "applianceTypes": list(raw.get("applianceTypes") or []),
                        "manufacturerName": str(
                            raw.get("manufacturerName") or ""
                        ).strip(),
                        "modelName": str(raw.get("modelName") or "").strip(),
                        "groupName": str(raw.get("groupName") or "").strip(),
                    }
                )

        return self.json({"devices": devices})


class AlexaDeviceApplyView(HomeAssistantView):
    """Apply rename / delete actions to Alexa appliances."""

    url = "/api/alexa_device_builder/apply"
    name = "api:alexa_device_builder:apply"

    async def post(self, request: web.Request) -> web.Response:
        """Handle POST – execute pending changes."""
        hass: HomeAssistant = request.app["hass"]
        entry = _get_amazon_entry(hass)
        if entry is None:
            return self.json({"error": "no_amazon_entry", "results": []})

        try:
            body = await request.json()
        except Exception:  # pylint: disable=broad-except
            return self.json_message(
                "Invalid JSON body. Expected: {\"actions\": [{\"applianceId\": \"...\", \"action\": \"rename|delete\", \"newName\": \"...\"}]}",
                status_code=400,
            )

        actions = body.get("actions") if isinstance(body, dict) else None
        if not isinstance(actions, list):
            return self.json_message("'actions' must be a list", status_code=400)

        amazon_region = str(
            entry.options.get(
                CONF_AMAZON_REGION,
                entry.data.get(CONF_AMAZON_REGION, DEFAULT_AMAZON_REGION),
            )
        ).strip()

        from . import (  # pylint: disable=import-outside-toplevel
            _delete_amazon_device,
            _get_alexa_api_class,
            _rename_amazon_device,
            _resolve_alexa_media_login,
        )

        alexa_api = _get_alexa_api_class()
        if alexa_api is None:
            return self.json({"error": "alexa_media_unavailable", "results": []})

        login_obj = _resolve_alexa_media_login(hass, amazon_region)
        if login_obj is None:
            return self.json({"error": "not_logged_in", "results": []})

        results: list[dict[str, Any]] = []
        for action in actions:
            if not isinstance(action, dict):
                continue

            appliance_id = str(action.get("applianceId") or "").strip()
            action_type = str(action.get("action") or "").strip()
            new_name = str(action.get("newName") or "").strip()

            if not appliance_id or action_type not in ("rename", "delete"):
                results.append(
                    {
                        "applianceId": appliance_id,
                        "action": action_type,
                        "success": False,
                        "error": "invalid_action",
                    }
                )
                continue

            if action_type == "delete":
                success = await _delete_amazon_device(
                    alexa_api, login_obj, appliance_id
                )
                results.append(
                    {
                        "applianceId": appliance_id,
                        "action": "delete",
                        "success": success,
                    }
                )
            else:
                if not new_name:
                    results.append(
                        {
                            "applianceId": appliance_id,
                            "action": "rename",
                            "success": False,
                            "error": "empty_name",
                        }
                    )
                    continue
                success = await _rename_amazon_device(
                    alexa_api, login_obj, appliance_id, new_name
                )
                results.append(
                    {
                        "applianceId": appliance_id,
                        "action": "rename",
                        "success": success,
                    }
                )

        return self.json({"results": results})
