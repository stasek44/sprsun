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
        set_fn_register=0x00CC,  # FIX: Correct address from modbus_reference.md
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
        set_fn_register=0x00CB,  # FIX: Correct address from modbus_reference.md
        set_fn_scale=2.0,  # Scale: 0.5°C
    ),
    SPRSUNNumberEntityDescription(
        key="hotwater_setp",
        translation_key="hotwater_setp",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=35,
        native_max_value=65,
        native_step=0.5,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("hotwater_setp"),
        set_fn_register=0x00CA,  # FIX: Correct address from modbus_reference.md
        set_fn_scale=2.0,  # FIX: Scale is 0.5°C, so multiply by 2 for register value
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
        set_fn_register=0x00C6,  # Correct address
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
        set_fn_register=0x00C8,  # Correct address
        set_fn_scale=1.0,  # Scale: 1°C
    ),
    # Economic Mode - Heating Parameters
    SPRSUNNumberEntityDescription(
        key="eco_heat_ambi_1",
        translation_key="eco_heat_ambi_1",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-30,
        native_max_value=50,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_heat_ambi_1"),
        set_fn_register=0x0169,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_heat_ambi_2",
        translation_key="eco_heat_ambi_2",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-30,
        native_max_value=50,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_heat_ambi_2"),
        set_fn_register=0x016A,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_heat_ambi_3",
        translation_key="eco_heat_ambi_3",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-30,
        native_max_value=50,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_heat_ambi_3"),
        set_fn_register=0x016B,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_heat_ambi_4",
        translation_key="eco_heat_ambi_4",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-30,
        native_max_value=50,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_heat_ambi_4"),
        set_fn_register=0x016C,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_heat_temp_1",
        translation_key="eco_heat_temp_1",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=10,
        native_max_value=55,
        native_step=0.5,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_heat_temp_1"),
        set_fn_register=0x0175,
        set_fn_scale=2.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_heat_temp_2",
        translation_key="eco_heat_temp_2",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=10,
        native_max_value=55,
        native_step=0.5,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_heat_temp_2"),
        set_fn_register=0x0176,
        set_fn_scale=2.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_heat_temp_3",
        translation_key="eco_heat_temp_3",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=10,
        native_max_value=55,
        native_step=0.5,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_heat_temp_3"),
        set_fn_register=0x0177,
        set_fn_scale=2.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_heat_temp_4",
        translation_key="eco_heat_temp_4",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=10,
        native_max_value=55,
        native_step=0.5,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_heat_temp_4"),
        set_fn_register=0x0178,
        set_fn_scale=2.0,
    ),
    # Economic Mode - Hot Water Parameters
    SPRSUNNumberEntityDescription(
        key="eco_water_ambi_1",
        translation_key="eco_water_ambi_1",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-30,
        native_max_value=50,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_water_ambi_1"),
        set_fn_register=0x016D,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_water_ambi_2",
        translation_key="eco_water_ambi_2",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-30,
        native_max_value=50,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_water_ambi_2"),
        set_fn_register=0x016E,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_water_ambi_3",
        translation_key="eco_water_ambi_3",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-30,
        native_max_value=50,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_water_ambi_3"),
        set_fn_register=0x016F,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_water_ambi_4",
        translation_key="eco_water_ambi_4",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-30,
        native_max_value=50,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_water_ambi_4"),
        set_fn_register=0x0170,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_water_temp_1",
        translation_key="eco_water_temp_1",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=10,
        native_max_value=55,
        native_step=0.5,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_water_temp_1"),
        set_fn_register=0x0179,
        set_fn_scale=2.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_water_temp_2",
        translation_key="eco_water_temp_2",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=10,
        native_max_value=55,
        native_step=0.5,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_water_temp_2"),
        set_fn_register=0x017A,
        set_fn_scale=2.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_water_temp_3",
        translation_key="eco_water_temp_3",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=10,
        native_max_value=55,
        native_step=0.5,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_water_temp_3"),
        set_fn_register=0x017B,
        set_fn_scale=2.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_water_temp_4",
        translation_key="eco_water_temp_4",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=10,
        native_max_value=55,
        native_step=0.5,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_water_temp_4"),
        set_fn_register=0x017C,
        set_fn_scale=2.0,
    ),
    # Economic Mode - Cooling Parameters
    SPRSUNNumberEntityDescription(
        key="eco_cool_ambi_1",
        translation_key="eco_cool_ambi_1",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-30,
        native_max_value=50,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_cool_ambi_1"),
        set_fn_register=0x0171,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_cool_ambi_2",
        translation_key="eco_cool_ambi_2",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-30,
        native_max_value=50,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_cool_ambi_2"),
        set_fn_register=0x0172,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_cool_ambi_3",
        translation_key="eco_cool_ambi_3",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-30,
        native_max_value=50,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_cool_ambi_3"),
        set_fn_register=0x0173,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_cool_ambi_4",
        translation_key="eco_cool_ambi_4",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-30,
        native_max_value=50,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_cool_ambi_4"),
        set_fn_register=0x0174,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_cool_temp_1",
        translation_key="eco_cool_temp_1",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=12,
        native_max_value=30,
        native_step=0.5,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_cool_temp_1"),
        set_fn_register=0x017D,
        set_fn_scale=2.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_cool_temp_2",
        translation_key="eco_cool_temp_2",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=12,
        native_max_value=30,
        native_step=0.5,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_cool_temp_2"),
        set_fn_register=0x017E,
        set_fn_scale=2.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_cool_temp_3",
        translation_key="eco_cool_temp_3",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=12,
        native_max_value=30,
        native_step=0.5,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_cool_temp_3"),
        set_fn_register=0x017F,
        set_fn_scale=2.0,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_cool_temp_4",
        translation_key="eco_cool_temp_4",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=12,
        native_max_value=30,
        native_step=0.5,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("eco_cool_temp_4"),
        set_fn_register=0x0180,
        set_fn_scale=2.0,
    ),
    # General Configuration Parameters
    SPRSUNNumberEntityDescription(
        key="hotwater_heater_delay",
        translation_key="hotwater_heater_delay",
        native_unit_of_measurement="min",
        native_min_value=1,
        native_max_value=60,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("hotwater_heater_delay"),
        set_fn_register=0x0181,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="heating_heater_delay",
        translation_key="heating_heater_delay",
        native_unit_of_measurement="min",
        native_min_value=1,
        native_max_value=60,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("heating_heater_delay"),
        set_fn_register=0x0182,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="hotwater_heater_ext_temp",
        translation_key="hotwater_heater_ext_temp",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-30,
        native_max_value=30,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("hotwater_heater_ext_temp"),
        set_fn_register=0x0183,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="heating_heater_ext_temp",
        translation_key="heating_heater_ext_temp",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-30,
        native_max_value=30,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("heating_heater_ext_temp"),
        set_fn_register=0x0184,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="pump_start_interval",
        translation_key="pump_start_interval",
        native_unit_of_measurement="min",
        native_min_value=1,
        native_max_value=120,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("pump_start_interval"),
        set_fn_register=0x0185,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="dc_pump_delta_temp",
        translation_key="dc_pump_delta_temp",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=5,
        native_max_value=30,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("dc_pump_delta_temp"),
        set_fn_register=0x018D,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="ambtemp_switch_setp",
        translation_key="ambtemp_switch_setp",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-20,
        native_max_value=30,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("ambtemp_switch_setp"),
        set_fn_register=0x0192,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="ambtemp_diff",
        translation_key="ambtemp_diff",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=1,
        native_max_value=10,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("ambtemp_diff"),
        set_fn_register=0x0193,
        set_fn_scale=1.0,
    ),
    # Antilegionella Configuration
    SPRSUNNumberEntityDescription(
        key="antilegionella_temp",
        translation_key="antilegionella_temp",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=30,
        native_max_value=70,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("antilegionella_temp"),
        set_fn_register=0x019A,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="antilegionella_weekday",
        translation_key="antilegionella_weekday",
        native_min_value=0,
        native_max_value=6,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("antilegionella_weekday"),
        set_fn_register=0x019B,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="antilegionella_start_hour",
        translation_key="antilegionella_start_hour",
        native_min_value=0,
        native_max_value=23,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("antilegionella_start_hour"),
        set_fn_register=0x019C,
        set_fn_scale=1.0,
    ),
    SPRSUNNumberEntityDescription(
        key="antilegionella_end_hour",
        translation_key="antilegionella_end_hour",
        native_min_value=0,
        native_max_value=23,
        native_step=1.0,
        mode=NumberMode.BOX,
        value_fn=lambda data: data.get("antilegionella_end_hour"),
        set_fn_register=0x019D,
        set_fn_scale=1.0,
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
        
        # Handle signed 16-bit conversion for negative values
        if scaled_value < 0:
            scaled_value += 65536
        scaled_value = scaled_value & 0xFFFF
        
        # Write to the register
        success = await self.coordinator.client.write_register(
            self.entity_description.set_fn_register,
            scaled_value,
        )

        if success:
            # Trigger an immediate data refresh after setting the value
            await self.coordinator.async_request_refresh()
