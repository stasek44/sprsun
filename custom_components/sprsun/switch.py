"""Switch platform for SPRSUN Heat Pump."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SPRSUNDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class SPRSUNSwitchEntityDescription(SwitchEntityDescription):
    """Describes SPRSUN switch entity."""

    value_fn: Callable[[dict], bool | None]
    set_fn_coil: int


SWITCHES: tuple[SPRSUNSwitchEntityDescription, ...] = (
    SPRSUNSwitchEntityDescription(
        key="power",
        translation_key="power",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda data: data.get("power_on"),
        set_fn_coil=0x0000,  # Coil address for power control
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN switch based on a config entry."""
    coordinator: SPRSUNDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        SPRSUNSwitchEntity(coordinator, description) for description in SWITCHES
    )


class SPRSUNSwitchEntity(
    CoordinatorEntity[SPRSUNDataUpdateCoordinator], SwitchEntity
):
    """Defines a SPRSUN switch entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SPRSUNDataUpdateCoordinator,
        description: SPRSUNSwitchEntityDescription,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator)
        self.entity_description: SPRSUNSwitchEntityDescription = description

        # Set unique_id
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"

        # Set device info to link entity to device
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        return self.entity_description.value_fn(self.coordinator.data)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        success = await self.coordinator.client.write_coil(
            self.entity_description.set_fn_coil,
            True,
        )

        if success:
            # Trigger an immediate data refresh
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        success = await self.coordinator.client.write_coil(
            self.entity_description.set_fn_coil,
            False,
        )

        if success:
            # Trigger an immediate data refresh
            await self.coordinator.async_request_refresh()
