"""The SPRSUN Heat Pump integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_SLAVE_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.CLIMATE,
    Platform.SELECT,
    Platform.NUMBER,
    Platform.BINARY_SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SPRSUN Heat Pump from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    slave_id = entry.data[CONF_SLAVE_ID]
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    coordinator = SprsunDataUpdateCoordinator(
        hass,
        host=host,
        port=port,
        slave_id=slave_id,
        scan_interval=scan_interval,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await hass.async_add_executor_job(coordinator.close)

    return unload_ok


class SprsunDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching SPRSUN data from Modbus."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        slave_id: int,
        scan_interval: int,
    ) -> None:
        """Initialize."""
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.client = ModbusTcpClient(host=host, port=port, timeout=5)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    def connect(self) -> bool:
        """Connect to Modbus device."""
        if not self.client.connected:
            return self.client.connect()
        return True

    def close(self) -> None:
        """Close Modbus connection."""
        if self.client.connected:
            self.client.close()

    def read_holding_registers(self, address: int, count: int = 1) -> list[int] | None:
        """Read holding registers."""
        try:
            if not self.connect():
                _LOGGER.error("Failed to connect to %s:%s", self.host, self.port)
                return None

            # Try slave parameter first (pymodbus 3.0-3.5)
            try:
                result = self.client.read_holding_registers(address, count, slave=self.slave_id)
            except TypeError:
                # Try unit parameter (pymodbus 3.6+)
                try:
                    result = self.client.read_holding_registers(address, count, unit=self.slave_id)
                except TypeError:
                    # Try as positional argument
                    result = self.client.read_holding_registers(address, count, self.slave_id)

            if result.isError():
                _LOGGER.error("Modbus read error at address %s: %s", address, result)
                return None

            return result.registers

        except ModbusException as ex:
            _LOGGER.error("Modbus exception: %s", ex)
            return None

    def write_register(self, address: int, value: int) -> bool:
        """Write a single register."""
        try:
            if not self.connect():
                _LOGGER.error("Failed to connect to %s:%s", self.host, self.port)
                return False

            # Try slave parameter first (pymodbus 3.0-3.5)
            try:
                result = self.client.write_register(address, value, slave=self.slave_id)
            except TypeError:
                # Try unit parameter (pymodbus 3.6+)
                try:
                    result = self.client.write_register(address, value, unit=self.slave_id)
                except TypeError:
                    # Try as positional argument  
                    result = self.client.write_register(address, value, self.slave_id)

            if result.isError():
                _LOGGER.error("Modbus write error at address %s: %s", address, result)
                return False

            return True

        except ModbusException as ex:
            _LOGGER.error("Modbus exception: %s", ex)
            return False

    async def _async_update_data(self):
        """Update data via Modbus."""
        return await self.hass.async_add_executor_job(self._update_data)

    def _update_data(self):
        """Fetch data from Modbus device."""
        try:
            if not self.connect():
                raise UpdateFailed(f"Failed to connect to {self.host}:{self.port}")

            # Read all important registers in batches for efficiency
            data = {}

            # Status registers (0-13)
            regs = self.read_holding_registers(0, 14)
            if regs:
                data["compressor_runtime"] = regs[0]
                data["switching_input"] = regs[2]
                data["working_status"] = regs[3]
                data["output_symbol_1"] = regs[4]
                data["output_symbol_2"] = regs[5]
                data["output_symbol_3"] = regs[6]
                data["failure_symbol_1"] = regs[7]
                data["failure_symbol_2"] = regs[8]
                data["failure_symbol_3"] = regs[9]
                data["failure_symbol_4"] = regs[10]
                data["failure_symbol_5"] = regs[11]
                data["failure_symbol_6"] = regs[12]
                data["failure_symbol_7"] = regs[13]

            # Temperature sensors (14-50)
            regs = self.read_holding_registers(14, 37)
            if regs:
                data["inlet_temp"] = self._convert_temp(regs[0], 0.1)
                data["hotwater_temp"] = self._convert_temp(regs[1], 0.1)
                data["ambient_temp"] = self._convert_temp(regs[3], 0.5)
                data["outlet_temp"] = self._convert_temp(regs[4], 0.1)
                data["suct_gas_temp"] = self._convert_temp(regs[7], 0.5)
                data["coil_temp"] = self._convert_temp(regs[8], 0.5)
                data["exhaust_temp"] = regs[13]
                data["evap_temp"] = self._convert_temp(regs[26], 0.1)
                data["cond_temp"] = self._convert_temp(regs[27], 0.1)
                data["comp_frequency"] = regs[16]
                data["comp_current"] = regs[21]
                data["target_frequency"] = regs[22]
                data["dc_bus_voltage"] = regs[19]
                data["dc_pump_speed"] = regs[32]
                data["dc_fan_1_speed"] = regs[24]
                data["dc_fan_2_speed"] = regs[25]

            # Configuration registers (54-58)
            regs = self.read_holding_registers(54, 5)
            if regs:
                data["unit_mode"] = regs[0]
                data["defrost_period_1"] = regs[2]
                data["defrost_period_2"] = regs[3]
                data["defrost_period_3"] = regs[4]

            # Setpoint registers (202-204)
            regs = self.read_holding_registers(202, 3)
            if regs:
                data["hotwater_setpoint"] = self._convert_temp(regs[0], 0.5)
                data["cooling_setpoint"] = self._convert_temp(regs[1], 0.5)
                data["heating_setpoint"] = self._convert_temp(regs[2], 0.5)

            # Additional config registers
            regs = self.read_holding_registers(389, 6)
            if regs:
                data["pump_cycle"] = regs[0]
                data["pump_min_freq"] = regs[5]

            regs = self.read_holding_registers(400, 1)
            if regs:
                data["fan_mode"] = regs[0]

            regs = self.read_holding_registers(414, 1)
            if regs:
                data["pump_mode"] = regs[0]

            regs = self.read_holding_registers(252, 2)
            if regs:
                data["water_freq_r00"] = regs[0]
                data["water_freq_r01"] = regs[1]

            regs = self.read_holding_registers(260, 2)
            if regs:
                data["heat_freq_r04"] = regs[0]
                data["heat_freq_r05"] = regs[1]

            return data

        except Exception as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err

    @staticmethod
    def _convert_temp(raw_value: int, scale: float) -> float:
        """Convert raw temperature value with scale factor."""
        # Handle signed 16-bit integers
        if raw_value > 32767:
            raw_value -= 65536
        return round(raw_value * scale, 1)
