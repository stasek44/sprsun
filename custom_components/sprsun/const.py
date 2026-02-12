"""Constants for the SPRSUN Heat Pump integration."""
from typing import Final

# Integration domain
DOMAIN: Final = "sprsun"

# Configuration constants
CONF_SLAVE_ID: Final = "slave_id"
CONF_SCAN_INTERVAL: Final = "scan_interval"
CONF_TIMEOUT: Final = "timeout"

# Default values
DEFAULT_NAME: Final = "SPRSUN Heat Pump"
DEFAULT_PORT: Final = 502
DEFAULT_SLAVE_ID: Final = 1
DEFAULT_SCAN_INTERVAL: Final = 30
DEFAULT_TIMEOUT: Final = 10

# Device info
MANUFACTURER: Final = "SPRSUN"
MODEL: Final = "Heat Pump"

# Temperature scaling factors
TEMP_SCALE_01: Final = 0.1  # Divide by 10
TEMP_SCALE_05: Final = 0.5  # Divide by 2
TEMP_SCALE_1: Final = 1.0   # No scaling

# Pressure scaling factor
PRESSURE_SCALE: Final = 0.1
