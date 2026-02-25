"""Core system-oriented CLI handlers extracted from cli.main."""

import os
from typing import Any, Callable


def handle_info(
    json_output: bool,
    output_json: Callable,
    print_fn: Callable[[str], None],
    version: str,
    codename: str,
    system_manager_cls,
    tweak_ops_cls,
) -> int:
    """Show system information."""
    is_atomic = system_manager_cls.is_atomic()
    pm = system_manager_cls.get_package_manager()
    profile = tweak_ops_cls.get_power_profile()

    if json_output:
        data = {
            "version": version,
            "codename": codename,
            "system_type": "Atomic" if is_atomic else "Traditional",
            "package_manager": pm,
            "power_profile": profile,
        }
        if is_atomic and system_manager_cls.has_pending_deployment():
            data["pending_deployment"] = True
        output_json(data)
    else:
        print_fn("═══════════════════════════════════════════")
        print_fn(f"   Loofi Fedora Tweaks v{version} CLI")
        print_fn("═══════════════════════════════════════════")
        print_fn(f"🖥️  System: {'Atomic' if is_atomic else 'Traditional'} Fedora")
        print_fn(f"📦 Package Manager: {pm}")
        print_fn(f"⚡ Power Profile: {profile}")

        if is_atomic and system_manager_cls.has_pending_deployment():
            print_fn("🔄 Pending deployment: ⚠️  Reboot required")

    return 0


def handle_health(
    json_output: bool,
    output_json: Callable,
    print_fn: Callable[[str], None],
    system_monitor_cls,
    disk_manager_cls,
    tweak_ops_cls,
    system_manager_cls,
) -> int:
    """Show system health overview."""
    health = system_monitor_cls.get_system_health()

    if json_output:
        data = {
            "hostname": health.hostname,
            "uptime": health.uptime,
        }
        if health.memory:
            data["memory"] = {
                "used": health.memory.used_human,
                "total": health.memory.total_human,
                "percent": health.memory.percent_used,
                "status": health.memory_status,
            }
        if health.cpu:
            data["cpu"] = {
                "load_1min": health.cpu.load_1min,
                "load_5min": health.cpu.load_5min,
                "load_15min": health.cpu.load_15min,
                "cores": health.cpu.core_count,
                "load_percent": health.cpu.load_percent,
                "status": health.cpu_status,
            }
        disk_level, disk_msg = disk_manager_cls.check_disk_health("/")
        data["disk"] = {"status": disk_level, "message": disk_msg}
        data["power_profile"] = tweak_ops_cls.get_power_profile()
        output_json(data)
    else:
        print_fn("═══════════════════════════════════════════")
        print_fn("   System Health Check")
        print_fn("═══════════════════════════════════════════")
        print_fn(f"🖥️  Hostname: {health.hostname}")
        print_fn(f"⏱️  Uptime: {health.uptime}")

        if health.memory:
            mem_icon = "🟢" if health.memory_status == "ok" else ("🟡" if health.memory_status == "warning" else "🔴")
            print_fn(f"{mem_icon} Memory: {health.memory.used_human} / {health.memory.total_human} ({health.memory.percent_used}%)")
        else:
            print_fn("⚪ Memory: Unable to read")

        if health.cpu:
            cpu_icon = "🟢" if health.cpu_status == "ok" else ("🟡" if health.cpu_status == "warning" else "🔴")
            print_fn(
                f"{cpu_icon} CPU Load: {health.cpu.load_1min} / {health.cpu.load_5min} / {health.cpu.load_15min} ({health.cpu.core_count} cores, {health.cpu.load_percent}%)"
            )
        else:
            print_fn("⚪ CPU: Unable to read")

        disk_level, disk_msg = disk_manager_cls.check_disk_health("/")
        disk_icon = "🟢" if disk_level == "ok" else ("🟡" if disk_level == "warning" else "🔴")
        print_fn(f"{disk_icon} {disk_msg}")
        print_fn(f"⚡ Power Profile: {tweak_ops_cls.get_power_profile()}")
        print_fn(f"💻 System: {'Atomic' if system_manager_cls.is_atomic() else 'Traditional'} Fedora ({system_manager_cls.get_variant_name()})")

    return 0


