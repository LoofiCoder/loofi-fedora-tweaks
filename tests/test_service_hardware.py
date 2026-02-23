"""Tests for services.hardware.* modules.

Covers BatteryManager, DiskManager, and TemperatureManager classes.
HardwareManager is already extensively tested in test_services_hardware_manager.py
and test_hardware_manager_deep.py.
"""

import glob
import os
import subprocess
import sys
import unittest
from unittest.mock import MagicMock, mock_open, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'loofi-fedora-tweaks'))

from services.hardware.battery import BatteryManager
from services.hardware.disk import DiskManager, DiskUsage, LargeDirectory
from services.hardware.temperature import TemperatureManager, TemperatureSensor, _classify_sensor, _read_sysfs_value, _read_millidegree


# ====================================================================================
# BatteryManager Tests
# ====================================================================================


class TestBatterySetLimit(unittest.TestCase):
    """Tests for BatteryManager.set_limit()."""

    @patch('services.hardware.battery.subprocess.run')
    @patch('builtins.open', new_callable=mock_open)
    @patch('services.hardware.battery.os.makedirs')
    def test_set_limit_success(self, mock_makedirs, mock_file, mock_run):
        """Set battery limit succeeds."""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        manager = BatteryManager()
        binary, args = manager.set_limit(80)
        self.assertEqual(binary, "echo")
        self.assertIn("80%", args[0])

    @patch('services.hardware.battery.subprocess.run')
    @patch('builtins.open', new_callable=mock_open)
    @patch('services.hardware.battery.os.makedirs')
    def test_set_limit_config_write_fails_but_proceeds(self, mock_makedirs, mock_file, mock_run):
        """Set battery limit proceeds even if config write fails."""
        # First open for config fails, second for tmp service file succeeds
        mock_file.side_effect = [
            OSError("permission denied"),  # config write fails
            mock_open(read_data="")(),  # tmp service file write succeeds
        ]
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        manager = BatteryManager()
        binary, args = manager.set_limit(80)
        # Should still complete service setup
        self.assertEqual(binary, "echo")
        self.assertIn("80%", args[0])

    @patch('services.hardware.battery.subprocess.run')
    @patch('builtins.open', new_callable=mock_open)
    @patch('services.hardware.battery.os.makedirs')
    def test_set_limit_service_move_fails(self, mock_makedirs, mock_file, mock_run):
        """Set battery limit handles service file move failure."""
        mock_run.return_value = MagicMock(returncode=1, stderr="access denied")
        manager = BatteryManager()
        binary, args = manager.set_limit(80)
        self.assertIsNone(binary)
        self.assertIsNone(args)

    @patch('services.hardware.battery.subprocess.run')
    @patch('builtins.open', new_callable=mock_open)
    @patch('services.hardware.battery.os.makedirs')
    def test_set_limit_daemon_reload_fails(self, mock_makedirs, mock_file, mock_run):
        """Set battery limit handles daemon-reload failure."""
        mock_run.side_effect = [
            MagicMock(returncode=0),  # mv succeeds
            MagicMock(returncode=1, stderr="daemon-reload failed"),  # daemon-reload fails
        ]
        manager = BatteryManager()
        binary, args = manager.set_limit(80)
        self.assertIsNone(binary)

    @patch('services.hardware.battery.subprocess.run')
    @patch('builtins.open', new_callable=mock_open)
    @patch('services.hardware.battery.os.makedirs')
    def test_set_limit_enable_service_fails(self, mock_makedirs, mock_file, mock_run):
        """Set battery limit handles service enable failure."""
        mock_run.side_effect = [
            MagicMock(returncode=0),  # mv succeeds
            MagicMock(returncode=0),  # daemon-reload succeeds
            MagicMock(returncode=1, stderr="enable failed"),  # enable fails
        ]
        manager = BatteryManager()
        binary, args = manager.set_limit(80)
        self.assertIsNone(binary)

    @patch('services.hardware.battery.subprocess.run')
    @patch('builtins.open', new_callable=mock_open)
    @patch('services.hardware.battery.os.makedirs')
    def test_set_limit_sysfs_write_fails(self, mock_makedirs, mock_file, mock_run):
        """Set battery limit handles sysfs write failure but service installed."""
        mock_run.side_effect = [
            MagicMock(returncode=0),  # mv succeeds
            MagicMock(returncode=0),  # daemon-reload succeeds
            MagicMock(returncode=0),  # enable succeeds
            MagicMock(returncode=1, stderr="sysfs write failed"),  # sysfs write fails
        ]
        manager = BatteryManager()
        binary, args = manager.set_limit(80)
        self.assertEqual(binary, "echo")
        self.assertIn("reboot", args[0].lower())

    @patch('services.hardware.battery.subprocess.run')
    @patch('builtins.open', new_callable=mock_open)
    @patch('services.hardware.battery.os.makedirs')
    def test_set_limit_exception(self, mock_makedirs, mock_file, mock_run):
        """Set battery limit handles subprocess exception."""
        mock_run.side_effect = OSError("boom")
        manager = BatteryManager()
        binary, args = manager.set_limit(80)
        self.assertIsNone(binary)
        self.assertIsNone(args)


