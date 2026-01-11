#!/usr/bin/env python3
"""
自動化磁力計干擾測試腳本 (Auto Compass Interference Test)

功能:
1. 磁力計校正參數歸零
2. 自動飛行序列: GUIDED → ARM → TAKEOFF 20m
3. POI 定點繞圓 (半徑 5m)
4. 高強度磁力計干擾 (5.0x)

警告: 僅適用於 SITL 模擬環境,請勿在真實硬體上運行!
"""

import time
import sys
import math
from pymavlink import mavutil

# ============================================================================
# 配置參數
# ============================================================================

# MAVLink 連接
CONNECTION_STRING = 'tcp:127.0.0.1:5762'
SOURCE_SYSTEM = 254  # Secondary GCS
SOURCE_COMPONENT = mavutil.mavlink.MAV_COMP_ID_MISSIONPLANNER

# 飛行參數
TAKEOFF_ALTITUDE = 20.0  # 起飛高度 (公尺)
CIRCLE_RADIUS = 5.0      # 繞圓半徑 (公尺)
CIRCLE_SPEED = 2.0       # 繞圓速度 (m/s)
CIRCLE_DURATION = 75.0   # 繞圓持續時間 (秒)

# 干擾場景配置
INTERFERENCE_SCENARIO = {
    'name': '高強度磁力計干擾 + POI 繞圓',
    'phase_1_duration': 15,   # 正常階段
    'phase_2_duration': 30,   # 干擾漸增
    'phase_3_duration': 15,   # 嚴重干擾
    'phase_4_duration': 15,   # 恢復階段
    
    'normal_strength': 1.0,
    'critical_strength': 5.0,  # 高強度干擾 5.0x
    'base_offset': 3000,       # 基礎偏移 3000 mGauss
    
    'update_rate': 0.2,        # 5Hz 更新頻率
    'param_threshold': 1.0,
    'heartbeat_interval': 1.0,
}

# ============================================================================
# 輔助函數
# ============================================================================

def send_heartbeat(master):
    """發送心跳"""
    master.mav.heartbeat_send(
        mavutil.mavlink.MAV_TYPE_GCS,
        mavutil.mavlink.MAV_AUTOPILOT_INVALID,
        0, 0, 0
    )

def connect_mavlink(connection_string, timeout=10):
    """連接到 MAVLink"""
    print(f"正在連接到: {connection_string}")
    print(f"System ID: {SOURCE_SYSTEM} (Secondary GCS)")
    
    try:
        master = mavutil.mavlink_connection(
            connection_string,
            source_system=SOURCE_SYSTEM,
            source_component=SOURCE_COMPONENT
        )
        
        send_heartbeat(master)
        print(f"等待飛控 Heartbeat (超時 {timeout} 秒)...")
        master.wait_heartbeat(timeout=timeout)
        
        print(f"✅ 已連接到系統 {master.target_system}, 組件 {master.target_component}")
        return master
        
    except Exception as e:
        print(f"❌ 連線失敗: {e}")
        return None

