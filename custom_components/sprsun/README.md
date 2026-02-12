# SPRSUN Heat Pump Integration for Home Assistant

Version 3.0.0 - Complete rewrite using synchronous Modbus pattern

## Architecture

This integration uses a **synchronous Modbus approach** with persistent TCP connection, following the patterns documented in `modbus_integration_guide.md`.

### Key Design Decisions

1. **Synchronous Modbus Client** (`modbus.py`)
   - Uses `ModbusTcpClient` (sync, not `AsyncModbusTcpClient`)
   - Persistent connection with `threading.Lock` for serial access
   - Fail-fast 10-second timeout
   - Auto-reconnect on connection loss

2. **Main Entity Pattern** (`climate.py`)
   - Climate entity has `should_poll = True`
   - `update()` method (synchronous) performs 12 optimized batch reads
   - Updates shared `_data_cache` dictionary with all register values
   - Other entities read from this cache (no direct Modbus access)

3. **Batch Read Strategy**
   - 12 optimized batches covering all 440 rows from Modbus reference
   - Handles documented gaps: 0x0010, 0x0035, 0x00C7-0x00C9, 0x018E-0x018F, 0x0194-0x0199
   - Minimizes network round-trips while respecting device memory layout

4. **Data Type Handling**
   - Helper functions: `decode_signed_int()`, `decode_temperature()`, `encode_temperature()`
   - Proper signed conversion for temperatures (can be negative)
   - Scale factors: 1, 10, 100 depending on parameter type

## Files

- `__init__.py` - Integration setup, creates Modbus client and forwards to platforms
- `config_flow.py` - UI configuration with connection validation
- `const.py` - All register addresses, bit mappings, validation ranges (359 lines)
- `modbus.py` - Synchronous Modbus wrapper with Lock (318 lines)
- `climate.py` - Main entity with update() method and _data_cache (330+ lines)
- `sensor.py` - Read-only sensors (temperatures, COP, electrical metrics)
- `binary_sensor.py` - Boolean status flags from bit fields
- `number.py` - Writable numeric parameters (setpoints, economic mode)
- `select.py` - Mode selections (unit mode, fan mode, pump mode)
- `switch.py` - On/off controls (power, economic mode, silent mode)
- `strings.json` + `translations/en.json` - UI translations

## Supported Entities

### Climate
- **Heat Pump** - Main control entity with HVAC modes (heat/cool/off)

### Sensors (23)
- Temperature sensors (9): inlet, outlet, ambient, coil, exhaust, etc.
- Performance: COP, heating/cooling capacity
- Electrical: AC voltage/current, DC bus voltage, compressor current
- Compressor: frequency, target frequency, runtime
- Fans: DC fan 1/2 speeds
- Flow: pump flow rate, EEV1/2 openings

### Binary Sensors (17)
- Demands: hotwater, heating, cooling
- Status: defrost, anti-legionella, compressor/fan/pump running
- Heaters: heating heater, hotwater heater
- Safety: water flow switch, emergency switch
- Faults: high voltage, high outlet, high exhaust, over/underpressure

### Numbers (18)
- Setpoints: heating, cooling, hotwater
- Economic mode: 4x heating ambient thresholds + 4x heating temp setpoints
- Anti-legionella: temperature, weekday, start/end hours
- Heater delays: hotwater, heating
- Pump: startup interval, DC pump temp diff

### Selects (4)
- Unit mode: DHW Only, Heating, Cooling, Heating+DHW, Cooling+DHW
- Fan mode: Normal, Economy, Night, Test
- Pump work mode: Interval, Normal, On Demand
- Mode control: No Linkage, Yes - Ambient

### Switches (4)
- Power, Economic Mode, Silent Mode, Anti-Legionella Enable

## Configuration

1. Install integration in `custom_components/sprsun/`
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "SPRSUN"
5. Enter:
   - **IP Address**: Heat pump Modbus TCP IP
   - **Port**: 502 (default)
   - **Slave ID**: 1 (default)

## Migration from 2.x

Version 3.0.0 is a **breaking change** - complete architectural rewrite:

- ❌ Removed: `DataUpdateCoordinator`, async Modbus, separate data classes
- ✅ Added: Synchronous pattern, persistent connection, batch reads, Lock

**Action required**: Remove old integration, restart HA, re-add new version. Device ID remains the same.

## Why Synchronous?

Measured data showed:
- Async overhead: 20-50ms per call
- Connection instability with frequent connect/disconnect
- Modbus protocol: master-slave, serial access required

Synchronous approach:
- ✅ Zero async overhead
- ✅ Stable persistent connection
- ✅ Explicit serialization via `threading.Lock`
- ✅ Simple executor-based async wrapping for HA
- ✅ Better error handling with fail-fast timeout

See `modbus_integration_guide.md` for detailed analysis.

## Requirements

- Home Assistant 2023.1+
- pymodbus 3.6.2
- Python 3.11+

## License

MIT License - see LICENSE file