def handle_disk(args, json_output: bool, output_json: Callable, print_fn: Callable[[str], None], disk_manager_cls) -> int:
    """Show disk usage information."""
    usage = disk_manager_cls.get_disk_usage("/")

    if json_output:
        data: dict[str, Any] = {"root": None, "home": None}
        if usage:
            level, _ = disk_manager_cls.check_disk_health("/")
            data["root"] = {
                "total": usage.total_human,
                "used": usage.used_human,
                "free": usage.free_human,
                "percent": usage.percent_used,
                "status": level,
            }
        home_usage = disk_manager_cls.get_disk_usage(os.path.expanduser("~"))
        if home_usage and home_usage.mount_point != "/":
            level, _ = disk_manager_cls.check_disk_health(home_usage.mount_point)
            data["home"] = {
                "mount_point": home_usage.mount_point,
                "total": home_usage.total_human,
                "used": home_usage.used_human,
                "free": home_usage.free_human,
                "percent": home_usage.percent_used,
                "status": level,
            }
        output_json(data)
    else:
        print_fn("═══════════════════════════════════════════")
        print_fn("   Disk Usage")
        print_fn("═══════════════════════════════════════════")

        if usage:
            level, _ = disk_manager_cls.check_disk_health("/")
            icon = "🟢" if level == "ok" else ("🟡" if level == "warning" else "🔴")
            print_fn(f"\n{icon} Root (/)")
            print_fn(f"   Total: {usage.total_human}")
            print_fn(f"   Used:  {usage.used_human} ({usage.percent_used}%)")
            print_fn(f"   Free:  {usage.free_human}")
        else:
            print_fn("❌ Unable to read root filesystem")

        home_usage = disk_manager_cls.get_disk_usage(os.path.expanduser("~"))
        if home_usage and home_usage.mount_point != "/":
            level, _ = disk_manager_cls.check_disk_health(home_usage.mount_point)
            icon = "🟢" if level == "ok" else ("🟡" if level == "warning" else "🔴")
            print_fn(f"\n{icon} Home ({home_usage.mount_point})")
            print_fn(f"   Total: {home_usage.total_human}")
            print_fn(f"   Used:  {home_usage.used_human} ({home_usage.percent_used}%)")
            print_fn(f"   Free:  {home_usage.free_human}")

        if getattr(args, "details", False):
            home_dir = os.path.expanduser("~")
            print_fn(f"\n📂 Largest directories in {home_dir}:")
            large_dirs = disk_manager_cls.find_large_directories(home_dir, max_depth=2, top_n=5)
            if large_dirs:
                for directory in large_dirs:
                    print_fn(f"   {directory.size_human:>10}  {directory.path}")
            else:
                print_fn("   (no results)")

    return 0


def handle_processes(args, json_output: bool, output_json: Callable, print_fn: Callable[[str], None], process_manager_cls) -> int:
    """Show top processes."""
    counts = process_manager_cls.get_process_count()
    n = getattr(args, "count", 10)
    sort_by = getattr(args, "sort", "cpu")

    if sort_by == "memory":
        processes = process_manager_cls.get_top_by_memory(n)
    else:
        processes = process_manager_cls.get_top_by_cpu(n)

    if json_output:
        data = {
            "counts": counts,
            "sort_by": sort_by,
            "processes": [
                {
                    "pid": p.pid,
                    "name": p.name,
                    "cpu_percent": p.cpu_percent,
                    "memory_percent": p.memory_percent,
                    "memory_bytes": p.memory_bytes,
                    "user": p.user,
                }
                for p in processes
            ],
        }
        output_json(data)
    else:
        print_fn("═══════════════════════════════════════════")
        print_fn("   Process Monitor")
        print_fn("═══════════════════════════════════════════")
        print_fn(f"\n📊 Total: {counts['total']} | Running: {counts['running']} | Sleeping: {counts['sleeping']} | Zombie: {counts['zombie']}")
        print_fn(f"\n🔍 Top {n} by {'Memory' if sort_by == 'memory' else 'CPU'}:")
        print_fn(f"{'PID':>7}  {'CPU%':>6}  {'MEM%':>6}  {'Memory':>10}  {'User':<12}  {'Name'}")
        print_fn("─" * 70)
        for process in processes:
            mem_human = process_manager_cls.bytes_to_human(process.memory_bytes)
            print_fn(f"{process.pid:>7}  {process.cpu_percent:>5.1f}%  {process.memory_percent:>5.1f}%  {mem_human:>10}  {process.user:<12}  {process.name}")

    return 0


