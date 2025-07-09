import pygame
import math
import numpy as np
from perlin_noise import PerlinNoise
import time

class EmotionalWave:
    """感情に応じて変化する波形を生成・描画するクラス"""
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.noise_gen = PerlinNoise()
        self.t = 150  # 波の高さの基本係数

        self.emotion_color_map = {
            'Angry': (255, 0, 0), 'Disgust': (107, 142, 35), 'Fear': (75, 0, 130),
            'Happy': (255, 255, 0), 'Sad': (0, 0, 139), 'Surprise': (255, 255, 255),
            'Neutral': (173, 216, 230)
        }
        self.emotion_wave_params = {
            'Angry': {'p':1.5, 'a':1.3, 's':1.5, 'n':1.4, 'ws':0.3},
            'Disgust': {'p':1.4, 'a':1.3, 's':0.7, 'n':2.6, 'ws':0.2},
            'Fear': {'p':1.4, 'a':1.0, 's':1.3, 'n':1.3, 'ws':0.3},
            'Happy': {'p':1.0, 'a':1.0, 's':1.3, 'n':0.8, 'ws':0.2},
            'Sad': {'p':0.5, 'a':0.5, 's':0.5, 'n':0.5, 'ws':0.1},
            'Surprise': {'p':1.8, 'a':1.8, 's':2.5, 'n':1.1, 'ws':0.3},
            'Neutral': {'p':1.2, 'a':0.8, 's':1.0, 'n':1.0, 'ws':0.1}
        }
        self.current_emotion = 'Neutral'
        self.last_update_time = time.time()
        self.transition_duration = 2.0
        self.current_params = self._get_params('Neutral')
        self.target_params = self._get_params('Neutral')

    def _get_params(self, emotion):
        p = self.emotion_wave_params.get(emotion, self.emotion_wave_params['Neutral'])
        c = self.emotion_color_map.get(emotion, self.emotion_color_map['Neutral'])
        return {'period':p['p'], 'amplitude':p['a'], 'speed':p['s'], 'noise_scale':p['n'], 'wave_speed':p['ws'], 'color':c}

    def _lerp(self, start, end, t):
        return start + (end - start) * t

    def _lerp_color(self, c1, c2, t):
        return tuple(int(self._lerp(c, d, t)) for c, d in zip(c1, c2))

    def update(self, emotion, frame_count):
        """パラメータと波形データを更新"""
        current_time = time.time()
        if emotion != self.current_emotion:
            self.current_emotion = emotion
            self.last_update_time = current_time
            self.target_params = self._get_params(emotion)

        t = min((current_time - self.last_update_time) / self.transition_duration, 1.0)
        
        # パラメータの線形補間
        for key in self.current_params:
            if key == 'color':
                self.current_params[key] = self._lerp_color(self.current_params[key], self.target_params[key], t)
            else:
                self.current_params[key] = self._lerp(self.current_params[key], self.target_params[key], t)

        # 描画用データの生成
        self.points_list = []
        phase_offset = (frame_count * self.current_params['wave_speed']) % (2 * math.pi)
        x_vals = np.arange(0, self.width, 3)

        for j in range(25): # 25本の線
            seed = j * 0.1 - frame_count * self.current_params['speed'] * 0.02
            noise_input = (seed + x_vals * 0.01).tolist()
            noise = np.array(self.noise_gen(noise_input))
            wave = np.sin((x_vals * self.current_params['period'] * (math.pi / 180)) + phase_offset)
            
            y_vals = (noise * self.t * self.current_params['noise_scale'] - self.t / 2 +
                      self.height / 4 * self.current_params['amplitude'] * wave + self.height / 2)
            
            self.points_list.append(np.column_stack((x_vals, y_vals)).astype(int))

    def draw(self):
        """波形を描画"""
        for points in self.points_list:
            if len(points) > 1:
                pygame.draw.lines(self.screen, self.current_params['color'], False, points, 2)