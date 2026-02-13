"""Climate platform for SPRSUN Heat Pump.

Main entity that polls Modbus and updates shared _data_cache for all platforms.
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    MANUFACTURER,
    MODEL,
    REG_AMBIENT_TEMP,
    REG_ANTILEGIONELLA_END_HOUR,
    REG_ANTILEGIONELLA_START_HOUR,
    REG_ANTILEGIONELLA_TEMP,
    REG_ANTILEGIONELLA_WEEKDAY,
    REG_CONTROL_MARK_1,
    REG_CONTROL_MARK_2,
    REG_COOLING_SETPOINT,
    REG_DC_PUMP_TEMP_DIFF,
    REG_ECO_COOL_AMBI_1,
    REG_ECO_COOL_TEMP_1,
    REG_ECO_HEAT_AMBI_1,
    REG_ECO_HEAT_TEMP_1,
    REG_ECO_WATER_AMBI_1,
    REG_ECO_WATER_TEMP_1,
    REG_FAN_MODE,
    REG_HEATING_HEATER_AMBIENT,
    REG_HEATING_HEATER_DELAY,
    REG_HEATING_SETPOINT,
    REG_HOTWATER_HEATER_AMBIENT,
    REG_HOTWATER_HEATER_DELAY,
    REG_HOTWATER_SETPOINT,
    REG_HOTWATER_TEMP,
    REG_INLET_TEMP,
    REG_MODE_CONTROL,
    REG_OUTLET_TEMP,
    REG_PARAMETER_MARKER,
    REG_PUMP_STARTUP_INTERVAL,
    REG_PUMP_WORK_MODE,
    REG_TEMP_DIFF_COOLING_HEATING,
    REG_UNIT_MODE,
    UNIT_MODE_COOLING,
    UNIT_MODE_COOLING_DHW,
    UNIT_MODE_DHW,
    UNIT_MODE_HEATING,
    UNIT_MODE_HEATING_DHW,
)
from .modbus import SPRSUNModbusClient, decode_temperature

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN climate entity."""
    data = hass.data[DOMAIN][entry.entry_id]
    client: SPRSUNModbusClient = data["client"]
    async_add_entities([SPRSUNClimate(client, entry)])


