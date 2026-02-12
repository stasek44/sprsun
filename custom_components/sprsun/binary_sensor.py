"""Binary sensor platform for SPRSUN Heat Pump."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SPRSUNDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class SPRSUNBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes SPRSUN binary sensor entity."""

    value_fn: Callable[[dict], bool | None]


BINARY_SENSORS: tuple[SPRSUNBinarySensorEntityDescription, ...] = (
    # Output status
    SPRSUNBinarySensorEntityDescription(
        key="compressor",
        translation_key="compressor",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda data: data.get("output_symbol_1", {}).get(0),
    ),
    SPRSUNBinarySensorEntityDescription(
        key="fan",
        translation_key="fan",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda data: data.get("output_symbol_1", {}).get(5),
    ),
    SPRSUNBinarySensorEntityDescription(
        key="4way_valve",
        translation_key="4way_valve",
        value_fn=lambda data: data.get("output_symbol_1", {}).get(6),
    ),
    SPRSUNBinarySensorEntityDescription(
        key="water_pump",
        translation_key="water_pump",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda data: data.get("output_symbol_3", {}).get(6),
    ),
    SPRSUNBinarySensorEntityDescription(
        key="chassis_heating",
        translation_key="chassis_heating",
        device_class=BinarySensorDeviceClass.HEAT,
        value_fn=lambda data: data.get("output_symbol_2", {}).get(0),
    ),
    SPRSUNBinarySensorEntityDescription(
        key="heating_heater",
        translation_key="heating_heater",
        device_class=BinarySensorDeviceClass.HEAT,
        value_fn=lambda data: data.get("output_symbol_2", {}).get(5),
    ),
    SPRSUNBinarySensorEntityDescription(
        key="hotwater_heater",
        translation_key="hotwater_heater",
        device_class=BinarySensorDeviceClass.HEAT,
        value_fn=lambda data: data.get("output_symbol_2", {}).get(7),
    ),
    # Working status
    SPRSUNBinarySensorEntityDescription(
        key="hotwater_demand",
        translation_key="hotwater_demand",
        value_fn=lambda data: data.get("working_status", {}).get(0),
    ),
    SPRSUNBinarySensorEntityDescription(
        key="heating_demand",
        translation_key="heating_demand",
        value_fn=lambda data: data.get("working_status", {}).get(1),
    ),
    SPRSUNBinarySensorEntityDescription(
        key="cooling_demand",
        translation_key="cooling_demand",
        value_fn=lambda data: data.get("working_status", {}).get(5),
    ),
    SPRSUNBinarySensorEntityDescription(
        key="defrost",
        translation_key="defrost",
        value_fn=lambda data: data.get("working_status", {}).get(7),
    ),
    SPRSUNBinarySensorEntityDescription(
        key="alarm_stop",
        translation_key="alarm_stop",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: data.get("working_status", {}).get(6),
    ),
    # Failure sensors (examples - can be expanded)
    SPRSUNBinarySensorEntityDescription(
        key="tank_temp_sensor_failure",
        name="Tank temperature sensor failure",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: data.get("failure_symbol_1", {}).get(0),
    ),
    SPRSUNBinarySensorEntityDescription(
        key="ambient_temp_sensor_failure",
        name="Ambient temperature sensor failure",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: data.get("failure_symbol_1", {}).get(1),
    ),
    SPRSUNBinarySensorEntityDescription(
        key="coil_temp_sensor_failure",
        name="Coil temperature sensor failure",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: data.get("failure_symbol_1", {}).get(2),
    ),
    SPRSUNBinarySensorEntityDescription(
        key="outlet_temp_sensor_failure",
        name="Outlet temperature sensor failure",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: data.get("failure_symbol_1", {}).get(4),
    ),
    SPRSUNBinarySensorEntityDescription(
        key="high_voltage_fault",
        name="High voltage fault",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: data.get("failure_symbol_1", {}).get(5),
    ),
    SPRSUNBinarySensorEntityDescription(
        key="water_flow_failure",
        name="Water flow switch failure",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: data.get("failure_symbol_2", {}).get(0),
    ),
    SPRSUNBinarySensorEntityDescription(
        key="high_pressure_protection",
        name="High pressure protection",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: data.get("failure_symbol_5", {}).get(1),
    ),
    SPRSUNBinarySensorEntityDescription(
        key="low_pressure_protection",
        name="Low pressure protection",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: data.get("failure_symbol_5", {}).get(0),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN binary sensor based on a config entry."""
    coordinator: SPRSUNDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        SPRSUNBinarySensorEntity(coordinator, description)
        for description in BINARY_SENSORS
    )


class SPRSUNBinarySensorEntity(
    CoordinatorEntity[SPRSUNDataUpdateCoordinator], BinarySensorEntity
):
    """Defines a SPRSUN binary sensor entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SPRSUNDataUpdateCoordinator,
        description: SPRSUNBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description: SPRSUNBinarySensorEntityDescription = description

        # Set unique_id
        self._attr_unique_id = (
            f"{coordinator.entry.entry_id}_{description.key}"
        )

        # Set device info to link entity to device
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.entity_description.value_fn(self.coordinator.data)
