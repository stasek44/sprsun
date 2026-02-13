"""Binary sensor platform for SPRSUN Heat Pump.

Binary sensors read from coordinator.data (no direct Modbus access).
"""
from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    MANUFACTURER,
    MODEL,
    FAILURE_SYMBOL_1_BITS,
    FAILURE_SYMBOL_2_BITS,
    FAILURE_SYMBOL_4_BITS,
    FAILURE_SYMBOL_5_BITS,
    OUTPUT_SYMBOL_1_BITS,
    OUTPUT_SYMBOL_2_BITS,
    OUTPUT_SYMBOL_3_BITS,
    SWITCHING_INPUT_BITS,
    WORKING_STATUS_BITS,
)
from .coordinator import SPRSUNDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class SPRSUNBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes SPRSUN binary sensor entity."""

    register: int | None = None
    bit: int | None = None


BINARY_SENSORS: tuple[SPRSUNBinarySensorEntityDescription, ...] = (
    # Working status - 0x0003
    SPRSUNBinarySensorEntityDescription(
        key="hotwater_demand",
        name="Hot Water Demand",
        register=0x0003,
        bit=0,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    SPRSUNBinarySensorEntityDescription(
        key="heating_demand",
        name="Heating Demand",
        register=0x0003,
        bit=1,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    SPRSUNBinarySensorEntityDescription(
        key="cooling_demand",
        name="Cooling Demand",
        register=0x0003,
        bit=5,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    SPRSUNBinarySensorEntityDescription(
        key="defrost",
        name="Defrost Active",
        register=0x0003,
        bit=7,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    SPRSUNBinarySensorEntityDescription(
        key="antilegionella_on",
        name="Anti-Legionella Active",
        register=0x0003,
        bit=4,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    
    # Output symbols - Component status
    SPRSUNBinarySensorEntityDescription(
        key="compressor_running",
        name="Compressor Running",
        register=0x0004,
        bit=0,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    SPRSUNBinarySensorEntityDescription(
        key="fan_running",
        name="Fan Running",
        register=0x0004,
        bit=5,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    SPRSUNBinarySensorEntityDescription(
        key="water_pump_running",
        name="Water Pump Running",
        register=0x0006,
        bit=6,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    SPRSUNBinarySensorEntityDescription(
        key="heating_heater_on",
        name="Heating Heater On",
        register=0x0005,
        bit=5,
        device_class=BinarySensorDeviceClass.HEAT,
    ),
    SPRSUNBinarySensorEntityDescription(
        key="hotwater_heater_on",
        name="Hot Water Heater On",
        register=0x0005,
        bit=7,
        device_class=BinarySensorDeviceClass.HEAT,
    ),
    
    # Switching inputs - Safety switches
    SPRSUNBinarySensorEntityDescription(
        key="water_flow_switch",
        name="Water Flow Switch",
        register=0x0002,
        bit=4,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    SPRSUNBinarySensorEntityDescription(
        key="emergency_switch",
        name="Emergency Switch",
        register=0x0002,
        bit=1,
        device_class=BinarySensorDeviceClass.SAFETY,
    ),
    
    # Failure symbols - Key alarms
    SPRSUNBinarySensorEntityDescription(
        key="high_voltage_fault",
        name="High Voltage Fault",
        register=0x0007,
        bit=5,
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    SPRSUNBinarySensorEntityDescription(
        key="high_heating_outlet",
        name="High Heating Outlet",
        register=0x0008,
        bit=2,
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    SPRSUNBinarySensorEntityDescription(
        key="high_exhaust_temp",
        name="High Exhaust Temperature",
        register=0x000A,
        bit=1,
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    SPRSUNBinarySensorEntityDescription(
        key="overpressure_high",
        name="Overpressure High",
        register=0x000B,
        bit=1,
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    SPRSUNBinarySensorEntityDescription(
        key="underpressure_low",
        name="Underpressure Low",
        register=0x000B,
        bit=0,
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN binary sensor entities."""
    coordinator: SPRSUNDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        SPRSUNBinarySensor(coordinator, entry, description)
        for description in BINARY_SENSORS
    ]
    
    async_add_entities(entities)


class SPRSUNBinarySensor(CoordinatorEntity[SPRSUNDataUpdateCoordinator], BinarySensorEntity):
    """Representation of a SPRSUN binary sensor.
    
    Reads from coordinator.data (no direct Modbus access).
    """

    _attr_has_entity_name = True
    entity_description: SPRSUNBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: SPRSUNDataUpdateCoordinator,
        entry: ConfigEntry,
        description: SPRSUNBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if self.entity_description.register is None or self.entity_description.bit is None:
            return None
        
        raw = self.coordinator.data.get(self.entity_description.register)
        if raw is None:
            return None
        
        # Check if bit is set
        return bool(raw & (1 << self.entity_description.bit))

    # available property inherited from CoordinatorEntity
