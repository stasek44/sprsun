"""DataUpdateCoordinator for SPRSUN heat pump."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_SLAVE_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    TEMP_SCALE_01,
    TEMP_SCALE_05,
    TEMP_SCALE_1,
)
from .modbus import SPRSUNModbusClient

_LOGGER = logging.getLogger(__name__)


class SPRSUNDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching SPRSUN data from Modbus."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.host = entry.data[CONF_HOST]
        self.port = entry.data[CONF_PORT]
        self.slave_id = entry.data.get(CONF_SLAVE_ID, 1)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        
        self.client = SPRSUNModbusClient(self.host, self.port, self.slave_id)
        self._device_info: DeviceInfo | None = None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        if self._device_info is None:
            sw_version = None
            if self.data:
                year = self.data.get("sw_version_year")
                month_day = self.data.get("sw_version_month_day")
                if year and month_day:
                    sw_version = f"{year}.{month_day}"
            
            self._device_info = DeviceInfo(
                identifiers={(DOMAIN, f"{self.host}_{self.port}")},
                name="SPRSUN Heat Pump",
                manufacturer=MANUFACTURER,
                model=MODEL,
                sw_version=sw_version,
                configuration_url=f"http://{self.host}",
            )
        return self._device_info

    async def _async_setup(self) -> None:
        """Set up the coordinator.
        
        This is called automatically during async_config_entry_first_refresh.
        """
        connected = await self.client.connect()
        if not connected:
            raise UpdateFailed("Failed to connect to SPRSUN heat pump")

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the heat pump.
        
        This fetches all parameters in optimized batch reads.
        """
        if not self.client._client or not self.client._client.connected:
            await self._async_setup()
        
        try:
            async with async_timeout.timeout(30):
                data = {}
                
                # Read system status (0x0000-0x0002)
                status_regs = await self.client.read_holding_registers(0x0000, 3)
                if status_regs:
                    data["compressor_runtime"] = status_regs[0]
                    data["cop"] = status_regs[1]
                    data["switching_input_symbol"] = self.client.parse_bit_field(status_regs[2])
                
                # Read working status and output symbols (0x0003-0x0006)
                working_regs = await self.client.read_holding_registers(0x0003, 4)
                if working_regs:
                    data["working_status"] = self.client.parse_bit_field(working_regs[0])
                    data["output_symbol_1"] = self.client.parse_bit_field(working_regs[1])
                    data["output_symbol_2"] = self.client.parse_bit_field(working_regs[2])
                    data["output_symbol_3"] = self.client.parse_bit_field(working_regs[3])
                
                # Read failure symbols (0x0007-0x000D)
                failure_regs = await self.client.read_holding_registers(0x0007, 7)
                if failure_regs:
                    for i in range(7):
                        data[f"failure_symbol_{i+1}"] = self.client.parse_bit_field(failure_regs[i])
                
                # Read temperature sensors (0x000E-0x0012, 0x0015-0x0016, 0x001B, 0x0022, 0x0028-0x0029)
                inlet_temp = await self.client.read_holding_registers(0x000E, 1)
                if inlet_temp:
                    data["inlet_temp"] = self.client.decode_temperature(inlet_temp[0], TEMP_SCALE_01)
                
                hotwater_temp = await self.client.read_holding_registers(0x000F, 1)
                if hotwater_temp:
                    data["hotwater_temp"] = self.client.decode_temperature(hotwater_temp[0], TEMP_SCALE_01)
                
                ambi_temp = await self.client.read_holding_registers(0x0011, 1)
                if ambi_temp:
                    data["ambi_temp"] = self.client.decode_temperature(ambi_temp[0], TEMP_SCALE_05)
                
                outlet_temp = await self.client.read_holding_registers(0x0012, 1)
                if outlet_temp:
                    data["outlet_temp"] = self.client.decode_temperature(outlet_temp[0], TEMP_SCALE_01)
                
                # Read software versions (0x0013-0x0014)
                version_regs = await self.client.read_holding_registers(0x0013, 2)
                if version_regs:
                    data["sw_version_year"] = version_regs[0]
                    data["sw_version_month_day"] = version_regs[1]
                
                # Read more temperatures
                suct_gas_temp = await self.client.read_holding_registers(0x0015, 2)
                if suct_gas_temp:
                    data["suct_gas_temp"] = self.client.decode_temperature(suct_gas_temp[0], TEMP_SCALE_05)
                    data["coil_temp"] = self.client.decode_temperature(suct_gas_temp[1], TEMP_SCALE_05)
                
                # Read system measurements (0x0017-0x001E)
                measurements = await self.client.read_holding_registers(0x0017, 8)
                if measurements:
                    data["ac_voltage"] = measurements[0]
                    data["pump_flow"] = measurements[1]
                    data["heating_cooling_capacity"] = measurements[2]
                    data["ac_current"] = measurements[3]
                    data["eev1_step"] = measurements[5]
                    data["eev2_step"] = measurements[6]
                    data["comp_frequency"] = measurements[7]
                
                # Read more measurements (0x001F-0x0027)
                more_measurements = await self.client.read_holding_registers(0x001F, 9)
                if more_measurements:
                    data["freq_conv_failure_1"] = more_measurements[0]
                    data["freq_conv_failure_2"] = more_measurements[1]
                    data["dc_bus_voltage"] = more_measurements[2]
                    data["driving_temp"] = self.client.decode_temperature(more_measurements[3], TEMP_SCALE_05)
                    data["comp_current"] = more_measurements[4]
                    data["target_frequency"] = more_measurements[5]
                    data["smart_grid_status"] = more_measurements[6]
                    data["dc_fan_1_speed"] = more_measurements[7]
                    data["dc_fan_2_speed"] = more_measurements[8]
                
                # Read evap/cond temps and more (0x0028-0x0031)
                final_temps = await self.client.read_holding_registers(0x0028, 10)
                if final_temps:
                    data["evap_temp"] = self.client.decode_temperature(final_temps[0], TEMP_SCALE_01)
                    data["cond_temp"] = self.client.decode_temperature(final_temps[1], TEMP_SCALE_01)
                    data["freq_conv_fault_high"] = final_temps[2]
                    data["freq_conv_fault_low"] = final_temps[3]
                    data["controller_version"] = final_temps[4]
                    data["display_version"] = final_temps[5]
                    data["dc_pump_speed"] = final_temps[6]
                    data["suct_press"] = self.client.decode_pressure(final_temps[7])
                    data["disch_press"] = self.client.decode_pressure(final_temps[8])
                    data["dc_fan_target"] = final_temps[9]
                
                # Read control registers (0x0032-0x0034)
                control_regs = await self.client.read_holding_registers(0x0032, 3)
                if control_regs:
                    data["parameter_marker"] = self.client.parse_bit_field(control_regs[0])
                    data["control_mark_1"] = self.client.parse_bit_field(control_regs[1])
                    data["control_mark_2"] = self.client.parse_bit_field(control_regs[2])
                
                # Read basic configuration (0x0036, 0x00C6, 0x00C8, 0x00CA-0x00CC)
                unit_mode = await self.client.read_holding_registers(0x0036, 1)
                if unit_mode:
                    data["unit_mode"] = unit_mode[0]
                
                temp_diffs = await self.client.read_holding_registers(0x00C6, 1)
                if temp_diffs:
                    data["cooling_heating_temp_diff"] = temp_diffs[0]
                
                hotwater_diff = await self.client.read_holding_registers(0x00C8, 1)
                if hotwater_diff:
                    data["hotwater_temp_diff"] = hotwater_diff[0]
                
                setpoints = await self.client.read_holding_registers(0x00CA, 3)
                if setpoints:
                    data["hotwater_setp"] = self.client.decode_temperature(setpoints[0] & 0xFF, TEMP_SCALE_05)
                    data["cooling_setp"] = self.client.decode_temperature(setpoints[1] & 0xFF, TEMP_SCALE_05)
                    data["heating_setp"] = self.client.decode_temperature(setpoints[2] & 0xFF, TEMP_SCALE_05)
                
                # Read exhaust temp (0x001B)
                exhaust_temp = await self.client.read_holding_registers(0x001B, 1)
                if exhaust_temp:
                    data["exhaust_temp"] = self.client.decode_temperature(exhaust_temp[0], TEMP_SCALE_1)
                
                return data
                
        except asyncio.TimeoutError as err:
            raise UpdateFailed("Timeout communicating with heat pump") from err
        except Exception as err:
            raise UpdateFailed(f"Error communicating with heat pump: {err}") from err

    async def async_write_register(self, address: int, value: int) -> None:
        """Write a register value."""
        success = await self.client.write_register(address, value)
        if not success:
            raise UpdateFailed(f"Failed to write register 0x{address:04X}")
        # Request immediate refresh
        await self.async_request_refresh()

    async def async_write_coil(self, address: int, value: bool) -> None:
        """Write a coil value."""
        success = await self.client.write_coil(address, value)
        if not success:
            raise UpdateFailed(f"Failed to write coil 0x{address:04X}")
        # Request immediate refresh
        await self.async_request_refresh()