# ====================================================================================
# DiskManager Tests
# ====================================================================================


class TestBytesToHuman(unittest.TestCase):
    """Tests for DiskManager.bytes_to_human()."""

    def test_bytes(self):
        """Bytes display correctly."""
        self.assertEqual(DiskManager.bytes_to_human(500), "500.0 B")

    def test_kilobytes(self):
        """Kilobytes display correctly."""
        self.assertEqual(DiskManager.bytes_to_human(1536), "1.5 KB")

    def test_megabytes(self):
        """Megabytes display correctly."""
        self.assertEqual(DiskManager.bytes_to_human(1048576), "1.0 MB")

    def test_gigabytes(self):
        """Gigabytes display correctly."""
        self.assertEqual(DiskManager.bytes_to_human(5368709120), "5.0 GB")

    def test_terabytes(self):
        """Terabytes display correctly."""
        self.assertEqual(DiskManager.bytes_to_human(1099511627776), "1.0 TB")


class TestGetDiskUsage(unittest.TestCase):
    """Tests for DiskManager.get_disk_usage()."""

    @patch('services.hardware.disk.shutil.disk_usage')
    def test_get_disk_usage_success(self, mock_usage):
        """Get disk usage succeeds."""
        mock_usage.return_value = MagicMock(total=100000000000, used=50000000000, free=50000000000)
        result = DiskManager.get_disk_usage("/")
        self.assertIsInstance(result, DiskUsage)
        self.assertEqual(result.mount_point, "/")
        self.assertEqual(result.percent_used, 50.0)

    @patch('services.hardware.disk.shutil.disk_usage')
    def test_get_disk_usage_oserror(self, mock_usage):
        """Get disk usage handles OSError."""
        mock_usage.side_effect = OSError("path not found")
        result = DiskManager.get_disk_usage("/invalid")
        self.assertIsNone(result)

    @patch('services.hardware.disk.shutil.disk_usage')
    def test_get_disk_usage_zero_total(self, mock_usage):
        """Get disk usage handles zero total bytes."""
        mock_usage.return_value = MagicMock(total=0, used=0, free=0)
        result = DiskManager.get_disk_usage("/")
        self.assertIsInstance(result, DiskUsage)
        self.assertEqual(result.percent_used, 0)


