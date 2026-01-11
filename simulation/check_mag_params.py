#!/usr/bin/env python3
"""
參數驗證工具 - 檢查 SITL 參數是否真的改變了
"""

import time
from pymavlink import mavutil

CONNECTION_STRING = 'tcp:127.0.0.1:5762'
SOURCE_SYSTEM = 254

def check_params():
    """檢查當前磁力計參數值"""
    print("正在連接到 SITL...")
    master = mavutil.mavlink_connection(
        CONNECTION_STRING,
        source_system=SOURCE_SYSTEM
    )
    
    # 發送心跳
    master.mav.heartbeat_send(
        mavutil.mavlink.MAV_TYPE_GCS,
        mavutil.mavlink.MAV_AUTOPILOT_INVALID,
        0, 0, 0
    )
    
    master.wait_heartbeat(timeout=5)
    print(f"✅ 已連接到系統 {master.target_system}\n")
    
    # 請求參數
    params_to_check = [
        'SIM_MAG_MOT_X',
        'SIM_MAG_MOT_Y',
        'SIM_MAG_MOT_Z',
        'SIM_MAG1_SCALING',
        'SIM_MAG1_OFS_X',
        'SIM_MAG1_OFS_Y',
        'SIM_MAG1_OFS_Z',
    ]
    
    print("📊 當前磁力計參數值:")
    print("="*50)
    
    for param_name in params_to_check:
        # 請求參數
        master.mav.param_request_read_send(
            master.target_system,
            master.target_component,
            param_name.encode('utf-8'),
            -1
        )
        
        # 等待回應
        msg = master.recv_match(type='PARAM_VALUE', blocking=True, timeout=2)
        if msg and msg.param_id == param_name:
            status = "⚠️ 異常" if msg.param_value != 0 else "✅ 正常"
            print(f"{param_name:20s} = {msg.param_value:10.2f}  {status}")
        else:
            print(f"{param_name:20s} = ???  ❌ 無法讀取")
    
    print("="*50)
    
    # 計算磁場總強度
    print("\n💡 判斷:")
    print("  - 如果所有值都是 0 → 參數未送達或已重置")
    print("  - 如果 SIM_MAG_MOT_* > 0 → 參數已送達,檢查干擾強度")
    print("  - 建議干擾值: SIM_MAG_MOT_X > 2000 才會觸發 EKF 警告")

if __name__ == '__main__':
    check_params()
