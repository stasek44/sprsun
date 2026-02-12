"""Switch platform for SPRSUN Heat Pump.

Switch entities control boolean settings via Modbus coils or registers.
Reads current values from climate._data_cache.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .climate import SPRSUNClimate
from .const import DOMAIN, REG_CONTROL_MARK_1, REG_CONTROL_MARK_2

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
        _LOGGER.error("Climate entity not found, cannot set up switches")
        return
    
    entities = [
        SPRSUNSwitch(climate_entity, client, entry, description)
        for description in SWITCHES
    ]
    
    async_add_entities(entities)


class SPRSUNSwitch(SwitchEntity):
    """Representation of a SPRSUN switch entity.
    
    Reads from climate entity's _data_cache but writes directly via client.
    """

    _attr_has_entity_name = True
    entity_description: SPRSUNSwitchEntityDescription

    def __init__(
        self,
        climate_entity: SPRSUNClimate,
        client,
        entry: ConfigEntry,
        description: SPRSUNSwitchEntityDescription,
    ) -> None:
        """Initialize the switch entity."""
        self.entity_description = description
        self._climate = climate_entity
        self._client = client
        
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = climate_entity.device_info

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        # If coil address is specified, use it directly
        if self.entity_description.coil_address is not None:
            # Coil state would need separate read - for now use cache
            return None
        
        # Otherwise check bit in register
        if self.entity_description.register is None or self.entity_description.bit is None:
            return None
        
        raw = self._climate._data_cache.get(self.entity_description.register)
        if raw is None:
            return None
        
        # Check if bit is set
        return bool(raw & (1 << self.entity_description.bit))

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the switch (async wrapper)."""
        await self.hass.async_add_executor_job(self._turn_on)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the switch (async wrapper)."""
        await self.hass.async_add_executor_job(self._turn_off)

    def _turn_on(self) -> None:
        """Turn on the switch (synchronous Modbus write)."""
        if self.entity_description.coil_address is not None:
            # Write coil
            success = self._client.write_coil(
                self.entity_description.coil_address,
                True,
            )
        elif self.entity_description.register is not None and self.entity_description.bit is not None:
            # Set bit in register
            raw = self._climate._data_cache.get(self.entity_description.register, 0)
            new_value = raw | (1 << self.entity_description.bit)
            success = self._client.write_register(
                self.entity_description.register,
                new_value,
            )
            if success:
                self._climate._data_cache[self.entity_description.register] = new_value
        else:
            _LOGGER.error("Switch %s has no register or coil defined", self.entity_description.key)
            return
        
        if not success:
            _LOGGER.error(
                "Failed to turn on %s",
                self.entity_description.key,
            )

    def _turn_off(self) -> None:
        """Turn off the switch (synchronous Modbus write)."""
        if self.entity_description.coil_address is not None:
            # Write coil
            success = self._client.write_coil(
                self.entity_description.coil_address,
                False,
            )
        elif self.entity_description.register is not None and self.entity_description.bit is not None:
            # Clear bit in register
            raw = self._climate._data_cache.get(self.entity_description.register, 0)
            new_value = raw & ~(1 << self.entity_description.bit)
            success = self._client.write_register(
                self.entity_description.register,
                new_value,
            )
            if success:
                self._climate._data_cache[self.entity_description.register] = new_value
        else:
            _LOGGER.error("Switch %s has no register or coil defined", self.entity_description.key)
            return
        
        if not success:
            _LOGGER.error(
                "Failed to turn off %s",
                self.entity_description.key,
            )

    @property
    def available(self) -> bool:
        """Return True if climate entity is available."""
        return self._climate.available
