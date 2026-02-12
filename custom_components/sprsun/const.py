"""Constants for SPRSUN heat pump integration."""
from homeassistant.const import Platform

# Integration domain
DOMAIN = "sprsun"

# Configuration keys
CONF_SLAVE_ID = "slave_id"

# Platforms
PLATFORMS = [
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SWITCH,
]

# Device information
MANUFACTURER = "SPRSUN"
MODEL = "Heat Pump"

# Configuration
CONF_SLAVE_ID = "slave_id"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1
DEFAULT_SCAN_INTERVAL = 30  # seconds

# Platforms
PLATFORMS = [
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SWITCH,
]

# Register addresses - System Status (Read-Only)
REG_COMPRESSOR_RUNTIME = 0x0000
REG_COP = 0x0001
REG_SWITCHING_INPUT = 0x0002
REG_WORKING_STATUS = 0x0003
REG_OUTPUT_SYMBOL_1 = 0x0004
REG_OUTPUT_SYMBOL_2 = 0x0005
REG_OUTPUT_SYMBOL_3 = 0x0006
REG_FAILURE_SYMBOL_1 = 0x0007
REG_FAILURE_SYMBOL_2 = 0x0008
REG_FAILURE_SYMBOL_3 = 0x0009
REG_FAILURE_SYMBOL_4 = 0x000A
REG_FAILURE_SYMBOL_5 = 0x000B
REG_FAILURE_SYMBOL_6 = 0x000C
REG_FAILURE_SYMBOL_7 = 0x000D

# Register addresses - Temperature Sensors (Read-Only)
REG_INLET_TEMP = 0x000E
REG_HOTWATER_TEMP = 0x000F
# Note: 0x0010 doesn't exist on this device
REG_AMBIENT_TEMP = 0x0011
REG_OUTLET_TEMP = 0x0012
REG_SW_VERSION_YEAR = 0x0013
REG_SW_VERSION_MONTH_DAY = 0x0014
REG_SUCT_GAS_TEMP = 0x0015
REG_COIL_TEMP = 0x0016
REG_AC_VOLTAGE = 0x0017
REG_PUMP_FLOW = 0x0018
REG_HEATING_COOLING_CAPACITY = 0x0019
REG_AC_CURRENT = 0x001A
REG_EXHAUST_TEMP = 0x001B
REG_EEV1_STEP = 0x001C
REG_EEV2_STEP = 0x001D
REG_COMP_FREQUENCY = 0x001E
REG_FREQ_CONV_FAILURE_1 = 0x001F
REG_FREQ_CONV_FAILURE_2 = 0x0020
REG_DC_BUS_VOLTAGE = 0x0021
REG_DRIVING_TEMP = 0x0022
REG_COMP_CURRENT = 0x0023
REG_TARGET_FREQUENCY = 0x0024
REG_SMART_GRID_STATUS = 0x0025
REG_DC_FAN_1_SPEED = 0x0026
REG_DC_FAN_2_SPEED = 0x0027
REG_EVAP_TEMP = 0x0028
REG_COND_TEMP = 0x0029
REG_FREQ_CONV_FAULT_HIGH = 0x002A
REG_FREQ_CONV_FAULT_LOW = 0x002B
REG_CONTROLLER_VERSION = 0x002C
REG_DISPLAY_VERSION = 0x002D
REG_DC_PUMP_SPEED = 0x002E
REG_SUCT_PRESS = 0x002F
REG_DISCH_PRESS = 0x0030
REG_DC_FAN_TARGET = 0x0031

# Register addresses - Control (Read/Write)
REG_PARAMETER_MARKER = 0x0032
REG_CONTROL_MARK_1 = 0x0033
REG_CONTROL_MARK_2 = 0x0034
# Note: 0x0035 doesn't exist on this device
REG_UNIT_MODE = 0x0036

# Register addresses - Basic Configuration (Read/Write)
REG_TEMP_DIFF_COOLING_HEATING = 0x00C6
# Note: 0x00C7, 0x00C8, 0x00C9 don't exist on this device
REG_HOTWATER_SETPOINT = 0x00CA
REG_COOLING_SETPOINT = 0x00CB
REG_HEATING_SETPOINT = 0x00CC

# Register addresses - Economic Mode Heating (Read/Write)
REG_ECO_HEAT_AMBI_1 = 0x0169
REG_ECO_HEAT_AMBI_2 = 0x016A
REG_ECO_HEAT_AMBI_3 = 0x016B
REG_ECO_HEAT_AMBI_4 = 0x016C

