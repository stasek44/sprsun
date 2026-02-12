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
        set_fn_register=0x001C,
        value_map={
            "dhw": 0,
            "heating": 1,
            "cooling": 2,
            "heating_dhw": 3,
            "cooling_dhw": 4,
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
