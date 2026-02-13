"""Number platform for SPRSUN Heat Pump.

Number entities allow setting numeric parameters via Modbus.
Reads from coordinator, writes directly to Modbus.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    COOLING_SETPOINT_MAX,
    COOLING_SETPOINT_MIN,
    DOMAIN,
    HEATING_SETPOINT_MAX,
    HEATING_SETPOINT_MIN,
    HOTWATER_SETPOINT_MAX,
    HOTWATER_SETPOINT_MIN,
    REG_COOLING_SETPOINT,
    REG_HEATING_SETPOINT,
    REG_HOTWATER_SETPOINT,
)
from .coordinator import SPRSUNDataUpdateCoordinator
from .modbus import decode_temperature, encode_temperature

_LOGGER = logging.getLogger(__name__)


@dataclass
class SPRSUNNumberEntityDescription(NumberEntityDescription):
    """Describes SPRSUN number entity."""

    register: int | None = None
    scale: float = 1.0
    signed: bool = False


NUMBERS: tuple[SPRSUNNumberEntityDescription, ...] = (
    # Heating setpoint
    SPRSUNNumberEntityDescription(
        key="heating_setpoint",
        name="Heating Setpoint",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=HEATING_SETPOINT_MIN,
        native_max_value=HEATING_SETPOINT_MAX,
        native_step=0.5,
        mode=NumberMode.BOX,
        register=REG_HEATING_SETPOINT,
        scale=0.1,
        signed=True,
    ),
    # Cooling setpoint
    SPRSUNNumberEntityDescription(
        key="cooling_setpoint",
        name="Cooling Setpoint",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=COOLING_SETPOINT_MIN,
        native_max_value=COOLING_SETPOINT_MAX,
        native_step=0.5,
        mode=NumberMode.BOX,
        register=REG_COOLING_SETPOINT,
        scale=0.1,
        signed=True,
    ),
    # Hot water setpoint
    SPRSUNNumberEntityDescription(
        key="hotwater_setpoint",
        name="Hot Water Setpoint",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=HOTWATER_SETPOINT_MIN,
        native_max_value=HOTWATER_SETPOINT_MAX,
        native_step=0.5,
        mode=NumberMode.BOX,
        register=REG_HOTWATER_SETPOINT,
        scale=0.1,
        signed=True,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN number entities."""
    coordinator: SPRSUNDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        SPRSUNNumber(coordinator, entry, description)
        for description in NUMBERS
    ]
    
    async_add_entities(entities)


class SPRSUNNumber(CoordinatorEntity[SPRSUNDataUpdateCoordinator], NumberEntity):
    """Representation of a SPRSUN number entity.
    
    Reads from coordinator.data, writes directly to Modbus.
    """

    _attr_has_entity_name = True
    entity_description: SPRSUNNumberEntityDescription

    def __init__(
        self,
        coordinator: SPRSUNDataUpdateCoordinator,
        entry: ConfigEntry,
        description: SPRSUNNumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self.entity_description = description
        
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> float | None:
        """Return the current value from coordinator data."""
        if self.entity_description.register is None:
            return None
        
        raw = self.coordinator.data.get(self.entity_description.register)
        if raw is None:
            return None
        
        # Decode temperature with scale
        if self.entity_description.device_class == NumberDeviceClass.TEMPERATURE:
            return decode_temperature(
                raw,
                self.entity_description.scale,
                self.entity_description.signed,
            )
        
        # Simple scaling for other numbers
        if self.entity_description.scale != 1.0:
            return raw * self.entity_description.scale
        
        return raw

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        if self.entity_description.register is None:
            return
        
        # Encode value
        if self.entity_description.device_class == NumberDeviceClass.TEMPERATURE:
            encoded = encode_temperature(
                value,
                self.entity_description.scale,
                self.entity_description.signed,
            )
        elif self.entity_description.scale != 1.0:
            encoded = int(value / self.entity_description.scale)
        else:
            encoded = int(value)
        
        # Write to Modbus (via executor to avoid blocking)
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_register,
            self.entity_description.register,
            encoded,
        )
        
        if success:
            # Request immediate coordinator refresh
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error(
                "Failed to write %s to register 0x%04X",
                self.entity_description.key,
                self.entity_description.register,
            )

    # available property inherited from CoordinatorEntity
