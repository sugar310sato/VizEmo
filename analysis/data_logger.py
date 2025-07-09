import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
import os
import time

class DataLogger:
    """
    センサーデータを記録し、終了時にレポートを生成するクラス
    """
    def __init__(self, log_file_path):
        self.log_file = log_file_path
        self.data_dir = os.path.dirname(log_file_path)
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def start_logging(self):
        """ログファイルのヘッダーを書き込む"""
        with open(self.log_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                "Timestamp", "Frame Count",
                "Cam1_Emotion", "Cam1_FaceDirection", "Cam1_Volume",
                "Cam2_Emotion", "Cam2_FaceDirection", "Cam2_Volume",
                "Gaze_Direction"
            ])

    def log(self, frame_count, data1, data2, gaze_direction):
        """1フレーム分のデータをCSVファイルに追記"""
        with open(self.log_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                time.strftime('%Y-%m-%d %H:%M:%S'), frame_count,
                data1['emotion'], data1['face_direction'], data1['volume'],
                data2['emotion'], data2['face_direction'], data2['volume'],
                gaze_direction
            ])

    def save_report(self):
        """ログファイルを読み込み、Excelとグラフでレポートを生成"""
        print("分析レポートを生成しています...")
        try:
            df = pd.read_csv(self.log_file)
        except pd.errors.EmptyDataError:
            print("ログファイルが空です。レポートは生成されません。")
            return
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_excel = os.path.join(self.data_dir, f"{timestamp}_report.xlsx")

        # データ集計
        emotions1 = df["Cam1_Emotion"].value_counts()
        emotions2 = df["Cam2_Emotion"].value_counts()
        emotions_avg = (emotions1.add(emotions2, fill_value=0) / 2)

        faces1 = df["Cam1_FaceDirection"].value_counts()
        faces2 = df["Cam2_FaceDirection"].value_counts()
        faces_avg = (faces1.add(faces2, fill_value=0) / 2)

        # Excelに書き出し
        with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
            emotions_avg.to_frame(name="Average").to_excel(writer, sheet_name='Summary', startrow=1)
            faces_avg.to_frame(name="Average").to_excel(writer, sheet_name='Summary', startrow=len(emotions_avg)+4)
            df.describe().to_excel(writer, sheet_name='RawDataSummary')
            
            workbook = writer.book
            worksheet = writer.sheets['Summary']
            worksheet.write(0, 0, "Emotion Average Count")
            worksheet.write(len(emotions_avg)+3, 0, "Face Direction Average Count")
        
        # グラフ生成
        self._plot_bar_chart(
            {"Camera 1": emotions1, "Camera 2": emotions2},
            "Emotion Distribution",
            os.path.join(self.data_dir, f"{timestamp}_emotion_bar.png"),
            ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
        )
        self._plot_bar_chart(
            {"Camera 1": faces1, "Camera 2": faces2},
            "Face Direction Distribution",
            os.path.join(self.data_dir, f"{timestamp}_facedir_bar.png"),
            ['center', 'left', 'right', 'up', 'down']
        )
        print(f"レポートが {self.data_dir} に保存されました。")

    def _plot_bar_chart(self, data_dict, title, filename, labels):
        x = np.arange(len(labels))
        width = 0.35
        fig, ax = plt.subplots(figsize=(12, 7))
        
        rects1 = ax.bar(x - width/2, [data_dict["Camera 1"].get(lbl, 0) for lbl in labels], width, label='Camera 1', color='#666666')
        rects2 = ax.bar(x + width/2, [data_dict["Camera 2"].get(lbl, 0) for lbl in labels], width, label='Camera 2', color='#AAAAAA')

        ax.set_ylabel('Frame Count')
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.legend()
        fig.tight_layout()
        plt.savefig(filename)
        plt.close(fig)