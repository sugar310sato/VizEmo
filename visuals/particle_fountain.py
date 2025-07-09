import pygame
import random
import math
import numpy as np

class Particle:
    """消滅時のパーティクル"""
    def __init__(self, x, y, speed, angle, color):
        self.x = x
        self.y = y
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.color = color
        self.lifetime = 30

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1

    def draw(self, screen):
        if self.lifetime > 0:
            alpha = max(0, int(255 * (self.lifetime / 30)))
            temp_surface = pygame.Surface((5, 5), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, (*self.color, alpha), (2, 2), 2)
            screen.blit(temp_surface, (self.x, self.y))

    def is_dead(self):
        return self.lifetime <= 0

class Ball:
    """噴出するボール"""
    def __init__(self, x, y, angle, emotion_params, speed):
        self.x, self.y = x, y
        self.params = emotion_params
        self.speed = self.params['speed'] * (speed / 10.0) # 初期速度を反映
        self.speed_x = self.speed * math.cos(angle)
        self.speed_y = self.speed * math.sin(angle)
        self.lifetime = random.randint(50, 150)
        
    def update(self):
        self.speed_y += self.params['gravity']
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifetime -= 1

    def draw(self, screen):
        pygame.draw.circle(screen, self.params['color'], (int(self.x), int(self.y)), int(self.params['size']))

    def is_dead(self):
        return self.lifetime <= 0

class ParticleFountain:
    """
    音量と感情に連動してパーティクルが噴出するエフェクト
    """
    def __init__(self, screen, position='left'):
        self.screen = screen
        self.position = position
        self.items = [] # ボールとパーティクルを格納
        self.current_emotion = 'Neutral'
        self.base_size = random.randint(7, 12)
        
        self.EMOTION_PARAMS = {
            'Neutral': {'color': (173, 216, 230), 'size': self.base_size, 'speed': 7, 'gravity': 0.0},
            'Angry': {'color': (255, 10, 10), 'size': self.base_size * 1.2, 'speed': 10, 'gravity': 0.0},
            'Fear': {'color': (144, 58, 178), 'size': self.base_size * 0.7, 'speed': 6, 'gravity': 0.01},
            'Disgust': {'color': (101, 139, 34), 'size': self.base_size * 0.8, 'speed': 10, 'gravity': 0.01},
            'Happy': {'color': (255, 255, 108), 'size': self.base_size * 1.2, 'speed': 8, 'gravity': 0.0},
            'Sad': {'color': (100, 100, 255), 'size': self.base_size * 0.6, 'speed': 5, 'gravity': 0.05},
            'Surprise': {'color': (255, 255, 255), 'size': self.base_size * 1.7, 'speed': 13, 'gravity': 0.0}
        }

        if self.position == 'left':
            self.start_x = 0
            self.angle_range = (-np.pi / 4, np.pi / 4)
        else: # right
            self.start_x = self.screen.get_width()
            self.angle_range = (3 * np.pi / 4, 5 * np.pi / 4)
        self.start_y = self.screen.get_height() // 2

    def update(self, emotion, volume):
        self.current_emotion = emotion
        self._create_balls(volume)

        for item in self.items[:]:
            item.update()
            if item.is_dead():
                if isinstance(item, Ball): # ボールが死んだらパーティクル生成
                    for _ in range(10):
                        p_speed = random.uniform(2, 5)
                        p_angle = random.uniform(0, 2 * np.pi)
                        self.items.append(Particle(item.x, item.y, p_speed, p_angle, item.params['color']))
                self.items.remove(item)

    def draw(self):
        for item in self.items:
            item.draw(self.screen)

    def _create_balls(self, volume):
        num_balls = int(volume / 5) # 音量に応じて生成数を調整
        if num_balls > 0:
            emotion_params = self.EMOTION_PARAMS.get(self.current_emotion, self.EMOTION_PARAMS['Neutral'])
            for _ in range(num_balls):
                angle = random.uniform(*self.angle_range)
                speed = random.uniform(5, 10) + volume / 10
                self.items.append(Ball(self.start_x, self.start_y, angle, emotion_params, speed))