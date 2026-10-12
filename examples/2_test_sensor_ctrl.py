#   Copyright (c) Meta Platforms, Inc. and affiliates.
import argparse
import time

from polymetis import RobotInterface
from dragonclaw_library import DragonClawSensor
import numpy as np
import torch

parser = argparse.ArgumentParser()
parser.add_argument("--robot-ip", required=True)
args = parser.parse_args()

sensor = DragonClawSensor("/dev/ttyACM0")
robot = RobotInterface(ip_address=args.robot_ip)

ee_pos_move_up = torch.Tensor([0, 0, 0.05])
ee_pos_move_down = torch.Tensor([0, 0, -0.05])

try:
    while True:
        sensor_data = sensor.read_sensor()
        if sensor_data is None:
            time.sleep(0.01)
            continue

        base_z_uT = np.mean(sensor_data.z_uT[0:3])
        if base_z_uT < 0:
            print("\nMoving UP ...\n")
            robot.move_to_ee_pose(
                position=ee_pos_move_up, orientation=None, time_to_go=2.0, delta=True
            )
            time.sleep(0.5)
        elif base_z_uT > 0:
            print("\nMoving DOWN ...\n")
            robot.move_to_ee_pose(
                position=ee_pos_move_down, orientation=None, time_to_go=2.0, delta=True
            )
            time.sleep(0.5)
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    sensor.stop()