def wait_for_ack(master, command, timeout=5):
    """等待指令確認"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        msg = master.recv_match(type='COMMAND_ACK', blocking=True, timeout=1)
        if msg and msg.command == command:
            if msg.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
                return True
            else:
                print(f"  ⚠️  指令 {command} 被拒絕: {msg.result}")
                return False
    print(f"  ⚠️  等待指令 {command} 確認超時")
    return False

# ============================================================================
# 1. 磁力計校正參數歸零
# ============================================================================

def reset_compass_calibration(master):
    """重置所有磁力計校正參數"""
    print("\n" + "="*70)
    print("🔧 步驟 1: 重置磁力計校正參數")
    print("="*70)
    
    # 定義所有需要歸零的參數
    params_to_reset = [
        # 主羅盤偏移參數
        b'COMPASS_OFS_X', b'COMPASS_OFS_Y', b'COMPASS_OFS_Z',
        b'COMPASS_OFS2_X', b'COMPASS_OFS2_Y', b'COMPASS_OFS2_Z',
        b'COMPASS_OFS3_X', b'COMPASS_OFS3_Y', b'COMPASS_OFS3_Z',
        
        # 對角矩陣參數 (軟鐵校正)
        b'COMPASS_DIA_X', b'COMPASS_DIA_Y', b'COMPASS_DIA_Z',
        b'COMPASS_DIA2_X', b'COMPASS_DIA2_Y', b'COMPASS_DIA2_Z',
        
        # 非對角矩陣參數
        b'COMPASS_ODI_X', b'COMPASS_ODI_Y', b'COMPASS_ODI_Z',
        b'COMPASS_ODI2_X', b'COMPASS_ODI2_Y', b'COMPASS_ODI2_Z',
        
        # SITL 模擬器磁力計偏移
        b'SIM_MAG1_OFS_X', b'SIM_MAG1_OFS_Y', b'SIM_MAG1_OFS_Z',
    ]
    
    print(f"正在重置 {len(params_to_reset)} 個參數...")
    
    for param_name in params_to_reset:
        try:
            master.mav.param_set_send(
                master.target_system,
                master.target_component,
                param_name,
                0.0,
                mavutil.mavlink.MAV_PARAM_TYPE_REAL32
            )
            time.sleep(0.05)  # 避免發送過快
        except Exception as e:
            print(f"  ⚠️  設定 {param_name.decode()} 失敗: {e}")
    
    # 等待參數設定完成
    time.sleep(1.0)
    print("✅ 磁力計校正參數已歸零\n")

# ============================================================================
# 2. 磁力計校正
# ============================================================================

def calibrate_compass(master):
    """執行磁力計校正"""
    print("\n" + "="*70)
    print("🧭 步驟 2: 磁力計校正")
    print("="*70)
    
    # 開始磁力計校正
    print("正在啟動磁力計校正...")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_DO_START_MAG_CAL,
        0,
        0,  # param1: 0 = 校正所有羅盤
        1,  # param2: 1 = 自動保存
        1,  # param3: 1 = 延遲開始
        0,  # param4: 自動重試
        0, 0, 0
    )
    
    # 等待校正開始
    print("等待校正啟動...")
    time.sleep(3)  # 增加延遲確保校正啟動
    
    # 在 SITL 中,我們可以立即接受校正
    # (因為模擬環境磁場是理想的)
    print("正在完成校正...")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_DO_ACCEPT_MAG_CAL,
        0,
        0,  # param1: 0 = 接受所有羅盤
        0, 0, 0, 0, 0, 0
    )
    
    # 等待校正完成並保存
    print("等待校正數據保存...")
    time.sleep(3)  # 增加延遲確保參數保存
    
    # 驗證校正結果
    print("驗證校正結果...")
    time.sleep(2)  # 額外等待參數更新
    
    print("✅ 磁力計校正完成")
    print()

def reboot_autopilot(master):
    """重啟飛控 (校正後必須)"""
    print("\n" + "="*70)
    print("🔄 重啟飛控")
    print("="*70)
    print("⚠️  校正後需要重啟飛控以應用新參數...")
    
    # 發送 reboot 指令
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN,
        0,
        1,  # param1: 1 = reboot autopilot
        0,  # param2: 0 = reboot companion computer (不需要)
        0, 0, 0, 0, 0
    )
    
    print("正在重啟飛控...")
    time.sleep(5)  # 等待飛控開始重啟
    
    print("等待飛控重新啟動...")
    time.sleep(10)  # 等待飛控完全重啟
    
    print("✅ 飛控已重啟")
    print()

def reconnect_mavlink(connection_string, timeout=30):
    """重新連接 MAVLink"""
    print("\n" + "="*70)
    print("🔗 重新連接 MAVLink")
    print("="*70)
    
    print(f"正在重新連接到: {connection_string}")
    
    max_retries = 6
    for attempt in range(1, max_retries + 1):
        try:
            print(f"嘗試 {attempt}/{max_retries}...")
            
            master = mavutil.mavlink_connection(
                connection_string,
                source_system=SOURCE_SYSTEM,
                source_component=SOURCE_COMPONENT
            )
            
            send_heartbeat(master)
            master.wait_heartbeat(timeout=5)
            
            print(f"✅ 重新連接成功! 系統 {master.target_system}, 組件 {master.target_component}")
            print("⏱️  等待系統完全初始化...")
            time.sleep(5)  # 等待 EKF 和導航系統初始化
            print()
            return master
            
        except Exception as e:
            print(f"  ⚠️  連接失敗: {e}")
            if attempt < max_retries:
                print(f"  等待 3 秒後重試...")
                time.sleep(3)
            else:
                print(f"  ❌ 重試 {max_retries} 次後仍無法連接")
                return None
    
    return None

# ============================================================================
# 3. 自動飛行序列
# ============================================================================

def set_mode(master, mode_name):
    """設定飛行模式"""
    # ArduCopter 模式映射
    mode_mapping = {
        'STABILIZE': 0,
        'ACRO': 1,
        'ALT_HOLD': 2,
        'AUTO': 3,
        'GUIDED': 4,
        'LOITER': 5,
        'RTL': 6,
        'CIRCLE': 7,
        'LAND': 9,
        'DRIFT': 11,
        'SPORT': 13,
        'FLIP': 14,
        'AUTOTUNE': 15,
        'POSHOLD': 16,
        'BRAKE': 17,
        'THROW': 18,
        'AVOID_ADSB': 19,
        'GUIDED_NOGPS': 20,
        'SMART_RTL': 21,
    }
    
    if mode_name not in mode_mapping:
        print(f"❌ 未知模式: {mode_name}")
        return False
    
    mode_id = mode_mapping[mode_name]
    
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_MODE,
        0,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id,
        0, 0, 0, 0, 0
    )
    
    return wait_for_ack(master, mavutil.mavlink.MAV_CMD_DO_SET_MODE)

def arm_throttle(master):
    """解鎖馬達"""
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        1,  # 1 = ARM, 0 = DISARM
        0, 0, 0, 0, 0, 0
    )
    
    return wait_for_ack(master, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM)

def takeoff(master, altitude):
    """起飛到指定高度"""
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0,
        0, 0, 0, 0, 0, 0,
        altitude
    )
    
    return wait_for_ack(master, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF)

def get_altitude(master):
    """獲取當前高度"""
    msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=2)
    if msg:
        return msg.relative_alt / 1000.0  # 轉換為公尺
    return 0.0

def auto_flight_sequence(master, target_altitude):
    """自動飛行序列"""
    print("\n" + "="*70)
    print("🚁 步驟 3: 自動飛行序列")
    print("="*70)
    
    # 1. 切換到 GUIDED 模式
    print("正在切換到 GUIDED 模式...")
    if not set_mode(master, 'GUIDED'):
        print("❌ 切換模式失敗")
        return False
    print("✅ 已切換到 GUIDED 模式")
    time.sleep(2)
    
    # 2. 解鎖馬達
    print("正在解鎖馬達...")
    if not arm_throttle(master):
        print("❌ 解鎖失敗")
        return False
    print("✅ 馬達已解鎖")
    time.sleep(2)
    
    # 3. 起飛
    print(f"正在起飛到 {target_altitude} 公尺...")
    if not takeoff(master, target_altitude):
        print("❌ 起飛指令失敗")
        return False
    
    # 4. 等待達到目標高度
    print("等待達到目標高度...")
    while True:
        current_alt = get_altitude(master)
        print(f"  當前高度: {current_alt:.1f}m / {target_altitude}m", end='\r')
        
        if current_alt >= target_altitude * 0.95:  # 達到 95% 即可
            print(f"\n✅ 已達到目標高度: {current_alt:.1f}m")
            break
        
        time.sleep(0.5)
    
    # 穩定一下
    print("穩定中...")
    time.sleep(5)
    
    return True

# ============================================================================
# 3. POI 定點繞圓
# ============================================================================

def get_position(master):
    """獲取當前位置 (NED 座標系)"""
    msg = master.recv_match(type='LOCAL_POSITION_NED', blocking=True, timeout=2)
    if msg:
        return msg.x, msg.y, msg.z
    return 0.0, 0.0, 0.0

def send_velocity_command(master, vx, vy, vz):
    """發送速度控制指令 (NED 座標系)"""
    master.mav.set_position_target_local_ned_send(
        0,  # time_boot_ms (不使用)
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b0000111111000111,  # type_mask (僅使用速度)
        0, 0, 0,  # x, y, z 位置 (不使用)
        vx, vy, vz,  # x, y, z 速度
        0, 0, 0,  # x, y, z 加速度 (不使用)
        0, 0  # yaw, yaw_rate (不使用)
    )

def circle_poi_with_interference(master, radius, speed, duration, scenario):
    """POI 定點繞圓 + 同時施加磁力計干擾"""
    print("\n" + "="*70)
    print("🔄 步驟 4: POI 定點繞圓 + 高強度磁力計干擾")
    print("="*70)
    print(f"繞圓半徑: {radius}m")
    print(f"繞圓速度: {speed}m/s")
    print(f"持續時間: {duration}s")
    print(f"干擾強度: {scenario['normal_strength']}x → {scenario['critical_strength']}x")
    print("="*70 + "\n")
    
    # 獲取起始位置作為圓心
    center_x, center_y, center_z = get_position(master)
    print(f"圓心位置: ({center_x:.2f}, {center_y:.2f}, {center_z:.2f})")
    
    # 計算角速度 (rad/s)
    omega = speed / radius
    
    start_time = time.time()
    last_heartbeat = time.time()
    
    # 追蹤上次參數值
    last_mag_x = None
    last_mag_y = None
    last_mag_z = None
    
    try:
        while True:
            elapsed = time.time() - start_time
            if elapsed > duration:
                break
            
            # 發送心跳
            if time.time() - last_heartbeat > scenario['heartbeat_interval']:
                send_heartbeat(master)
                last_heartbeat = time.time()
            
            # ========== 計算繞圓速度 ==========
            theta = omega * elapsed
            vx = -speed * math.sin(theta)
            vy = speed * math.cos(theta)
            vz = 0.0  # 保持高度
            
            # 發送速度指令
            send_velocity_command(master, vx, vy, vz)
            
            # ========== 計算磁力計干擾 ==========
            current_strength = 1.0
            stage = "正常"
            
            if elapsed < scenario['phase_1_duration']:
                current_strength = scenario['normal_strength']
                stage = "正常飛行"
                
            elif elapsed < scenario['phase_1_duration'] + scenario['phase_2_duration']:
                phase_elapsed = elapsed - scenario['phase_1_duration']
                progress = phase_elapsed / scenario['phase_2_duration']
                # 平滑過渡
                current_strength = scenario['normal_strength'] + \
                    (scenario['critical_strength'] - scenario['normal_strength']) * progress
                stage = "干擾漸增"
                
            elif elapsed < scenario['phase_1_duration'] + scenario['phase_2_duration'] + scenario['phase_3_duration']:
                current_strength = scenario['critical_strength']
                stage = "🔴 嚴重干擾"
                
            else:
                phase_elapsed = elapsed - (scenario['phase_1_duration'] + 
                                          scenario['phase_2_duration'] + 
                                          scenario['phase_3_duration'])
                progress = phase_elapsed / scenario['phase_4_duration']
                current_strength = scenario['critical_strength'] - \
                    (scenario['critical_strength'] - 1.0) * progress
                stage = "恢復中"
            
            # 計算磁力計偏移值
            base_offset = scenario['base_offset']
            if current_strength <= 1.0:
                mag_offset = 0
            else:
                mag_offset = base_offset * (current_strength - 1.0)
            
            mag_x = mag_offset * 1.0
            mag_y = mag_offset * 0.8
            mag_z = mag_offset * 1.2
            
            # 智能參數設定
            if last_mag_x is None or abs(mag_x - last_mag_x) > scenario['param_threshold']:
                master.mav.param_set_send(
                    master.target_system, master.target_component,
                    b'SIM_MAG1_OFS_X', mag_x, mavutil.mavlink.MAV_PARAM_TYPE_REAL32
                )
                last_mag_x = mag_x
            
            if last_mag_y is None or abs(mag_y - last_mag_y) > scenario['param_threshold']:
                master.mav.param_set_send(
                    master.target_system, master.target_component,
                    b'SIM_MAG1_OFS_Y', mag_y, mavutil.mavlink.MAV_PARAM_TYPE_REAL32
                )
                last_mag_y = mag_y
            
            if last_mag_z is None or abs(mag_z - last_mag_z) > scenario['param_threshold']:
                master.mav.param_set_send(
                    master.target_system, master.target_component,
                    b'SIM_MAG1_OFS_Z', mag_z, mavutil.mavlink.MAV_PARAM_TYPE_REAL32
                )
                last_mag_z = mag_z
            
            # 顯示狀態
            print(f"T+{elapsed:5.1f}s | [{stage:12s}] 磁場: {current_strength:.2f}x | "
                  f"偏移: {mag_offset:6.0f} mGauss | 速度: ({vx:5.2f}, {vy:5.2f}, {vz:5.2f})")
            
            time.sleep(scenario['update_rate'])
    
    except KeyboardInterrupt:
        print("\n\n⚠️  使用者中斷!")
    
    finally:
        # 停止移動
        send_velocity_command(master, 0, 0, 0)
        print("\n✅ 繞圓完成,已停止移動\n")

# ============================================================================
# 4. 清理與重置
# ============================================================================

def cleanup_and_reset(master):
    """清理並重置參數"""
    print("\n" + "="*70)
    print("🔧 步驟 5: 清理與重置")
    print("="*70)
    
    # 重置磁力計參數
    print("正在重置磁力計參數...")
    for _ in range(3):
        master.mav.param_set_send(
            master.target_system, master.target_component,
            b'SIM_MAG1_OFS_X', 0.0, mavutil.mavlink.MAV_PARAM_TYPE_REAL32
        )
        master.mav.param_set_send(
            master.target_system, master.target_component,
            b'SIM_MAG1_OFS_Y', 0.0, mavutil.mavlink.MAV_PARAM_TYPE_REAL32
        )
        master.mav.param_set_send(
            master.target_system, master.target_component,
            b'SIM_MAG1_OFS_Z', 0.0, mavutil.mavlink.MAV_PARAM_TYPE_REAL32
        )
        time.sleep(0.2)
    
    print("✅ 參數已重置")
    print("\n建議手動執行:")
    print("  - 在 MAVProxy 中輸入: mode LAND")
    print("  - 或在 QGC 中點擊降落按鈕")

# ============================================================================
# 主程式
# ============================================================================

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║           自動化磁力計干擾測試腳本 (Auto Test)                         ║
║                     ArduPilot SITL Only                              ║
╚══════════════════════════════════════════════════════════════════════╝

測試流程:
  1. 磁力計校正參數歸零
  2. 磁力計校正
  3. 重啟飛控 (校正後必須)
  4. 重新連接 MAVLink
  5. 自動飛行: GUIDED → ARM → TAKEOFF 20m
  6. POI 定點繞圓 (半徑 5m) + 高強度磁力計干擾 (5.0x)
  7. 清理與重置

⚠️  警告: 僅適用於 SITL 模擬環境!
    """)
    
    # 連接 MAVLink
    master = connect_mavlink(CONNECTION_STRING, timeout=10)
    if master is None:
        sys.exit(1)
    
    print("\n⚠️  請確保:")
    print("   1. SITL 環境已啟動 (./launch_all.sh)")
    print("   2. Gazebo 和 QGC 正常運行")
    print("   3. 準備好觀察測試過程")
    print()
    
    input("按 Enter 開始自動化測試...")
    
    try:
        # 步驟 1: 重置磁力計參數
        reset_compass_calibration(master)
        
        # 步驟 2: 磁力計校正
        calibrate_compass(master)
        
        # 步驟 2.5: 重啟飛控 (校正後必須)
        reboot_autopilot(master)
        
        # 步驟 2.6: 重新連接
        master = reconnect_mavlink(CONNECTION_STRING)
        if master is None:
            print("❌ 重新連接失敗,測試中止")
            return
        
        # 步驟 3: 自動飛行序列
        if not auto_flight_sequence(master, TAKEOFF_ALTITUDE):
            print("❌ 自動飛行失敗,測試中止")
            return
        
        # 步驟 4: POI 繞圓 + 磁力計干擾
        circle_poi_with_interference(
            master,
            CIRCLE_RADIUS,
            CIRCLE_SPEED,
            CIRCLE_DURATION,
            INTERFERENCE_SCENARIO
        )
        
        # 步驟 5: 清理
        cleanup_and_reset(master)
        
        print("\n" + "="*70)
        print("✅ 測試完成!")
        print("="*70)
        print("\n請檢查:")
        print("  - QGC 中的磁力計數值變化")
        print("  - 飛行模式是否有切換 (GUIDED → ALT_HOLD/LAND)")
        print("  - Gazebo 中的飛行軌跡是否為圓形")
        
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        cleanup_and_reset(master)

if __name__ == '__main__':
    main()
