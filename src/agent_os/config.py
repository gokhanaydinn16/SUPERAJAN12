"""Configuration helpers for the autonomous crypto agent system."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass(slots=True)
class VenueConfig:
    alias: str
    heartbeat_seconds: int = 3
    stale_after_seconds: int = 8


@dataclass(slots=True)
class RiskConfig:
    max_position_size: float = 3.0
    max_order_notional: float = 150000.0
    max_leverage: float = 5.0
    duplicate_window_seconds: int = 30


@dataclass(slots=True)
class StorageConfig:
    path: Path = Path("agent_os_data/agent_os.sqlite3")
    recent_event_limit: int = 250


@dataclass(slots=True)
class AppConfig:
    host: str = "127.0.0.1"
    port: int = 8080
    system_name: str = "otonom-kripto-ajan-os"
    symbol: str = "BTC-PERP"
    shadow_mode: bool = True
    preferred_venue: str = "Binance USDT Futures"
    venues: List[VenueConfig] = field(
        default_factory=lambda: [VenueConfig(alias="binance-futures"), VenueConfig(alias="deribit")]
    )
    risk: RiskConfig = field(default_factory=RiskConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)


def load_config() -> AppConfig:
    config = AppConfig()
    config.host = os.getenv("AGENT_OS_HOST", config.host)
    config.port = int(os.getenv("AGENT_OS_PORT", str(config.port)))
    config.symbol = os.getenv("AGENT_OS_SYMBOL", config.symbol)
    config.shadow_mode = os.getenv("AGENT_OS_SHADOW_MODE", "true").lower() != "false"
    config.preferred_venue = os.getenv("AGENT_OS_PREFERRED_VENUE", config.preferred_venue)
    storage_path = os.getenv("AGENT_OS_DB_PATH")
    if storage_path:
        config.storage.path = Path(storage_path)
    return config
