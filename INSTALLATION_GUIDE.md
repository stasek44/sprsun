# SPRSUN Heat Pump Integration - Installation Guide

## Quick Start

Your SPRSUN Heat Pump custom integration is now ready! Here's how to install and use it.

---

## Installation Steps

### Step 1: Copy to Home Assistant

Copy the entire `custom_components/sprsun` folder to your Home Assistant configuration directory:

```
config/
  └── custom_components/
      └── sprsun/
          ├── __init__.py
          ├── binary_sensor.py
          ├── climate.py
          ├── config_flow.py
          ├── const.py
          ├── manifest.json
          ├── number.py
          ├── select.py
          ├── sensor.py
          ├── strings.json
          └── README.md
```

**Methods to copy:**
- **File Share**: Access HA via Samba/File Editor addon
- **SSH/Terminal**: Use SCP or terminal addon
- **VS Code**: Use the Home Assistant VS Code addon

### Step 2: Restart Home Assistant

Go to **Settings** → **System** → **Restart**

### Step 3: Add the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ ADD INTEGRATION** (bottom right)
3. Search for **"SPRSUN Heat Pump"**
4. Enter your connection details:
   - **IP Address**: Your Modbus TCP gateway IP (e.g., 192.168.6.203)
   - **Port**: 502 (default Modbus TCP port)
   - **Slave ID**: 1 (default)
   - **Scan Interval**: 30 seconds (default)
5. Click **Submit**

---

## What You Get

Once configured, you'll see:

### 🌡️ Climate Entities (3)
- Heating Temperature Control
- Cooling Temperature Control  
- Hot Water Temperature Control

### 📊 Sensors (17+)
- All temperature readings
- Compressor frequency and current
- Pump speed, fan speeds
- System voltages and runtime

### 🔘 Binary Sensors (15+)
- Hot water demand, heating demand
- Compressor running, pump running
- Three-way valve status
- Alarms and defrost status

### ⚙️ Select Controls (3)
- **Unit Mode**: DHW / Heating / Cooling / Heating+DHW / Cooling+DHW
- **Fan Mode**: Normal / ECO / Night / Test
- **Pump Mode**: Interval / Normal / Demand

### 🔢 Number Controls (9)
- Defrost periods (1, 2, 3)
- Pump cycle time
- Pump minimum frequency
- Compressor frequencies for different temperature ranges

---

## Understanding the Unit Mode Issue

### The Problem

You mentioned the pump shows "CWU" (DHW) mode but it's actually running "CO + CWU" (Heating + DHW), and changing the mode doesn't affect anything.

### The Solution in This Integration

The new **Select** entity for Unit Mode:

1. **Shows the actual register value** from the heat pump
2. **Provides extra attributes** showing real-time demands:
   ```yaml
   mode_value: 3  # What's actually set in register
   hotwater_demand: true
   heating_demand: true
   cooling_demand: false
   ```

3. **Updates immediately** when you change the mode

### How to Check What's Really Running

Don't rely on just the mode setting! Check these binary sensors:

- ✅ **"Hot Water Demand"** - Is DHW being requested?
- ✅ **"Heating Demand"** - Is heating being requested?
- ✅ **"Three-Way Valve"** - Is it directing to hot water tank?
- ✅ **"Compressor"** - Is compressor running?
- ✅ **"Heating Heater"** - Is electric heater assisting?

### Why Mode Changes Might Not Work

The heat pump may ignore mode changes if:
- ❌ Current cycle is in progress (wait for completion)
- ❌ Temperature conditions don't match the new mode
- ❌ Safety lockouts are active
- ❌ Other control systems are overriding (timer, external controller)

### How to Fix Mode Issues

**Option 1: Use the New Integration**
- The Select entity writes directly to register 54 (0x0036)
- Shows immediate feedback via attributes
- No automation complexity needed

**Option 2: Check Your Old Automation**
If the old automation isn't working, it's likely because:
```yaml
# Old automation extracts first character: "3 Heating + DHW" → 3
value: '{{ trigger.to_state.state[0] | int(0) }}'
```

This works IF your input_select option format is exactly:
- `"0 CWU"` ✅
- `"3 Ogrzewanie i CWU"` ✅

But fails if format is:
- `"CWU"` ❌ (no number)
- `"Mode 3"` ❌ (number not first)

---

## Complete Feature List

### Climate Control
| Entity | Range | Step | Register |
|--------|-------|------|----------|
| Heating Setpoint | 10-55°C | 0.5°C | 204 (0x00CC) |
| Cooling Setpoint | 12-30°C | 0.5°C | 203 (0x00CB) |
| Hot Water Setpoint | 10-55°C | 0.5°C | 202 (0x00CA) |

