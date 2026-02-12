# SPRSUN Heat Pump Integration - Technical Documentation

## Architecture

This integration follows Home Assistant best practices and uses the modern architecture patterns:

### DataUpdateCoordinator Pattern

The integration uses a `SPRSUNDataUpdateCoordinator` to centralize data fetching:
- Single Modbus TCP connection shared across all entities
- Efficient batch reads of related registers
- 30-second update interval (configurable)
- Automatic error handling and retry logic
- Entity state updates via subscription pattern

### Modbus Client

The `SPRSUNModbusClient` wraps pymodbus `AsyncModbusTcpClient`:
- Async/await throughout for non-blocking I/O
- Supports all 5 Modbus function codes:
  - FC01: Read Coils
  - FC03: Read Holding Registers
  - FC05: Write Single Coil
  - FC06: Write Single Register
  - FC16: Write Multiple Registers
- Built-in connection management and error handling
- Helper methods for temperature/pressure decoding
- Bit field parsing for status registers

### Entity Platforms

The integration implements 5 entity platforms:

#### 1. Sensor Platform (`sensor.py`)
- 26 read-only sensor entities
- Temperature, electrical, pressure, flow, and component state sensors
- Uses `CoordinatorEntity` for automatic updates
- Device class and unit of measurement for proper handling
- Icon selection based on measurement type

#### 2. Binary Sensor Platform (`binary_sensor.py`)
- 12 binary sensors for status and alarms
- Parses bit fields from status registers
- Device class (running, problem, heat) for proper icons
- Real-time status monitoring

#### 3. Number Platform (`number.py`)
- 5 number entities for temperature setpoints
- Min/max/step validation
- Proper scaling (0.5°C or 1°C steps)
- Box mode for direct input
- Write to Modbus registers on change

#### 4. Select Platform (`select.py`)
- 1 select entity for unit mode
- Dropdown list of operating modes
- Translation keys for localized mode names
- Maps string options to numeric Modbus values

#### 5. Switch Platform (`switch.py`)
- 1 switch entity for power control
- Uses Modbus coils (FC05)
- Triggers immediate refresh after state change

### Config Flow

UI-based configuration with validation:
- Host/port/slave_id input
- Connection test before saving
- Unique ID based on host/slave_id
- Error handling with user-friendly messages

## File Structure

```
custom_components/sprsun/
├── __init__.py           # Integration setup/teardown
├── manifest.json         # Integration metadata
├── const.py             # Constants and default values
├── config_flow.py       # UI configuration flow
├── strings.json         # UI translations
├── coordinator.py       # DataUpdateCoordinator
├── modbus.py           # Modbus TCP client wrapper
├── sensor.py           # Sensor platform
├── binary_sensor.py    # Binary sensor platform
├── number.py           # Number platform
├── select.py           # Select platform
├── switch.py           # Switch platform
└── README.md           # This file
```

## Modbus Register Map

### Holding Registers (FC03/06/16)

| Address | Name | Type | Scale | R/W |
|---------|------|------|-------|-----|
| 0x001C | Unit mode | uint16 | 1 | R/W |
| 0x001D | Heating setpoint | int16 | 0.5°C | R/W |
| 0x001E | Cooling setpoint | int16 | 0.5°C | R/W |
| 0x001F | Hot water setpoint | int16 | 1°C | R/W |
| 0x0024 | Heating/cooling temp diff | uint16 | 0.5°C | R/W |
| 0x0025 | Hot water temp diff | uint16 | 1°C | R/W |
| 0x0032 | Inlet temperature | int16 | 0.1°C | R |
| 0x0033 | Outlet temperature | int16 | 0.1°C | R |
| 0x0034 | Hot water temperature | int16 | 0.1°C | R |
| ... | ... | ... | ... | ... |

See modbus_reference.md for complete register map.

### Coils (FC01/05/15)

| Address | Name | R/W |
|---------|------|-----|
| 0x0000 | Power on/off | R/W |

### Status Registers (Bit Fields)

| Address | Name | Bits |
|---------|------|------|
| 0x0002 | Switching input status | 16 |
| 0x0003 | Working status | 16 |
| 0x0008-0x000A | Output symbols 1-3 | 48 |
| 0x000B-0x0011 | Failure symbols 1-7 | 112 |

## Error Handling

### Connection Errors
- Logged with context (host, port, slave_id)
- Integration reports unavailable
- Automatic reconnection on next update cycle
- Config flow validates connection before saving

### Modbus Errors
- Invalid register addresses logged
- Timeout errors trigger backoff
- CRC/frame errors retry automatically
- Write failures don't crash entity

### Data Validation
- Temperature bounds checking
- Pressure range validation
- Bit field boundary checks
- None returned for invalid data

## Performance Considerations

### Batch Reads
The coordinator performs batch reads to minimize round trips:
```python
# Single read for all temperatures (10 registers)
temps = await client.read_holding_registers(0x0032, 10)

# Single read for all electrical (6 registers)
electrical = await client.read_holding_registers(0x003C, 6)
```

### Update Frequency
- Default: 30 seconds
- Configurable in coordinator
- Balances responsiveness vs. bus load
- Immediate refresh after write operations

### Memory Usage
- Single Modbus connection
- Lightweight entity objects
- Coordinator caches all data
- No entity polling

## Extending the Integration

### Adding New Sensors

1. Add register definition to `sensor.py`:
```python
SPRSUNSensorEntityDescription(
    key="my_new_sensor",
    translation_key="my_new_sensor",
    device_class=SensorDeviceClass.TEMPERATURE,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    state_class=SensorStateClass.MEASUREMENT,
    value_fn=lambda data: data.get("my_register"),
)
```

2. Add data fetching to `coordinator.py`:
```python
my_register = await self.client.read_holding_registers(0xXXXX, 1)
data["my_register"] = self.client.decode_temperature(my_register[0], scale=0.1)
```

3. Add translation to `strings.json`:
```json
"my_new_sensor": {"name": "My New Sensor"}
```

### Adding Writable Controls

Follow the pattern in `number.py` or `select.py`:
- Define entity description with `set_fn_register`
- Implement `async_set_native_value` or similar
- Call `client.write_register` or `client.write_coil`
- Trigger `coordinator.async_request_refresh()`

## Testing

### Manual Testing
1. Set up test environment with heat pump
2. Configure integration via UI
3. Verify all entities appear
4. Test read operations (check sensor values)
5. Test write operations (change setpoints)
6. Monitor logs for errors

### Network Troubleshooting
```bash
# Test Modbus TCP connectivity
python3 -m pymodbus.console tcp --host 192.168.1.100 --port 502

# Read a register
client.read_holding_registers address=50 count=1 unit=1
```

## Contributing

When contributing to this integration:
1. Follow Home Assistant coding standards
2. Use type hints throughout
3. Add docstrings to new functions
4. Update this documentation
5. Test with real hardware if possible
6. Enable debug logging during development

## References

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [PyModbus Documentation](https://pymodbus.readthedocs.io/)
- [SPRSUN Modbus Protocol](../../../.agent/modbus_reference.md)
- [Integration Blueprint](../../../integration_blueprint/)
