"""Select platform for SPRSUN Heat Pump."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SPRSUNDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class SPRSUNSelectEntityDescription(SelectEntityDescription):
    """Describes SPRSUN select entity."""

    value_fn: Callable[[dict], str | None]
    set_fn_register: int
    value_map: dict[str, int]


SELECTS: tuple[SPRSUNSelectEntityDescription, ...] = (
    SPRSUNSelectEntityDescription(
        key="unit_mode",
        translation_key="unit_mode",
        options=["dhw", "heating", "cooling", "heating_dhw", "cooling_dhw"],
        value_fn=lambda data: {
            0: "dhw",
            1: "heating",
            2: "cooling",
            3: "heating_dhw",
            4: "cooling_dhw",
        }.get(data.get("unit_mode")),
        set_fn_register=0x0036,  # FIX: Correct address from modbus_reference.md (P06 Unit Mode)
        value_map={
            "dhw": 0,
            "heating": 1,
            "cooling": 2,
            "heating_dhw": 3,
            "cooling_dhw": 4,
        },
    ),
    SPRSUNSelectEntityDescription(
        key="fan_mode",
        translation_key="fan_mode",
        options=["normal", "eco", "night", "test"],
        value_fn=lambda data: {
            0: "normal",
            1: "eco",
            2: "night",
            3: "test",
        }.get(data.get("fan_mode")),
        set_fn_register=0x0190,
        value_map={
            "normal": 0,
            "eco": 1,
            "night": 2,
            "test": 3,
        },
    ),
    SPRSUNSelectEntityDescription(
        key="enable_switch",
        translation_key="enable_switch",
        options=["no_linkage", "yes_amb"],
        value_fn=lambda data: {
            0: "no_linkage",
            1: "yes_amb",
        }.get(data.get("enable_switch")),
        set_fn_register=0x0191,
        value_map={
            "no_linkage": 0,
            "yes_amb": 1,
        },
    ),
    SPRSUNSelectEntityDescription(
        key="pump_work_mode",
        translation_key="pump_work_mode",
        options=["interval", "normal", "demand"],
        value_fn=lambda data: {
            0: "interval",
            1: "normal",
            2: "demand",
        }.get(data.get("pump_work_mode")),
        set_fn_register=0x019E,
        value_map={
            "interval": 0,
            "normal": 1,
            "demand": 2,
        },
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN select based on a config entry."""
    coordinator: SPRSUNDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        SPRSUNSelectEntity(coordinator, description) for description in SELECTS
    )


class SPRSUNSelectEntity(
    CoordinatorEntity[SPRSUNDataUpdateCoordinator], SelectEntity
):
    """Defines a SPRSUN select entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SPRSUNDataUpdateCoordinator,
        description: SPRSUNSelectEntityDescription,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self.entity_description: SPRSUNSelectEntityDescription = description

        # Set unique_id
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"

        # Set device info to link entity to device
        self._attr_device_info = coordinator.device_info

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        return self.entity_description.value_fn(self.coordinator.data)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Get the register value for this option
        value = self.entity_description.value_map.get(option)
        
        if value is None:
            return

        # Write to the register
        success = await self.coordinator.client.write_register(
            self.entity_description.set_fn_register,
            value,
        )

        if success:
            # Trigger an immediate data refresh after setting the value
            await self.coordinator.async_request_refresh()
