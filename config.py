import os

# --- 基本設定 ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 920
FPS = 30
DURATION = 180  # プログラムの実行時間 (秒)
CAMERA_WAIT_TIME = 10 # カメラやマイクが安定するまでの待機時間 (秒)

# --- 機能の有効化 ---
SHOW_DEBUG_WINDOWS = True
NUM_SENSORS = 1
USE_GAZE_TRACKING = False 
ACTIVE_VISUALS = ['fountain' ] # 使用するビジュアル: 'confetti', 'fountain', 'boids', 'wave', 'gaze'

# --- デバイスID ---
# NUM_SENSORS = 1 の場合、CAMERA1_ID と MIC1_ID のみが使用されます
CAMERA1_ID = 0
CAMERA2_ID = 0
GAZE_CAMERA_ID = 0
# NUM_SENSORS = 2 の場合にのみ、以下のIDが使用されます
MIC1_ID = 1  
MIC2_ID = 5

# --- ファイルパス設定 ---
ASSETS_DIR = "assets"
DATA_DIR = "data"

# モデルファイルのパス
SHAPE_PREDICTOR_PATH = os.path.join(ASSETS_DIR, "shape_predictor_68_face_landmarks.dat")
EMOTION_MODEL_PATH = os.path.join(ASSETS_DIR, "emotion_cnn1.pth")
YOLO_FACE_MODEL_PATH = os.path.join(ASSETS_DIR, "yolov8n-face.pt")

# ログファイルのパス
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
LOG_FILE_PATH = os.path.join(DATA_DIR, "mapping_log.csv")
