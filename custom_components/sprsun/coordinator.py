"""DataUpdateCoordinator for SPRSUN Heat Pump.

Handles all Modbus polling and data distribution to entities.
Uses synchronous Modbus reads wrapped in executor jobs.
"""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, MANUFACTURER, MODEL
from .modbus import SPRSUNModbusClient

_LOGGER = logging.getLogger(__name__)


class SPRSUNDataUpdateCoordinator(DataUpdateCoordinator[dict[int, int]]):
    """Class to manage fetching SPRSUN data from Modbus device.
    
    Polls Modbus device every 30 seconds and stores register values.
    All entities subscribe to this coordinator for updates.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        client: SPRSUNModbusClient,
        entry: ConfigEntry,
        scan_interval: int = 30,
    ) -> None:
        """Initialize the coordinator.
        
        Args:
            hass: Home Assistant instance
            client: Modbus client (already connected)
            entry: Config entry with device info
            scan_interval: Polling interval in seconds
        """
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        
        self.client = client
        self.entry = entry
        
        # Device info for all entities
        self._device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"{MANUFACTURER} {MODEL}",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for entities."""
        return self._device_info

    async def _async_update_data(self) -> dict[int, int]:
        """Fetch data from Modbus device.
        
        This method is called by Home Assistant every SCAN_INTERVAL.
        Returns a dictionary mapping register addresses to values.
        
        Uses synchronous Modbus reads wrapped in executor jobs.
        Reads registers in optimized batches to minimize network traffic.
        
        Returns:
            Dictionary of {register_address: register_value}
            
        Raises:
            UpdateFailed: If critical data fetch fails
        """
        data: dict[int, int] = {}
        failed_batches = []
        
        try:
            # Batch 1: System status (0x0000-0x000D) - 14 registers
            batch = await self.hass.async_add_executor_job(
                self.client.read_batch, 0x0000, 14
            )
            if batch is None:
                failed_batches.append("0x0000-0x000D")
                _LOGGER.warning("Failed to read system status registers (0x0000-0x000D)")
            else:
                for i, val in enumerate(batch):
                    data[0x0000 + i] = val
            
            # Batch 2: First temperature block (0x000E-0x000F) - 2 registers
            batch = await self.hass.async_add_executor_job(
                self.client.read_batch, 0x000E, 2
            )
            if batch is None:
                failed_batches.append("0x000E-0x000F")
                _LOGGER.warning("Failed to read temperature block (0x000E-0x000F)")
            else:
                for i, val in enumerate(batch):
                    data[0x000E + i] = val
            
            # Batch 3: Main temperature/sensor block (0x0011-0x0031) - 33 registers
            batch = await self.hass.async_add_executor_job(
                self.client.read_batch, 0x0011, 33
            )
            if batch is None:
                failed_batches.append("0x0011-0x0031")
                _LOGGER.warning("Failed to read main sensor block (0x0011-0x0031)")
            else:
                for i, val in enumerate(batch):
                    data[0x0011 + i] = val
            
            # Batch 4: Control markers (0x0032-0x0034) - 3 registers
            batch = await self.hass.async_add_executor_job(
                self.client.read_batch, 0x0032, 3
            )
            if batch is None:
                failed_batches.append("0x0032-0x0034")
                _LOGGER.warning("Failed to read control markers (0x0032-0x0034)")
            else:
                for i, val in enumerate(batch):
                    data[0x0032 + i] = val
            
            # Batch 5: Unit mode (0x0036) - 1 register
            batch = await self.hass.async_add_executor_job(
                self.client.read_batch, 0x0036, 1
            )
            if batch is None:
                failed_batches.append("0x0036")
                _LOGGER.warning("Failed to read unit mode (0x0036)")
            else:
                data[0x0036] = batch[0]
            
            # Batch 6: Temperature differential (0x00C6) - 1 register
            batch = await self.hass.async_add_executor_job(
                self.client.read_batch, 0x00C6, 1
            )
            if batch is None:
                failed_batches.append("0x00C6")
                _LOGGER.warning("Failed to read temperature differential (0x00C6)")
            else:
                data[0x00C6] = batch[0]
            
            # Batch 7: Setpoints (0x00CA-0x00CC) - 3 registers
            batch = await self.hass.async_add_executor_job(
                self.client.read_batch, 0x00CA, 3
            )
            if batch is None:
                failed_batches.append("0x00CA-0x00CC")
                _LOGGER.warning("Failed to read setpoints (0x00CA-0x00CC)")
            else:
                for i, val in enumerate(batch):
                    data[0x00CA + i] = val
            
            # Batch 8: Economic mode settings (0x0169-0x0180) - 24 registers
            batch = await self.hass.async_add_executor_job(
                self.client.read_batch, 0x0169, 24
            )
            if batch is None:
                failed_batches.append("0x0169-0x0180")
                _LOGGER.warning("Failed to read economic mode settings (0x0169-0x0180)")
            else:
                for i, val in enumerate(batch):
                    data[0x0169 + i] = val
            
            # Batch 9: General configuration (0x0181-0x0185) - 5 registers
            batch = await self.hass.async_add_executor_job(
                self.client.read_batch, 0x0181, 5
            )
            if batch is None:
                failed_batches.append("0x0181-0x0185")
                _LOGGER.warning("Failed to read general configuration (0x0181-0x0185)")
            else:
                for i, val in enumerate(batch):
                    data[0x0181 + i] = val
            
            # Batch 10: DC pump configuration (0x018D) - 1 register
            batch = await self.hass.async_add_executor_job(
                self.client.read_batch, 0x018D, 1
            )
            if batch is None:
                failed_batches.append("0x018D")
                _LOGGER.warning("Failed to read DC pump configuration (0x018D)")
            else:
                data[0x018D] = batch[0]
            
            # Batch 11: Mode control (0x0190-0x0193) - 4 registers
            batch = await self.hass.async_add_executor_job(
                self.client.read_batch, 0x0190, 4
            )
            if batch is None:
                failed_batches.append("0x0190-0x0193")
                _LOGGER.warning("Failed to read mode control (0x0190-0x0193)")
            else:
                for i, val in enumerate(batch):
                    data[0x0190 + i] = val
            
            # Batch 12: Anti-legionella settings (0x019A-0x019E) - 5 registers
            batch = await self.hass.async_add_executor_job(
                self.client.read_batch, 0x019A, 5
            )
            if batch is None:
                failed_batches.append("0x019A-0x019E")
                _LOGGER.warning("Failed to read anti-legionella settings (0x019A-0x019E)")
            else:
                for i, val in enumerate(batch):
                    data[0x019A + i] = val
            
            # Log summary
            if failed_batches:
                _LOGGER.warning(
                    "Partial data fetch: %d/%d batches failed: %s",
                    len(failed_batches), 12, ", ".join(failed_batches)
                )
            
            # Only fail if NO data was retrieved at all (complete communication failure)
            if not data:
                raise UpdateFailed("Complete communication failure: no data retrieved from device")
            
            _LOGGER.debug(
                "Successfully fetched %d registers from SPRSUN device",
                len(data)
            )
            
            return data
            
        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Error fetching data from SPRSUN device: {err}") from err