def handle_temperature(json_output: bool, output_json: Callable, print_fn: Callable[[str], None], temperature_manager_cls) -> int:
    """Show temperature readings."""
    sensors = temperature_manager_cls.get_all_sensors()

    if json_output:
        data = {
            "sensors": [
                {
                    "label": s.label,
                    "current": s.current,
                    "high": s.high,
                    "critical": s.critical,
                }
                for s in sensors
            ]
        }
        if sensors:
            data["avg"] = sum(s.current for s in sensors) / len(sensors)
            data["max"] = max(s.current for s in sensors)
        output_json(data)
    else:
        print_fn("═══════════════════════════════════════════")
        print_fn("   Temperature Monitor")
        print_fn("═══════════════════════════════════════════")

        if not sensors:
            print_fn("\n⚠️  No temperature sensors found.")
            from utils.install_hints import build_install_hint

            print_fn(f"   Ensure lm_sensors is installed: {build_install_hint('lm_sensors')}")
            return 1

        for sensor in sensors:
            if sensor.critical and sensor.current >= sensor.critical:
                icon = "🔴"
            elif sensor.high and sensor.current >= sensor.high:
                icon = "🟡"
            else:
                icon = "🟢"

            line = f"{icon} {sensor.label:<20} {sensor.current:>5.1f}°C"
            if sensor.high:
                line += f"  (high: {sensor.high:.0f}°C)"
            if sensor.critical:
                line += f"  (crit: {sensor.critical:.0f}°C)"
            print_fn(line)

        if len(sensors) > 1:
            avg_temp = sum(s.current for s in sensors) / len(sensors)
            hottest = max(sensors, key=lambda s: s.current)
            print_fn(f"\n📊 Summary: avg {avg_temp:.1f}°C | max {hottest.current:.1f}°C ({hottest.label})")

    return 0


def handle_netmon(args, json_output: bool, output_json: Callable, print_fn: Callable[[str], None], network_monitor_cls) -> int:
    """Show network interface stats."""
    interfaces = network_monitor_cls.get_all_interfaces()

    if json_output:
        data = {
            "interfaces": [
                {
                    "name": i.name,
                    "type": i.type,
                    "is_up": i.is_up,
                    "ip_address": i.ip_address if hasattr(i, "ip_address") else None,
                    "bytes_recv": i.bytes_recv,
                    "bytes_sent": i.bytes_sent,
                }
                for i in interfaces
            ],
            "summary": network_monitor_cls.get_bandwidth_summary(),
        }
        output_json(data)
    else:
        print_fn("═══════════════════════════════════════════")
        print_fn("   Network Monitor")
        print_fn("═══════════════════════════════════════════")

        if not interfaces:
            print_fn("\n⚠️  No network interfaces found.")
            return 1

        for iface in interfaces:
            status = "UP" if iface.is_up else "DOWN"
            icon = "🟢" if iface.is_up else "🔴"
            print_fn(f"\n{icon} {iface.name} ({iface.type}) [{status}]")
            if iface.ip_address:
                print_fn(f"   IP: {iface.ip_address}")
            print_fn(f"   RX: {network_monitor_cls.bytes_to_human(iface.bytes_recv)}  TX: {network_monitor_cls.bytes_to_human(iface.bytes_sent)}")
            if iface.recv_rate > 0 or iface.send_rate > 0:
                print_fn(f"   Rate: ↓{network_monitor_cls.bytes_to_human(int(iface.recv_rate))}/s  ↑{network_monitor_cls.bytes_to_human(int(iface.send_rate))}/s")

        summary = network_monitor_cls.get_bandwidth_summary()
        print_fn(f"\n📊 Total: ↓{network_monitor_cls.bytes_to_human(summary['total_recv'])} ↑{network_monitor_cls.bytes_to_human(summary['total_sent'])}")

        if getattr(args, "connections", False):
            connections = network_monitor_cls.get_active_connections()
            if connections:
                print_fn(f"\n🔗 Active Connections ({len(connections)}):")
                print_fn(f"{'Proto':<6} {'Local':>21} {'Remote':>21} {'State':<14} {'Process'}")
                print_fn("─" * 80)
                for conn in connections[:20]:
                    local = f"{conn.local_addr}:{conn.local_port}"
                    remote = f"{conn.remote_addr}:{conn.remote_port}" if conn.remote_addr != "0.0.0.0" else "*"
                    print_fn(f"{conn.protocol:<6} {local:>21} {remote:>21} {conn.state:<14} {conn.process_name}")

    return 0