# Register addresses - Economic Mode Hot Water (Read/Write)
REG_ECO_WATER_AMBI_1 = 0x016D
REG_ECO_WATER_AMBI_2 = 0x016E
REG_ECO_WATER_AMBI_3 = 0x016F
REG_ECO_WATER_AMBI_4 = 0x0170

# Register addresses - Economic Mode Cooling (Read/Write)
REG_ECO_COOL_AMBI_1 = 0x0171
REG_ECO_COOL_AMBI_2 = 0x0172
REG_ECO_COOL_AMBI_3 = 0x0173
REG_ECO_COOL_AMBI_4 = 0x0174

# Register addresses - Economic Mode Temperature Setpoints (Read/Write)
REG_ECO_HEAT_TEMP_1 = 0x0175
REG_ECO_HEAT_TEMP_2 = 0x0176
REG_ECO_HEAT_TEMP_3 = 0x0177
REG_ECO_HEAT_TEMP_4 = 0x0178
REG_ECO_WATER_TEMP_1 = 0x0179
REG_ECO_WATER_TEMP_2 = 0x017A
REG_ECO_WATER_TEMP_3 = 0x017B
REG_ECO_WATER_TEMP_4 = 0x017C
REG_ECO_COOL_TEMP_1 = 0x017D
REG_ECO_COOL_TEMP_2 = 0x017E
REG_ECO_COOL_TEMP_3 = 0x017F
REG_ECO_COOL_TEMP_4 = 0x0180

# Register addresses - General Configuration (Read/Write)
REG_HOTWATER_HEATER_DELAY = 0x0181
REG_HEATING_HEATER_DELAY = 0x0182
REG_HOTWATER_HEATER_AMBIENT = 0x0183
REG_HEATING_HEATER_AMBIENT = 0x0184
REG_PUMP_STARTUP_INTERVAL = 0x0185
REG_DC_PUMP_TEMP_DIFF = 0x018D
# Note: 0x018E, 0x018F don't exist on this device
REG_FAN_MODE = 0x0190
REG_MODE_CONTROL = 0x0191
REG_AMBIENT_SWITCH_SETPOINT = 0x0192
REG_AMBIENT_SWITCH_DIFF = 0x0193
# Note: 0x0194-0x0199 don't exist on this device
REG_ANTILEGIONELLA_TEMP = 0x019A
REG_ANTILEGIONELLA_WEEKDAY = 0x019B
REG_ANTILEGIONELLA_START_HOUR = 0x019C
REG_ANTILEGIONELLA_END_HOUR = 0x019D
REG_PUMP_WORK_MODE = 0x019E

# Unit mode options
UNIT_MODE_DHW = 0
UNIT_MODE_HEATING = 1
UNIT_MODE_COOLING = 2
UNIT_MODE_HEATING_DHW = 3
UNIT_MODE_COOLING_DHW = 4

UNIT_MODE_OPTIONS = {
    UNIT_MODE_DHW: "DHW Only",
    UNIT_MODE_HEATING: "Heating Only",
    UNIT_MODE_COOLING: "Cooling Only",
    UNIT_MODE_HEATING_DHW: "Heating + DHW",
    UNIT_MODE_COOLING_DHW: "Cooling + DHW",
}

# Fan mode options
FAN_MODE_NORMAL = 0
FAN_MODE_ECO = 1
FAN_MODE_NIGHT = 2
FAN_MODE_TEST = 3

FAN_MODE_OPTIONS = {
    FAN_MODE_NORMAL: "Normal",
    FAN_MODE_ECO: "Economy",
    FAN_MODE_NIGHT: "Night",
    FAN_MODE_TEST: "Test",
}

# Pump work mode options
PUMP_MODE_INTERVAL = 0
PUMP_MODE_NORMAL = 1
PUMP_MODE_DEMAND = 2

PUMP_MODE_OPTIONS = {
    PUMP_MODE_INTERVAL: "Interval",
    PUMP_MODE_NORMAL: "Normal",
    PUMP_MODE_DEMAND: "On Demand",
}

# Mode control options
MODE_CONTROL_NO_LINKAGE = 0
MODE_CONTROL_YES_AMBIENT = 1

MODE_CONTROL_OPTIONS = {
    MODE_CONTROL_NO_LINKAGE: "No Linkage",
    MODE_CONTROL_YES_AMBIENT: "Yes - Ambient",
}

# Bit field mappings for status registers

