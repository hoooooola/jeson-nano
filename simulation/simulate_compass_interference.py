#!/usr/bin/env python3
"""
動態磁力計干擾模擬腳本 (Dynamic Compass Interference Simulator)

模擬真實飛行中磁力計逐漸受到干擾的情況
基於實際案例: 磁場強度從 0.75 逐漸上升到 2.0

使用方法:
1. 在 SITL 運行時,於另一個終端執行此腳本
2. 腳本會透過 MAVLink 動態調整 SIM_MAG 參數
"""

import time
import sys
from pymavlink import mavutil

# ============================================================================
# 配置參數
# ============================================================================

# MAVLink 連接
MAVLINK_CONNECTION = 'udp:127.0.0.1:14550'  # SITL 預設端口

# 干擾場景配置 (基於您的實際案例) - 已優化
SCENARIO = {
    'name': '馬達磁場逐漸增強 (優化版)',
    'description': '模擬馬達電流干擾逐漸增強,導致磁場總強度從 0.75 上升到 2.0',
    
    # 時間軸 (秒) - 增加間隔,避免通訊阻塞
    'phase_1_duration': 15,   # 正常階段 (0-15秒) - 增加
    'phase_2_duration': 30,   # 干擾漸增 (15-45秒) - 增加
    'phase_3_duration': 10,   # 嚴重干擾 (45-55秒) - 增加
    'phase_4_duration': 15,   # 恢復階段 (55-70秒) - 增加
    
    # 磁場強度目標 (相對於地球磁場)
    'normal_strength': 0.75,      # 正常強度
    'warning_strength': 1.2,      # 開始警告
    'critical_strength': 2.0,     # 嚴重干擾
    
    # 地球磁場強度 (台灣地區)
    'earth_field_mgauss': 45000,  # 45,000 mGauss
    
    # 優化參數
    'update_interval': 2.0,       # 參數更新間隔 (秒) - 降低頻率
    'param_set_delay': 0.1,       # 每個參數設定後的延遲 (秒)
}

# ============================================================================
# 輔助函數
# ============================================================================

def connect_mavlink():
    """連接到 MAVLink"""
    print(f"正在連接到 {MAVLINK_CONNECTION}...")
    try:
        mav = mavutil.mavlink_connection(MAVLINK_CONNECTION)
        mav.wait_heartbeat()
        print(f"✅ 已連接到系統 {mav.target_system}, 組件 {mav.target_component}")
        return mav
    except Exception as e:
        print(f"❌ 連接失敗: {e}")
        sys.exit(1)

def set_param(mav, param_name, param_value, delay=0.1):
    """設定參數 (優化版,添加延遲)"""
    try:
        mav.mav.param_set_send(
            mav.target_system,
            mav.target_component,
            param_name.encode('utf-8'),
            param_value,
            mavutil.mavlink.MAV_PARAM_TYPE_REAL32
        )
        print(f"  設定 {param_name} = {param_value:.2f}")
        time.sleep(delay)  # 添加延遲,避免通訊阻塞
    except Exception as e:
        print(f"  ⚠️  設定 {param_name} 失敗: {e}")

def calculate_mag_mot_from_strength(target_strength, earth_field):
    """
    根據目標磁場強度計算 SIM_MAG_MOT 值
    
    公式: 磁場總強度 = sqrt(earth_field^2 + (mag_mot * current)^2)
    假設油門 50% 時電流約 10A
    """
    if target_strength <= 1.0:
        return 0  # 正常範圍不需要干擾
    
    # 計算需要的額外磁場強度
    extra_field = earth_field * (target_strength - 1.0)
    
    # 假設平均電流 10A
    avg_current = 10.0
    mag_mot = extra_field / avg_current
    
    return mag_mot

def smooth_transition(start_val, end_val, progress):
    """平滑過渡函數 (使用 ease-in-out)"""
    # 使用三次函數實現平滑過渡
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

