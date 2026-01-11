import sys
import argparse  # 命令列解析

from jetson_inference import detectNet  # 建立物體偵測神經網路
from jetson_utils import videoSource, videoOutput, Log  # 建立視訊來源 (Camera/Video) 與輸出 (Display/File/Stream)


# 解析命令列參數 (Parse the command line)
parser = argparse.ArgumentParser(description="使用物體偵測 DNN 模型在即時攝影機串流中定位物體。", 
                                 formatter_class=argparse.RawTextHelpFormatter, 
                                 epilog=detectNet.Usage() + videoSource.Usage() + videoOutput.Usage() + Log.Usage())

parser.add_argument("input", type=str, default="", nargs='?', help="輸入串流的 URI (例如: /dev/video0, input.mp4)")
parser.add_argument("output", type=str, default="", nargs='?', help="輸出串流的 URI (例如: display://0, output.mp4, webrtc://@:8554/output)")
parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="要載入的預訓練模型 (預設: ssd-mobilenet-v2)")
parser.add_argument("--overlay", type=str, default="box,labels,conf", help="偵測結果疊加選項 (例如 --overlay=box,labels,conf)\n有效組合包含: 'box', 'labels', 'conf', 'none'")
parser.add_argument("--threshold", type=float, default=0.5, help="最小偵測閾值 (信心度大於此值才顯示)") 

# 舉例參數如何設置 ./detectnet.py --network=ssd-mobilenet-v2 --overlay=box,labels,conf --threshold=0.5 --input=csi://0 --output=display://0
try:
	args = parser.parse_known_args()[0]
except:
	print("")
	parser.print_help()
	sys.exit(0)

# 建立視訊來源 (Camera/Video) 與輸出 (Display/File/Stream)
# input = videoSource("csi://0")  # 如果是 CSI 相機
# input = videoSource("/dev/video0") # 如果是 USB 相機
input = videoSource(args.input, argv=sys.argv)
output = videoOutput(args.output, argv=sys.argv)
	
# 載入物體偵測神經網路 (Object Detection Network)
# 這裡會下載或載入模型，第一次執行會花幾分鐘進行 TensorRT 最佳化
net = detectNet(args.network, sys.argv, args.threshold)

# 備註: 若要載入自定義模型 (ONNX)，可以使用類似以下的寫法:
# net = detectNet(model="model/ssd-mobilenet.onnx", labels="model/labels.txt", 
#                 input_blob="input_0", output_cvg="scores", output_bbox="boxes", 
#                 threshold=args.threshold)

# 主迴圈：持續處理每個影格，直到結束串流或使用者退出
while True:
    # 1. 擷取下一個影像 (Capture the next image)
    # img 是一個 CUDA 記憶體中的影像物件
    img = input.Capture()

    if img is None: # 若沒抓到影像 (timeout) 則繼續
        continue  
        
    # 2. 執行物體偵測 (Detect objects)
    # net.Detect() 會執行推論，並自動把結果 (框框、標籤) 畫在 img 上
    # overlay 參數決定要畫什麼 (box=框, labels=名稱, conf=信心度)
    detections = net.Detect(img, overlay=args.overlay)

    # 3. 列印偵測結果 (Print the detections)
    # detections 是經過解析後的物件列表
    print("detected {:d} objects in image".format(len(detections)))

    for detection in detections:
        print(detection) # 印出每個物件的 ID, 類別, 信心度, 座標

    # 4. 顯示影像 (Render the image)
    # 將畫好框框的結果輸出到螢幕或網路串流
    output.Render(img)

    # 5. 更新視窗標題 (Update the title bar)
    # 顯示目前使用的網路名稱與 FPS (每秒偵測張數)
    output.SetStatus("{:s} | Network {:.0f} FPS".format(args.network, net.GetNetworkFPS()))

    # 6. 印出效能分析 (Print performance info)
    # 顯示網路每一層的執行時間 (Profiling)
    net.PrintProfilerTimes()

    # 若輸入或輸出結束 (EOS)，則跳出迴圈
    if not input.IsStreaming() or not output.IsStreaming():
        break
