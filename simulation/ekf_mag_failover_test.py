#!/usr/bin/env python3
"""
SITL Magnetic Interference Test (SAFE VERSION)
------------------------------------------------
- 不會造成 QGC 斷線
- 使用 SIM_MAG1_OFS_* 注入磁力干擾
- 漸進式干擾 (Ramp)
- 持續送 GCS heartbeat
"""

import time
import math
from pymavlink import mavutil

# =========================
# MAVLink 設定
# =========================
CONNECTION = "tcp:127.0.0.1:5762"
SRC_SYS = 255
SRC_COMP = mavutil.mavlink.MAV_COMP_ID_MISSIONPLANNER

# =========================
# 干擾參數
# =========================
TEST_DURATION = 90          # 秒
RAMP_TIME = 30              # 干擾漸增時間
MAX_OFFSET = 2500           # mGauss（安全上限，別超過 3000）
UPDATE_RATE = 0.5           # seconds
HEARTBEAT_RATE = 1.0        # seconds

# =========================
# 工具函式
# =========================
def heartbeat(master):
    master.mav.heartbeat_send(
        mavutil.mavlink.MAV_TYPE_GCS,
        mavutil.mavlink.MAV_AUTOPILOT_INVALID,
        0, 0, 0
    )

def set_param(master, name, value):
    master.mav.param_set_send(
        master.target_system,
        master.target_component,
        name.encode(),
        float(value),
        mavutil.mavlink.MAV_PARAM_TYPE_REAL32
    )

def get_ekf_status(master):
    msg = master.recv_match(type="EKF_STATUS_REPORT", blocking=False)
    if not msg:
        return None
    return msg.flags

# =========================
# 主流程
# =========================
def main():
    print("🔌 Connecting to SITL...")
    master = mavutil.mavlink_connection(
        CONNECTION,
        source_system=SRC_SYS,
        source_component=SRC_COMP
    )
    master.wait_heartbeat()
    print("✅ Connected to autopilot")

    last_hb = time.time()
    start = time.time()

    last_offset = -1

    print("\n🚧 Starting magnetic interference test\n")

    while True:
        now = time.time()
        elapsed = now - start

        # 結束條件
        if elapsed > TEST_DURATION:
            break

        # Heartbeat（防止 QGC timeout）
        if now - last_hb > HEARTBEAT_RATE:
            heartbeat(master)
            last_hb = now

        # =========================
        # 干擾強度計算（漸增）
        # =========================
        if elapsed < RAMP_TIME:
            scale = elapsed / RAMP_TIME
        else:
            scale = 1.0

        offset = int(MAX_OFFSET * scale)

        # 避免無意義重複寫 param
        if abs(offset - last_offset) > 10:
            set_param(master, "SIM_MAG1_OFS_X", offset)
            set_param(master, "SIM_MAG1_OFS_Y", offset * 0.7)
            set_param(master, "SIM_MAG1_OFS_Z", offset * 1.2)
            last_offset = offset

        # EKF 狀態監看
        ekf_flags = get_ekf_status(master)

        print(
            f"T+{elapsed:5.1f}s | "
            f"MagOffset={offset:4d} mG | "
            f"EKF={'OK' if ekf_flags else '---'}"
        )

        time.sleep(UPDATE_RATE)

    # =========================
    # 清理
    # =========================
    print("\n🧹 Reset magnetic offsets")
    set_param(master, "SIM_MAG1_OFS_X", 0)
    set_param(master, "SIM_MAG1_OFS_Y", 0)
    set_param(master, "SIM_MAG1_OFS_Z", 0)

    time.sleep(2)
    heartbeat(master)

    print("✅ Test finished safely")

# =========================
if __name__ == "__main__":
    main()
