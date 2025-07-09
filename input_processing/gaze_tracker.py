import cv2
import dlib
import numpy as np
import threading
import time
from config import SHAPE_PREDICTOR_PATH, SHOW_DEBUG_WINDOWS

class GazeTracker:
    """
    dlibを使用して視線方向を追跡するクラス
    """
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(SHAPE_PREDICTOR_PATH)
        
        self.current_gaze_direction = "Center"
        self.last_frame = None
        self.running = False
        self.thread = None
        self.debug_window_name = f"Gaze Tracker {self.camera_id} - Debug"


    def start(self):
        """視線追跡を別スレッドで開始"""
        self.running = True
        self.thread = threading.Thread(target=self._tracking_thread, daemon=True)
        self.thread.start()
        print("GazeTracker started.")

    def stop(self):
        """視線追跡を停止"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("GazeTracker stopped.")

    def get_current_gaze(self):
        return self.current_gaze_direction

    def _tracking_thread(self):
        cap = cv2.VideoCapture(self.camera_id)
        if not cap.isOpened():
            print(f"GazeTracker: Camera {self.camera_id} could not be opened.")
            return

        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector(gray)

            if len(faces) > 0:
                face = faces[0] # 最初の顔を対象とする
                landmarks = self.predictor(gray, face)
                
                # 右目の処理
                self.current_gaze_direction = self._detect_gaze_from_eye(landmarks, frame, range(36, 42))
            else:
                self.current_gaze_direction = "Center"

            # デバッグ用にテキストを描画
            cv2.putText(frame, self.current_gaze_direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            self.last_frame = frame.copy()
            
            if SHOW_DEBUG_WINDOWS:
                cv2.imshow(self.debug_window_name, self.last_frame)
                cv2.waitKey(1) 
        
        cap.release()
        if SHOW_DEBUG_WINDOWS:
                    try:
                        cv2.destroyWindow(self.debug_window_name)
                    except cv2.error:
                        pass
                    
    def _detect_gaze_from_eye(self, landmarks, frame, eye_points):
        # 目の領域を抽出
        region = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in eye_points], np.int32)
        x, y, w, h = cv2.boundingRect(region)
        
        eye_frame = frame[y:y+h, x:x+w]
        if eye_frame.size == 0:
            return "Blink"

        # 瞳孔検出（簡略版）
        eye_gray = cv2.cvtColor(eye_frame, cv2.COLOR_BGR2GRAY)
        eye_gray = cv2.GaussianBlur(eye_gray, (7, 7), 0)
        _, threshold = cv2.threshold(eye_gray, 40, 255, cv2.THRESH_BINARY_INV)
        
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=lambda c: cv2.contourArea(c), reverse=True)

        if len(contours) > 0:
            cnt = contours[0]
            (px, py, pw, ph) = cv2.boundingRect(cnt)
            pupil_center = (px + pw // 2, py + ph // 2)
            
            # 視線方向の判定
            eye_center_x = w // 2
            dx = pupil_center[0] - eye_center_x
            
            if dx > 8:
                return "Left" # カメラから見て
            elif dx < -8:
                return "Right" # カメラから見て
            else:
                return "Center"
        return "Blink"