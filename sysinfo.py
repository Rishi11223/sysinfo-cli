#!/usr/bin/env python3

import platform
import socket
import os
import sys
import time
from datetime import timedelta

HEADER = '\033[95m'
BLUE = '\033[94m'
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
DIM = '\033[2m'
RESET = '\033[0m'


def get_size(bytes_):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_ < 1024:
            return f"{bytes_:.1f}{unit}"
        bytes_ /= 1024
    return f"{bytes_:.1f}PB"


def get_uptime():
    if sys.platform == "win32":
        import ctypes
        lib = ctypes.windll.kernel32
        uptime_ms = lib.GetTickCount64()
        return timedelta(milliseconds=uptime_ms)
    else:
        with open('/proc/uptime', 'r') as f:
            return timedelta(seconds=float(f.read().split()[0]))


def get_cpu_info():
    if sys.platform == "win32":
        import wmi
        c = wmi.WMI()
        cpu = c.Win32_Processor()[0]
        return f"{cpu.Name.strip()} ({cpu.NumberOfCores} cores)"
    else:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('model name'):
                    return line.split(':')[1].strip()
    return "Unknown"


def get_cpu_usage():
    if sys.platform == "win32":
        import wmi
        c = wmi.WMI()
        return c.Win32_Processor()[0].LoadPercentage
    else:
        with open('/proc/stat', 'r') as f:
            data = f.read().split()
        idle = int(data[4])
        total = sum(int(v) for v in data[1:9] if v.isdigit())
        return 100 * (1 - idle / total) if total else 0


def get_memory():
    if sys.platform == "win32":
        import wmi
        c = wmi.WMI()
        mem = c.Win32_ComputerSystem()[0]
        total = int(mem.TotalPhysicalMemory)
        free = int(mem.FreePhysicalMemory) * 1024
        return total, total - free
    else:
        with open('/proc/meminfo', 'r') as f:
            data = f.read()
        total = int([l for l in data.split('\n') if 'MemTotal' in l][0].split()[1]) * 1024
        avail = int([l for l in data.split('\n') if 'MemAvailable' in l][0].split()[1]) * 1024
        return total, total - avail


def get_disk():
    import shutil
    total, used, free = shutil.disk_usage('.')
    return total, used


def get_network():
    data = {}
    if sys.platform == "win32":
        import wmi
        c = wmi.WMI()
        for nic in c.Win32_NetworkAdapter(NetEnabled=True):
            if nic.Name and nic.MACAddress and nic.NetConnectionID:
                data[nic.NetConnectionID] = nic.MACAddress
    else:
        import netifaces
        for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_LINK in addrs:
                data[iface] = addrs[netifaces.AF_LINK][0]['addr']
    return data


def get_shell():
    return os.environ.get('SHELL', os.environ.get('ComSpec', 'cmd.exe'))


def get_packages():
    count = "N/A"
    if sys.platform != "win32":
        try:
            result = os.popen('dpkg --get-selections 2>/dev/null | wc -l').read()
            if result:
                count = result.strip()
        except:
            pass
    return count


def get_terminal():
    return os.environ.get('TERM', os.environ.get('WT_SESSION', 'N/A'))


def get_resolution():
    if sys.platform == "win32":
        try:
            import ctypes
            user32 = ctypes.windll.user32
            return f"{user32.GetSystemMetrics(0)}x{user32.GetSystemMetrics(1)}"
        except:
            pass
    return "N/A"


def get_de():
    if sys.platform != "win32":
        return os.environ.get('XDG_CURRENT_DESKTOP', os.environ.get('DESKTOP_SESSION', 'N/A'))
    return "N/A"


def collect_all():
    data = {}
    data["hostname"] = socket.gethostname()
    data["username"] = os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
    data["os"] = f"{platform.system()} {platform.release()}"
    data["kernel"] = platform.version()
    data["arch"] = platform.machine()
    data["uptime"] = str(get_uptime())
    data["shell"] = get_shell()
    data["terminal"] = get_terminal()
    data["de"] = get_de()
    data["packages"] = get_packages()
    data["resolution"] = get_resolution()
    data["cpu"] = get_cpu_info()
    data["cpu_usage"] = round(get_cpu_usage(), 1)

    try:
        import psutil
        mem_total, mem_used = get_memory()
        disk_total, disk_used = get_disk()
        data["memory"] = {"total": mem_total, "used": mem_used}
        data["disk"] = {"total": disk_total, "used": disk_used}
        data["processes"] = len(psutil.pids())
        data["users"] = len(psutil.users())
    except ImportError:
        data["memory"] = None
        data["disk"] = None

    data["network"] = get_network()
    return data


