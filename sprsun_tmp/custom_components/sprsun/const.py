"""Constants for the SPRSUN Heat Pump integration."""
from enum import IntEnum

DOMAIN = "sprsun"
MANUFACTURER = "SPRSUN"
DEFAULT_NAME = "SPRSUN Heat Pump"
DEFAULT_PORT = 502
DEFAULT_SLAVE = 1
DEFAULT_SCAN_INTERVAL = 30

CONF_SLAVE_ID = "slave_id"

# Unit modes (P06 Unit mode - Register 0x0036 = 54)
class UnitMode(IntEnum):
    """Unit operating modes."""
    DHW = 0  # Hot water only (CWU)
    HEATING = 1  # Heating only (Ogrzewanie)
    COOLING = 2  # Cooling only (Chłodzenie)
    HEATING_DHW = 3  # Heating + Hot water (Ogrzewanie i CWU)
    COOLING_DHW = 4  # Cooling + Hot water (Chłodzenie i CWU)

UNIT_MODE_NAMES = {
    UnitMode.DHW: "DHW",
    UnitMode.HEATING: "Heating",
    UnitMode.COOLING: "Cooling",
    UnitMode.HEATING_DHW: "Heating + DHW",
    UnitMode.COOLING_DHW: "Cooling + DHW",
}

# Fan/Compressor modes (P07 FAN mode - Register 0x0190 = 400)
class FanMode(IntEnum):
    """Fan/Compressor operating modes."""
    NORMAL = 0
    ECO = 1
    NIGHT = 2
    TEST = 3

FAN_MODE_NAMES = {
    FanMode.NORMAL: "Normal",
    FanMode.ECO: "ECO",
    FanMode.NIGHT: "Night",
    FanMode.TEST: "Test",
}

# Pump work modes (G02 Pump work - Register 0x019E = 414)
class PumpMode(IntEnum):
    """Pump operating modes."""
    INTERVAL = 0
    NORMAL = 1
    DEMAND = 2

PUMP_MODE_NAMES = {
    PumpMode.INTERVAL: "Interval",
    PumpMode.NORMAL: "Normal",
    PumpMode.DEMAND: "Demand",
}

# Register addresses (in decimal for consistency)
REG_UNIT_MODE = 54  # 0x0036
REG_FAN_MODE = 400  # 0x0190
REG_PUMP_MODE = 414  # 0x019E

REG_WORKING_STATUS = 3  # 0x0003
REG_OUTPUT_SYMBOL_1 = 4  # 0x0004
REG_OUTPUT_SYMBOL_2 = 5  # 0x0005
REG_OUTPUT_SYMBOL_3 = 6  # 0x0006

REG_INLET_TEMP = 14  # 0x000E
REG_HOTWATER_TEMP = 15  # 0x000F
REG_AMBIENT_TEMP = 17  # 0x0011
REG_OUTLET_TEMP = 18  # 0x0012
REG_COMP_FREQ = 30  # 0x001E
REG_COMP_CURRENT = 35  # 0x0023
REG_TARGET_FREQ = 36  # 0x0024
REG_DC_PUMP_SPEED = 46  # 0x002E

REG_HEATING_SETPOINT = 204  # 0x00CC
REG_COOLING_SETPOINT = 203  # 0x00CB
REG_HOTWATER_SETPOINT = 202  # 0x00CA

REG_DEFROST_PERIOD_1 = 56  # 0x0038
REG_DEFROST_PERIOD_2 = 57  # 0x0039
REG_DEFROST_PERIOD_3 = 58  # 0x003A
REG_PUMP_CYCLE = 389  # 0x0185
REG_PUMP_MIN_FREQ = 394  # 0x018A
REG_WATER_FREQ_R00 = 252  # 0x00FC
REG_WATER_FREQ_R01 = 253  # 0x00FD
REG_HEAT_FREQ_R04 = 260  # 0x0104
REG_HEAT_FREQ_R05 = 261  # 0x0105

# Bit masks for status registers
BIT_HOTWATER_DEMAND = 0x01
BIT_HEATING_DEMAND = 0x02
BIT_WITH_HEATING = 0x04
BIT_WITH_COOLING = 0x08
BIT_ANTILEGIONELLA = 0x10
BIT_COOLING_DEMAND = 0x20
BIT_ALARM = 0x40
BIT_DEFROST = 0x80

BIT_COMPRESSOR = 0x01
BIT_FAN = 0x20
BIT_FOUR_WAY_VALVE = 0x40

BIT_THREE_WAY_VALVE = 0x40
BIT_HEATING_HEATER = 0x20
BIT_HOTWATER_HEATER = 0x80

BIT_PUMP = 0x40
BIT_AC_PUMP = 0x01
