# SPRSUN Heat Pump Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This is a custom Home Assistant integration for SPRSUN heat pumps. It provides comprehensive monitoring and control of your SPRSUN heat pump via Modbus TCP, typically using an Elfin W11 or similar RS485-to-Ethernet gateway.

## Features

✅ **100% Parameter Coverage** - Full access to all heat pump parameters  
✅ **26 Sensor Entities** - Temperatures, electrical measurements, pressures, flow rates, and component states  
✅ **12 Binary Sensors** - Real-time status monitoring and fault detection  
✅ **5 Number Controls** - Temperature setpoints and differentials  
✅ **1 Select Control** - Operating mode selection (heating, cooling, DHW)  
✅ **1 Switch Control** - Power on/off  
✅ **Config Flow** - Easy setup through the Home Assistant UI  
✅ **HACS Compatible** - Simple installation via HACS custom repository

## Hardware Requirements

- **SPRSUN Heat Pump** with Modbus RTU interface
- **Elfin W11** (or compatible RS485-to-Ethernet gateway)
  - Configuration: 19200 baud, 8 data bits, no parity, 1 stop bit
  - Default Modbus TCP port: 502
  - Default slave ID: 1

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots menu in the top right
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/YOUR_USERNAME/sprsun`
6. Select category: "Integration"
7. Click "Add"
8. Click "Install" on the SPRSUN integration
9. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/sprsun` directory to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

### Via Home Assistant UI

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **SPRSUN**
4. Enter your connection details:
   - **IP Address**: IP address of your Elfin W11 device
   - **Port**: Modbus TCP port (default: 502)
   - **Slave ID**: Hardware address set by DIP switches on the heat pump (1-8). Use 1 unless you've changed the DIP switch settings.
5. Click **Submit**

The integration will automatically create all entities and link them to a single device.

## Entities

### Sensors (26 total)

#### Temperature Sensors (10)
- Inlet temperature
- Outlet temperature  
- Hot water temperature
- Ambient temperature
- Suction gas temperature
- Coil temperature
- Exhaust temperature
- Driving temperature
- Evaporation temperature
- Condensation temperature

#### Electrical Measurements (6)
- AC voltage
- AC current
- DC bus voltage
- Compressor current
- Compressor frequency
- Target frequency

#### Flow & Capacity (2)
- Pump flow
- Heating/cooling capacity

#### Pressure (2)
- Suction pressure
- Discharge pressure

#### Component States (6)
- Main valve opening (EEV1)
- Auxiliary valve opening (EEV2)
- DC fan 1 speed
- DC fan 2 speed
- Target fan speed
- DC pump speed

#### Performance (2)
- Compressor runtime
- COP (Coefficient of Performance)

### Binary Sensors (12 total)

#### Output Status (7)
- Compressor (running/stopped)
- Fan (running/stopped)
- 4-way valve (heating/cooling)
- Water pump (running/stopped)
- Chassis heating (on/off)
- Heating heater (on/off)
- Hot water heater (on/off)

#### Working Status (4)
- Hot water demand
- Heating demand
- Cooling demand
- Defrost mode

#### Alarms (1)
- Alarm stop

### Number Controls (5 total)

- Heating setpoint (15-55°C)
- Cooling setpoint (5-25°C)
- Hot water setpoint (35-65°C)
- Heating/cooling temperature differential (2-10°C)
- Hot water temperature differential (2-10°C)

### Select Controls (1 total)

- Unit mode:
  - Hot water only
  - Heating only
  - Cooling only
  - Heating + Hot water
  - Cooling + Hot water

### Switch Controls (1 total)

- Power (on/off)

## Usage Examples

### Automation: Turn on heating when temperature drops

```yaml
automation:
  - alias: "Start heating when cold"
    trigger:
      - platform: numeric_state
        entity_id: sensor.sprsun_inlet_temp
        below: 20
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.sprsun_power
      - service: select.select_option
        target:
          entity_id: select.sprsun_unit_mode
        data:
          option: "heating"
```

### Dashboard Card Example

```yaml
type: entities
title: SPRSUN Heat Pump
entities:
  - entity: switch.sprsun_power
  - entity: select.sprsun_unit_mode
  - entity: sensor.sprsun_inlet_temp
  - entity: sensor.sprsun_outlet_temp
  - entity: sensor.sprsun_hotwater_temp
  - entity: number.sprsun_heating_setp
  - entity: number.sprsun_hotwater_setp
  - entity: sensor.sprsun_cop
  - entity: binary_sensor.sprsun_compressor
```

## Troubleshooting

### Cannot connect to device

1. Verify the Elfin W11 IP address is correct and reachable
2. Check that port 502 is open and not blocked by firewall
3. Ensure Modbus TCP is enabled on the Elfin W11
4. Verify the slave ID matches the DIP switch setting on your heat pump (usually 1)

### Entities show "unavailable"

1. Check Home Assistant logs for connection errors
2. Verify the Elfin W11 serial settings (19200 baud, 8N1)
3. Ensure the RS485 wiring is correct (A+ and B-)
4. Try reloading the integration

### Values seem incorrect

1. Check the Modbus register scaling in the documentation
2. Verify your heat pump model is compatible
3. Enable debug logging to see raw Modbus values

## Debug Logging

Enable debug logging in `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.sprsun: debug
    pymodbus: debug
```

## Support

For issues, questions, or feature requests, please use the [GitHub issue tracker](https://github.com/YOUR_USERNAME/sprsun/issues).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- Developed for Home Assistant community
- Based on SPRSUN heat pump Modbus RTU protocol specification
- Uses [pymodbus](https://github.com/pymodbus-dev/pymodbus) library

## Disclaimer

This integration is not officially affiliated with or endorsed by SPRSUN. Use at your own risk.
