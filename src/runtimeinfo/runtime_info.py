import os
import socket
import uuid
from typing import Optional, Any
import json
import jcs
import hashlib
import base64
import ipaddress
import getpass


class RuntimeInfo:
    """Information about a machine and path."""

    def __init__(self, path: Optional[str] = None) -> None:
        self.hostname: Optional[str] = None
        self.mac_address: Optional[str] = None
        self.ip_address: Optional[str] = None
        self.path: Optional[str] = None
        self.username: Optional[str] = None

        try:
            self.hostname = socket.gethostname()
        except Exception:
            self.hostname = None

        try:
            self.username = getpass.getuser()
        except Exception:
            self.username = None

        try:
            node = uuid.getnode()
            self.mac_address = ":".join(
                f"{(node >> i) & 0xFF:02x}" for i in range(40, -1, -8)
            )
        except Exception:
            self.mac_address = None

        try:
            self.ip_address = None
            if self.hostname:
                for info in socket.getaddrinfo(self.hostname, None):
                    addr = info[4][0]
                    try:
                        if not ipaddress.ip_address(addr).is_loopback:
                            self.ip_address = addr
                            break
                    except Exception:
                        pass
        except Exception:
            self.ip_address = None

        if path is not None:
            try:
                self.path = os.fspath(path)
            except Exception:
                self.path = None
        else:
            try:
                self.path = os.path.abspath(os.getcwd())
            except Exception:
                self.path = None

    @staticmethod
    def canonical_hash(data: Any) -> str:
        """Return first 10 chars of base64url SHA1 of canonical JSON of ``data``."""
        json_bytes = jcs.canonicalize(data)
        digest = hashlib.sha1(json_bytes).digest()
        b64 = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
        return b64[:10]

    def to_json(self) -> str:
        """Return canonical JSON string of this instance."""
        data = {
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "username": self.username,
            "path": self.path,
        }
        return jcs.canonicalize(data).decode("utf-8")

    def __str__(self) -> str:
        """Return human readable JSON representation of this instance."""
        data = {
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "username": self.username,
            "path": self.path,
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