def run_interference_scenario(mav, scenario):
    """執行干擾場景"""
    
    print("\n" + "="*70)
    print(f"🎯 場景: {scenario['name']}")
    print(f"📝 說明: {scenario['description']}")
    print("="*70 + "\n")
    
    earth_field = scenario['earth_field_mgauss']
    
    # ========================================================================
    # Phase 1: 正常階段
    # ========================================================================
    print(f"\n📍 Phase 1: 正常飛行 (0-{scenario['phase_1_duration']}秒)")
    print(f"   目標磁場強度: {scenario['normal_strength']:.2f}x")
    
    set_param(mav, 'SIM_MAG_MOT_X', 0)
    set_param(mav, 'SIM_MAG_MOT_Y', 0)
    set_param(mav, 'SIM_MAG_MOT_Z', 0)
    set_param(mav, 'SIM_MAG1_SCALING', scenario['normal_strength'])
    
    print(f"   等待 {scenario['phase_1_duration']} 秒...")
    time.sleep(scenario['phase_1_duration'])
    
    # ========================================================================
    # Phase 2: 干擾漸增 (優化版 - 減少更新頻率)
    # ========================================================================
    print(f"\n⚠️  Phase 2: 干擾逐漸增強 ({scenario['phase_1_duration']}-{scenario['phase_1_duration'] + scenario['phase_2_duration']}秒)")
    print(f"   磁場強度: {scenario['normal_strength']:.2f}x → {scenario['critical_strength']:.2f}x")
    print(f"   ⏱️  更新間隔: {scenario['update_interval']}秒 (避免通訊阻塞)")
    
    duration = scenario['phase_2_duration']
    # 減少步驟數,避免過於頻繁的參數更新
    steps = int(duration / scenario['update_interval'])  # 根據間隔計算步驟數
    interval = duration / steps
    
    for i in range(steps + 1):
        progress = i / steps
        
        # 計算當前磁場強度
        current_strength = smooth_transition(
            scenario['normal_strength'],
            scenario['critical_strength'],
            progress
        )
        
        # 計算對應的 MAG_MOT 值
        mag_mot = calculate_mag_mot_from_strength(current_strength, earth_field)
        
        # 設定參數 (使用優化後的延遲)
        set_param(mav, 'SIM_MAG_MOT_X', mag_mot, scenario['param_set_delay'])
        set_param(mav, 'SIM_MAG_MOT_Y', mag_mot * 0.8, scenario['param_set_delay'])
        set_param(mav, 'SIM_MAG_MOT_Z', mag_mot * 1.2, scenario['param_set_delay'])
        
        print(f"   [{i+1}/{steps+1}] 磁場強度: {current_strength:.2f}x, MAG_MOT: {mag_mot:.0f} mGauss/A")
        
        time.sleep(interval)
    
    # ========================================================================
    # Phase 3: 嚴重干擾維持
    # ========================================================================
    print(f"\n🔴 Phase 3: 嚴重干擾 ({scenario['phase_1_duration'] + scenario['phase_2_duration']}-{scenario['phase_1_duration'] + scenario['phase_2_duration'] + scenario['phase_3_duration']}秒)")
    print(f"   磁場強度維持在: {scenario['critical_strength']:.2f}x")
    print(f"   預期: Compass Unhealthy 警告,可能切換到姿態模式")
    
    time.sleep(scenario['phase_3_duration'])
    
    # ========================================================================
    # Phase 4: 恢復正常 (優化版)
    # ========================================================================
    print(f"\n✅ Phase 4: 干擾消除,恢復正常")
    
    duration = scenario['phase_4_duration']
    steps = int(duration / scenario['update_interval'])  # 根據間隔計算步驟數
    interval = duration / steps
    
    for i in range(steps + 1):
        progress = i / steps
        
        current_strength = smooth_transition(
            scenario['critical_strength'],
            1.0,  # 恢復到正常
            progress
        )
        
        mag_mot = calculate_mag_mot_from_strength(current_strength, earth_field)
        
        set_param(mav, 'SIM_MAG_MOT_X', mag_mot, scenario['param_set_delay'])
        set_param(mav, 'SIM_MAG_MOT_Y', mag_mot * 0.8, scenario['param_set_delay'])
        set_param(mav, 'SIM_MAG_MOT_Z', mag_mot * 1.2, scenario['param_set_delay'])
        
        print(f"   [{i+1}/{steps+1}] 磁場強度: {current_strength:.2f}x")
        
        time.sleep(interval)
    
    print("\n" + "="*70)
    print("✅ 場景模擬完成!")
    print("="*70 + "\n")

# ============================================================================
# 主程式
# ============================================================================

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║          動態磁力計干擾模擬器 (Dynamic Compass Interference)          ║
║                    基於真實飛行案例設計                                ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # 連接 MAVLink
    mav = connect_mavlink()
    
    # 等待用戶準備
    print("\n⚠️  請確保:")
    print("   1. SITL 已經啟動並解鎖")
    print("   2. 無人機已經起飛到安全高度 (建議 10 公尺)")
    print("   3. 已切換到 LOITER 或 AUTO 模式")
    print()
    
    input("按 Enter 開始模擬...")
    
    # 執行場景
    try:
        run_interference_scenario(mav, SCENARIO)
    except KeyboardInterrupt:
        print("\n\n⚠️  用戶中斷,正在恢復正常參數...")
        set_param(mav, 'SIM_MAG_MOT_X', 0)
        set_param(mav, 'SIM_MAG_MOT_Y', 0)
        set_param(mav, 'SIM_MAG_MOT_Z', 0)
        set_param(mav, 'SIM_MAG1_SCALING', 1.0)
        print("✅ 已恢復")
    
    print("\n建議後續動作:")
    print("  - 檢查 QGC 中的磁力計狀態")
    print("  - 查看日誌中的 EKF 警告")
    print("  - 練習切換到 STABILIZE 模式")

if __name__ == '__main__':
    main()