class TestGetAllMountPoints(unittest.TestCase):
    """Tests for DiskManager.get_all_mount_points()."""

    @patch('services.hardware.disk.subprocess.run')
    def test_get_all_mount_points_success(self, mock_run):
        """Get all mount points succeeds."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Mounted on               Size  Used Avail Use% Filesystem\n"
                   "/                  100000000 50000000 50000000  50% /dev/sda1\n"
                   "/home              200000000 100000000 100000000  50% /dev/sda2\n"
        )
        result = DiskManager.get_all_mount_points()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    @patch('services.hardware.disk.subprocess.run')
    def test_get_all_mount_points_filters_virtual(self, mock_run):
        """Get all mount points filters virtual filesystems."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Mounted on               Size  Used Avail Use% Filesystem\n"
                   "/                  100000000 50000000 50000000  50% /dev/sda1\n"
                   "/dev               10000 5000 5000  50% devtmpfs\n"
                   "/sys               10000 5000 5000  50% sysfs\n"
                   "/proc              10000 5000 5000  50% proc\n"
        )
        result = DiskManager.get_all_mount_points()
        # Should only include / and skip virtual filesystems
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].mount_point, "/")

    @patch('services.hardware.disk.subprocess.run')
    def test_get_all_mount_points_subprocess_error(self, mock_run):
        """Get all mount points handles subprocess error."""
        mock_run.side_effect = OSError("df not found")
        result = DiskManager.get_all_mount_points()
        self.assertEqual(result, [])

    @patch('services.hardware.disk.subprocess.run')
    def test_get_all_mount_points_nonzero_exit(self, mock_run):
        """Get all mount points handles non-zero exit code."""
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        result = DiskManager.get_all_mount_points()
        self.assertEqual(result, [])


class TestCheckDiskHealth(unittest.TestCase):
    """Tests for DiskManager.check_disk_health()."""

    @patch('services.hardware.disk.DiskManager.get_disk_usage')
    def test_check_disk_health_ok(self, mock_usage):
        """Disk health check returns ok status."""
        mock_usage.return_value = DiskUsage(
            mount_point="/", total_bytes=100000000000, used_bytes=50000000000,
            free_bytes=50000000000, percent_used=50.0
        )
        level, message = DiskManager.check_disk_health("/")
        self.assertEqual(level, "ok")
        self.assertIn("healthy", message.lower())

    @patch('services.hardware.disk.DiskManager.get_disk_usage')
    def test_check_disk_health_warning(self, mock_usage):
        """Disk health check returns warning status."""
        mock_usage.return_value = DiskUsage(
            mount_point="/", total_bytes=100000000000, used_bytes=85000000000,
            free_bytes=15000000000, percent_used=85.0
        )
        level, message = DiskManager.check_disk_health("/")
        self.assertEqual(level, "warning")
        self.assertIn("low", message.lower())

    @patch('services.hardware.disk.DiskManager.get_disk_usage')
    def test_check_disk_health_critical(self, mock_usage):
        """Disk health check returns critical status."""
        mock_usage.return_value = DiskUsage(
            mount_point="/", total_bytes=100000000000, used_bytes=95000000000,
            free_bytes=5000000000, percent_used=95.0
        )
        level, message = DiskManager.check_disk_health("/")
        self.assertEqual(level, "critical")
        self.assertIn("critically full", message.lower())

    @patch('services.hardware.disk.DiskManager.get_disk_usage')
    def test_check_disk_health_unable(self, mock_usage):
        """Disk health check handles None result."""
        mock_usage.return_value = None
        level, message = DiskManager.check_disk_health("/")
        self.assertEqual(level, "unknown")
        self.assertIn("Unable", message)


class TestFindLargeDirectories(unittest.TestCase):
    """Tests for DiskManager.find_large_directories()."""

    @patch('services.hardware.disk.subprocess.run')
    def test_find_large_directories_success(self, mock_run):
        """Find large directories succeeds."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="5000000000\t/home/user/Videos\n"
                   "3000000000\t/home/user/Downloads\n"
                   "1000000000\t/home/user/Documents\n"
                   "10000000000\t/home/user\n"
        )
        result = DiskManager.find_large_directories("/home/user", max_depth=2, top_n=3)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].path, "/home/user/Videos")
        self.assertEqual(result[0].size_bytes, 5000000000)

    @patch('services.hardware.disk.subprocess.run')
    def test_find_large_directories_subprocess_error(self, mock_run):
        """Find large directories handles subprocess error."""
        mock_run.side_effect = OSError("du not found")
        result = DiskManager.find_large_directories("/home")
        self.assertEqual(result, [])

    @patch('services.hardware.disk.subprocess.run')
    def test_find_large_directories_permission_error(self, mock_run):
        """Find large directories handles permission errors in du."""
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        result = DiskManager.find_large_directories("/root")
        self.assertEqual(result, [])

    @patch('services.hardware.disk.subprocess.run')
    def test_find_large_directories_excludes_root(self, mock_run):
        """Find large directories excludes the root path itself."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="1000000\t/home/user/test\n"
                   "5000000\t/home/user\n"
        )
        result = DiskManager.find_large_directories("/home/user")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].path, "/home/user/test")


