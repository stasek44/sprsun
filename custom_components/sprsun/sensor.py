"""Sensor platform for SPRSUN Heat Pump."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfTemperature,
    UnitOfTime,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SprsunDataUpdateCoordinator
from .const import DOMAIN, MANUFACTURER


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN sensor entities."""
    coordinator: SprsunDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        # Temperature sensors
        SprsunTemperatureSensor(coordinator, entry, "Inlet Temperature", "inlet_temp"),
        SprsunTemperatureSensor(coordinator, entry, "Hot Water Temperature", "hotwater_temp"),
        SprsunTemperatureSensor(coordinator, entry, "Ambient Temperature", "ambient_temp"),
        SprsunTemperatureSensor(coordinator, entry, "Outlet Temperature", "outlet_temp"),
        SprsunTemperatureSensor(coordinator, entry, "Suction Gas Temperature", "suct_gas_temp"),
        SprsunTemperatureSensor(coordinator, entry, "Coil Temperature", "coil_temp"),
        SprsunTemperatureSensor(coordinator, entry, "Exhaust Temperature", "exhaust_temp"),
        SprsunTemperatureSensor(coordinator, entry, "Evaporator Temperature", "evap_temp"),
        SprsunTemperatureSensor(coordinator, entry, "Condenser Temperature", "cond_temp"),
        
        # Frequency/Speed sensors
        SprsunFrequencySensor(coordinator, entry, "Compressor Frequency", "comp_frequency"),
        SprsunFrequencySensor(coordinator, entry, "Target Frequency", "target_frequency"),
        SprsunSensor(coordinator, entry, "DC Pump Speed", "dc_pump_speed", PERCENTAGE, SensorStateClass.MEASUREMENT),
        SprsunSensor(coordinator, entry, "DC Fan 1 Speed", "dc_fan_1_speed", "rpm", SensorStateClass.MEASUREMENT),
        SprsunSensor(coordinator, entry, "DC Fan 2 Speed", "dc_fan_2_speed", "rpm", SensorStateClass.MEASUREMENT),
        
        # Electrical sensors
        SprsunSensor(coordinator, entry, "Compressor Current", "comp_current", UnitOfElectricCurrent.AMPERE, SensorStateClass.MEASUREMENT, SensorDeviceClass.CURRENT),
        SprsunSensor(coordinator, entry, "DC Bus Voltage", "dc_bus_voltage", UnitOfElectricPotential.VOLT, SensorStateClass.MEASUREMENT, SensorDeviceClass.VOLTAGE),
        
        # Runtime sensor
        SprsunSensor(coordinator, entry, "Compressor Runtime", "compressor_runtime", UnitOfTime.MINUTES, SensorStateClass.TOTAL_INCREASING, SensorDeviceClass.DURATION),
    ]

    async_add_entities(entities)


class SprsunSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for SPRSUN sensor entities."""

    def __init__(
        self,
        coordinator: SprsunDataUpdateCoordinator,
        entry: ConfigEntry,
        name: str,
        key: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = f"{entry.title} {name}"
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._key = key
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": MANUFACTURER,
        }


class SprsunSensor(SprsunSensorBase):
    """Generic SPRSUN sensor."""

    def __init__(
        self,
        coordinator: SprsunDataUpdateCoordinator,
        entry: ConfigEntry,
        name: str,
        key: str,
        unit: str | None = None,
        state_class: SensorStateClass | None = None,
        device_class: SensorDeviceClass | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, name, key)
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = state_class
        self._attr_device_class = device_class

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and self._key in self.coordinator.data:
            return self.coordinator.data[self._key]
        return None


class SprsunTemperatureSensor(SprsunSensorBase):
    """Temperature sensor for SPRSUN."""

    def __init__(
        self,
        coordinator: SprsunDataUpdateCoordinator,
        entry: ConfigEntry,
        name: str,
        key: str,
    ) -> None:
        """Initialize the temperature sensor."""
        super().__init__(coordinator, entry, name, key)
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the temperature value."""
        if self.coordinator.data and self._key in self.coordinator.data:
            return self.coordinator.data[self._key]
        return None


class SprsunFrequencySensor(SprsunSensorBase):
    """Frequency sensor for SPRSUN."""

    def __init__(
        self,
        coordinator: SprsunDataUpdateCoordinator,
        entry: ConfigEntry,
        name: str,
        key: str,
    ) -> None:
        """Initialize the frequency sensor."""
        super().__init__(coordinator, entry, name, key)
        self._attr_native_unit_of_measurement = UnitOfFrequency.HERTZ
        self._attr_device_class = SensorDeviceClass.FREQUENCY
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the frequency value."""
        if self.coordinator.data and self._key in self.coordinator.data:
            return self.coordinator.data[self._key]
        return None
