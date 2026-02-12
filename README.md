# SPRSUN Heat Pump Integration for Home Assistant

Home Assistant custom integration for SPRSUN heat pumps with Modbus TCP support.

## Features

- **Climate Control**: Heating, cooling, and DHW (domestic hot water) temperature control
- **Sensors**: Monitor temperatures, compressor frequency, pump speeds, and more
- **Binary Sensors**: Status indicators for compressor, defrost, alarms, and system states
- **Selects**: Change operating modes (unit mode, fan mode, pump mode)
- **Numbers**: Adjust defrost periods, pump frequencies, and compressor settings

## Supported Models

This integration is designed for SPRSUN heat pumps with Modbus TCP connectivity, including models like:
- CGK-025V3L-B (9.5 kW, 380V)
- Other SPRSUN models with Modbus TCP interface

## Installation

### Prerequisites

- Home Assistant 2024.1.0 or newer
- HACS (Home Assistant Community Store) installed
- SPRSUN heat pump with Modbus TCP gateway connected to your network

### Installation via HACS

1. **Add Custom Repository**:
   - Open HACS in your Home Assistant
   - Click on "Integrations"
   - Click the three dots menu (⋮) in the top right
   - Select "Custom repositories"
   - Add the repository URL: `https://github.com/stasek44/sprsun`
   - Category: "Integration"
   - Click "Add"

2. **Install Integration**:
   - Search for "SPRSUN Heat Pump" in HACS
   - Click "Download"
   - Restart Home Assistant

3. **Configure Integration**:
   - Go to Settings → Devices & Services
   - Click "+ Add Integration"
   - Search for "SPRSUN"
   - Enter your heat pump connection details:
     - **IP Address**: Your heat pump's Modbus TCP gateway IP
     - **Port**: Default is 502
     - **Slave ID**: Default is 1
     - **Scan Interval**: Default is 30 seconds

## Configuration

After installation, the integration will create:
- 1 Climate entity for temperature control
- Multiple sensor entities for monitoring
- Binary sensor entities for status monitoring
- Select entities for mode selection
- Number entities for parameter adjustment

## Troubleshooting

### Connection Issues

- Verify the IP address and port of your Modbus TCP gateway
- Ensure the gateway is accessible on your network
- Check that the Slave ID matches your device configuration
- Confirm your heat pump's Modbus TCP interface is enabled

### Compatibility Issues

This integration requires `pymodbus>=3.5.4` and is compatible with pymodbus 3.11.1.

## Support

For issues, feature requests, or questions:
- [Open an issue](https://github.com/stasek44/sprsun/issues)
- Check existing issues for solutions

## Credits

Based on Modbus register documentation for SPRSUN heat pumps.

## License

This project is provided as-is for personal use.
