"""configuration utilities"""

import os
from pathlib import Path
from dataclasses import dataclass
import yaml
from server.core.mode import Mode


@dataclass
class TopicConfig:
    """Topic configuration DTO"""

    name: str
    mode: Mode


@dataclass
class Server:
    """Server information"""

    host: str
    ip: str
    port: int


@dataclass
class ServerConfig:
    """Server Configuration DTO"""

    socket: Server
    web: Server
    topics: list[TopicConfig]
    queue_ack_mode_default: str
    queue_ack_timeout_ms: int
    queue_auto_ack_delay_ms: int


def read_config():
    """read utility function"""
    sms_config_path = os.path.join(
        Path(__file__).resolve().parents[2], "sms_config.yaml"
    )
    with open(sms_config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return ServerConfig(
        socket=Server(
            "Socket",
            str(config["socket_server"]["ip"]),
            int(config["socket_server"]["port"]),
        ),
        web=Server(
            "Web", str(config["web_server"]["ip"]), int(config["web_server"]["port"])
        ),
        topics=[
            TopicConfig(name=t["name"], mode=Mode.get_from_str(t["mode"]))
            for t in config["topics"]
        ],
        queue_ack_mode_default=str(config.get("queue_settings", {}).get("ack_mode_default", "manual")),
        queue_ack_timeout_ms=int(config.get("queue_settings", {}).get("ack_timeout_ms", 60000)),
        queue_auto_ack_delay_ms=int(config.get("queue_settings", {}).get("auto_ack_delay_ms", 30000)),
    )
