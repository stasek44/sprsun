"""Sensor platform for SPRSUN Heat Pump.

Sensors read from coordinator.data (no direct Modbus access).
"""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import SPRSUNDataUpdateCoordinator
from .modbus import decode_temperature

_LOGGER = logging.getLogger(__name__)


@dataclass
class SPRSUNSensorEntityDescription(SensorEntityDescription):
    """Describes SPRSUN sensor entity."""

    register: int | None = None
    scale: float = 1.0
    signed: bool = False
    decode_fn: Callable[[int], float | int] | None = None


SENSORS: tuple[SPRSUNSensorEntityDescription, ...] = (
    # Temperature sensors (scale=0.1 means multiply raw by 0.1, i.e., raw 235 = 23.5°C)
    SPRSUNSensorEntityDescription(
        key="inlet_temp",
        name="Water Inlet Temperature",
        register=0x000E,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        scale=0.1,
        signed=True,
    ),
    SPRSUNSensorEntityDescription(
        key="hotwater_temp",
        name="Hot Water Temperature",
        register=0x000F,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        scale=0.1,
        signed=True,
    ),
    SPRSUNSensorEntityDescription(
        key="ambient_temp",
        name="Ambient Temperature",
        register=0x0011,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        scale=0.1,
        signed=True,
    ),
    SPRSUNSensorEntityDescription(
        key="outlet_temp",
        name="Water Outlet Temperature",
        register=0x0012,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        scale=0.1,
        signed=True,
    ),
    SPRSUNSensorEntityDescription(
        key="suction_gas_temp",
        name="Suction Gas Temperature",
        register=0x0015,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        scale=0.1,
        signed=True,
    ),
    SPRSUNSensorEntityDescription(
        key="coil_temp",
        name="Coil Temperature",
        register=0x0016,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        scale=0.1,
        signed=True,
    ),
    SPRSUNSensorEntityDescription(
        key="exhaust_temp",
        name="Exhaust Temperature",
        register=0x001B,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        scale=0.1,
        signed=True,
    ),
    SPRSUNSensorEntityDescription(
        key="evaporator_temp",
        name="Evaporator Temperature",
        register=0x0028,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        scale=0.1,
        signed=True,
    ),
    SPRSUNSensorEntityDescription(
        key="condenser_temp",
        name="Condenser Temperature",
        register=0x0029,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        scale=0.1,
        signed=True,
    ),
    
    # Performance metrics (scale is DIVISOR for non-temperature)
    SPRSUNSensorEntityDescription(
        key="cop",
        name="Coefficient of Performance",
        register=0x0001,
        state_class=SensorStateClass.MEASUREMENT,
        scale=100,  # raw 350 / 100 = 3.50
    ),
    SPRSUNSensorEntityDescription(
        key="heating_cooling_capacity",
        name="Heating/Cooling Capacity",
        register=0x0019,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        scale=100,
    ),
    
    # Electrical measurements (scale is DIVISOR)
    SPRSUNSensorEntityDescription(
        key="ac_voltage",
        name="AC Voltage",
        register=0x0017,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    SPRSUNSensorEntityDescription(
        key="ac_current",
        name="AC Current",
        register=0x001A,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        scale=10,  # raw 125 / 10 = 12.5A
    ),
    SPRSUNSensorEntityDescription(
        key="dc_bus_voltage",
        name="DC Bus Voltage",
        register=0x0021,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    SPRSUNSensorEntityDescription(
        key="compressor_current",
        name="Compressor Current",
        register=0x0023,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        scale=10,
    ),
    
    # Compressor & Fan
    SPRSUNSensorEntityDescription(
        key="compressor_frequency",
        name="Compressor Frequency",
        register=0x001E,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
    ),
    SPRSUNSensorEntityDescription(
        key="target_frequency",
        name="Target Frequency",
        register=0x0024,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
    ),
    SPRSUNSensorEntityDescription(
        key="dc_fan_1_speed",
        name="DC Fan 1 Speed",
        register=0x0026,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
    ),
    SPRSUNSensorEntityDescription(
        key="dc_fan_2_speed",
        name="DC Fan 2 Speed",
        register=0x0027,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
    ),
    
    # Flow & Valves
    SPRSUNSensorEntityDescription(
        key="pump_flow",
        name="Pump Flow Rate",
        register=0x0018,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
        scale=10,
    ),
    SPRSUNSensorEntityDescription(
        key="eev1_step",
        name="EEV1 Opening",
        register=0x001C,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
    ),
    SPRSUNSensorEntityDescription(
        key="eev2_step",
        name="EEV2 Opening",
        register=0x001D,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
    ),
    
    # Runtime
    SPRSUNSensorEntityDescription(
        key="compressor_runtime",
        name="Compressor Runtime",
        register=0x0000,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="h",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN sensor entities."""
    coordinator: SPRSUNDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        SPRSUNSensor(coordinator, entry, description)
        for description in SENSORS
    ]
    
    async_add_entities(entities)


class SPRSUNSensor(CoordinatorEntity[SPRSUNDataUpdateCoordinator], SensorEntity):
    """Representation of a SPRSUN sensor.
    
    Reads from coordinator.data (no direct Modbus access).
    """

    _attr_has_entity_name = True
    entity_description: SPRSUNSensorEntityDescription

    def __init__(
        self,
        coordinator: SPRSUNDataUpdateCoordinator,
        entry: ConfigEntry,
        description: SPRSUNSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> float | int | None:
        """Return the sensor value from coordinator data."""
        if self.entity_description.register is None:
            return None
        
        raw = self.coordinator.data.get(self.entity_description.register)
        if raw is None:
            return None
        
        # Use custom decode function if provided
        if self.entity_description.decode_fn:
            return self.entity_description.decode_fn(raw)
        
        # Temperature sensors: use decode_temperature (scale is MULTIPLIER)
        # Example: raw=235, scale=0.1 → 235 * 0.1 = 23.5°C
        if self.entity_description.device_class == SensorDeviceClass.TEMPERATURE:
            return decode_temperature(
                raw,
                self.entity_description.scale,
                self.entity_description.signed,
            )
        
        # Non-temperature sensors: scale is DIVISOR
        # Example: COP raw=350, scale=100 → 350 / 100 = 3.50
        if self.entity_description.scale != 1.0:
            return raw / self.entity_description.scale
        
        return raw

    # available property inherited from CoordinatorEntity