# ====================================================================================
# TemperatureManager Tests
# ====================================================================================


class TestClassifySensor(unittest.TestCase):
    """Tests for _classify_sensor()."""

    def test_classify_cpu(self):
        """CPU sensors classified correctly."""
        self.assertEqual(_classify_sensor("coretemp"), "cpu")
        self.assertEqual(_classify_sensor("k10temp"), "cpu")
        self.assertEqual(_classify_sensor("zenpower"), "cpu")
        self.assertEqual(_classify_sensor("cpu_thermal"), "cpu")

    def test_classify_gpu(self):
        """GPU sensors classified correctly."""
        self.assertEqual(_classify_sensor("amdgpu"), "gpu")
        self.assertEqual(_classify_sensor("nouveau"), "gpu")
        self.assertEqual(_classify_sensor("nvidia"), "gpu")
        self.assertEqual(_classify_sensor("radeon"), "gpu")

    def test_classify_disk(self):
        """Disk sensors classified correctly."""
        self.assertEqual(_classify_sensor("nvme"), "disk")
        self.assertEqual(_classify_sensor("drivetemp"), "disk")

    def test_classify_other(self):
        """Unknown sensors classified as other."""
        self.assertEqual(_classify_sensor("unknown_device"), "other")
        self.assertEqual(_classify_sensor("acpitz"), "other")


class TestReadSysfsValue(unittest.TestCase):
    """Tests for _read_sysfs_value()."""

    @patch('builtins.open', new_callable=mock_open, read_data="test_value\n")
    def test_read_sysfs_value_success(self, mock_file):
        """Read sysfs value succeeds."""
        result = _read_sysfs_value("/sys/test/file")
        self.assertEqual(result, "test_value")

    @patch('builtins.open', side_effect=OSError("file not found"))
    def test_read_sysfs_value_oserror(self, mock_file):
        """Read sysfs value handles OSError."""
        result = _read_sysfs_value("/sys/test/file")
        self.assertIsNone(result)

    @patch('builtins.open', side_effect=IOError("permission denied"))
    def test_read_sysfs_value_ioerror(self, mock_file):
        """Read sysfs value handles IOError."""
        result = _read_sysfs_value("/sys/test/file")
        self.assertIsNone(result)


class TestReadMillidegree(unittest.TestCase):
    """Tests for _read_millidegree()."""

    @patch('services.hardware.temperature._read_sysfs_value', return_value="45000")
    def test_read_millidegree_success(self, mock_read):
        """Read millidegree converts to celsius."""
        result = _read_millidegree("/sys/test/temp1_input")
        self.assertEqual(result, 45.0)

    @patch('services.hardware.temperature._read_sysfs_value', return_value=None)
    def test_read_millidegree_none(self, mock_read):
        """Read millidegree handles None result."""
        result = _read_millidegree("/sys/test/temp1_input")
        self.assertEqual(result, 0.0)

    @patch('services.hardware.temperature._read_sysfs_value', return_value="invalid")
    def test_read_millidegree_invalid(self, mock_read):
        """Read millidegree handles invalid value."""
        result = _read_millidegree("/sys/test/temp1_input")
        self.assertEqual(result, 0.0)


