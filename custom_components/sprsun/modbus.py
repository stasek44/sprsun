"""Modbus client for SPRSUN heat pump."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

_LOGGER = logging.getLogger(__name__)


class SPRSUNModbusClient:
    """SPRSUN Modbus TCP client."""

    def __init__(self, host: str, port: int, slave_id: int = 1) -> None:
        """Initialize the Modbus client.
        
        Args:
            host: IP address of the Elfin W11 device
            port: Modbus TCP port (typically 502)
            slave_id: Modbus device ID (default: 1)
            
        Note:
            In pymodbus 3.11.x, the slave_id is passed as device_id parameter to all requests.
            Most SPRSUN heat pumps use device ID 1.
        """
        self._host = host
        self._port = port
        self._slave_id = slave_id  # Stored for future use if needed
        self._client: AsyncModbusTcpClient | None = None
        self._lock = asyncio.Lock()

    async def connect(self) -> bool:
        """Connect to the Modbus device.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._client = AsyncModbusTcpClient(
                host=self._host,
                port=self._port,
                timeout=5,
            )
            result = await self._client.connect()
            if result:
                _LOGGER.info("Connected to SPRSUN heat pump at %s:%s", self._host, self._port)
            return result
        except Exception as err:
            _LOGGER.error("Failed to connect to %s:%s: %s", self._host, self._port, err)
            return False

    async def disconnect(self) -> None:
        """Disconnect from the Modbus device."""
        if self._client:
            self._client.close()
            self._client = None
            _LOGGER.info("Disconnected from SPRSUN heat pump")

    async def read_holding_registers(
        self, address: int, count: int = 1
    ) -> list[int] | None:
        """Read holding registers (function code 03H).
        
        Args:
            address: Starting register address
            count: Number of registers to read
            
        Returns:
            List of register values, or None if error
        """
        if not self._client or not self._client.connected:
            _LOGGER.error("Client not connected")
            return None

        async with self._lock:
            try:
                # pymodbus 3.11.x API - address as positional, rest as keywords
                result = await self._client.read_holding_registers(
                    address, count=count, device_id=self._slave_id
                )
                if result.isError():
                    _LOGGER.error("Error reading registers at 0x%04X: %s", address, result)
                    return None
                return result.registers
            except ModbusException as err:
                _LOGGER.error("Modbus exception reading 0x%04X: %s", address, err)
                return None
            except Exception as err:
                _LOGGER.error("Unexpected error reading 0x%04X: %s", address, err)
                return None

    async def write_register(self, address: int, value: int) -> bool:
        """Write single register (function code 06H).
        
        Args:
            address: Register address
            value: Value to write (16-bit)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._client or not self._client.connected:
            _LOGGER.error("Client not connected")
            return False

        async with self._lock:
            try:
                # pymodbus 3.11.x API - address and value as positional, device_id as keyword
                result = await self._client.write_register(
                    address, value, device_id=self._slave_id
                )
                if result.isError():
                    _LOGGER.error("Error writing register 0x%04X: %s", address, result)
                    return False
                _LOGGER.debug("Wrote value %d to register 0x%04X", value, address)
                return True
            except ModbusException as err:
                _LOGGER.error("Modbus exception writing 0x%04X: %s", address, err)
                return False
            except Exception as err:
                _LOGGER.error("Unexpected error writing 0x%04X: %s", address, err)
                return False

    async def write_registers(self, address: int, values: list[int]) -> bool:
        """Write multiple registers (function code 10H).
        
        Args:
            address: Starting register address
            values: List of values to write
            
        Returns:
            True if successful, False otherwise
        """
        if not self._client or not self._client.connected:
            _LOGGER.error("Client not connected")
            return False

        async with self._lock:
            try:
                # pymodbus 3.11.x API - address and values as positional, device_id as keyword
                result = await self._client.write_registers(
                    address, values, device_id=self._slave_id
                )
                if result.isError():
                    _LOGGER.error("Error writing registers at 0x%04X: %s", address, result)
                    return False
                _LOGGER.debug("Wrote %d values to registers starting at 0x%04X", len(values), address)
                return True
            except ModbusException as err:
                _LOGGER.error("Modbus exception writing 0x%04X: %s", address, err)
                return False
            except Exception as err:
                _LOGGER.error("Unexpected error writing 0x%04X: %s", address, err)
                return False

    async def read_coils(self, address: int, count: int = 1) -> list[bool] | None:
        """Read coils (function code 01H).
        
        Args:
            address: Starting coil address
            count: Number of coils to read
            
        Returns:
            List of coil states (True/False), or None if error
        """
        if not self._client or not self._client.connected:
            _LOGGER.error("Client not connected")
            return None

        async with self._lock:
            try:
                # pymodbus 3.11.x API - address as positional, count and device_id as keywords
                result = await self._client.read_coils(
                    address, count=count, device_id=self._slave_id
                )
                if result.isError():
                    _LOGGER.error("Error reading coils at 0x%04X: %s", address, result)
                    return None
                return result.bits[:count]
            except ModbusException as err:
                _LOGGER.error("Modbus exception reading coils 0x%04X: %s", address, err)
                return None
            except Exception as err:
                _LOGGER.error("Unexpected error reading coils 0x%04X: %s", address, err)
                return None

    async def write_coil(self, address: int, value: bool) -> bool:
        """Write single coil (function code 05H).
        
        Args:
            address: Coil address
            value: Coil state (True/False)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._client or not self._client.connected:
            _LOGGER.error("Client not connected")
            return False

        async with self._lock:
            try:
                # pymodbus 3.11.x API - address and value as positional, device_id as keyword
                result = await self._client.write_coil(
                    address, value, device_id=self._slave_id
                )
                if result.isError():
                    _LOGGER.error("Error writing coil 0x%04X: %s", address, result)
                    return False
                _LOGGER.debug("Wrote coil 0x%04X to %s", address, value)
                return True
            except ModbusException as err:
                _LOGGER.error("Modbus exception writing coil 0x%04X: %s", address, err)
                return False
            except Exception as err:
                _LOGGER.error("Unexpected error writing coil 0x%04X: %s", address, err)
                return False

    def decode_temperature(self, raw_value: int, scale: float) -> float:
        """Decode temperature from raw register value.
        
        Args:
            raw_value: Raw 16-bit register value
            scale: Scaling factor (0.1, 0.5, or 1.0)
            
        Returns:
            Temperature in degrees Celsius
        """
        # Handle signed 16-bit values
        if raw_value > 32767:
            raw_value -= 65536
        return raw_value * scale

    def encode_temperature(self, temp: float, scale: float) -> int:
        """Encode temperature to raw register value.
        
        Args:
            temp: Temperature in degrees Celsius
            scale: Scaling factor (0.1, 0.5, or 1.0)
            
        Returns:
            Raw 16-bit register value
        """
        value = int(temp / scale)
        # Handle signed 16-bit values
        if value < 0:
            value += 65536
        return value & 0xFFFF

    def decode_pressure(self, raw_value: int) -> float:
        """Decode pressure from raw register value.
        
        Args:
            raw_value: Raw 16-bit register value
            
        Returns:
            Pressure in bar
        """
        # Handle signed 16-bit values
        if raw_value > 32767:
            raw_value -= 65536
        return raw_value * 0.1

    def parse_bit_field(self, value: int) -> dict[int, bool]:
        """Parse a 16-bit register into individual bit flags.
        
        Args:
            value: 16-bit register value
            
        Returns:
            Dictionary mapping bit position to boolean value
        """
        return {bit: bool(value & (1 << bit)) for bit in range(16)}
