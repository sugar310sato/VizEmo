import pygame
import random

class Petal:
    """
    一つ一つの紙吹雪（花びら）を管理するクラス
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = random.randint(0, width)
        self.y = random.randint(-height, 0)
        self.size = random.randint(2, 5)
        self.color = (255, 182, 193)  # 薄いピンク
        self.speed_x = random.uniform(-1, 1)
        self.speed_y = random.uniform(2, 4)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.y > self.height or self.x < 0 or self.x > self.width:
            self.x = random.randint(0, self.width)
            self.y = random.randint(-self.height // 2, 0)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)


class Confetti:
    """
    紙吹雪エフェクト全体を管理するクラス
    Happy状態が続くと表示される
    """
    def __init__(self, screen_width, screen_height, num_petals=100):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.num_petals = num_petals
        self.petals = []
        
        self.happy_timer = 0
        self.time_threshold = 1.0  # Happyが1秒続いたら表示
        self.display_duration = 3.0  # 3秒間表示
        self.display_timer = 0
        self.is_displaying = False

    def update(self, is_happy, delta_time):
        """
        状態を更新
        is_happy: 両者がHappyかどうか (True/False)
        delta_time: 前フレームからの経過時間(秒)
        """
        if is_happy:
            self.happy_timer += delta_time
            if self.happy_timer >= self.time_threshold and not self.is_displaying:
                self.is_displaying = True
                self.display_timer = self.display_duration
                self.petals = [Petal(self.screen_width, self.screen_height) for _ in range(self.num_petals)]
        else:
            self.happy_timer = 0

        if self.is_displaying:
            self.display_timer -= delta_time
            if self.display_timer <= 0:
                self.is_displaying = False
        
        if not self.is_displaying and len(self.petals) > 0:
             # 表示終了後、徐々に消えていく
            if random.random() < 0.1:
                self.petals.pop()
                
        for petal in self.petals:
            petal.update()
            
    def draw(self, screen):
        for petal in self.petals:
            petal.draw(screen)