"""Shared Cerebro API client."""

from cerebro_client.client import CerebroClient, CerebroConfig
from cerebro_client.channels import (
    STATUS_MAP,
    channel_address,
    channel_groups,
    channel_in_networks,
    items_from_payload,
    normalize_networks,
    total_from_payload,
    camera_status,
)

__all__ = [
    "CerebroClient",
    "CerebroConfig",
    "STATUS_MAP",
    "channel_address",
    "channel_groups",
    "channel_in_networks",
    "items_from_payload",
    "normalize_networks",
    "total_from_payload",
    "camera_status",
]

__version__ = "0.1.0"