SWITCHING_INPUT_BITS = {
    0: "end_linkage_switch",
    1: "emergency_switch",
    2: "heating_control_switch",
    3: "cooling_control_switch",
    4: "water_flow_switch",
    5: "high_voltage_switch",
    6: "phase_sequence_switch",
    7: "grid_sg_signal",
    8: "grid_euv_signal",
}

WORKING_STATUS_BITS = {
    0: "hotwater_demand",
    1: "heating_demand",
    2: "with_heating",
    3: "with_cooling",
    4: "antilegionella_on",
    5: "cooling_demand",
    6: "alarm_stop",
    7: "defrost",
}

OUTPUT_SYMBOL_1_BITS = {
    0: "compressor",
    5: "fan",
    6: "four_way_valve",
    7: "high_low_wind",
}

OUTPUT_SYMBOL_2_BITS = {
    0: "chassis_electric_heating",
    5: "heating_heater",
    6: "three_way_valve",
    7: "hotwater_heater",
}

OUTPUT_SYMBOL_3_BITS = {
    0: "end_pump",
    1: "crank_heater",
    5: "enhanced_enthalpy_valve",
    6: "water_pump",
}

FAILURE_SYMBOL_1_BITS = {
    0: "tank_temp_sensor",
    1: "ambient_temp_sensor",
    2: "coil_temp_sensor",
    4: "outlet_temp_sensor",
    5: "high_voltage_fault",
    7: "power_phase_failure",
}

FAILURE_SYMBOL_2_BITS = {
    0: "water_flow_switch",
    2: "high_heating_outlet",
}

FAILURE_SYMBOL_3_BITS = {
    6: "outlet_gas_temp",
}

FAILURE_SYMBOL_4_BITS = {
    0: "inlet_temp_sensor",
    1: "high_exhaust_temp",
    2: "eco_inlet_temp_sensor",
    3: "eco_outlet_temp_sensor",
    5: "overcooling_outlet",
    6: "return_air_temp_sensor",
}

FAILURE_SYMBOL_5_BITS = {
    0: "underpressure_low",
    1: "overpressure_high",
    2: "high_coil_temp",
    6: "high_pressure_sensor",
    7: "low_pressure_sensor",
}

FAILURE_SYMBOL_6_BITS = {
    4: "secondary_antifreeze",
    5: "primary_antifreeze",
}

FAILURE_SYMBOL_7_BITS = {
    1: "low_ambient_temp",
    4: "inverter_comm_failure",
    5: "dc_fan_2_fault",
    6: "dc_fan_1_fault",
}

# Temperature scaling factors
TEMP_SCALE_01 = 0.1  # Most temperature sensors
TEMP_SCALE_05 = 0.5  # Some sensors and setpoints
TEMP_SCALE_10 = 1.0  # Exhaust temperature

# Pressure scaling factor
PRESSURE_SCALE = 0.01

# Parameter validation ranges
TEMP_DIFF_MIN = 2.0
TEMP_DIFF_MAX = 18.0

HEATING_SETPOINT_MIN = 10.0
HEATING_SETPOINT_MAX = 55.0

COOLING_SETPOINT_MIN = 12.0
COOLING_SETPOINT_MAX = 30.0

HOTWATER_SETPOINT_MIN = 10.0
HOTWATER_SETPOINT_MAX = 60.0

ECO_AMBIENT_MIN = -30.0
ECO_AMBIENT_MAX = 50.0

ECO_HEATING_TEMP_MIN = 10.0
ECO_HEATING_TEMP_MAX = 55.0

ECO_COOLING_TEMP_MIN = 12.0
ECO_COOLING_TEMP_MAX = 30.0

ECO_HOTWATER_TEMP_MIN = 10.0
ECO_HOTWATER_TEMP_MAX = 55.0

HEATER_DELAY_MIN = 1
HEATER_DELAY_MAX = 60

HEATER_AMBIENT_MIN = -30
HEATER_AMBIENT_MAX = 30

PUMP_INTERVAL_MIN = 1
PUMP_INTERVAL_MAX = 120

DC_PUMP_DIFF_MIN = 5
DC_PUMP_DIFF_MAX = 30

AMBIENT_SWITCH_SETPOINT_MIN = -20
AMBIENT_SWITCH_SETPOINT_MAX = 30

AMBIENT_SWITCH_DIFF_MIN = 1
AMBIENT_SWITCH_DIFF_MAX = 10

ANTILEGIONELLA_TEMP_MIN = 30
ANTILEGIONELLA_TEMP_MAX = 70
