"""Select platform for SPRSUN Heat Pump.

Select entities allow choosing from predefined options via Modbus.
Reads current values from climate._data_cache.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .climate import SPRSUNClimate
from .const import (
    DOMAIN,
    FAN_MODE_OPTIONS,
    MODE_CONTROL_OPTIONS,
    PUMP_MODE_OPTIONS,
    REG_FAN_MODE,
    REG_MODE_CONTROL,
    REG_PUMP_WORK_MODE,
    REG_UNIT_MODE,
    UNIT_MODE_OPTIONS,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class SPRSUNSelectEntityDescription(SelectEntityDescription):
    """Describes SPRSUN select entity."""

    register: int | None = None
    options_map: dict[int, str] | None = None


SELECTS: tuple[SPRSUNSelectEntityDescription, ...] = (
    SPRSUNSelectEntityDescription(
        key="unit_mode",
        name="Unit Mode",
        register=REG_UNIT_MODE,
        options_map=UNIT_MODE_OPTIONS,
    ),
    SPRSUNSelectEntityDescription(
        key="fan_mode",
        name="Fan Mode",
        register=REG_FAN_MODE,
        options_map=FAN_MODE_OPTIONS,
    ),
    SPRSUNSelectEntityDescription(
        key="pump_work_mode",
        name="Pump Work Mode",
        register=REG_PUMP_WORK_MODE,
        options_map=PUMP_MODE_OPTIONS,
    ),
    SPRSUNSelectEntityDescription(
        key="mode_control",
        name="Mode Control",
        register=REG_MODE_CONTROL,
        options_map=MODE_CONTROL_OPTIONS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN select entities."""
    # Get client for writes
    client = hass.data[DOMAIN][entry.entry_id]
    
    # Get climate entity to access _data_cache
    climate_entity = None
    for entity in hass.data["entity_platform"][entry.entry_id].values():
        for ent in entity.entities.values():
            if isinstance(ent, SPRSUNClimate):
                climate_entity = ent
                break
    
    if not climate_entity:
        _LOGGER.error("Climate entity not found, cannot set up selects")
        return
    
    entities = [
        SPRSUNSelect(climate_entity, client, entry, description)
        for description in SELECTS
    ]
    
    async_add_entities(entities)


class SPRSUNSelect(SelectEntity):
    """Representation of a SPRSUN select entity.
    
    Reads from climate entity's _data_cache but writes directly via client.
    """

    _attr_has_entity_name = True
    entity_description: SPRSUNSelectEntityDescription

    def __init__(
        self,
        climate_entity: SPRSUNClimate,
        client,
        entry: ConfigEntry,
        description: SPRSUNSelectEntityDescription,
    ) -> None:
        """Initialize the select entity."""
        self.entity_description = description
        self._climate = climate_entity
        self._client = client
        
        # Set available options from options_map
        if description.options_map:
            self._attr_options = list(description.options_map.values())
        
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = climate_entity.device_info

    @property
    def current_option(self) -> str | None:
        """Return the current option from cache."""
        if self.entity_description.register is None:
            return None
        
        raw = self._climate._data_cache.get(self.entity_description.register)
        if raw is None:
            return None
        
        # Map raw value to string option
        if self.entity_description.options_map:
            return self.entity_description.options_map.get(raw)
        
        return None

    async def async_select_option(self, option: str) -> None:
        """Select new option (async wrapper)."""
        await self.hass.async_add_executor_job(self._select_option, option)

    def _select_option(self, option: str) -> None:
        """Select new option (synchronous Modbus write)."""
        if self.entity_description.register is None:
            return
        
        # Find value for option string
        value = None
        if self.entity_description.options_map:
            for val, opt in self.entity_description.options_map.items():
                if opt == option:
                    value = val
                    break
        
        if value is None:
            _LOGGER.error("Unknown option %s for %s", option, self.entity_description.key)
            return
        
        # Write to Modbus
        success = self._client.write_register(
            self.entity_description.register,
            value,
        )
        
        if success:
            # Update cache
            self._climate._data_cache[self.entity_description.register] = value
        else:
            _LOGGER.error(
                "Failed to write %s to register 0x%04X",
                self.entity_description.key,
                self.entity_description.register,
            )

    @property
    def available(self) -> bool:
        """Return True if climate entity is available."""
        return self._climate.available
