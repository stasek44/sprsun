"""Sensor platform for SPRSUN Heat Pump."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SPRSUNDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class SPRSUNSensorEntityDescription(SensorEntityDescription):
    """Describes SPRSUN sensor entity."""

    value_fn: Callable[[dict], StateType]


SENSORS: tuple[SPRSUNSensorEntityDescription, ...] = (
    # Temperature sensors
    SPRSUNSensorEntityDescription(
        key="inlet_temp",
        translation_key="inlet_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda data: data.get("inlet_temp"),
    ),
    SPRSUNSensorEntityDescription(
        key="outlet_temp",
        translation_key="outlet_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda data: data.get("outlet_temp"),
    ),
    SPRSUNSensorEntityDescription(
        key="hotwater_temp",
        translation_key="hotwater_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda data: data.get("hotwater_temp"),
    ),
    SPRSUNSensorEntityDescription(
        key="ambi_temp",
        translation_key="ambi_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda data: data.get("ambi_temp"),
    ),
    SPRSUNSensorEntityDescription(
        key="suct_gas_temp",
        translation_key="suct_gas_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda data: data.get("suct_gas_temp"),
    ),
    SPRSUNSensorEntityDescription(
        key="coil_temp",
        translation_key="coil_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda data: data.get("coil_temp"),
    ),
    SPRSUNSensorEntityDescription(
        key="exhaust_temp",
        translation_key="exhaust_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=0,
        value_fn=lambda data: data.get("exhaust_temp"),
    ),
    SPRSUNSensorEntityDescription(
        key="driving_temp",
        translation_key="driving_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda data: data.get("driving_temp"),
    ),
    SPRSUNSensorEntityDescription(
        key="evap_temp",
        translation_key="evap_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda data: data.get("evap_temp"),
    ),
    SPRSUNSensorEntityDescription(
        key="cond_temp",
        translation_key="cond_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda data: data.get("cond_temp"),
    ),
    # System status
    SPRSUNSensorEntityDescription(
        key="compressor_runtime",
        translation_key="compressor_runtime",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfTime.HOURS,
        value_fn=lambda data: data.get("compressor_runtime"),
    ),
    SPRSUNSensorEntityDescription(
        key="cop",
        translation_key="cop",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: data.get("cop"),
    ),
    # Electrical measurements
    SPRSUNSensorEntityDescription(
        key="ac_voltage",
        translation_key="ac_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        value_fn=lambda data: data.get("ac_voltage"),
    ),
    SPRSUNSensorEntityDescription(
        key="ac_current",
        translation_key="ac_current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=1,
        value_fn=lambda data: data.get("ac_current"),
    ),
    SPRSUNSensorEntityDescription(
        key="dc_bus_voltage",
        translation_key="dc_bus_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        value_fn=lambda data: data.get("dc_bus_voltage"),
    ),
    SPRSUNSensorEntityDescription(
        key="comp_current",
        translation_key="comp_current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=1,
        value_fn=lambda data: data.get("comp_current"),
    ),
    SPRSUNSensorEntityDescription(
        key="comp_frequency",
        translation_key="comp_frequency",
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        value_fn=lambda data: data.get("comp_frequency"),
    ),
    SPRSUNSensorEntityDescription(
        key="target_frequency",
        translation_key="target_frequency",
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        value_fn=lambda data: data.get("target_frequency"),
    ),
    # Flow and capacity
    SPRSUNSensorEntityDescription(
        key="pump_flow",
        translation_key="pump_flow",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="m³/h",
        suggested_display_precision=2,
        value_fn=lambda data: data.get("pump_flow"),
    ),
    SPRSUNSensorEntityDescription(
        key="heating_cooling_capacity",
        translation_key="heating_cooling_capacity",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda data: data.get("heating_cooling_capacity"),
    ),
    # Pressure
    SPRSUNSensorEntityDescription(
        key="suct_press",
        translation_key="suct_press",
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.BAR,
        suggested_display_precision=1,
        value_fn=lambda data: data.get("suct_press"),
    ),
    SPRSUNSensorEntityDescription(
        key="disch_press",
        translation_key="disch_press",
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.BAR,
        suggested_display_precision=1,
        value_fn=lambda data: data.get("disch_press"),
    ),
    # Component states
    SPRSUNSensorEntityDescription(
        key="eev1_step",
        translation_key="eev1_step",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("eev1_step"),
    ),
    SPRSUNSensorEntityDescription(
        key="eev2_step",
        translation_key="eev2_step",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("eev2_step"),
    ),
    SPRSUNSensorEntityDescription(
        key="dc_fan_1_speed",
        translation_key="dc_fan_1_speed",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("dc_fan_1_speed"),
    ),
    SPRSUNSensorEntityDescription(
        key="dc_fan_2_speed",
        translation_key="dc_fan_2_speed",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("dc_fan_2_speed"),
    ),
    SPRSUNSensorEntityDescription(
        key="dc_fan_target",
        translation_key="dc_fan_target",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("dc_fan_target"),
    ),
    SPRSUNSensorEntityDescription(
        key="dc_pump_speed",
        translation_key="dc_pump_speed",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("dc_pump_speed"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN sensor based on a config entry."""
    coordinator: SPRSUNDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        SPRSUNSensorEntity(coordinator, description)
        for description in SENSORS
    )


class SPRSUNSensorEntity(CoordinatorEntity[SPRSUNDataUpdateCoordinator], SensorEntity):
    """Defines a SPRSUN sensor entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SPRSUNDataUpdateCoordinator,
        description: SPRSUNSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description: SPRSUNSensorEntityDescription = description

        # Set unique_id
        self._attr_unique_id = (
            f"{coordinator.entry.entry_id}_{description.key}"
        )

        # Set device info to link entity to device
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)
