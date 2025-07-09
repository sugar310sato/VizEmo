import pygame
import time
import threading
from config import *

# モジュールのインポート
from input_processing.sensor import Sensor
from input_processing.gaze_tracker import GazeTracker
from analysis.data_logger import DataLogger
# ビジュアルエフェクト
from visuals.confetti import Confetti
from visuals.particle_fountain import ParticleFountain
from visuals.boids import Boids
from visuals.emotional_wave import EmotionalWave
from visuals.gaze_particles import GazeParticles


def main():
    """メイン関数"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("インタラクティブ・プロジェクション")
    clock = pygame.time.Clock()

    # --- モジュールの初期化 ---
    print("各モジュールを初期化しています...")
    # 入力処理
    sensor1 = Sensor(camera_id=CAMERA1_ID, mic_id=MIC1_ID)
    sensor2 = None
    # --- 設定に応じてsensor2を初期化 ---
    if NUM_SENSORS == 2:
        print("センサー2を初期化します...")
        sensor2 = Sensor(camera_id=CAMERA2_ID, mic_id=MIC2_ID)

    if USE_GAZE_TRACKING:
        gaze_tracker = GazeTracker(camera_id=GAZE_CAMERA_ID)

    # ビジュアルエフェクト
    visual_effects = []
    if 'confetti' in ACTIVE_VISUALS: visual_effects.append(Confetti(SCREEN_WIDTH, SCREEN_HEIGHT))
    if 'fountain' in ACTIVE_VISUALS:
        visual_effects.append(ParticleFountain(screen, position='left'))
        visual_effects.append(ParticleFountain(screen, position='right'))
    if 'boids' in ACTIVE_VISUALS: visual_effects.append(Boids(screen, shape='triangle'))
    if 'wave' in ACTIVE_VISUALS: visual_effects.append(EmotionalWave(screen))
    if 'gaze' in ACTIVE_VISUALS and USE_GAZE_TRACKING: visual_effects.append(GazeParticles(screen))
    
    # データロガー
    logger = DataLogger(LOG_FILE_PATH)
    logger.start_logging()

    # --- スレッドの開始 ---
    print("センシング用のスレッドを開始します...")
    sensor1.start()
    if sensor2:
        sensor2.start()
    if USE_GAZE_TRACKING: 
        gaze_tracker.start()
    
    print(f"{CAMERA_WAIT_TIME}秒待機して、センサーの準備をします...")
    time.sleep(CAMERA_WAIT_TIME)
    print("ログ記録と描画を開始します。")

    # --- メインループ ---
    running = True
    start_time = time.time()
    frame_count = 0

    while running:
        if time.time() - start_time > DURATION: running = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                running = False

        # --- データ取得 ---
        data1 = sensor1.get_all_data()
        data2 = sensor2.get_all_data() if sensor2 else data1
        gaze_direction = gaze_tracker.get_current_gaze() if USE_GAZE_TRACKING else "center"
        gaze_direction = "center"

        # --- データ記録 ---
        logger.log(frame_count, data1, data1, gaze_direction)

        # --- 描画処理 ---
        screen.fill((0, 0, 0))
        """
        # ビジュアルの更新と描画
        for effect in visual_effects:
            # 各エフェクトが必要とするデータを渡す
            if isinstance(effect, Confetti):
                effect.update(data1['emotion'] == 'Happy' and data2['emotion'] == 'Happy', clock.get_time() / 1000.0)
            elif isinstance(effect, ParticleFountain):
                # 左右を判定
                if effect.position == 'left':
                    effect.update(data1['emotion'], data1['volume'])
                else:
                    effect.update(data2['emotion'], data2['volume'])
            elif isinstance(effect, Boids):
                effect.update(data1['emotion']) # 例として片方の感情に連動
            elif isinstance(effect, EmotionalWave):
                effect.update(data1['emotion'], frame_count)
            elif isinstance(effect, GazeParticles):
                effect.update(gaze_direction)
        """
        for effect in visual_effects:
            # 各エフェクトが必要とするデータを渡す
            if isinstance(effect, Confetti):
                # センサーが1つの場合はdata1のHappyだけで判定
                is_happy = data1['emotion'] == 'Happy'
                if sensor2: # センサーが2つあれば両方のHappyを考慮
                    is_happy = is_happy and (data2['emotion'] == 'Happy')
                effect.update(is_happy, clock.get_time() / 1000.0)
            elif isinstance(effect, ParticleFountain):
                if effect.position == 'left':
                    effect.update(data1['emotion'], data1['volume'])
                else:
                    # sensor2がなければdata1のデータを使う
                    effect.update(data2['emotion'], data2['volume'])
            elif isinstance(effect, Boids):
                effect.update(data1['emotion']) # 例として片方の感情に連動
            elif isinstance(effect, EmotionalWave):
                effect.update(data1['emotion'], frame_count)
            elif isinstance(effect, GazeParticles):
                effect.update(gaze_direction)


            effect.draw()

        pygame.display.flip()
        frame_count += 1
        clock.tick(FPS)

    # --- 終了処理 ---
    print("終了処理を開始します...")
    sensor1.stop()
    if sensor2:
        sensor2.stop()    
    
    if USE_GAZE_TRACKING: 
        gaze_tracker.stop()
        
    logger.save_report()
    pygame.quit()
    print("プログラムを終了しました。")

if __name__ == "__main__":
    main()