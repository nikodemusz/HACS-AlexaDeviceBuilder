"""Constants for Alexa Device Builder."""

DOMAIN = "alexa_device_builder"

CONF_PACKAGE_PATH = "package_path"
DEFAULT_PACKAGE_PATH = "packages/alexa_devices.yaml"

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
