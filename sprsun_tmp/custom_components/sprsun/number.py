"""Number platform for SPRSUN Heat Pump."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfFrequency, UnitOfTime, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SprsunDataUpdateCoordinator
from .const import (
    DOMAIN,
    MANUFACTURER,
    REG_DEFROST_PERIOD_1,
    REG_DEFROST_PERIOD_2,
    REG_DEFROST_PERIOD_3,
    REG_HEAT_FREQ_R04,
    REG_HEAT_FREQ_R05,
    REG_PUMP_CYCLE,
    REG_PUMP_MIN_FREQ,
    REG_WATER_FREQ_R00,
    REG_WATER_FREQ_R01,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN number entities."""
    coordinator: SprsunDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        SprsunNumber(
            coordinator, entry,
            "Defrost Period 1", "defrost_period_1", REG_DEFROST_PERIOD_1,
            10, 120, 5, UnitOfTime.MINUTES
        ),
        SprsunNumber(
            coordinator, entry,
            "Defrost Period 2", "defrost_period_2", REG_DEFROST_PERIOD_2,
            10, 120, 5, UnitOfTime.MINUTES
        ),
        SprsunNumber(
            coordinator, entry,
            "Defrost Period 3", "defrost_period_3", REG_DEFROST_PERIOD_3,
            10, 120, 5, UnitOfTime.MINUTES
        ),
        SprsunNumber(
            coordinator, entry,
            "Pump Cycle", "pump_cycle", REG_PUMP_CYCLE,
            1, 120, 5, UnitOfTime.MINUTES
        ),
        SprsunNumber(
            coordinator, entry,
            "Pump Min Frequency", "pump_min_freq", REG_PUMP_MIN_FREQ,
            60, 100, 5, PERCENTAGE
        ),
        SprsunNumber(
            coordinator, entry,
            "DHW Freq (T>14°C)", "water_freq_r00", REG_WATER_FREQ_R00,
            30, 60, 1, UnitOfFrequency.HERTZ
        ),
        SprsunNumber(
            coordinator, entry,
            "DHW Freq (9-14°C)", "water_freq_r01", REG_WATER_FREQ_R01,
            30, 70, 1, UnitOfFrequency.HERTZ
        ),
        SprsunNumber(
            coordinator, entry,
            "Heating Freq (T>14°C)", "heat_freq_r04", REG_HEAT_FREQ_R04,
            30, 60, 1, UnitOfFrequency.HERTZ
        ),
        SprsunNumber(
            coordinator, entry,
            "Heating Freq (9-14°C)", "heat_freq_r05", REG_HEAT_FREQ_R05,
            30, 70, 1, UnitOfFrequency.HERTZ
        ),
    ]

    async_add_entities(entities)


class SprsunNumber(CoordinatorEntity, NumberEntity):
    """Number entity for SPRSUN parameters."""

    def __init__(
        self,
        coordinator: SprsunDataUpdateCoordinator,
        entry: ConfigEntry,
        name: str,
        key: str,
        register: int,
        min_value: float,
        max_value: float,
        step: float,
        unit: str,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_name = f"{entry.title} {name}"
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._key = key
        self._register = register
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = unit
        self._attr_mode = NumberMode.BOX
        self._attr_entity_category = EntityCategory.CONFIG
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": MANUFACTURER,
        }

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if self.coordinator.data and self._key in self.coordinator.data:
            return self.coordinator.data[self._key]
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        int_value = int(value)
        
        success = await self.hass.async_add_executor_job(
            self.coordinator.write_register, self._register, int_value
        )

        if success:
            # Update the coordinator data immediately
            if self.coordinator.data:
                self.coordinator.data[self._key] = int_value
            # Request a refresh to confirm
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to write to register %s", self._register)