class SPRSUNClimate(ClimateEntity):
    """Representation of SPRSUN heat pump climate entity.
    
    Main entity with should_poll=True that updates shared _data_cache.
    """

    _attr_has_entity_name = True
    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_hvac_modes = [
        HVACMode.OFF,
        HVACMode.HEAT,
        HVACMode.COOL,
        HVACMode.HEAT_COOL,
    ]
    
    # Enable polling (synchronous updates)
    _attr_should_poll = True

    def __init__(self, client: SPRSUNModbusClient, entry: ConfigEntry) -> None:
        """Initialize the climate entity."""
        self._client = client
        self._entry = entry
        self._hass = None  # Set in async_added_to_hass
        self._data_cache = None  # Set in async_added_to_hass
        
        # Device info
        self._attr_unique_id = f"{entry.entry_id}_climate"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"{MANUFACTURER} {MODEL}",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }
        
        # State variables
        self._attr_current_temperature: float | None = None
        self._attr_target_temperature: float | None = None
        self._attr_hvac_mode: HVACMode = HVACMode.OFF
        self._available = False

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to hass."""
        await super().async_added_to_hass()
        # Get reference to shared data cache
        self._data_cache = self.hass.data[DOMAIN][self._entry.entry_id][\"data_cache\"]

    def update(self) -> None:
        """Fetch new state data from the Modbus device (synchronous).
        
        Reads all registers in optimized batches and updates _data_cache.
        Other entities read from this cache.
        """
        try:
            # Batch 1: System status (0x0000-0x000D) - 14 registers
            batch = self._client.read_batch(0x0000, 14)
            if batch is None:
                raise RuntimeError("Failed to read system status")
            for i, val in enumerate(batch):
                self._data_cache[0x0000 + i] = val
            
            # Batch 2: First temperature block (0x000E-0x000F) - 2 registers
            # Note: 0x0010 doesn't exist on this device
            batch = self._client.read_batch(0x000E, 2)
            if batch is None:
                raise RuntimeError("Failed to read first temp block")
            for i, val in enumerate(batch):
                self._data_cache[0x000E + i] = val
            
            # Batch 3: Main temperature/sensor block (0x0011-0x0031) - 33 registers
            batch = self._client.read_batch(0x0011, 33)
            if batch is None:
                raise RuntimeError("Failed to read main sensor block")
            for i, val in enumerate(batch):
                self._data_cache[0x0011 + i] = val
            
            # Batch 4: Control markers (0x0032-0x0034) - 3 registers
            # Note: 0x0035 doesn't exist
            batch = self._client.read_batch(0x0032, 3)
            if batch is None:
                raise RuntimeError("Failed to read control markers")
            for i, val in enumerate(batch):
                self._data_cache[0x0032 + i] = val
            
            # Batch 5: Unit mode (0x0036) - 1 register
            batch = self._client.read_batch(0x0036, 1)
            if batch is None:
                raise RuntimeError("Failed to read unit mode")
            self._data_cache[0x0036] = batch[0]
            
            # Batch 6: Temperature differential (0x00C6) - 1 register
            # Note: 0x00C7-0x00C9 don't exist
            batch = self._client.read_batch(0x00C6, 1)
            if batch is None:
                raise RuntimeError("Failed to read temp differential")
            self._data_cache[0x00C6] = batch[0]
            
            # Batch 7: Setpoints (0x00CA-0x00CC) - 3 registers
            batch = self._client.read_batch(0x00CA, 3)
            if batch is None:
                raise RuntimeError("Failed to read setpoints")
            for i, val in enumerate(batch):
                self._data_cache[0x00CA + i] = val
            
            # Batch 8: Economic mode block (0x0169-0x0180) - 24 registers
            batch = self._client.read_batch(0x0169, 24)
            if batch is None:
                raise RuntimeError("Failed to read economic mode")
            for i, val in enumerate(batch):
                self._data_cache[0x0169 + i] = val
            
            # Batch 9: General configuration (0x0181-0x0185) - 5 registers
            batch = self._client.read_batch(0x0181, 5)
            if batch is None:
                raise RuntimeError("Failed to read general config")
            for i, val in enumerate(batch):
                self._data_cache[0x0181 + i] = val
            
            # Batch 10: DC pump temp diff (0x018D) - 1 register
            # Note: 0x018E-0x018F don't exist
            batch = self._client.read_batch(0x018D, 1)
            if batch is None:
                raise RuntimeError("Failed to read DC pump config")
            self._data_cache[0x018D] = batch[0]
            
            # Batch 11: Mode control block (0x0190-0x0193) - 4 registers
            # Note: 0x0194-0x0199 don't exist
            batch = self._client.read_batch(0x0190, 4)
            if batch is None:
                raise RuntimeError("Failed to read mode control")
            for i, val in enumerate(batch):
                self._data_cache[0x0190 + i] = val
            
            # Batch 12: Anti-legionella + pump mode (0x019A-0x019E) - 5 registers
            batch = self._client.read_batch(0x019A, 5)
            if batch is None:
                raise RuntimeError("Failed to read anti-legionella config")
            for i, val in enumerate(batch):
                self._data_cache[0x019A + i] = val
            
            # Update entity state from cache
            self._update_from_cache()
            self._available = True
            
        except Exception as err:
            _LOGGER.error("Failed to update SPRSUN data: %s", err)
            self._available = False

    def _update_from_cache(self) -> None:
        """Update entity attributes from cached data."""
        # Current temperature from water outlet
        if REG_OUTLET_TEMP in self._data_cache:
            self._attr_current_temperature = decode_temperature(
                self._data_cache[REG_OUTLET_TEMP],
                scale=10,
                signed=True,
            )
        
        # Get unit mode to determine HVAC mode and target temp
        if REG_UNIT_MODE in self._data_cache:
            unit_mode = self._data_cache[REG_UNIT_MODE]
            
            if unit_mode == UNIT_MODE_DHW:
                self._attr_hvac_mode = HVACMode.OFF  # DHW only, no HVAC
                if REG_HOTWATER_SETPOINT in self._data_cache:
                    self._attr_target_temperature = decode_temperature(
                        self._data_cache[REG_HOTWATER_SETPOINT],
                        scale=10,
                        signed=True,
                    )
            elif unit_mode in (UNIT_MODE_HEATING, UNIT_MODE_HEATING_DHW):
                self._attr_hvac_mode = HVACMode.HEAT
                if REG_HEATING_SETPOINT in self._data_cache:
                    self._attr_target_temperature = decode_temperature(
                        self._data_cache[REG_HEATING_SETPOINT],
                        scale=10,
                        signed=True,
                    )
            elif unit_mode in (UNIT_MODE_COOLING, UNIT_MODE_COOLING_DHW):
                self._attr_hvac_mode = HVACMode.COOL
                if REG_COOLING_SETPOINT in self._data_cache:
                    self._attr_target_temperature = decode_temperature(
                        self._data_cache[REG_COOLING_SETPOINT],
                        scale=10,
                        signed=True,
                    )
            else:
                self._attr_hvac_mode = HVACMode.OFF

    def set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target HVAC mode (synchronous)."""
        mode_map = {
            HVACMode.OFF: UNIT_MODE_DHW,
            HVACMode.HEAT: UNIT_MODE_HEATING_DHW,
            HVACMode.COOL: UNIT_MODE_COOLING_DHW,
        }
        
        if hvac_mode not in mode_map:
            _LOGGER.error("Unsupported HVAC mode: %s", hvac_mode)
            return
        
        new_mode = mode_map[hvac_mode]
        success = self._client.write_register(REG_UNIT_MODE, new_mode)
        
        if success:
            self._data_cache[REG_UNIT_MODE] = new_mode
            self._update_from_cache()
        else:
            _LOGGER.error("Failed to write HVAC mode to Modbus")

    def set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature (synchronous)."""
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        
        # Determine which setpoint to write based on current mode
        if REG_UNIT_MODE not in self._data_cache:
            _LOGGER.error("Cannot set temperature: unit mode unknown")
            return
        
        unit_mode = self._data_cache[REG_UNIT_MODE]
        
        # Map mode to appropriate setpoint register
        if unit_mode in (UNIT_MODE_HEATING, UNIT_MODE_HEATING_DHW):
            reg = REG_HEATING_SETPOINT
        elif unit_mode in (UNIT_MODE_COOLING, UNIT_MODE_COOLING_DHW):
            reg = REG_COOLING_SETPOINT
        elif unit_mode == UNIT_MODE_DHW:
            reg = REG_HOTWATER_SETPOINT
        else:
            _LOGGER.error("Cannot set temperature: invalid unit mode %s", unit_mode)
            return
        
        # Encode temperature (scale=10, signed)
        from .modbus import encode_temperature
        
        encoded = encode_temperature(temp, scale=10, signed=True)
        success = self._client.write_register(reg, encoded)
        
        if success:
            self._data_cache[reg] = encoded
            self._update_from_cache()
        else:
            _LOGGER.error("Failed to write temperature setpoint to Modbus")