class TestGetAllSensors(unittest.TestCase):
    """Tests for TemperatureManager.get_all_sensors()."""

    @patch('services.hardware.temperature.glob.glob')
    def test_get_all_sensors_no_hwmon(self, mock_glob):
        """Get all sensors handles no hwmon devices."""
        mock_glob.return_value = []
        result = TemperatureManager.get_all_sensors()
        self.assertEqual(result, [])

    @patch('services.hardware.temperature.glob.glob')
    def test_get_all_sensors_glob_error(self, mock_glob):
        """Get all sensors handles glob error."""
        mock_glob.side_effect = OSError("permission denied")
        result = TemperatureManager.get_all_sensors()
        self.assertEqual(result, [])

    @patch('services.hardware.temperature._read_sysfs_value')
    @patch('services.hardware.temperature._read_millidegree')
    @patch('services.hardware.temperature.glob.glob')
    def test_get_all_sensors_success(self, mock_glob_outer, mock_millidegree, mock_sysfs):
        """Get all sensors succeeds."""
        # First glob returns hwmon dirs, second glob returns temp files
        mock_glob_outer.side_effect = [
            ["/sys/class/hwmon/hwmon0"],
            ["/sys/class/hwmon/hwmon0/temp1_input"]
        ]
        mock_sysfs.side_effect = ["coretemp", "Core 0"]
        mock_millidegree.side_effect = [55.0, 80.0, 100.0]  # current, high, critical

        result = TemperatureManager.get_all_sensors()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "coretemp")
        self.assertEqual(result[0].sensor_type, "cpu")
        self.assertEqual(result[0].current, 55.0)

    @patch('services.hardware.temperature._read_sysfs_value', return_value=None)
    @patch('services.hardware.temperature.glob.glob')
    def test_get_all_sensors_no_name_file(self, mock_glob, mock_sysfs):
        """Get all sensors skips devices without name file."""
        mock_glob.side_effect = [
            ["/sys/class/hwmon/hwmon0"],
            []
        ]
        result = TemperatureManager.get_all_sensors()
        self.assertEqual(result, [])


class TestGetCpuTemps(unittest.TestCase):
    """Tests for TemperatureManager.get_cpu_temps()."""

    @patch('services.hardware.temperature.TemperatureManager.get_all_sensors')
    def test_get_cpu_temps_filters(self, mock_all):
        """Get CPU temps filters by sensor type."""
        mock_all.return_value = [
            TemperatureSensor(name="coretemp", label="Core 0", current=55.0, high=80.0, critical=100.0, sensor_type="cpu"),
            TemperatureSensor(name="amdgpu", label="GPU Edge", current=65.0, high=90.0, critical=110.0, sensor_type="gpu"),
            TemperatureSensor(name="k10temp", label="Tctl", current=50.0, high=70.0, critical=95.0, sensor_type="cpu"),
        ]
        result = TemperatureManager.get_cpu_temps()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].sensor_type, "cpu")
        self.assertEqual(result[1].sensor_type, "cpu")

    @patch('services.hardware.temperature.TemperatureManager.get_all_sensors')
    def test_get_cpu_temps_empty(self, mock_all):
        """Get CPU temps handles no CPU sensors."""
        mock_all.return_value = []
        result = TemperatureManager.get_cpu_temps()
        self.assertEqual(result, [])


class TestGetGpuTemps(unittest.TestCase):
    """Tests for TemperatureManager.get_gpu_temps()."""

    @patch('services.hardware.temperature.TemperatureManager.get_all_sensors')
    def test_get_gpu_temps_filters(self, mock_all):
        """Get GPU temps filters by sensor type."""
        mock_all.return_value = [
            TemperatureSensor(name="coretemp", label="Core 0", current=55.0, high=80.0, critical=100.0, sensor_type="cpu"),
            TemperatureSensor(name="amdgpu", label="GPU Edge", current=65.0, high=90.0, critical=110.0, sensor_type="gpu"),
            TemperatureSensor(name="nouveau", label="GPU", current=70.0, high=95.0, critical=115.0, sensor_type="gpu"),
        ]
        result = TemperatureManager.get_gpu_temps()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].sensor_type, "gpu")
        self.assertEqual(result[1].sensor_type, "gpu")

    @patch('services.hardware.temperature.TemperatureManager.get_all_sensors')
    def test_get_gpu_temps_empty(self, mock_all):
        """Get GPU temps handles no GPU sensors."""
        mock_all.return_value = []
        result = TemperatureManager.get_gpu_temps()
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
