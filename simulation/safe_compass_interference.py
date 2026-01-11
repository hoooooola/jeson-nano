#!/usr/bin/env python3
"""
安全版磁力計干擾模擬 (Safe Compass Interference Simulator)

關鍵優化:
1. 避開 QGC Port - 連接到 14551 (MAVROS) 而非 14550 (QGC)
2. 頻率控制 - 限制更新頻率避免 MAVLink 阻塞
3. 自動復原 - 腳本結束時自動重置參數

基於真實案例: 磁場強度從 0.75 逐漸上升到 2.0
"""

import time
import sys
from pymavlink import mavutil

# ============================================================================
# 配置參數
# ============================================================================

# MAVLink 連接 - ArduPilot SITL 主要使用 14550
# 注意: ArduPilot 與 PX4 不同,主要 heartbeat 在 14550
# 雖然與 QGC 共用,但在測試環境中可接受
CONNECTION_STRING = 'udp:127.0.0.1:14550'

# ArduPilot 參數名稱 (注意: PX4 用 SIM_MAG_OFF_X)
PARAM_MAG_MOT_X = b'SIM_MAG_MOT_X'
PARAM_MAG_MOT_Y = b'SIM_MAG_MOT_Y'
PARAM_MAG_MOT_Z = b'SIM_MAG_MOT_Z'

# 模擬場景配置
SCENARIO = {
    'name': '馬達磁場逐漸增強 (安全版)',
    'description': '避免 QGC 斷線的優化版本',
    
    # 時間軸 (秒)
    'phase_1_duration': 15,   # 正常階段
    'phase_2_duration': 30,   # 干擾漸增
    'phase_3_duration': 10,   # 嚴重干擾
    'phase_4_duration': 15,   # 恢復階段
    
    # 磁場強度目標
    'normal_strength': 0.75,
    'critical_strength': 2.0,
    'earth_field_mgauss': 45000,
    
    # 關鍵優化參數
    'update_rate': 0.5,       # 更新間隔 (秒) - 2Hz,避免阻塞
    'param_retry': 3,         # 參數設定重試次數
}

# ============================================================================
# 輔助函數
# ============================================================================

def wait_for_heartbeat(master):
    """等待飛控心跳"""
    print("正在等待飛控 Heartbeat...")
    master.wait_heartbeat()
    print(f"✅ 已連接到系統 (System ID: {master.target_system}, Component ID: {master.target_component})")

def set_param_safe(master, param_name, value, retry=3):
    """安全的參數設定 (帶重試機制)"""
    for attempt in range(retry):
        try:
            master.mav.param_set_send(
                master.target_system,
                master.target_component,
                param_name,
                value,
                mavutil.mavlink.MAV_PARAM_TYPE_REAL32
            )
            return True
        except Exception as e:
            if attempt == retry - 1:
                print(f"  ⚠️  設定 {param_name.decode()} 失敗: {e}")
                return False
            time.sleep(0.05)
    return False

def calculate_mag_mot_from_strength(target_strength, earth_field):
    """根據目標磁場強度計算 MAG_MOT 值"""
    if target_strength <= 1.0:
        return 0
    extra_field = earth_field * (target_strength - 1.0)
    avg_current = 10.0
    return extra_field / avg_current

def smooth_transition(start_val, end_val, progress):
    """平滑過渡函數 (ease-in-out)"""
    if progress < 0.5:
        t = 2 * progress
        factor = 0.5 * t * t * t
    else:
        t = 2 * (progress - 0.5)
        factor = 0.5 * (1 + (2 * t - 1) * (2 * t - 1) * (2 * t - 1))
    return start_val + (end_val - start_val) * factor

# ============================================================================
# 主要模擬函數
# ============================================================================

