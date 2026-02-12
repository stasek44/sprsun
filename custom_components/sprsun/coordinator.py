"""DataUpdateCoordinator for SPRSUN heat pump."""
from __future__ import annotations

import asyncio
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
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
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
        self.port = int(entry.data[CONF_PORT])
        self.slave_id = int(entry.data.get(CONF_SLAVE_ID, 1))
        self.scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        self.timeout = entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=self.scan_interval),
        )
        
        self.client = SPRSUNModbusClient(self.host, self.port, self.slave_id, self.timeout)
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
            async with async_timeout.timeout(60):
                data = {}
                
                # Use BATCH READS like integration_old for better reliability
                # This reduces the number of Modbus transactions significantly
                
                # Batch 1: Status registers (0x0000-0x000D) - 14 registers
                status_batch = await self.client.read_holding_registers(0x0000, 14)
                if status_batch:
                    data["compressor_runtime"] = status_batch[0]
                    data["cop"] = status_batch[1]
                    data["switching_input_symbol"] = self.client.parse_bit_field(status_batch[2])
                    data["working_status"] = self.client.parse_bit_field(status_batch[3])
                    data["output_symbol_1"] = self.client.parse_bit_field(status_batch[4])
                    data["output_symbol_2"] = self.client.parse_bit_field(status_batch[5])
                    data["output_symbol_3"] = self.client.parse_bit_field(status_batch[6])
                    for i in range(7):
                        data[f"failure_symbol_{i+1}"] = self.client.parse_bit_field(status_batch[7 + i])
                else:
                    _LOGGER.warning("Failed to read status batch")
                
                # Batch 2: Temperature sensors and measurements (0x000E-0x0031) - 36 registers
                temp_batch = await self.client.read_holding_registers(0x000E, 36)
                if temp_batch:
                    data["inlet_temp"] = self.client.decode_temperature(temp_batch[0], TEMP_SCALE_01)
                    data["hotwater_temp"] = self.client.decode_temperature(temp_batch[1], TEMP_SCALE_01)
                    data["ambi_temp"] = self.client.decode_temperature(temp_batch[3], TEMP_SCALE_05)
                    data["outlet_temp"] = self.client.decode_temperature(temp_batch[4], TEMP_SCALE_01)
                    data["sw_version_year"] = temp_batch[5]
                    data["sw_version_month_day"] = temp_batch[6]
                    data["suct_gas_temp"] = self.client.decode_temperature(temp_batch[7], TEMP_SCALE_05)
                    data["coil_temp"] = self.client.decode_temperature(temp_batch[8], TEMP_SCALE_05)
                    data["ac_voltage"] = temp_batch[9]
                    data["pump_flow"] = temp_batch[10]
                    data["heating_cooling_capacity"] = temp_batch[11]
                    data["ac_current"] = temp_batch[12]
                    data["exhaust_temp"] = self.client.decode_temperature(temp_batch[13], TEMP_SCALE_1)
                    data["eev1_step"] = temp_batch[14]
                    data["eev2_step"] = temp_batch[15]
                    data["comp_frequency"] = temp_batch[16]
                    data["freq_conv_failure_1"] = temp_batch[17]
                    data["freq_conv_failure_2"] = temp_batch[18]
                    data["dc_bus_voltage"] = temp_batch[19]
                    data["driving_temp"] = self.client.decode_temperature(temp_batch[20], TEMP_SCALE_05)
                    data["comp_current"] = temp_batch[21]
                    data["target_frequency"] = temp_batch[22]
                    data["smart_grid_status"] = temp_batch[23]
                    data["dc_fan_1_speed"] = temp_batch[24]
                    data["dc_fan_2_speed"] = temp_batch[25]
                    data["evap_temp"] = self.client.decode_temperature(temp_batch[26], TEMP_SCALE_01)
                    data["cond_temp"] = self.client.decode_temperature(temp_batch[27], TEMP_SCALE_01)
                    data["freq_conv_fault_high"] = temp_batch[28]
                    data["freq_conv_fault_low"] = temp_batch[29]
                    data["controller_version"] = temp_batch[30]
                    data["display_version"] = temp_batch[31]
                    data["dc_pump_speed"] = temp_batch[32]
                    data["suct_press"] = self.client.decode_pressure(temp_batch[33])
                    data["disch_press"] = self.client.decode_pressure(temp_batch[34])
                    data["dc_fan_target"] = temp_batch[35]
                else:
                    _LOGGER.warning("Failed to read temperature batch")
                
                # Batch 3: Control registers (0x0032-0x0036) - 5 registers
                control_batch = await self.client.read_holding_registers(0x0032, 5)
                if control_batch:
                    data["parameter_marker"] = self.client.parse_bit_field(control_batch[0])
                    data["control_mark_1"] = self.client.parse_bit_field(control_batch[1])
                    data["control_mark_2"] = self.client.parse_bit_field(control_batch[2])
                    data["unit_mode"] = control_batch[4]
                else:
                    _LOGGER.warning("Failed to read control batch")
                
                # Batch 4: Configuration setpoints (0x00C6-0x00CC) - 7 registers
                config_batch = await self.client.read_holding_registers(0x00C6, 7)
                if config_batch:
                    data["cooling_heating_temp_diff"] = config_batch[0]
                    data["hotwater_temp_diff"] = config_batch[2]
                    # FIX: Remove & 0xFF mask - it was truncating values to 8 bits!
                    data["hotwater_setp"] = self.client.decode_temperature(config_batch[4], TEMP_SCALE_05)
                    data["cooling_setp"] = self.client.decode_temperature(config_batch[5], TEMP_SCALE_05)
                    data["heating_setp"] = self.client.decode_temperature(config_batch[6], TEMP_SCALE_05)
                else:
                    _LOGGER.warning("Failed to read config batch")
                
                # Batch 5: Economic mode - heating (0x0169-0x0178) - 16 registers
                eco_heat_batch = await self.client.read_holding_registers(0x0169, 16)
                if eco_heat_batch:
                    data["eco_heat_ambi_1"] = eco_heat_batch[0]
                    data["eco_heat_ambi_2"] = eco_heat_batch[1]
                    data["eco_heat_ambi_3"] = eco_heat_batch[2]
                    data["eco_heat_ambi_4"] = eco_heat_batch[3]
                    data["eco_heat_temp_1"] = self.client.decode_temperature(eco_heat_batch[12], TEMP_SCALE_05)
                    data["eco_heat_temp_2"] = self.client.decode_temperature(eco_heat_batch[13], TEMP_SCALE_05)
                    data["eco_heat_temp_3"] = self.client.decode_temperature(eco_heat_batch[14], TEMP_SCALE_05)
                    data["eco_heat_temp_4"] = self.client.decode_temperature(eco_heat_batch[15], TEMP_SCALE_05)
                    # Also includes water ambi in same batch (offset 4-7)
                    data["eco_water_ambi_1"] = eco_heat_batch[4]
                    data["eco_water_ambi_2"] = eco_heat_batch[5]
                    data["eco_water_ambi_3"] = eco_heat_batch[6]
                    data["eco_water_ambi_4"] = eco_heat_batch[7]
                    # And cooling ambi (offset 8-11)
                    data["eco_cool_ambi_1"] = eco_heat_batch[8]
                    data["eco_cool_ambi_2"] = eco_heat_batch[9]
                    data["eco_cool_ambi_3"] = eco_heat_batch[10]
                    data["eco_cool_ambi_4"] = eco_heat_batch[11]
                else:
                    _LOGGER.warning("Failed to read eco heating batch")
                
                # Batch 6: Economic mode - water and cooling temps (0x0179-0x0180) - 8 registers
                eco_temps_batch = await self.client.read_holding_registers(0x0179, 8)
                if eco_temps_batch:
                    data["eco_water_temp_1"] = self.client.decode_temperature(eco_temps_batch[0], TEMP_SCALE_05)
                    data["eco_water_temp_2"] = self.client.decode_temperature(eco_temps_batch[1], TEMP_SCALE_05)
                    data["eco_water_temp_3"] = self.client.decode_temperature(eco_temps_batch[2], TEMP_SCALE_05)
                    data["eco_water_temp_4"] = self.client.decode_temperature(eco_temps_batch[3], TEMP_SCALE_05)
                    data["eco_cool_temp_1"] = self.client.decode_temperature(eco_temps_batch[4], TEMP_SCALE_05)
                    data["eco_cool_temp_2"] = self.client.decode_temperature(eco_temps_batch[5], TEMP_SCALE_05)
                    data["eco_cool_temp_3"] = self.client.decode_temperature(eco_temps_batch[6], TEMP_SCALE_05)
                    data["eco_cool_temp_4"] = self.client.decode_temperature(eco_temps_batch[7], TEMP_SCALE_05)
                else:
                    _LOGGER.warning("Failed to read eco temps batch")
                
                # Batch 7: General configuration (0x0181-0x0185) - 5 registers
                general_config_1 = await self.client.read_holding_registers(0x0181, 5)
                if general_config_1:
                    data["hotwater_heater_delay"] = general_config_1[0]
                    data["heating_heater_delay"] = general_config_1[1]
                    data["hotwater_heater_ext_temp"] = general_config_1[2]
                    data["heating_heater_ext_temp"] = general_config_1[3]
                    data["pump_start_interval"] = general_config_1[4]
                else:
                    _LOGGER.warning("Failed to read general config 1 batch")
                
                # Batch 8: More general config (0x018D, 0x0190-0x019E) - read in chunks
                dc_pump_delta = await self.client.read_holding_registers(0x018D, 1)
                if dc_pump_delta:
                    data["dc_pump_delta_temp"] = dc_pump_delta[0]
                
                general_config_2 = await self.client.read_holding_registers(0x0190, 15)
                if general_config_2:
                    data["fan_mode"] = general_config_2[0]
                    data["enable_switch"] = general_config_2[1]
                    data["ambtemp_switch_setp"] = general_config_2[2]
                    data["ambtemp_diff"] = general_config_2[3]
                    # Antilegionella (0x019A = offset 10 from 0x0190)
                    if len(general_config_2) >= 14:
                        data["antilegionella_temp"] = general_config_2[10]
                        data["antilegionella_weekday"] = general_config_2[11]
                        data["antilegionella_start_hour"] = general_config_2[12]
                        data["antilegionella_end_hour"] = general_config_2[13]
                    # Pump work mode (0x019E = offset 14 from 0x0190)
                    if len(general_config_2) >= 15:
                        data["pump_work_mode"] = general_config_2[14]
                else:
                    _LOGGER.warning("Failed to read general config 2 batch")
                
                return data
                
        except asyncio.TimeoutError as err:
            # On timeout, disconnect to force reconnect on next update
            _LOGGER.warning("Timeout fetching data, will reconnect on next update")
            await self.client.disconnect()
            raise UpdateFailed("Timeout communicating with heat pump") from err
        except Exception as err:
            # On any error, disconnect to force reconnect
            _LOGGER.error("Error communicating with heat pump: %s", err)
            await self.client.disconnect()
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
