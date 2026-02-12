# SPRSUN Heat Pump - Complete Documentation

## Table of Contents
1. [Modbus Communication Protocol](#modbus-communication-protocol)
2. [Register Map](#register-map)
3. [Home Assistant Integration](#home-assistant-integration)
4. [Address Mapping Reference](#address-mapping-reference)

---

## Modbus Communication Protocol

### Communication Parameters
- **Protocol**: RS485 Modbus RTU
- **Baud Rate**: 19200 bps
- **Data Format**: 
  - 1 start bit
  - 8 data bits
  - 2 stop bits
  - No parity
  - 16-bit data structure
- **CRC Checksum**: 16-bit (low byte first, high byte second)
- **Unit Address**: #1 to #8 (determined by dial codes 2-4)

### Supported Commands

#### 03H - Read Holding Registers (4x)
**TX Format:**
```
[Device Address] + [03H] + [Start Register High 8] + [Low 8] + [Count High 8] + [Low 8] + [CRC Low] + [CRC High]
```

**RX Format:**
```
[Device Address] + [03H] + [Byte Count] + [Data 1] + [Data 2] + ... + [Data N] + [CRC Low] + [CRC High]
```

#### 06H - Write Single Register
**TX Format:**
```
[Device Address] + [06H] + [Register High 8] + [Low 8] + [Data High 8] + [Low 8] + [CRC Low] + [CRC High]
```

**RX Format:**
```
Returns same command if successful, otherwise no response
```

#### 10H - Write Multiple Registers
**TX Format:**
```
[Device Address] + [10H] + [Start Register High 8] + [Low 8] + [Count High 8] + [Low 8] + [Byte Count] + 
[Data 1 High] + [Low] + ... + [Data N High] + [Low] + [CRC Low] + [CRC High]
```

**RX Format:**
```
[Device Address] + [10H] + [Start Register High 8] + [Low 8] + [Count High 8] + [Low 8] + [CRC Low] + [CRC High]
```

#### 01H - Read Coils
**TX Format:**
```
[Device Address] + [01H] + [Bit Address High 8] + [Low 8] + [Count High 8] + [Low 8] + [CRC Low] + [CRC High]
```

**RX Format:**
```
[Device Address] + [01H] + [Byte Count] + [Data 1] + [Data 2] + ... + [Data N] + [CRC Low] + [CRC High]
```

#### 05H - Write Single Coil
**TX Format:**
```
[Device Address] + [05H] + [Bit Address High 8] + [Low 8] + [Data High 8] + [Low 8] + [CRC Low] + [CRC High]
```
- Lower data [FF][00] = 1 (ON)
- Lower data [00][00] = 0 (OFF)

**RX Format:**
```
Returns same command if successful, otherwise no response
```

### Important Notes
- Modify parameters only in #1 machine
- Other units can only query (read-only)

---

## Register Map

### Status and Monitoring Registers (Read Only)

| Hex Address | Dec Address | Name | Scale | Unit | Description |
|-------------|-------------|------|-------|------|-------------|
| R 0x0000 | 0 | Compressor running time | 1 | min | Accumulated operating time |
| R 0x0001 | 1 | COP | 1 | - | Coefficient of Performance |
| R 0x0002 | 2 | Switching input symbol | - | - | Bit flags for input switches |
| R 0x0003 | 3 | Working status mark | - | - | Bit flags for working status |
| R 0x0004 | 4 | Output symbol 1 | - | - | Compressor, Fan, 4-way valve status |
| R 0x0005 | 5 | Output symbol 2 | - | - | Heaters, Three-way valve status |
| R 0x0006 | 6 | Output symbol 3 | - | - | Pumps, Solenoid valve status |
| R 0x0007 | 7 | Failure symbol 1 | - | - | Temperature sensor failures |
| R 0x0008 | 8 | Failure symbol 2 | - | - | Flow and protection failures |
| R 0x0009 | 9 | Failure symbol 3 | - | - | Gas temperature failures |
| R 0x000A | 10 | Failure symbol 4 | - | - | Inlet/Exhaust failures |
| R 0x000B | 11 | Failure symbol 5 | - | - | Pressure protection failures |
| R 0x000C | 12 | Failure symbol 6 | - | - | Antifreeze failures |
| R 0x000D | 13 | Failure symbol 7 | - | - | Fan and module failures |
| R 0x000E | 14 | Inlet temp. | 0.1 | °C | Water inlet temperature |
| R 0x000F | 15 | Hotwater temp. | 0.1 | °C | Water tank temperature |
| R 0x0010 | 16 | Reserved | - | - | - |
| R 0x0011 | 17 | Ambi temp. | 0.5 | °C | Ambient temperature |
| R 0x0012 | 18 | Outlet temp. | 0.1 | °C | Water outlet temperature |
| R 0x0013 | 19 | Software year | - | - | Software change time (years) |
| R 0x0014 | 20 | Software month/day | - | - | Software change time (month/day) |
| R 0x0015 | 21 | Suct gas temp. | 0.5 | °C | Return gas temperature |
| R 0x0016 | 22 | Coil temp. | 0.5 | °C | Coil temperature |
| R 0x0017 | 23 | AC Voltage | 1 | W | AC Voltage |
| R 0x0018 | 24 | PUMP FLOW | 1 | m³/h | Pump water flow |
| R 0x0019 | 25 | Heating/cooling capacity | 1 | W | Heating/cooling capacity |
| R 0x001A | 26 | AC current | 1 | A | AC current |
| R 0x001B | 27 | Exhaust temp. | 1 | °C | Exhaust temperature |
| R 0x001C | 28 | EEV1 step. | 1 | - | Main valve opening |
| R 0x001D | 29 | EEV2 step. | 1 | - | Auxiliary valve opening |
| R 0x001E | 30 | Comp.frequency | 1 | Hz | Actual frequency of compressor |
| R 0x001F | 31 | Frequency conversion failure 1 | - | - | DC inverter failure 1 |
| R 0x0020 | 32 | Frequency conversion failure 2 | - | - | DC inverter failure 2 |
| R 0x0021 | 33 | DC bus voltage | 1 | V | DC bus voltage value |
| R 0x0022 | 34 | Driving temp. | 0.5 | °C | Heat sink temperature |
| R 0x0023 | 35 | Comp.current | 1 | A | Compressor current |
| R 0x0024 | 36 | Target frequency | 1 | Hz | Compressor target frequency |
| R 0x0025 | 37 | Smart Grid Status | - | - | Smart Grid Status |
| R 0x0026 | 38 | DC fan 1 speed | 1 | rpm | Actual speed of DC fan 1 |
| R 0x0027 | 39 | DC fan 2 speed | 1 | rpm | Actual speed of DC fan 2 |
| R 0x0028 | 40 | Evap.temp. | 0.1 | °C | Evaporation temperature |
| R 0x0029 | 41 | Cond.temp. | 0.1 | °C | Condensation temperature |
| R 0x002A | 42 | Frequency conversion fault high | - | - | Inverter fault high 8 bit |
| R 0x002B | 43 | Frequency conversion fault low | - | - | Inverter fault low 8 bit |
| R 0x002C | 44 | Controller Version | - | - | Master software version |
| R 0x002D | 45 | Display Version | - | - | Line controller software version |
| R 0x002E | 46 | DC pump speed | 1 | % | DC water pump speed |
| R 0x002F | 47 | Suct.press | 0.1 | bar | High pressure value |
| R 0x0030 | 48 | Disch.press | 0.1 | bar | Low pressure value |
| R 0x0031 | 49 | DC fan target | 1 | rpm | Target wind speed |

### Configuration Registers (Read/Write)

| Hex Address | Dec Address | Name | Range | Scale | Unit | Description |
|-------------|-------------|------|-------|-------|------|-------------|
| RW 0x0032 | 50 | Parameter marker definition | - | - | - | Control bits (ON/OFF, modes) |
| RW 0x0033 | 51 | Control mark 1 | - | - | - | Control bits (failure reset, etc.) |
| RW 0x0034 | 52 | Control mark 2 | - | - | - | Control bits (antilegionella, etc.) |
| RW 0x0036 | 54 | **P06 Unit mode** | **0-4** | **1** | - | **0=DHW, 1=Heat, 2=Cool, 3=Heat+DHW, 4=Cool+DHW** |
| RW 0x0037 | 55 | H01 Defrost freq | - | 1 | Hz | Defrost frequency |
| RW 0x0038 | 56 | **H08 Defrost period 1** | **10-120** | **1** | **min** | **Defrost period 1** |
| RW 0x0039 | 57 | **H11 Defrost period 2** | **10-120** | **1** | **min** | **Defrost period 2** |
| RW 0x003A | 58 | **H14 Defrost period 3** | **10-120** | **1** | **min** | **Defrost period 3** |
| RW 0x003B | 59 | H15 Comp total run | - | 5 | min | Compressor total run time |
| RW 0x003C | 60 | H16 Comp continuous run | - | 1 | min | Compressor continuous run |
| RW 0x003D | 61 | H05 Defrost time | - | 1 | min | Defrost time |
| RW 0x00C6 | 198 | P03 Temp.diff | 2-18 | 1 | °C | Cooling/heating startup difference |
| RW 0x00C8 | 200 | P05 Temp.diff | 2-18 | 1 | °C | Hot water startup difference |
| RW 0x00CA | 202 | P04 Hotwater setp. | 10-55 | 0.5 | °C | Hot water setting temperature |
| RW 0x00CB | 203 | P02 Cooling setp | 12-30 | 0.5 | °C | Cooling setting temperature |
| RW 0x00CC | 204 | P01 Heating setp | 10-55 | 0.5 | °C | Heating setting temperature |
| RW 0x00FB | 251 | Manual frequency setting | - | 1 | Hz | Manual frequency |
| RW 0x00FC | 252 | **Freq of water R00 T>14** | **30-60** | **1** | **Hz** | **DHW freq when T>14°C** |
| RW 0x00FD | 253 | **Freq of water R01 T=(9,14)** | **30-70** | **1** | **Hz** | **DHW freq when 9<T<14°C** |
| RW 0x0104 | 260 | **Freq of heat R04 T>14** | **30-60** | **1** | **Hz** | **Heating freq when T>14°C** |
| RW 0x0105 | 261 | **Freq of heat R05 T=(9,14)** | **30-70** | **1** | **Hz** | **Heating freq when 9<T<14°C** |
| RW 0x0181 | 385 | G08 Comp.delay | 1-60 | 1 | min | Hot water heater startup delay |
| RW 0x0182 | 386 | G06 Comp.delay | 1-60 | 1 | min | Heating heater startup delay |
| RW 0x0183 | 387 | G07 Hotwater heater Ext. | -30~30 | 1 | °C | Hot water heater startup temp |
| RW 0x0184 | 388 | G05 heating heater Ext. | -30~30 | 1 | °C | Heating heater startup temp |
| RW 0x0185 | 389 | **G03 Start internal** | **1-120** | **1** | **min** | **Pump start/stop cycle** |
| RW 0x018A | 394 | **F17 DC pump min freq** | **60-100** | **1** | **%** | **DC pump minimum frequency** |
| RW 0x018D | 397 | G04 Delta temp.set | 5-30 | 1 | °C | DC pump temp difference setting |
| RW 0x0190 | 400 | **P07 FAN mode** | **0-3** | **1** | - | **0=Normal, 1=ECO, 2=Night, 3=Test** |
| RW 0x0191 | 401 | G09 Enable switch | - | - | - | Mode control (NO linkage/YES amb) |
| RW 0x0192 | 402 | G10 Ambtemp switch setp. | -20~30 | 1 | °C | Ambient temperature setting |
| RW 0x0193 | 403 | G11 Ambtemp diff. | 1-10 | 1 | °C | Ambient temperature difference |
| RW 0x019A | 410 | Temp.set point of antilegionella | 30-70 | 1 | °C | Antilegionella temperature |
| RW 0x019B | 411 | weekday of antilegionella | 0-6 | 1 | - | Weekday (0=Sun, 6=Sat) |
| RW 0x019C | 412 | Start timer of antilegionella | 0-23 | 1 | h | Start hour |
| RW 0x019D | 413 | End timer of antilegionella | 0-23 | 1 | h | End hour |
| RW 0x019E | 414 | **G02 Pump work** | **0-2** | **1** | - | **0=Interval, 1=Normal, 2=Demand** |

**Bold entries** indicate registers commonly used for automation control.

---

## Bit Flag Definitions

### 0x0002 - Switching Input Symbol
- **Bit 0**: A/C Linkage switch
- **Bit 1**: Emergency/Linkage switch
- **Bit 2**: Heating linkage
- **Bit 3**: Cooling linkage
- **Bit 4**: Flow Switch
- **Bit 5**: High pressure switch
- **Bit 6**: Phase sequence detection
- **Bit 7**: Invalid/Grid Signal

### 0x0003 - Working Status Mark
- **Bit 0**: Hotwater demand
- **Bit 1**: Heating demand
- **Bit 2**: With or without heating
- **Bit 3**: With or without cooling
- **Bit 4**: Antilegionella on
- **Bit 5**: Cooling demand
- **Bit 6**: Alarm downtime
- **Bit 7**: Defrost active

### 0x0004 - Output Symbol 1
- **Bit 0**: Compressor status
- **Bit 1-4**: Reserved
- **Bit 5**: Fan status
- **Bit 6**: 4-way valve status
- **Bit 7**: High/low fan speed (0=low, 1=high)

### 0x0005 - Output Symbol 2
- **Bit 0**: Chassis heater
- **Bit 1-4**: Reserved
- **Bit 5**: Heating heater status
- **Bit 6**: Three-way valve status
- **Bit 7**: Hotwater heater status

### 0x0006 - Output Symbol 3
- **Bit 0**: A/C Pump (end pump)
- **Bit 1**: Crank heater status
- **Bit 2-4**: Reserved
- **Bit 5**: Assistant solenoid valve (enhanced enthalpy)
- **Bit 6**: Pump status
- **Bit 7**: Reserved

### 0x0007 - Failure Symbol 1
- **Bit 0**: Hotwater temperature sensor failure
- **Bit 1**: Ambient temperature sensor failure
- **Bit 2**: Coil temperature sensor failure
- **Bit 3**: Reserved
- **Bit 4**: Outlet temperature sensor failure
- **Bit 5**: High pressure sensor failure
- **Bit 6**: Reserved
- **Bit 7**: Phase sequence failure

### 0x0008 - Failure Symbol 2
- **Bit 0**: Water flow switch failure
- **Bit 1**: Reserved
- **Bit 2**: High protection of heating water outlet
- **Bit 3-7**: Reserved

### 0x0009 - Failure Symbol 3
- **Bit 0-5**: Reserved
- **Bit 6**: Outlet gas temperature failure
- **Bit 7**: Reserved

### 0x000A - Failure Symbol 4
- **Bit 0**: Water inlet temperature sensor failure
- **Bit 1**: Exhaust temperature too high protection
- **Bit 2**: Economy into temperature sensor failure
- **Bit 3**: Economy out temperature sensor failure
- **Bit 4**: Reserved
- **Bit 5**: Overcooling protection of cooling outlet water
- **Bit 6**: Return air temperature sensor failure
- **Bit 7**: Reserved

### 0x000B - Failure Symbol 5
- **Bit 0**: Low pressure underpressure protection
- **Bit 1**: High pressure overpressure protection
- **Bit 2**: Coil temperature too high protection
- **Bit 3-5**: Reserved
- **Bit 6**: High pressure sensor failure
- **Bit 7**: Low pressure sensor failure

### 0x000C - Failure Symbol 6
- **Bit 0-3**: Reserved
- **Bit 4**: Secondary antifreeze
- **Bit 5**: Primary antifreeze
- **Bit 6-7**: Reserved

### 0x000D - Failure Symbol 7
- **Bit 0**: Reserved
- **Bit 1**: Ambient temperature too low protection
- **Bit 2-3**: Reserved
- **Bit 4**: Inverter module communication failure
- **Bit 5**: DC fan 2 fault
- **Bit 6**: DC fan 1 fault
- **Bit 7**: Reserved

### 0x0032 - Parameter Marker Definition
- **Bit 0**: Unit ON/OFF (0=OFF, 1=ON) [Bit address: 0x0320]
- **Bit 1**: Main valve mode (0=Auto, 1=Manual) [Bit address: 0x0321]
- **Bit 2**: Manual frequency selection [Bit address: 0x0322]
- **Bit 3**: Reserved
- **Bit 4**: Reserved
- **Bit 5**: Auxiliary valve mode (0=Auto, 1=Manual) [Bit address: 0x0325]
- **Bit 6**: Expansion valve initial opening (0=fixed, 1=adjustable) [Bit address: 0x0326]
- **Bit 7**: Reserved

### 0x0033 - Control Mark 1
- **Bit 0**: Thermostatic adjustment (0=no, 1=yes)
- **Bit 1**: Pressure sensor valid (0=no, 1=yes)
- **Bit 2**: Cooling auxiliary circuit enable (0=allowed, 1=not allowed)
- **Bit 3**: Auxiliary expansion valve mode (0=Enhanced enthalpy superheat, 1=Exhaust superheat)
- **Bit 4**: DC Fan 1 selection (0=no, 1=yes)
- **Bit 5**: DC Fan 2 selection (0=no, 1=yes)
- **Bit 6**: Parameter reset selection (0=normal, 1=requires reset)
- **Bit 7**: Lockout fault reset selection (0=normal, 1=requires reset)

### 0x0034 - Control Mark 2
- **Bit 0**: Antilegionella enable (0=no, 1=yes)
- **Bit 1**: With or without hot water (0=no, 1=yes)
- **Bit 2**: Clock is at night 20:00-08:00 (0=no, 1=yes)
- **Bit 3**: Load fast check mode (0=normal, 1=load)
- **Bit 4**: Forced defrost (0=no effect, 1=forced entry)
- **Bit 5**: Reserved
- **Bit 6**: With or without smart grid (0=no, 1=yes)
- **Bit 7**: Smart grid with or without electric heater (0=no, 1=yes)

---

## Home Assistant Integration

### Quick Connection Guide

1. **RS485 to Ethernet Converter**: Configure for Modbus TCP
2. **Connection Parameters**:
   - IP: Your converter's IP address
   - Port: 502 (standard Modbus TCP)
   - Slave ID: 1 (default)
3. **Home Assistant Configuration**: Add to `configuration.yaml`

### Basic Configuration Template

```yaml
modbus:
  - name: "Sprsun PC"
    type: tcp
    host: 192.168.x.x  # Your Modbus TCP gateway IP
    port: 502
    delay: 5
    timeout: 5
```

---

## Address Mapping Reference

### Decimal ↔ Hexadecimal Quick Reference

| Function | Decimal | Hexadecimal | Register Name |
|----------|---------|-------------|---------------|
| Unit Mode | 54 | 0x0036 | P06 Unit mode |
| Defrost Period 1 | 56 | 0x0038 | H08 Defrost period 1 |
| Defrost Period 2 | 57 | 0x0039 | H11 Defrost period 2 |
| Defrost Period 3 | 58 | 0x003A | H14 Defrost period 3 |
| DHW Freq (T>14) | 252 | 0x00FC | Freq of water R00 |
| DHW Freq (9-14) | 253 | 0x00FD | Freq of water R01 |
| Heat Freq (T>14) | 260 | 0x0104 | Freq of heat R04 |
| Heat Freq (9-14) | 261 | 0x0105 | Freq of heat R05 |
| Pump Start Cycle | 389 | 0x0185 | G03 Start internal |
| Pump Min Freq | 394 | 0x018A | F17 DC pump min freq |
| Compressor Mode | 400 | 0x0190 | P07 FAN mode |
| Pump Work Mode | 414 | 0x019E | G02 Pump work |

### Important Notes on Address Formats

- **Modbus Sensor Configuration**: Uses hexadecimal format (0x0036)
- **Automation Write Commands**: Uses decimal format (54)
- **Both refer to the same register**: Just different representations
- **Conversion**: Hex to Dec in Windows Calculator (Programmer mode)

**Example:**
- `0x0036` (hex) = `54` (decimal) = Same register

---

## Document Version
- **Created**: 2026-02-12
- **Based on**: SPRSUN Modbus Communication Protocol Documentation
- **Integration**: Home Assistant
