import torch
import cv2
import numpy as np
import logging
from torchvision import transforms
from ultralytics import YOLO
from config import YOLO_FACE_MODEL_PATH

# YOLOv8のログ出力を抑制
logging.getLogger('ultralytics').setLevel(logging.ERROR)
torch.set_num_threads(4)

class EmotionDetector:
    """
    YOLOv8で顔を検出し、CNNモデルで表情を認識するクラス
    """
    def __init__(self, device=None):
        self.emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
        self.device = device or (torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu'))
        print(f"EmotionDetector using device: {self.device}")

        # YOLOv8 顔検出モデル
        self.yolo_model = YOLO(YOLO_FACE_MODEL_PATH)
        self.yolo_model.model.to(self.device).eval()
        self.yolo_model.model.conf = 0.5  # 信頼度の閾値
        self.yolo_model.model.iou = 0.45  # IoUの閾値

        # 画像の前処理
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Grayscale(),
            transforms.Resize((48, 48)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])

    def detect(self, frame: np.ndarray, model: torch.nn.Module) -> tuple[str, np.ndarray]:
        """
        フレームから最も確信度の高い感情を検出する
        """
        if frame is None:
            return "Neutral", frame

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        results = self.yolo_model(frame, verbose=False)

        detected_emotion = "Neutral"
        max_confidence = 0

        if results:
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                    try:
                        roi_gray = gray[y1:y2, x1:x2]
                        if roi_gray.size == 0:
                            continue

                        roi_tensor = self.transform(roi_gray).unsqueeze(0).to(self.device)
                        model.to(self.device).eval()

                        with torch.no_grad():
                            outputs = model(roi_tensor)
                            probabilities = torch.softmax(outputs, dim=1)
                            max_prob, predicted = torch.max(probabilities, 1)

                        prob_value = max_prob.item()
                        if prob_value > max_confidence:
                            max_confidence = prob_value
                            detected_emotion = self.emotion_labels[predicted.item()]
                        
                        # 検出結果を描画（デバッグ用）
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                        cv2.putText(frame, f"{detected_emotion}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

                    except Exception as e:
                        print(f"Error processing face region: {e}")
                        continue

        return detected_emotion, frame