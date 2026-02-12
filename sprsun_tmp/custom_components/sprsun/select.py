"""Select platform for SPRSUN Heat Pump."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SprsunDataUpdateCoordinator
from .const import (
    DOMAIN,
    FAN_MODE_NAMES,
    MANUFACTURER,
    PUMP_MODE_NAMES,
    REG_FAN_MODE,
    REG_PUMP_MODE,
    REG_UNIT_MODE,
    UNIT_MODE_NAMES,
    UnitMode,
    FanMode,
    PumpMode,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN select entities."""
    coordinator: SprsunDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        SprsunUnitModeSelect(coordinator, entry),
        SprsunFanModeSelect(coordinator, entry),
        SprsunPumpModeSelect(coordinator, entry),
    ]

    async_add_entities(entities)


class SprsunSelectBase(CoordinatorEntity, SelectEntity):
    """Base class for SPRSUN select entities."""

    def __init__(
        self,
        coordinator: SprsunDataUpdateCoordinator,
        entry: ConfigEntry,
        name: str,
        key: str,
        register: int,
        options_dict: dict,
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator)
        self._attr_name = f"{entry.title} {name}"
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._key = key
        self._register = register
        self._options_dict = options_dict
        self._attr_options = list(options_dict.values())
        self._attr_entity_category = EntityCategory.CONFIG
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": MANUFACTURER,
        }

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        if self.coordinator.data and self._key in self.coordinator.data:
            value = self.coordinator.data[self._key]
            return self._options_dict.get(value)
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Find the numeric value for this option
        value = None
        for key, val in self._options_dict.items():
            if val == option:
                value = key
                break

        if value is None:
            _LOGGER.error("Invalid option: %s", option)
            return

        # Write to Modbus register
        success = await self.hass.async_add_executor_job(
            self.coordinator.write_register, self._register, value
        )

        if success:
            # Update the coordinator data immediately
            if self.coordinator.data:
                self.coordinator.data[self._key] = value
            # Request a refresh to confirm
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to write to register %s", self._register)


class SprsunUnitModeSelect(SprsunSelectBase):
    """Select entity for unit operating mode (P06)."""

    def __init__(
        self,
        coordinator: SprsunDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the unit mode select."""
        super().__init__(
            coordinator,
            entry,
            "Unit Mode",
            "unit_mode",
            REG_UNIT_MODE,
            UNIT_MODE_NAMES,
        )
        self._attr_icon = "mdi:heat-pump"

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        attrs = {}
        if self.coordinator.data:
            mode = self.coordinator.data.get("unit_mode")
            attrs["mode_value"] = mode
            attrs["register"] = REG_UNIT_MODE
            
            # Add helpful information about what's actually running
            working_status = self.coordinator.data.get("working_status", 0)
            attrs["hotwater_demand"] = bool(working_status & 0x01)
            attrs["heating_demand"] = bool(working_status & 0x02)
            attrs["cooling_demand"] = bool(working_status & 0x20)
            
        return attrs


class SprsunFanModeSelect(SprsunSelectBase):
    """Select entity for fan/compressor mode (P07)."""

    def __init__(
        self,
        coordinator: SprsunDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the fan mode select."""
        super().__init__(
            coordinator,
            entry,
            "Fan Mode",
            "fan_mode",
            REG_FAN_MODE,
            FAN_MODE_NAMES,
        )
        self._attr_icon = "mdi:fan"


class SprsunPumpModeSelect(SprsunSelectBase):
    """Select entity for pump operating mode (G02)."""

    def __init__(
        self,
        coordinator: SprsunDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the pump mode select."""
        super().__init__(
            coordinator,
            entry,
            "Pump Mode",
            "pump_mode",
            REG_PUMP_MODE,
            PUMP_MODE_NAMES,
        )
        self._attr_icon = "mdi:pump"
