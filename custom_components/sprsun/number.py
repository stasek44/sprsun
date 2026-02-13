"""Number platform for SPRSUN Heat Pump.

Number entities allow setting writable parameters via Modbus.
Reads current values from shared data_cache.
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

from .const import (
    AMBIENT_SWITCH_DIFF_MAX,
    AMBIENT_SWITCH_DIFF_MIN,
    AMBIENT_SWITCH_SETPOINT_MAX,
    AMBIENT_SWITCH_SETPOINT_MIN,
    ANTILEGIONELLA_TEMP_MAX,
    ANTILEGIONELLA_TEMP_MIN,
    COOLING_SETPOINT_MAX,
    COOLING_SETPOINT_MIN,
    DC_PUMP_DIFF_MAX,
    DC_PUMP_DIFF_MIN,
    DOMAIN,
    ECO_AMBIENT_MAX,
    ECO_AMBIENT_MIN,
    ECO_COOLING_TEMP_MAX,
    ECO_COOLING_TEMP_MIN,
    ECO_HEATING_TEMP_MAX,
    ECO_HEATING_TEMP_MIN,
    ECO_HOTWATER_TEMP_MAX,
    ECO_HOTWATER_TEMP_MIN,
    HEATER_AMBIENT_MAX,
    HEATER_AMBIENT_MIN,
    HEATER_DELAY_MAX,
    HEATER_DELAY_MIN,
    HEATING_SETPOINT_MAX,
    HEATING_SETPOINT_MIN,
    HOTWATER_SETPOINT_MAX,
    HOTWATER_SETPOINT_MIN,
    MANUFACTURER,
    MODEL,
    PUMP_INTERVAL_MAX,
    PUMP_INTERVAL_MIN,
    REG_AMBIENT_SWITCH_DIFF,
    REG_AMBIENT_SWITCH_SETPOINT,
    REG_ANTILEGIONELLA_END_HOUR,
    REG_ANTILEGIONELLA_START_HOUR,
    REG_ANTILEGIONELLA_TEMP,
    REG_ANTILEGIONELLA_WEEKDAY,
    REG_COOLING_SETPOINT,
    REG_DC_PUMP_TEMP_DIFF,
    REG_ECO_COOL_AMBI_1,
    REG_ECO_COOL_AMBI_2,
    REG_ECO_COOL_AMBI_3,
    REG_ECO_COOL_AMBI_4,
    REG_ECO_COOL_TEMP_1,
    REG_ECO_COOL_TEMP_2,
    REG_ECO_COOL_TEMP_3,
    REG_ECO_COOL_TEMP_4,
    REG_ECO_HEAT_AMBI_1,
    REG_ECO_HEAT_AMBI_2,
    REG_ECO_HEAT_AMBI_3,
    REG_ECO_HEAT_AMBI_4,
    REG_ECO_HEAT_TEMP_1,
    REG_ECO_HEAT_TEMP_2,
    REG_ECO_HEAT_TEMP_3,
    REG_ECO_HEAT_TEMP_4,
    REG_ECO_WATER_AMBI_1,
    REG_ECO_WATER_AMBI_2,
    REG_ECO_WATER_AMBI_3,
    REG_ECO_WATER_AMBI_4,
    REG_ECO_WATER_TEMP_1,
    REG_ECO_WATER_TEMP_2,
    REG_ECO_WATER_TEMP_3,
    REG_ECO_WATER_TEMP_4,
    REG_HEATING_HEATER_AMBIENT,
    REG_HEATING_HEATER_DELAY,
    REG_HEATING_SETPOINT,
    REG_HOTWATER_HEATER_AMBIENT,
    REG_HOTWATER_HEATER_DELAY,
    REG_HOTWATER_SETPOINT,
    REG_PUMP_STARTUP_INTERVAL,
    TEMP_DIFF_MAX,
    TEMP_DIFF_MIN,
)
from .modbus import decode_temperature, encode_temperature

_LOGGER = logging.getLogger(__name__)


@dataclass
class SPRSUNNumberEntityDescription(NumberEntityDescription):
    """Describes SPRSUN number entity."""

    register: int | None = None
    scale: float = 1.0
    signed: bool = False


NUMBERS: tuple[SPRSUNNumberEntityDescription, ...] = (
    # Main setpoints
    SPRSUNNumberEntityDescription(
        key="heating_setpoint",
        name="Heating Setpoint",
        register=REG_HEATING_SETPOINT,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=HEATING_SETPOINT_MIN,
        native_max_value=HEATING_SETPOINT_MAX,
        native_step=0.5,
        mode=NumberMode.BOX,
        scale=10,
        signed=True,
    ),
    SPRSUNNumberEntityDescription(
        key="cooling_setpoint",
        name="Cooling Setpoint",
        register=REG_COOLING_SETPOINT,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=COOLING_SETPOINT_MIN,
        native_max_value=COOLING_SETPOINT_MAX,
        native_step=0.5,
        mode=NumberMode.BOX,
        scale=10,
        signed=True,
    ),
    SPRSUNNumberEntityDescription(
        key="hotwater_setpoint",
        name="Hot Water Setpoint",
        register=REG_HOTWATER_SETPOINT,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=HOTWATER_SETPOINT_MIN,
        native_max_value=HOTWATER_SETPOINT_MAX,
        native_step=0.5,
        mode=NumberMode.BOX,
        scale=10,
        signed=True,
    ),
    
    # Economic mode - Heating ambient thresholds
    SPRSUNNumberEntityDescription(
        key="eco_heat_ambient_1",
        name="Eco Heating Ambient 1",
        register=REG_ECO_HEAT_AMBI_1,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=ECO_AMBIENT_MIN,
        native_max_value=ECO_AMBIENT_MAX,
        native_step=0.5,
        scale=10,
        signed=True,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_heat_ambient_2",
        name="Eco Heating Ambient 2",
        register=REG_ECO_HEAT_AMBI_2,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=ECO_AMBIENT_MIN,
        native_max_value=ECO_AMBIENT_MAX,
        native_step=0.5,
        scale=10,
        signed=True,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_heat_ambient_3",
        name="Eco Heating Ambient 3",
        register=REG_ECO_HEAT_AMBI_3,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=ECO_AMBIENT_MIN,
        native_max_value=ECO_AMBIENT_MAX,
        native_step=0.5,
        scale=10,
        signed=True,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_heat_ambient_4",
        name="Eco Heating Ambient 4",
        register=REG_ECO_HEAT_AMBI_4,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=ECO_AMBIENT_MIN,
        native_max_value=ECO_AMBIENT_MAX,
        native_step=0.5,
        scale=10,
        signed=True,
    ),
    
    # Economic mode - Heating temperature setpoints
    SPRSUNNumberEntityDescription(
        key="eco_heat_temp_1",
        name="Eco Heating Temp 1",
        register=REG_ECO_HEAT_TEMP_1,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=ECO_HEATING_TEMP_MIN,
        native_max_value=ECO_HEATING_TEMP_MAX,
        native_step=0.5,
        scale=10,
        signed=True,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_heat_temp_2",
        name="Eco Heating Temp 2",
        register=REG_ECO_HEAT_TEMP_2,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=ECO_HEATING_TEMP_MIN,
        native_max_value=ECO_HEATING_TEMP_MAX,
        native_step=0.5,
        scale=10,
        signed=True,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_heat_temp_3",
        name="Eco Heating Temp 3",
        register=REG_ECO_HEAT_TEMP_3,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=ECO_HEATING_TEMP_MIN,
        native_max_value=ECO_HEATING_TEMP_MAX,
        native_step=0.5,
        scale=10,
        signed=True,
    ),
    SPRSUNNumberEntityDescription(
        key="eco_heat_temp_4",
        name="Eco Heating Temp 4",
        register=REG_ECO_HEAT_TEMP_4,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=ECO_HEATING_TEMP_MIN,
        native_max_value=ECO_HEATING_TEMP_MAX,
        native_step=0.5,
        scale=10,
        signed=True,
    ),
    
    # Anti-legionella configuration
    SPRSUNNumberEntityDescription(
        key="antilegionella_temp",
        name="Anti-Legionella Temperature",
        register=REG_ANTILEGIONELLA_TEMP,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=ANTILEGIONELLA_TEMP_MIN,
        native_max_value=ANTILEGIONELLA_TEMP_MAX,
        native_step=1,
        scale=10,
        signed=True,
    ),
    SPRSUNNumberEntityDescription(
        key="antilegionella_weekday",
        name="Anti-Legionella Weekday",
        register=REG_ANTILEGIONELLA_WEEKDAY,
        native_min_value=1,
        native_max_value=7,
        native_step=1,
    ),
    SPRSUNNumberEntityDescription(
        key="antilegionella_start_hour",
        name="Anti-Legionella Start Hour",
        register=REG_ANTILEGIONELLA_START_HOUR,
        native_min_value=0,
        native_max_value=23,
        native_step=1,
    ),
    SPRSUNNumberEntityDescription(
        key="antilegionella_end_hour",
        name="Anti-Legionella End Hour",
        register=REG_ANTILEGIONELLA_END_HOUR,
        native_min_value=0,
        native_max_value=23,
        native_step=1,
    ),
    
    # Heater delays
    SPRSUNNumberEntityDescription(
        key="hotwater_heater_delay",
        name="Hot Water Heater Delay",
        register=REG_HOTWATER_HEATER_DELAY,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        native_min_value=HEATER_DELAY_MIN,
        native_max_value=HEATER_DELAY_MAX,
        native_step=1,
    ),
    SPRSUNNumberEntityDescription(
        key="heating_heater_delay",
        name="Heating Heater Delay",
        register=REG_HEATING_HEATER_DELAY,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        native_min_value=HEATER_DELAY_MIN,
        native_max_value=HEATER_DELAY_MAX,
        native_step=1,
    ),
    
    # Pump configuration
    SPRSUNNumberEntityDescription(
        key="pump_startup_interval",
        name="Pump Startup Interval",
        register=REG_PUMP_STARTUP_INTERVAL,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        native_min_value=PUMP_INTERVAL_MIN,
        native_max_value=PUMP_INTERVAL_MAX,
        native_step=1,
    ),
    SPRSUNNumberEntityDescription(
        key="dc_pump_temp_diff",
        name="DC Pump Temperature Difference",
        register=REG_DC_PUMP_TEMP_DIFF,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=DC_PUMP_DIFF_MIN,
        native_max_value=DC_PUMP_DIFF_MAX,
        native_step=1,
        scale=10,
        signed=True,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN number entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    client = data["client"]
    data_cache = data["data_cache"]
    
    entities = [
        SPRSUNNumber(data_cache, client, entry, description)
        for description in NUMBERS
    ]
    
    async_add_entities(entities)


class SPRSUNNumber(NumberEntity):
    """Representation of a SPRSUN number entity.
    
    Reads from shared data_cache but writes directly via client.
    """

    _attr_has_entity_name = True
    entity_description: SPRSUNNumberEntityDescription

    def __init__(
        self,
        data_cache: dict[int, int],
        client,
        entry: ConfigEntry,
        description: SPRSUNNumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
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
    def native_value(self) -> float | None:
        """Return the current value from cache."""
        if self.entity_description.register is None:
            return None
        
        raw = self._data_cache.get(self.entity_description.register)
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
            return raw / self.entity_description.scale
        
        return raw

    async def async_set_native_value(self, value: float) -> None:
        """Set new value (async wrapper)."""
        await self.hass.async_add_executor_job(self._set_value, value)

    def _set_value(self, value: float) -> None:
        """Set new value (synchronous Modbus write)."""
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
            encoded = int(value * self.entity_description.scale)
        else:
            encoded = int(value)
        
        # Write to Modbus
        success = self._client.write_register(
            self.entity_description.register,
            encoded,
        )
        
        if success:
            # Update cache
            self._data_cache[self.entity_description.register] = encoded
        else:
            _LOGGER.error(
                "Failed to write %s to register 0x%04X",
                self.entity_description.key,
                self.entity_description.register,
            )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return len(self._data_cache) > 0
