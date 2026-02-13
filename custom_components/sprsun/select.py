"""Select platform for SPRSUN Heat Pump.

Select entities allow choosing from predefined options via Modbus.
Reads from coordinator, writes directly to Modbus.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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
from .coordinator import SPRSUNDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class SPRSUNSelectEntityDescription(SelectEntityDescription):
    """Describes SPRSUN select entity."""

    register: int | None = None
    options_map: dict[int, str] | None = None


SELECTS: tuple[SPRSUNSelectEntityDescription, ...] = (
    # Unit mode
    SPRSUNSelectEntityDescription(
        key="unit_mode",
        name="Unit Mode",
        register=REG_UNIT_MODE,
        options_map=UNIT_MODE_OPTIONS,
    ),
    # Fan mode
    SPRSUNSelectEntityDescription(
        key="fan_mode",
        name="Fan Mode",
        register=REG_FAN_MODE,
        options_map=FAN_MODE_OPTIONS,
    ),
    # Mode control
    SPRSUNSelectEntityDescription(
        key="mode_control",
        name="Mode Control",
        register=REG_MODE_CONTROL,
        options_map=MODE_CONTROL_OPTIONS,
    ),
    # Pump work mode
    SPRSUNSelectEntityDescription(
        key="pump_work_mode",
        name="Pump Work Mode",
        register=REG_PUMP_WORK_MODE,
        options_map=PUMP_MODE_OPTIONS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN select entities."""
    coordinator: SPRSUNDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        SPRSUNSelect(coordinator, entry, description)
        for description in SELECTS
    ]
    
    async_add_entities(entities)


class SPRSUNSelect(CoordinatorEntity[SPRSUNDataUpdateCoordinator], SelectEntity):
    """Representation of a SPRSUN select entity.
    
    Reads from coordinator.data, writes directly to Modbus.
    """

    _attr_has_entity_name = True
    entity_description: SPRSUNSelectEntityDescription

    def __init__(
        self,
        coordinator: SPRSUNDataUpdateCoordinator,
        entry: ConfigEntry,
        description: SPRSUNSelectEntityDescription,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self.entity_description = description
        
        # Set available options from options_map
        if description.options_map:
            self._attr_options = list(description.options_map.values())
        
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def current_option(self) -> str | None:
        """Return the current option from coordinator data."""
        if self.entity_description.register is None:
            return None
        
        raw = self.coordinator.data.get(self.entity_description.register)
        if raw is None:
            return None
        
        # Map raw value to string option
        if self.entity_description.options_map:
            return self.entity_description.options_map.get(raw)
        
        return None

    async def async_select_option(self, option: str) -> None:
        """Select new option."""
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
        
        # Write to Modbus (via executor to avoid blocking)
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_register,
            self.entity_description.register,
            value,
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
