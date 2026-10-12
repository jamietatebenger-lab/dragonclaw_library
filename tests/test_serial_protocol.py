import struct
import unittest
from unittest.mock import MagicMock, patch

from dragonclaw_library import DragonClaw, DragonClawSensor


class SerialProtocolTests(unittest.TestCase):
    def setUp(self):
        self.serial = MagicMock()
        self.serial.isOpen.return_value = True

    def test_actuator_uses_firmware_baud_rate(self):
        with patch("dragonclaw_library.dragonclaw.serial.Serial", return_value=self.serial) as serial:
            DragonClaw()

        serial.assert_called_once_with("/dev/ttyACM0", 9600)

    def test_sensor_uses_firmware_baud_rate(self):
        with patch(
            "dragonclaw_library.dragonclaw_sensor.serial.Serial",
            return_value=self.serial,
        ) as serial:
            DragonClawSensor()

        serial.assert_called_once_with("/dev/ttyACM0", 250000)

    def test_sensor_decodes_binary_packet(self):
        values = [123.0]
        for sensor_index in range(7):
            values.extend(
                [20.0 + sensor_index, 1.0 + sensor_index, 2.0, 3.0]
            )
        self.serial.inWaiting.return_value = 1
        self.serial.read.return_value = struct.pack("<29f", *values) + b"\r\n"

        with patch(
            "dragonclaw_library.dragonclaw_sensor.serial.Serial",
            return_value=self.serial,
        ):
            sensor = DragonClawSensor()

        result = sensor.read_sensor()

        self.assertEqual(result.timestamp_us, 123.0)
        self.assertEqual(result.temp_C.tolist(), [20.0 + i for i in range(7)])
        self.assertEqual(result.x_uT.tolist(), [1.0 + i for i in range(7)])
        self.assertAlmostEqual(result.mag_uT[0], 14**0.5)

    def test_sensor_rejects_incomplete_packet(self):
        self.serial.inWaiting.return_value = 1
        self.serial.read.return_value = b"short"

        with patch(
            "dragonclaw_library.dragonclaw_sensor.serial.Serial",
            return_value=self.serial,
        ):
            sensor = DragonClawSensor()

        with self.assertRaisesRegex(ValueError, "Incomplete or invalid"):
            sensor.read_sensor()

    def test_sensor_stop_closes_serial_connection(self):
        with patch(
            "dragonclaw_library.dragonclaw_sensor.serial.Serial",
            return_value=self.serial,
        ):
            sensor = DragonClawSensor()

        sensor.stop()

        self.serial.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