def output_json(data):
    import json
    print(json.dumps(data, indent=2))


def output_simple(data):
    print(f"{data['username']}@{data['hostname']}")
    print(f"{data['os']} | {data['arch']} | {data['cpu']}")
    print(f"RAM: {get_size(data['memory']['used'])}/{get_size(data['memory']['total'])}" if data['memory'] else "RAM: N/A")
    print(f"Disk: {get_size(data['disk']['used'])}/{get_size(data['disk']['total'])}" if data['disk'] else "Disk: N/A")
    print(f"Uptime: {data['uptime']}")


def main():
    parser = argparse.ArgumentParser(description="Cross-platform system information tool")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--simple", action="store_true", help="Minimal output (one line per section)")
    args = parser.parse_args()

    try:
        import psutil
        HAS_PSUTIL = True
    except ImportError:
        HAS_PSUTIL = False

    if args.json:
        data = collect_all()
        output_json(data)
        return

    if args.simple:
        data = collect_all()
        output_simple(data)
        return

    hostname = socket.gethostname()
    username = os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
    os_name = f"{platform.system()} {platform.release()}"
    kernel = platform.version()
    arch = platform.machine()
    uptime = get_uptime()

    ascii_art = f"""
{BOLD}{CYAN}         .-.
        (0 0)
    +---ooU----+       {RESET}{BOLD}{username}@{hostname}{RESET}
{BOLD}{CYAN}   |          |      {RESET}{DIM}----------------------{RESET}
{BOLD}{CYAN}   |  O    O  |      {RESET}{GREEN}OS:{RESET}      {os_name}
{BOLD}{CYAN}   |          |      {RESET}{GREEN}Kernel:{RESET}  {kernel}
{BOLD}{CYAN}   +----------+      {RESET}{GREEN}Arch:{RESET}    {arch}
{BOLD}{CYAN}    |________|       {RESET}{GREEN}Uptime:{RESET}  {uptime}
"""
    print(ascii_art)

    print(f" {GREEN}Shell:{RESET}     {get_shell()}")
    print(f" {GREEN}Terminal:{RESET}   {get_terminal()}")
    print(f" {GREEN}DE/WM:{RESET}     {get_de()}")
    print(f" {GREEN}Packages:{RESET}   {get_packages()}")
    print(f" {GREEN}Resolution:{RESET} {get_resolution()}")
    print(f" {GREEN}CPU:{RESET}       {get_cpu_info()}")
    print(f" {GREEN}CPU Usage:{RESET}  {get_cpu_usage():.1f}%")

    if HAS_PSUTIL:
        mem_total, mem_used = get_memory()
        disk_total, disk_used = get_disk()
        mem_pct = (mem_used / mem_total * 100)
        disk_pct = (disk_used / disk_total * 100)

        bar_len = 20
        mem_fill = int(mem_pct / 100 * bar_len)
        disk_fill = int(disk_pct / 100 * bar_len)

        print(f" {GREEN}RAM:{RESET}       {get_size(mem_used)} / {get_size(mem_total)}")
        print(f"           {'█' * mem_fill}{'░' * (bar_len - mem_fill)} {mem_pct:.1f}%")
        print(f" {GREEN}Disk:{RESET}      {get_size(disk_used)} / {get_size(disk_total)}")
        print(f"           {'█' * disk_fill}{'░' * (bar_len - disk_fill)} {disk_pct:.1f}%")

        print(f"\n {GREEN}Processes:{RESET}  {len(psutil.pids())}")
        print(f" {GREEN}Users:{RESET}     {len(psutil.users())}")
    else:
        print(f"\n {GREEN}RAM:{RESET}       Install 'psutil' for detailed stats")
        print(f" {GREEN}Disk:{RESET}      pip install psutil")

    print(f"\n {GREEN}Network:{RESET}")
    net = get_network()
    for iface, mac in list(net.items())[:5]:
        print(f"   {iface}: {DIM}{mac}{RESET}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(0)
    except Exception as e:
        print(f"{RED}Error:{RESET} {e}")
        sys.exit(1)
