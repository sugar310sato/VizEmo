import cv2
import dlib
import torch
import sounddevice as sd
import numpy as np
import threading
import time
from config import SHOW_DEBUG_WINDOWS, SHAPE_PREDICTOR_PATH, EMOTION_MODEL_PATH
from .emotion_detector import EmotionDetector
from train_model import EmotionCNN 

class Sensor:
    """
    1台のカメラとマイクからの情報（感情、顔向き、音量）を処理するクラス
    """
    def __init__(self, camera_id=0, mic_id=1):
        # デバイスID
        self.camera_id = camera_id
        self.mic_id = mic_id

        # 状態変数
        self.current_emotion = "Neutral"
        self.current_face_direction = "center"
        self.current_volume = 0
        self.last_processed_frame = None
        self.running = False

        # モデルと検出器の初期化
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.emotion_model = self._load_emotion_model()
        self.emotion_detector = EmotionDetector(device=self.device)
        self.face_detector = dlib.get_frontal_face_detector()
        self.landmark_predictor = dlib.shape_predictor(SHAPE_PREDICTOR_PATH)
        self.debug_window_name = f"Sensor {self.camera_id} - Debug"

        # スレッド
        self.capture_thread = None
        self.audio_thread = None

    def _load_emotion_model(self):
        try:
            model = EmotionCNN()
            model.load_state_dict(torch.load(EMOTION_MODEL_PATH, map_location=self.device))
            model.to(self.device)
            model.eval()
            print(f"Sensor {self.camera_id}: Emotion model loaded successfully.")
            return model
        except Exception as e:
            print(f"Sensor {self.camera_id}: Failed to load emotion model - {e}")
            return None

    def start(self):
        """センサーの処理を別スレッドで開始"""
        self.running = True
        self.capture_thread = threading.Thread(target=self._run_capture, daemon=True)
        self.audio_thread = threading.Thread(target=self._run_audio, daemon=True)
        self.capture_thread.start()
        self.audio_thread.start()
        print(f"Sensor (Cam: {self.camera_id}, Mic: {self.mic_id}) started.")

    def stop(self):
        """センサーを停止"""
        self.running = False
        if self.capture_thread: self.capture_thread.join()
        if self.audio_thread: self.audio_thread.join() # Audio stream stops when flag is false
        print(f"Sensor (Cam: {self.camera_id}, Mic: {self.mic_id}) stopped.")

    def _run_capture(self):
        cap = cv2.VideoCapture(self.camera_id)
        if not cap.isOpened():
            print(f"Error: Could not open camera {self.camera_id}.")
            return
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue
            
            # 感情認識
            if self.emotion_model:
                self.current_emotion, _ = self.emotion_detector.detect(frame.copy(), self.emotion_model)
            
            # 顔向き認識
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector(gray)
            if len(faces) > 0:
                largest_face = max(faces, key=lambda rect: rect.width() * rect.height())
                landmarks = self.landmark_predictor(gray, largest_face)
                self.current_face_direction = self._get_face_orientation(landmarks, largest_face, frame.shape[1], frame.shape[0])
                # 顔の矩形を描画
                x, y, w, h = largest_face.left(), largest_face.top(), largest_face.width(), largest_face.height()
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            

            info_text_emo = f"Emotion: {self.current_emotion}"
            info_text_face = f"Face: {self.current_face_direction}"
            info_text_vol = f"Volume: {self.current_volume:.2f}"
            cv2.putText(frame, info_text_emo, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, info_text_face, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, info_text_vol, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            if SHOW_DEBUG_WINDOWS:
                cv2.imshow(self.debug_window_name, frame)
                cv2.waitKey(1)

        
        cap.release()
        if SHOW_DEBUG_WINDOWS:
            try:
                cv2.destroyWindow(self.debug_window_name)
            except cv2.error:
                pass
    
    def _run_audio(self):
        def audio_callback(indata, frames, time, status):
            if status:
                print(status)
            self.current_volume = np.linalg.norm(indata) * 10
        
        try:
            with sd.InputStream(device=self.mic_id, callback=audio_callback):
                print(f"Audio stream started for Mic ID: {self.mic_id}")
                while self.running:
                    sd.sleep(100)
        except Exception as e:
            print(f"Error with audio stream on Mic ID {self.mic_id}: {e}")

    def _get_face_orientation(self, landmarks, face_rect, frame_width, frame_height):
        # 顔のバウンディングボックスの座標
        x1 = face_rect.left()
        y1 = face_rect.top()
        x2 = face_rect.right()
        y2 = face_rect.bottom()

        # 顔の幅と高さ
        face_width = x2 - x1
        face_height = y2 - y1

        # 画面に対する顔の大きさの割合
        face_area_ratio = (face_width * face_height) / (frame_width * frame_height)

        # 顔のランドマークの座標
        nose_tip = landmarks.part(30)  # 鼻先
        chin = landmarks.part(8)       # 顎
        left_cheek = landmarks.part(1)  # 左頬
        right_cheek = landmarks.part(15) # 右頬

        # 差分を計算
        dx = nose_tip.x - (left_cheek.x + right_cheek.x) // 2
        dy = nose_tip.y - chin.y

        # 向き判定の閾値を顔の大きさに応じてスケーリング
        dx_threshold = 15 * face_area_ratio * 10
        dy_threshold_up = -110 * face_area_ratio * 13
        dy_threshold_down = -68 * face_area_ratio * 18

        direction = "center"

        # 向きの判定
        if dx < -dx_threshold and dy < dy_threshold_up:
            direction = "up-right"
        elif dx > dx_threshold and dy < dy_threshold_up:
            direction = "up-left"
        elif dx < -dx_threshold and dy > dy_threshold_down:
            direction = "down-right"
        elif dx > dx_threshold and dy > dy_threshold_down:
            direction = "down-left"
        elif dx < -dx_threshold:
            direction = "right"
        elif dx > dx_threshold:
            direction = "left"
        elif dy < dy_threshold_up:
            direction = "up"
        elif dy > dy_threshold_down:
            direction = "down"

        return direction

    def get_all_data(self):
        """現在のセンサーデータを辞書で返す"""
        return {
            "emotion": self.current_emotion,
            "face_direction": self.current_face_direction,
            "volume": self.current_volume,
        }