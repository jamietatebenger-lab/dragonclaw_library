#   Copyright (c) Meta Platforms, Inc. and affiliates.

import time

from dragonclaw_library import DragonClaw


claw = DragonClaw("/dev/ttyACM0")
try:
    while True:
        pressure_data = claw.read_press()
        if pressure_data is None:
            time.sleep(0.01)
        else:
            print(pressure_data)
except KeyboardInterrupt:
    pass
finally:
    claw.release()
    claw.ser.close()
