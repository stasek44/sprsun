"""Binary sensor platform for SPRSUN Heat Pump."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SprsunDataUpdateCoordinator
from .const import (
    BIT_ALARM,
    BIT_ANTILEGIONELLA,
    BIT_COMPRESSOR,
    BIT_COOLING_DEMAND,
    BIT_DEFROST,
    BIT_FAN,
    BIT_HEATING_DEMAND,
    BIT_HEATING_HEATER,
    BIT_HOTWATER_DEMAND,
    BIT_HOTWATER_HEATER,
    BIT_PUMP,
    BIT_THREE_WAY_VALVE,
    BIT_WITH_COOLING,
    BIT_WITH_HEATING,
    DOMAIN,
    MANUFACTURER,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN binary sensor entities."""
    coordinator: SprsunDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        # Working status (register 3)
        SprsunBinarySensor(coordinator, entry, "Hot Water Demand", "working_status", BIT_HOTWATER_DEMAND, "mdi:water-boiler-alert"),
        SprsunBinarySensor(coordinator, entry, "Heating Demand", "working_status", BIT_HEATING_DEMAND, "mdi:radiator", BinarySensorDeviceClass.HEAT),
        SprsunBinarySensor(coordinator, entry, "With Heating", "working_status", BIT_WITH_HEATING, "mdi:radiator"),
        SprsunBinarySensor(coordinator, entry, "With Cooling", "working_status", BIT_WITH_COOLING, "mdi:snowflake"),
        SprsunBinarySensor(coordinator, entry, "Antilegionella", "working_status", BIT_ANTILEGIONELLA, "mdi:bacteria"),
        SprsunBinarySensor(coordinator, entry, "Cooling Demand", "working_status", BIT_COOLING_DEMAND, "mdi:snowflake-alert", BinarySensorDeviceClass.COLD),
        SprsunBinarySensor(coordinator, entry, "Alarm", "working_status", BIT_ALARM, "mdi:alert-circle", BinarySensorDeviceClass.PROBLEM),
        SprsunBinarySensor(coordinator, entry, "Defrost", "working_status", BIT_DEFROST, "mdi:snowflake-melt"),
        
        # Output symbol 1 (register 4)
        SprsunBinarySensor(coordinator, entry, "Compressor", "output_symbol_1", BIT_COMPRESSOR, "mdi:engine", BinarySensorDeviceClass.RUNNING),
        SprsunBinarySensor(coordinator, entry, "Fan", "output_symbol_1", BIT_FAN, "mdi:fan", BinarySensorDeviceClass.RUNNING),
        SprsunBinarySensor(coordinator, entry, "4-Way Valve", "output_symbol_1", BIT_FOUR_WAY_VALVE, "mdi:valve"),
        
        # Output symbol 2 (register 5)
        SprsunBinarySensor(coordinator, entry, "Heating Heater", "output_symbol_2", BIT_HEATING_HEATER, "mdi:radiator", BinarySensorDeviceClass.HEAT),
        SprsunBinarySensor(coordinator, entry, "Three-Way Valve", "output_symbol_2", BIT_THREE_WAY_VALVE, "mdi:valve"),
        SprsunBinarySensor(coordinator, entry, "Hot Water Heater", "output_symbol_2", BIT_HOTWATER_HEATER, "mdi:water-boiler", BinarySensorDeviceClass.HEAT),
        
        # Output symbol 3 (register 6)
        SprsunBinarySensor(coordinator, entry, "Pump", "output_symbol_3", BIT_PUMP, "mdi:pump", BinarySensorDeviceClass.RUNNING),
    ]

    async_add_entities(entities)


class SprsunBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for SPRSUN status bits."""

    def __init__(
        self,
        coordinator: SprsunDataUpdateCoordinator,
        entry: ConfigEntry,
        name: str,
        key: str,
        bit_mask: int,
        icon: str,
        device_class: BinarySensorDeviceClass | None = None,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_name = f"{entry.title} {name}"
        self._attr_unique_id = f"{entry.entry_id}_{key}_{bit_mask}"
        self._key = key
        self._bit_mask = bit_mask
        self._attr_icon = icon
        self._attr_device_class = device_class
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": MANUFACTURER,
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if self.coordinator.data and self._key in self.coordinator.data:
            value = self.coordinator.data[self._key]
            return bool(value & self._bit_mask)
        return None
