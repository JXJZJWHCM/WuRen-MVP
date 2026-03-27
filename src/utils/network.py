import socket
import struct
import subprocess
import logging
import os
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def get_ip_address(ifname):
    """
    Get IP address for a network interface.
    Supports Linux (fcntl) and generic fallback.
    Returns None if interface cannot be found or OS is not supported.
    """
    try:
        import fcntl
        # Method 1: Socket + fcntl (Standard Linux way)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15].encode('utf-8'))
        )[20:24])
    except Exception as e:
        logger.debug(f"Socket method failed for {ifname}: {e}")
        
    try:
        # Method 2: 'ip' command (Robust fallback for Linux)
        result = subprocess.check_output(f"ip -4 addr show {ifname}", shell=True).decode()
        import re
        ip = re.search(r'inet\s(\d+(\.\d+){3})', result)
        if ip:
            return ip.group(1)
    except Exception as e:
        logger.debug(f"Failed to get IP for {ifname}: {e}")
        
    return None

def list_network_interfaces() -> List[Dict[str, Optional[str]]]:
    interfaces: List[Dict[str, Optional[str]]] = []
    names: List[str] = []
    try:
        names = [n for n in os.listdir("/sys/class/net") if n]
    except Exception:
        names = []

    if not names:
        try:
            names = [name for _, name in socket.if_nameindex()]
        except Exception:
            names = []

    for name in sorted(set(names)):
        operstate = None
        try:
            operstate_path = f"/sys/class/net/{name}/operstate"
            if os.path.exists(operstate_path):
                with open(operstate_path, "r", encoding="utf-8") as f:
                    operstate = f.read().strip()
        except Exception:
            operstate = None

        ipv4 = None
        try:
            ipv4 = get_ip_address(name)
        except Exception:
            ipv4 = None

        interfaces.append({
            "name": name,
            "ipv4": ipv4,
            "up": operstate == "up" if operstate is not None else None,
            "loopback": name == "lo",
        })

    interfaces.sort(key=lambda x: (
        1 if x.get("loopback") else 0,
        0 if x.get("up") else 1,
        x.get("name") or "",
    ))

    return interfaces

def get_default_interface_name() -> Optional[str]:
    try:
        result = subprocess.check_output("ip route show default", shell=True, text=True, stderr=subprocess.DEVNULL)
        import re
        m = re.search(r"\bdev\s+(\S+)", result)
        if m:
            return m.group(1)
    except Exception:
        pass

    interfaces = list_network_interfaces()
    preferred = next((i for i in interfaces if not i.get("loopback") and i.get("up") and i.get("ipv4")), None)
    if preferred:
        return preferred.get("name")
    fallback = next((i for i in interfaces if not i.get("loopback")), None)
    return fallback.get("name") if fallback else None

def get_primary_ipv4() -> Optional[str]:
    ifname = get_default_interface_name()
    if ifname:
        ip = get_ip_address(ifname)
        if ip:
            return ip

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("1.1.1.1", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None
