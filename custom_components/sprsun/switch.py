"""Switch platform for SPRSUN Heat Pump.

Switch entities control boolean settings via Modbus.
Reads from coordinator, writes directly to Modbus.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    REG_CONTROL_MARK_1,
    REG_CONTROL_MARK_2,
)
from .coordinator import SPRSUNDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class SPRSUNSwitchEntityDescription(SwitchEntityDescription):
    """Describes SPRSUN switch entity."""

    register: int | None = None
    bit: int | None = None
    coil_address: int | None = None


SWITCHES: tuple[SPRSUNSwitchEntityDescription, ...] = (
    # Power control
    SPRSUNSwitchEntityDescription(
        key="power",
        name="Power",
        register=REG_CONTROL_MARK_1,
        bit=0,
    ),
    # Economic mode
    SPRSUNSwitchEntityDescription(
        key="economic_mode",
        name="Economic Mode",
        register=REG_CONTROL_MARK_1,
        bit=1,
    ),
    # Silent mode
    SPRSUNSwitchEntityDescription(
        key="silent_mode",
        name="Silent Mode",
        register=REG_CONTROL_MARK_1,
        bit=2,
    ),
    # Anti-legionella enable
    SPRSUNSwitchEntityDescription(
        key="antilegionella_enable",
        name="Anti-Legionella Enable",
        register=REG_CONTROL_MARK_2,
        bit=0,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN switch entities."""
    coordinator: SPRSUNDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        SPRSUNSwitch(coordinator, entry, description)
        for description in SWITCHES
    ]
    
    async_add_entities(entities)


class SPRSUNSwitch(CoordinatorEntity[SPRSUNDataUpdateCoordinator], SwitchEntity):
    """Representation of a SPRSUN switch entity.
    
    Reads from coordinator.data, writes directly to Modbus.
    """

    _attr_has_entity_name = True
    entity_description: SPRSUNSwitchEntityDescription

    def __init__(
        self,
        coordinator: SPRSUNDataUpdateCoordinator,
        entry: ConfigEntry,
        description: SPRSUNSwitchEntityDescription,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator)
        self.entity_description = description
        
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        # If coil address is specified, would need separate coil read
        # For now, we only support register bit switches
        if self.entity_description.register is None or self.entity_description.bit is None:
            return None
        
        raw = self.coordinator.data.get(self.entity_description.register)
        if raw is None:
            return None
        
        # Check if bit is set
        return bool(raw & (1 << self.entity_description.bit))

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the switch."""
        success = False
        
        if self.entity_description.coil_address is not None:
            # Write coil
            success = await self.hass.async_add_executor_job(
                self.coordinator.client.write_coil,
                self.entity_description.coil_address,
                True,
            )
        elif self.entity_description.register is not None and self.entity_description.bit is not None:
            # Set bit in register (read-modify-write)
            # CRITICAL: Read FRESH value from device, not cached coordinator.data
            # This prevents race condition when multiple bits in same register
            batch = await self.hass.async_add_executor_job(
                self.coordinator.client.read_batch,
                self.entity_description.register,
                1,
            )
            if not batch:
                _LOGGER.error("Failed to read register 0x%04X before turning on %s", 
                              self.entity_description.register, self.entity_description.key)
                return
            
            raw = batch[0]
            new_value = raw | (1 << self.entity_description.bit)
            success = await self.hass.async_add_executor_job(
                self.coordinator.client.write_register,
                self.entity_description.register,
                new_value,
            )
        
        if success:
            # Request immediate coordinator refresh
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to turn on %s", self.entity_description.key)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the switch."""
        success = False
        
        if self.entity_description.coil_address is not None:
            # Write coil
            success = await self.hass.async_add_executor_job(
                self.coordinator.client.write_coil,
                self.entity_description.coil_address,
                False,
            )
        elif self.entity_description.register is not None and self.entity_description.bit is not None:
            # Clear bit in register (read-modify-write)
            # CRITICAL: Read FRESH value from device, not cached coordinator.data
            # This prevents race condition when multiple bits in same register
            batch = await self.hass.async_add_executor_job(
                self.coordinator.client.read_batch,
                self.entity_description.register,
                1,
            )
            if not batch:
                _LOGGER.error("Failed to read register 0x%04X before turning off %s",
                              self.entity_description.register, self.entity_description.key)
                return
            
            raw = batch[0]
            new_value = raw & ~(1 << self.entity_description.bit)
            success = await self.hass.async_add_executor_job(
                self.coordinator.client.write_register,
                self.entity_description.register,
                new_value,
            )
        
        if success:
            # Request immediate coordinator refresh
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to turn off %s", self.entity_description.key)

    # available property inherited from CoordinatorEntity
