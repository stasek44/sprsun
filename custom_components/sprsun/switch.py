"""Switch platform for SPRSUN Heat Pump.

Switch entities control boolean settings via Modbus coils or registers.
Reads current values from shared data_cache.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    MANUFACTURER,
    MODEL,
    REG_CONTROL_MARK_1,
    REG_CONTROL_MARK_2,
)
from .modbus import SPRSUNModbusClient

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
    data = hass.data[DOMAIN][entry.entry_id]
    client = data["client"]
    data_cache = data["data_cache"]
    
    entities = [
        SPRSUNSwitch(data_cache, client, entry, description)
        for description in SWITCHES
    ]
    
    async_add_entities(entities)


class SPRSUNSwitch(SwitchEntity):
    """Representation of a SPRSUN switch entity.
    
    Reads from shared data_cache but writes directly via client.
    """

    _attr_has_entity_name = True
    entity_description: SPRSUNSwitchEntityDescription

    def __init__(
        self,
        data_cache: dict[int, int],
        client: SPRSUNModbusClient,
        entry: ConfigEntry,
        description: SPRSUNSwitchEntityDescription,
    ) -> None:
        """Initialize the switch entity."""
        self.entity_description = description
        self._data_cache = data_cache
        self._client = client
        self._entry = entry
        
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"{MANUFACTURER} {MODEL}",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

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
        
        raw = self._data_cache.get(self.entity_description.register)
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
            raw = self._data_cache.get(self.entity_description.register, 0)
            new_value = raw | (1 << self.entity_description.bit)
            success = self._client.write_register(
                self.entity_description.register,
                new_value,
            )
            if success:
                self._data_cache[self.entity_description.register] = new_value
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
            raw = self._data_cache.get(self.entity_description.register, 0)
            new_value = raw & ~(1 << self.entity_description.bit)
            success = self._client.write_register(
                self.entity_description.register,
                new_value,
            )
            if success:
                self._data_cache[self.entity_description.register] = new_value
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
        """Return True if entity is available."""
        # Switch is available if data_cache has been populated
        return len(self._data_cache) > 0
