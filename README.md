# VizEmo
このプロジェクトは、カメラとマイクからの入力（表情、顔の向き、音量など）をリアルタイムで解析し、インタラクティブなビジュアルエフェクトを生成するアプリケーションです。

## 主な機能

  - **リアルタイム感情認識**: `YOLOv8n-face`による顔検出と、カスタム`CNN`モデルによる7種類の表情分類（怒り, 嫌悪, 恐怖, 喜び, 悲しみ, 驚き, 普通）を行います。
  - **顔の向き・視線検出**: `dlib`ライブラリを用いて、顔の上下左右の向きや視線を検出します。
  - **音量検出**: マイクからの入力音量をリアルタイムで測定します。
  - **ダイナミックなビジュアル**: 認識された感情や音量に応じて、複数のビジュアルエフェクトが動的に変化します。
      - パーティクルの噴出
      - 感情の波
      - 紙吹雪
      - 群衆シミュレーション（Boids）
  - **データ記録と分析**: 実行中の各種センサーデータをCSVファイルに記録し、プログラム終了時にExcelとグラフで分析レポートを自動生成します。
  - **デバッグモード**: 各センサーのカメラ映像をリアルタイムで表示し、認識状況を直接確認できます。

## 必要なライブラリ

本プロジェクトは以下の主要なライブラリに依存しています。

  - `pygame`
  - `opencv-python`
  - `dlib`
  - `torch` & `torchvision`
  - `sounddevice`
  - `numpy` & `pandas`
  - `ultralytics`
  - `perlin-noise`

## セットアップ方法

1.  **リポジトリのクローン**:

    ```bash
    git clone https://github.com/your-username/interactive-projection.git
    cd interactive-projection
    ```

2.  **仮想環境の作成と有効化（推奨）**:

    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **依存ライブラリのインストール**:

    ```bash
    pip install -r requirements.txt
    ```

4.  **モデルファイルの配置**:
    `assets` ディレクトリに、以下の学習済みモデルファイルを配置してください。

      - `shape_predictor_68_face_landmarks.dat`: [dlib公式サイト](http://dlib.net/files/)などからダウンロード。
      - `emotion_cnn1.pth`: `train_model.py`で学習させた、または別途用意した感情認識モデル。
      - `yolov8n-face.pt`: `YOLOv8`の顔検出モデル。

## 実行方法

1.  **設定の確認**:
    `config.py` を開き、ご自身のPC環境に合わせて `CAMERA_ID` や `MIC_ID` などのデバイス設定、`NUM_SENSORS` や `ACTIVE_VISUALS` などの機能設定が正しく行われているか確認してください。

2.  **メインスクリプトの実行**:
    ターミナルで以下のコマンドを実行します。

    ```bash
    python main.py
    ```

3.  **プログラムの終了**:

      - Pygameウィンドウを選択した状態で `q` キーを押すと、プログラムが安全に終了します。
      - プログラム終了後、分析レポートが `data/` ディレクトリに保存されます。
