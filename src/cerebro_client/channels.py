"""Channel payload helpers shared by cms and equipment-bot."""
from __future__ import annotations

import ipaddress
from ipaddress import IPv4Network
from typing import Any, Iterable

STATUS_MAP = {
    "online": "online",
    "connected": "online",
    "ok": "online",
    "degraded": "maintenance",
    "offline": "offline",
    "disconnected": "offline",
}


def normalize_networks(values: Iterable[str]) -> list[IPv4Network]:
    networks: list[IPv4Network] = []
    for value in values:
        try:
            network = ipaddress.ip_network(str(value).strip(), strict=False)
        except ValueError as exc:
            raise ValueError(f"Некорректная сеть: {value}") from exc
        if not isinstance(network, ipaddress.IPv4Network):
            raise ValueError(f"Только IPv4: {value}")
        networks.append(network)
    if not networks:
        raise ValueError("Нужна хотя бы одна IPv4-сеть (CIDR)")
    return networks


def channel_in_networks(host: str | None, networks: Iterable[IPv4Network]) -> bool:
    if not host:
        return False
    try:
        address = ipaddress.ip_address(host.strip())
    except ValueError:
        return False
    return isinstance(address, ipaddress.IPv4Address) and any(
        address in network for network in networks
    )


def items_from_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("items", "results", "channels", "entity_groups", "data", "result"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            nested = items_from_payload(value)
            if nested:
                return nested
    return []


def total_from_payload(payload: Any) -> int | None:
    if not isinstance(payload, dict):
        return None
    for key in ("total", "total_count", "count"):
        if isinstance(payload.get(key), int):
            return payload[key]
    for key in ("data", "result"):
        if isinstance(payload.get(key), dict):
            value = total_from_payload(payload[key])
            if value is not None:
                return value
    return None


def camera_status(value: Any) -> str:
    if isinstance(value, dict):
        value = value.get("status")
    return STATUS_MAP.get(str(value or "").lower(), "unknown")


def channel_address(channel: dict[str, Any]) -> str | None:
    address = channel.get("address")
    if isinstance(address, str):
        return address.strip() or None
    if not isinstance(address, dict):
        return None
    parts = [
        address.get("country"),
        address.get("region"),
        address.get("city"),
        address.get("street"),
        address.get("place_info"),
    ]
    value = ", ".join(str(p).strip() for p in parts if p)
    return value or None


def channel_groups(channel: dict[str, Any]) -> list[dict[str, Any]]:
    groups = [
        g
        for g in (channel.get("entity_groups") or [])
        if isinstance(g, dict) and g.get("id") is not None
    ]
    return sorted(
        groups,
        key=lambda item: (int(item.get("group_level") or 999), str(item.get("name") or "")),
    )
