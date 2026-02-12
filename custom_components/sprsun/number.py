"""Number platform for SPRSUN Heat Pump."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SPRSUNDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class SPRSUNNumberEntityDescription(NumberEntityDescription):
    """Describes SPRSUN number entity."""

    value_fn: Callable[[dict], float | None]
    set_fn_register: int
    set_fn_scale: float = 1.0


NUMBERS: tuple[SPRSUNNumberEntityDescription, ...] = (
    SPRSUNNumberEntityDescription(
        key="heating_setp",
        translation_key="heating_setp",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=15,
        native_max_value=55,
        native_step=0.5,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("heating_setp"),
        set_fn_register=0x001D,
        set_fn_scale=2.0,  # Scale: 0.5°C (register value = actual * 2)
    ),
    SPRSUNNumberEntityDescription(
        key="cooling_setp",
        translation_key="cooling_setp",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=5,
        native_max_value=25,
        native_step=0.5,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("cooling_setp"),
        set_fn_register=0x001E,
        set_fn_scale=2.0,  # Scale: 0.5°C
    ),
    SPRSUNNumberEntityDescription(
        key="hotwater_setp",
        translation_key="hotwater_setp",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=35,
        native_max_value=65,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("hotwater_setp"),
        set_fn_register=0x001F,
        set_fn_scale=1.0,  # Scale: 1°C
    ),
    SPRSUNNumberEntityDescription(
        key="cooling_heating_temp_diff",
        translation_key="cooling_heating_temp_diff",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=2,
        native_max_value=10,
        native_step=0.5,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("cooling_heating_temp_diff"),
        set_fn_register=0x0024,
        set_fn_scale=2.0,  # Scale: 0.5°C
    ),
    SPRSUNNumberEntityDescription(
        key="hotwater_temp_diff",
        translation_key="hotwater_temp_diff",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=2,
        native_max_value=10,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("hotwater_temp_diff"),
        set_fn_register=0x0025,
        set_fn_scale=1.0,  # Scale: 1°C
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN number based on a config entry."""
    coordinator: SPRSUNDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        SPRSUNNumberEntity(coordinator, description) for description in NUMBERS
    )


class SPRSUNNumberEntity(
    CoordinatorEntity[SPRSUNDataUpdateCoordinator], NumberEntity
):
    """Defines a SPRSUN number entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SPRSUNDataUpdateCoordinator,
        description: SPRSUNNumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self.entity_description: SPRSUNNumberEntityDescription = description

        # Set unique_id
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"

        # Set device info to link entity to device
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> float | None:
        """Return the entity value to represent the entity state."""
        return self.entity_description.value_fn(self.coordinator.data)

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        # Scale the value according to register specification
        scaled_value = int(value * self.entity_description.set_fn_scale)
        
        # Write to the register
        success = await self.coordinator.client.write_register(
            self.entity_description.set_fn_register,
            scaled_value,
        )

        if success:
            # Trigger an immediate data refresh after setting the value
            await self.coordinator.async_request_refresh()