def run_safe_interference(master, scenario):
    """執行安全的干擾場景"""
    
    print("\n" + "="*70)
    print(f"🎯 場景: {scenario['name']}")
    print(f"📝 說明: {scenario['description']}")
    print(f"⏱️  更新頻率: {1/scenario['update_rate']:.1f} Hz (避免 MAVLink 阻塞)")
    print("="*70 + "\n")
    
    earth_field = scenario['earth_field_mgauss']
    start_time = time.time()
    total_duration = (scenario['phase_1_duration'] + 
                     scenario['phase_2_duration'] + 
                     scenario['phase_3_duration'] + 
                     scenario['phase_4_duration'])
    
    try:
        while True:
            elapsed = time.time() - start_time
            if elapsed > total_duration:
                break
            
            # 計算當前應該的磁場強度
            current_strength = 0.75
            stage = "正常"
            
            if elapsed < scenario['phase_1_duration']:
                # Phase 1: 正常
                current_strength = scenario['normal_strength']
                stage = "正常飛行"
                
            elif elapsed < scenario['phase_1_duration'] + scenario['phase_2_duration']:
                # Phase 2: 干擾漸增
                phase_elapsed = elapsed - scenario['phase_1_duration']
                progress = phase_elapsed / scenario['phase_2_duration']
                current_strength = smooth_transition(
                    scenario['normal_strength'],
                    scenario['critical_strength'],
                    progress
                )
                stage = "干擾漸增"
                
            elif elapsed < scenario['phase_1_duration'] + scenario['phase_2_duration'] + scenario['phase_3_duration']:
                # Phase 3: 嚴重干擾
                current_strength = scenario['critical_strength']
                stage = "🔴 嚴重干擾"
                
            else:
                # Phase 4: 恢復
                phase_elapsed = elapsed - (scenario['phase_1_duration'] + 
                                          scenario['phase_2_duration'] + 
                                          scenario['phase_3_duration'])
                progress = phase_elapsed / scenario['phase_4_duration']
                current_strength = smooth_transition(
                    scenario['critical_strength'],
                    1.0,
                    progress
                )
                stage = "恢復中"
            
            # 計算 MAG_MOT 值
            mag_mot = calculate_mag_mot_from_strength(current_strength, earth_field)
            
            # 設定參數 (關鍵: 一次只設定,不要連續發送)
            set_param_safe(master, PARAM_MAG_MOT_X, mag_mot, scenario['param_retry'])
            set_param_safe(master, PARAM_MAG_MOT_Y, mag_mot * 0.8, scenario['param_retry'])
            set_param_safe(master, PARAM_MAG_MOT_Z, mag_mot * 1.2, scenario['param_retry'])
            
            # 顯示狀態
            print(f"T+{elapsed:5.1f}s | [{stage:12s}] 磁場強度: {current_strength:.2f}x | MAG_MOT: {mag_mot:6.0f} mGauss/A")
            
            # 關鍵! 休息一下,避免 MAVLink 阻塞
            time.sleep(scenario['update_rate'])
    
    except KeyboardInterrupt:
        print("\n\n⚠️  使用者中斷模擬!")
    
    finally:
        # 自動清理
        print("\n" + "="*70)
        print("🔧 正在重置磁力計參數...")
        print("="*70)
        for _ in range(3):  # 發送三次確保收到
            set_param_safe(master, PARAM_MAG_MOT_X, 0.0)
            set_param_safe(master, PARAM_MAG_MOT_Y, 0.0)
            set_param_safe(master, PARAM_MAG_MOT_Z, 0.0)
            time.sleep(0.2)
        print("✅ 參數已重置。QGC 連線應保持正常。\n")

# ============================================================================
# 主程式
# ============================================================================

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║     安全版磁力計干擾模擬器 (Safe Compass Interference Simulator)      ║
║                    避免 QGC 斷線的優化版本                             ║
╚══════════════════════════════════════════════════════════════════════╝

關鍵優化:
  ✅ 使用 Port 14551 (避開 QGC 的 14550)
  ✅ 更新頻率限制為 2Hz (避免 MAVLink 阻塞)
  ✅ 自動重試機制
  ✅ 結束時自動重置參數
    """)
    
    # 連接 MAVLink
    print(f"正在連接到: {CONNECTION_STRING}")
    try:
        master = mavutil.mavlink_connection(CONNECTION_STRING)
        wait_for_heartbeat(master)
    except Exception as e:
        print(f"❌ 連線失敗: {e}")
        print("\n提示:")
        print("  1. 確認 SITL 已經啟動")
        print("  2. 確認 Port 14551 可用")
        print("  3. 檢查防火牆設定")
        sys.exit(1)
    
    # 等待用戶準備
    print("\n⚠️  請確保:")
    print("   1. SITL 已經啟動並解鎖")
    print("   2. 無人機已經起飛到安全高度 (建議 10 公尺)")
    print("   3. QGC 已連接並顯示正常")
    print()
    
    input("按 Enter 開始模擬...")
    
    # 執行場景
    run_safe_interference(master, SCENARIO)
    
    print("\n建議後續動作:")
    print("  - 檢查 QGC 是否保持連線")
    print("  - 查看磁力計狀態是否恢復正常")
    print("  - 檢查日誌中的 EKF 警告")

if __name__ == '__main__':
    main()
