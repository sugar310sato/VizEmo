import sounddevice as sd
import cv2

def check_audio_devices():
    """
    利用可能なオーディオデバイス（マイクとスピーカー）の一覧を表示します。
    """
    print("--- Audio Devices ---")
    try:
        devices = sd.query_devices()
        if not devices:
            print("オーディオデバイスが見つかりませんでした。")
            return

        print("ID | Device Name (Input Channels, Output Channels)")
        print("-" * 60)
        for i, device in enumerate(devices):
            # デバイス名にShift_JISでないと表示できない文字が含まれる場合のエラー対策
            try:
                device_name = device['name']
            except UnicodeDecodeError:
                device_name = device['name'].encode('shift_jis').decode('utf-8', 'ignore')

            print(f"{i:2d} | {device_name} ({device['max_input_channels']}, {device['max_output_channels']})")
        print("-" * 60)
        print("\nマイクとして使用するには、'Input Channels'が1以上のデバイスのIDをconfig.pyに設定してください。")

    except Exception as e:
        print(f"オーディオデバイスの取得中にエラーが発生しました: {e}")
        print("sounddeviceライブラリが正しくインストールされているか確認してください。")

def check_video_devices():
    """
    利用可能なビデオデバイス（カメラ）の一覧を試行して表示します。
    """
    print("\n--- Video Devices ---")
    print("利用可能なカメラIDを検索しています...（数秒かかる場合があります）")
    index = 0
    available_cameras = []
    # 一般的にカメラは10台も接続されていないため、0から9まで試行する
    while index < 10:
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available_cameras.append(index)
            cap.release()
        index += 1

    if available_cameras:
        print(f"利用可能なカメラのID: {available_cameras}")
        print("これらのIDをconfig.pyのCAMERA1_ID, CAMERA2_ID, GAZE_CAMERA_IDに設定してください。")
    else:
        print("利用可能なカメラが見つかりませんでした。")
        print("カメラがPCに正しく接続され、ドライバがインストールされているか確認してください。")
    print("-" * 60)


if __name__ == "__main__":
    check_audio_devices()
    check_video_devices()