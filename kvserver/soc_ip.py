
import psutil
import socket

def get_wifi_ip():
    addrs = psutil.net_if_addrs()
    
    # Common Wi-Fi interface names on Windows, Linux, Mac
    wifi_keywords = ["wlan", "wi-fi", "wifi", "wl", "airport"]

    for iface, snic_list in addrs.items():
        if any(kw.lower() in iface.lower() for kw in wifi_keywords):
            for snic in snic_list:
                if snic.family.name == 'AF_INET' and not snic.address.startswith("127."):
                    return snic.address

    # Fallback: active interface (best guess)
    try:return get_active_ip()
    except:return f"[Errno 101]"


def get_active_ip():
    """Return IP of the interface currently being used to connect to the Internet."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip




wlan_ip = get_wifi_ip()