### Mode Selection  
| Entity | Options | Register |
|--------|---------|----------|
| Unit Mode | DHW, Heating, Cooling, Heating+DHW, Cooling+DHW | 54 (0x0036) |
| Fan Mode | Normal, ECO, Night, Test | 400 (0x0190) |
| Pump Mode | Interval, Normal, Demand | 414 (0x019E) |

### Adjustable Parameters
| Entity | Range | Step | Register |
|--------|-------|------|----------|
| Defrost Period 1 | 10-120 min | 5 min | 56 (0x0038) |
| Defrost Period 2 | 10-120 min | 5 min | 57 (0x0039) |
| Defrost Period 3 | 10-120 min | 5 min | 58 (0x003A) |
| Pump Cycle | 1-120 min | 5 min | 389 (0x0185) |
| Pump Min Freq | 60-100% | 5% | 394 (0x018A) |
| DHW Freq (T>14) | 30-60 Hz | 1 Hz | 252 (0x00FC) |
| DHW Freq (9-14) | 30-70 Hz | 1 Hz | 253 (0x00FD) |
| Heat Freq (T>14) | 30-60 Hz | 1 Hz | 260 (0x0104) |
| Heat Freq (9-14) | 30-70 Hz | 1 Hz | 261 (0x0105) |

---

## Dashboard Card Example

Create a nice dashboard card to control your heat pump:

```yaml
type: entities
title: SPRSUN Heat Pump
entities:
  # Mode Control
  - entity: select.sprsun_heat_pump_unit_mode
    name: Operating Mode
  - entity: select.sprsun_heat_pump_fan_mode
    name: Fan Mode
  - entity: select.sprsun_heat_pump_pump_mode
    name: Pump Mode
  
  # Temperature Controls
  - entity: climate.sprsun_heat_pump_heating
    name: Heating
  - entity: climate.sprsun_heat_pump_hot_water
    name: Hot Water
  
  # Status
  - type: section
    label: Current Status
  - entity: binary_sensor.sprsun_heat_pump_hot_water_demand
    name: DHW Demand
  - entity: binary_sensor.sprsun_heat_pump_heating_demand
    name: Heating Demand
  - entity: binary_sensor.sprsun_heat_pump_compressor
    name: Compressor
  - entity: binary_sensor.sprsun_heat_pump_three_way_valve
    name: Three-Way Valve
  
  # Temperatures
  - type: section
    label: Temperatures
  - entity: sensor.sprsun_heat_pump_outlet_temperature
    name: Outlet
  - entity: sensor.sprsun_heat_pump_inlet_temperature
    name: Inlet
  - entity: sensor.sprsun_heat_pump_hot_water_temperature
    name: Hot Water
  - entity: sensor.sprsun_heat_pump_ambient_temperature
    name: Ambient
  
  # Compressor
  - type: section
    label: Compressor
  - entity: sensor.sprsun_heat_pump_compressor_frequency
    name: Frequency
  - entity: sensor.sprsun_heat_pump_compressor_current
    name: Current
```

---

## Troubleshooting

### Integration doesn't appear
- Check Home Assistant logs: **Settings** → **System** → **Logs**
- Verify files are in `config/custom_components/sprsun/`
- Restart Home Assistant again

### Cannot connect
- Verify gateway IP is correct and accessible
- Check port 502 is not blocked by firewall
- Test with Modbus testing tool first
- Verify slave ID matches heat pump setting

### Values not updating
- Check scan interval (default 30 seconds)
- Look for Modbus errors in logs
- Verify only this integration is accessing the heat pump

### Mode changes don't take effect
- Check the entity's attributes for actual register value
- Look at the binary sensor demands  
- Wait for current heating/cooling cycle to complete
- Check heat pump display for lockouts or errors

---

## Next Steps

1. ✅ **Install the integration** following steps above
2. ✅ **Create dashboard cards** for easy control
3. ✅ **Set up automations** based on demands and status
4. ✅ **Monitor** the extra attributes on Unit Mode entity
5. ✅ **Compare** to your old YAML configuration

---

## Migrating from Old YAML Config

If you want to keep both running temporarily:

1. **Install this integration first**
2. **Disable old automations** (don't delete yet)
3. **Test the new Select entities**
4. **Compare behavior** for a few days
5. **Remove old YAML** when satisfied

The integration is **more reliable** because:
- ✅ Direct register access (no template complexity)
- ✅ Immediate feedback via attributes
- ✅ Better error handling and logging
- ✅ UI configuration (no YAML editing)

---

## Support

- Check logs in **Settings** → **System** → **Logs**
- Review [README.md](custom_components/sprsun/README.md) for detailed info
- See [SPRSUN_Complete_Documentation.md](SPRSUN_Complete_Documentation.md) for register details

---

**🎉 Enjoy your new SPRSUN integration!**
