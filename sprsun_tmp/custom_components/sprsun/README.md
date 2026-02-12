# SPRSUN Heat Pump Integration for Home Assistant

A custom integration for SPRSUN heat pumps using Modbus TCP protocol.

## Features

- ✅ **Automatic Discovery**: Configure via Home Assistant UI
- 🌡️ **Climate Control**: Set heating, cooling, and hot water temperatures
- 📊 **Comprehensive Sensors**: Monitor all temperatures, pressures, and system status
- 🔧 **Configuration**: Adjust defrost periods, pump settings, and compressor frequencies
- 🔄 **Mode Selection**: Control unit mode, fan mode, and pump mode
- 🚨 **Status Monitoring**: Real-time alerts for demands, failures, and system states

## Installation

### Method 1: Manual Installation

1. Copy the `custom_components/sprsun` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Go to **Settings** → **Devices & Services** → **Add Integration**
4. Search for "SPRSUN Heat Pump"
5. Enter your Modbus TCP gateway details:
   - IP Address (e.g., 192.168.1.100)
   - Port (default: 502)
   - Slave ID (default: 1)
   - Scan Interval (default: 30 seconds)

### Method 2: HACS Installation (Future)

This integration can be added to HACS once published to a GitHub repository.

## Requirements

- **Hardware**: 
  - SPRSUN heat pump with Modbus RTU interface
  - RS485 to Ethernet (Modbus TCP) gateway
  
- **Software**:
  - Home Assistant 2023.1 or later
  - pymodbus library (automatically installed)

## Configuration

### Modbus TCP Gateway Setup

1. Connect your RS485 to Ethernet gateway to the heat pump's Modbus RTU port
2. Configure the gateway for:
   - Baud rate: 19200 bps
   - Data bits: 8
   - Stop bits: 2
   - Parity: None
   - Modbus slave ID: 1 (or as configured on your heat pump)

### Integration Setup

After adding the integration, you'll get:

#### Climate Entities
- **Heating Temperature Control** (10-55°C, 0.5°C steps)
- **Cooling Temperature Control** (12-30°C, 0.5°C steps)
- **Hot Water Temperature Control** (10-55°C, 0.5°C steps)

#### Select Entities
- **Unit Mode**: DHW, Heating, Cooling, Heating+DHW, Cooling+DHW
- **Fan Mode**: Normal, ECO, Night, Test
- **Pump Mode**: Interval, Normal, Demand

#### Number Entities
- Defrost Period 1, 2, 3 (10-120 minutes)
- Pump Cycle (1-120 minutes)
- Pump Min Frequency (60-100%)
- DHW Frequency for T>14°C (30-60 Hz)
- DHW Frequency for 9-14°C (30-70 Hz)
- Heating Frequency for T>14°C (30-60 Hz)
- Heating Frequency for 9-14°C (30-70 Hz)

#### Sensor Entities
- Temperatures: Inlet, Outlet, Ambient, Hot Water, Coil, Exhaust, etc.
- Compressor Frequency and Current
- DC Pump Speed
- Fan Speeds
- DC Bus Voltage
- Compressor Runtime

#### Binary Sensor Entities
- Hot Water Demand, Heating Demand, Cooling Demand
- Compressor Running, Fan Running, Pump Running
- Three-Way Valve Status
- Heater Status (Heating, Hot Water)
- Defrost Mode
- Alarm Status
- Antilegionella Status

## Understanding Unit Mode

The **Unit Mode** select entity controls what the heat pump is configured to do:

- **DHW** (0): Hot water only
- **Heating** (1): Space heating only
- **Cooling** (2): Space cooling only  
- **Heating + DHW** (3): Both space heating and hot water
- **Cooling + DHW** (4): Both space cooling and hot water

### Important: Status vs Mode

⚠️ **The displayed mode may differ from actual operation!**

The unit mode setting tells the heat pump what it's *allowed* to do, but:
- **Actual operation** depends on current demands (see binary sensors)
- Check the **"Hot Water Demand"** and **"Heating Demand"** binary sensors for real-time status
- The **"Three-Way Valve"** binary sensor shows if hot water is currently being heated

**Example:** If mode is set to "DHW" but the system is actually running "Heating + DHW":
- The mode setting may not have been successfully written
- Check the unit mode extra attributes for `mode_value` and demand flags
- The heat pump may ignore mode changes if certain conditions aren't met

### Troubleshooting Mode Changes

If changing the unit mode doesn't work:

1. **Check Current Demands**: Look at the binary sensors:
   - Hot Water Demand
   - Heating Demand
   - Cooling Demand

2. **Check Mode Value**: Look at the Unit Mode entity attributes:
   ```yaml
   mode_value: 3  # Actual register value
   hotwater_demand: true
   heating_demand: true
   cooling_demand: false
   ```

3. **Verify Register**: The mode is stored in register 0x0036 (decimal 54)

4. **Check Heat Pump Display**: Compare with the actual heat pump's display panel

## Modbus Register Reference

See [SPRSUN_Complete_Documentation.md](../SPRSUN_Complete_Documentation.md) for complete register documentation.

## Troubleshooting

### Cannot Connect

- Verify gateway IP address and port
- Check that gateway is on the same network
- Confirm heat pump Modbus settings match gateway configuration
- Test connection with a Modbus testing tool

### Wrong Values / Not Updating

- Check scan interval (default 30 seconds)
- Verify slave ID matches heat pump configuration
- Check Home Assistant logs for Modbus errors
- Ensure only one device is communicating with the heat pump at a time

### Mode Changes Don't Work

- Some modes may be locked out by the heat pump based on:
  - Current operating state
  - Active alarms
  - Temperature conditions
- Check the heat pump's display for error codes
- Wait for current cycle to complete before changing mode

## Support

For issues and feature requests, please use the GitHub issues page (when available).

## Credits

Based on the SPRSUN Modbus RTU protocol documentation and extensive testing.

## License

This integration is provided as-is for use with SPRSUN heat pumps. No warranty is provided.
