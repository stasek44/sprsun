"""Modbus client wrapper for SPRSUN heat pump integration.

Synchronous implementation with persistent connection for optimal performance.
Based on modbus_integration_guide.md best practices.
"""
from __future__ import annotations

import logging
from threading import Lock
from typing import Callable

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

_LOGGER = logging.getLogger(__name__)


def decode_signed_int(raw: int) -> int:
    """Convert 16-bit unsigned to signed integer.
    
    Raw Values:
    - 0-32767: Positive (0 to +32767)
    - 32768-65535: Negative (-32768 to -1)
    
    Args:
        raw: Raw register value (0-65535)
    
    Returns:
        Signed integer (-32768 to +32767)
    """
    if raw > 32767:
        return raw - 65536
    return raw


def decode_temperature(raw: int, scale: float = 0.1, signed: bool = False) -> float:
    """Decode temperature from raw register.
    
    Args:
        raw: Raw register value (0-65535)
        scale: Scaling factor (0.1, 0.5, or 1.0)
        signed: True for ambient/setpoint temps that can be negative
    
    Returns:
        Temperature in °C
    """
    value = decode_signed_int(raw) if signed else raw
    return round(value * scale, 1)


def encode_temperature(temp: float, scale: float = 0.1, signed: bool = False) -> int:
    """Encode temperature to register value.
    
    Args:
        temp: Temperature in °C (can be negative)
        scale: Scaling factor (0.1, 0.5, or 1.0)
        signed: True if parameter can be negative
    
    Returns:
        Register value (0-65535)
    """
    raw = int(temp / scale)
    
    # Convert negative to 16-bit unsigned
    if signed and raw < 0:
        raw += 65536
    
    return raw & 0xFFFF


def decode_pressure(raw: int) -> float:
    """Decode pressure from raw register.
    
    Args:
        raw: Raw register value
    
    Returns:
        Pressure in bar
    """
    return round(raw * 0.01, 2)


def parse_bit_field(register: int, bit_map: dict[int, str]) -> dict[str, bool]:
    """Parse bit field into individual boolean flags.
    
    Args:
        register: Register value
        bit_map: Mapping of bit positions to flag names
    
    Returns:
        Dictionary of flag names to boolean values
    """
    return {
        name: bool(register & (1 << bit))
        for bit, name in bit_map.items()
    }


class SPRSUNModbusClient:
    """Modbus TCP client with persistent connection.
    
    Implements synchronous pattern with threading.Lock for serial access.
    Follows modbus_integration_guide.md best practices.
    """
    
    def __init__(
        self,
        host: str,
        port: int,
        slave_id: int = 1,
        timeout: int = 10,
    ) -> None:
        """Initialize Modbus client.
        
        Args:
            host: IP address or hostname
            port: TCP port (typically 502)
            slave_id: Modbus slave ID (typically 1)
            timeout: Socket timeout in seconds (fail-fast: 10s recommended)
        """
        self._host = host
        self._port = port
        self._slave_id = slave_id
        self._client = ModbusTcpClient(
            host=host,
            port=port,
            timeout=timeout,
            retries=3,
        )
        self._lock = Lock()
        self._connected = False
    
    def connect(self) -> bool:
        """Connect to Modbus device.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._connected = self._client.connect()
            if self._connected:
                _LOGGER.info("Connected to SPRSUN at %s:%s", self._host, self._port)
            else:
                _LOGGER.error("Failed to connect to %s:%s", self._host, self._port)
            return self._connected
        except Exception as err:
            _LOGGER.error("Connection exception to %s:%s: %s", self._host, self._port, err)
            self._connected = False
            return False
    
    def close(self) -> None:
        """Close connection."""
        if self._client:
            self._client.close()
            self._connected = False
            _LOGGER.info("Closed connection to %s:%s", self._host, self._port)
    
    def read_batch(self, address: int, count: int) -> list[int] | None:
        """Read holding registers in batch.
        
        Implements auto-reconnect on connection loss.
        Thread-safe with Lock for serial Modbus access.
        
        Args:
            address: Starting register address (hex)
            count: Number of registers to read
        
        Returns:
            List of register values or None on error
        """
        with self._lock:
            # Auto-reconnect if connection lost
            if not self._client.is_socket_open():
                _LOGGER.warning(
                    "Connection lost to %s:%s, reconnecting...",
                    self._host, self._port
                )
                if not self.connect():
                    return None
            
            try:
                result = self._client.read_holding_registers(
                    address, count=count, device_id=self._slave_id
                )
                
                if result.isError():
                    _LOGGER.error(
                        "Modbus error reading 0x%04X (count: %d): %s",
                        address, count, result
                    )
                    return None
                
                _LOGGER.debug(
                    "Read 0x%04X (count: %d): first values %s",
                    address, count, result.registers[:3] if count > 3 else result.registers
                )
                return result.registers
                
            except ModbusException as err:
                _LOGGER.error(
                    "Modbus exception at 0x%04X (count: %d): %s",
                    address, count, err
                )
                return None
                
            except Exception as err:
                _LOGGER.exception(
                    "Unexpected error at 0x%04X (count: %d)",
                    address, count
                )
                return None
    
    def write_register(self, address: int, value: int) -> bool:
        """Write single register.
        
        Thread-safe with Lock for serial Modbus access.
        
        Args:
            address: Register address (hex)
            value: Value to write (0-65535)
        
        Returns:
            True on success, False on error
        """
        with self._lock:
            if not self._client.is_socket_open():
                if not self.connect():
                    return False
            
            try:
                result = self._client.write_register(
                    address, value, device_id=self._slave_id
                )
                
                if result.isError():
                    _LOGGER.error(
                        "Modbus write error at 0x%04X: %s",
                        address, result
                    )
                    return False
                
                _LOGGER.info("Wrote value %d (0x%04X) to register 0x%04X", value, value, address)
                return True
                
            except ModbusException as err:
                _LOGGER.error("Modbus write exception at 0x%04X: %s", address, err)
                return False
                
            except Exception as err:
                _LOGGER.exception("Unexpected write error at 0x%04X", address)
                return False
    
    def write_coil(self, address: int, value: bool) -> bool:
        """Write single coil (bit).
        
        Args:
            address: Coil address (calculated as register × 16 + bit)
            value: True for ON, False for OFF
        
        Returns:
            True on success, False on error
        """
        with self._lock:
            if not self._client.is_socket_open():
                if not self.connect():
                    return False
            
            try:
                result = self._client.write_coil(
                    address, value, device_id=self._slave_id
                )
                
                if result.isError():
                    _LOGGER.error(
                        "Modbus coil write error at 0x%04X: %s",
                        address, result
                    )
                    return False
                
                _LOGGER.info("Wrote coil 0x%04X = %s", address, value)
                return True
                
            except ModbusException as err:
                _LOGGER.error("Modbus coil write exception at 0x%04X: %s", address, err)
                return False
                
            except Exception as err:
                _LOGGER.exception("Unexpected coil write error at 0x%04X", address)
                return False
