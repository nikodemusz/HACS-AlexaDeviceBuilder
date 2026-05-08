"""Constants for Alexa Device Builder."""

DOMAIN = "alexa_device_builder"

CONF_PACKAGE_PATH = "package_path"
DEFAULT_PACKAGE_PATH = "packages/alexa_devices.yaml"

CONF_LOCALE = "locale"
ALEXA_SUPPORTED_LOCALES = [
    "de-DE",
    "en-AU",
    "en-CA",
    "en-GB",
    "en-IN",
    "en-US",
    "es-ES",
    "es-MX",
    "es-US",
    "fr-CA",
    "fr-FR",
    "hi-IN",
    "it-IT",
    "ja-JP",
    "pt-BR",
]

# Home Assistant domains supported by the Alexa Smart Home integration
ALEXA_SUPPORTED_DOMAINS = [
    "alarm_control_panel",
    "binary_sensor",
    "camera",
    "climate",
    "cover",
    "fan",
    "group",
    "humidifier",
    "input_boolean",
    "input_number",
    "input_select",
    "light",
    "lock",
    "media_player",
    "remote",
    "scene",
    "script",
    "sensor",
    "switch",
    "vacuum",
    "water_heater",
]
