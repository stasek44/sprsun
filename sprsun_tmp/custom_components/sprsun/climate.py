"""Climate platform for SPRSUN Heat Pump."""
from __future__ import annotations

import logging

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SprsunDataUpdateCoordinator
from .const import (
    DOMAIN,
    MANUFACTURER,
    REG_COOLING_SETPOINT,
    REG_HEATING_SETPOINT,
    REG_HOTWATER_SETPOINT,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN climate entities."""
    coordinator: SprsunDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        SprsunClimate(coordinator, entry, "Heating", "heating", REG_HEATING_SETPOINT, 10, 55),
        SprsunClimate(coordinator, entry, "Cooling", "cooling", REG_COOLING_SETPOINT, 12, 30),
        SprsunClimate(coordinator, entry, "Hot Water", "hotwater", REG_HOTWATER_SETPOINT, 10, 55),
    ]

    async_add_entities(entities)


class SprsunClimate(CoordinatorEntity, ClimateEntity):
    """Climate entity for SPRSUN temperature control."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.AUTO]
    _attr_target_temperature_step = 0.5

    def __init__(
        self,
        coordinator: SprsunDataUpdateCoordinator,
        entry: ConfigEntry,
        name: str,
        key: str,
        register: int,
        min_temp: float,
        max_temp: float,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._attr_name = f"{entry.title} {name}"
        self._attr_unique_id = f"{entry.entry_id}_climate_{key}"
        self._key = key
        self._register = register
        self._attr_min_temp = min_temp
        self._attr_max_temp = max_temp
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": MANUFACTURER,
        }

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        # For now, always return AUTO since we don't have an on/off control per setpoint
        return HVACMode.AUTO

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        if not self.coordinator.data:
            return None
            
        if self._key == "heating":
            return self.coordinator.data.get("outlet_temp")
        elif self._key == "cooling":
            return self.coordinator.data.get("outlet_temp")
        elif self._key == "hotwater":
            return self.coordinator.data.get("hotwater_temp")
        
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        if self.coordinator.data:
            key = f"{self._key}_setpoint"
            return self.coordinator.data.get(key)
        return None

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode - not fully implemented."""
        # This would require writing to the unit mode register
        # For now, we focus on temperature control
        pass

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        # Convert to register value (multiply by 2 for 0.5°C resolution)
        register_value = int(temperature * 2)

        success = await self.hass.async_add_executor_job(
            self.coordinator.write_register, self._register, register_value
        )

        if success:
            # Update the coordinator data immediately
            if self.coordinator.data:
                key = f"{self._key}_setpoint"
                self.coordinator.data[key] = temperature
            # Request a refresh to confirm
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to write temperature to register %s", self._register)
