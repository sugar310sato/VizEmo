import pygame
import random

class Particle:
    """パーティクル一つ一つを管理するクラス"""
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.uniform(-2, 2), random.uniform(-2, 2))
        self.gravity = pygame.Vector2(0, 0.09)
        self.lifespan = random.randint(50, 155)
        self.size = random.randint(3, 5)

    def update(self):
        self.lifespan -= 1
        self.vel += self.gravity
        self.pos += self.vel

    def is_dead(self):
        return self.lifespan <= 0

    def draw(self, screen):
        if self.lifespan > 0:
            alpha = max(10, self.lifespan)
            color = (255, 255, 245, alpha) # 少し黄色がかった白
            temp_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, color, (self.size, self.size), self.size)
            screen.blit(temp_surface, self.pos - pygame.Vector2(self.size, self.size))

class ParticleSystem:
    """パーティクル群全体を管理するクラス"""
    def __init__(self, num_particles):
        self.particles = []
        self.num_particles = num_particles
        self.emitter_pos = pygame.Vector2(0, 0)

    def set_emitter(self, x, y):
        # 目標位置に滑らかに移動
        self.emitter_pos.x += (x - self.emitter_pos.x) * 0.1
        self.emitter_pos.y += (y - self.emitter_pos.y) * 0.1

    def update(self):
        # 死んだパーティクルを新しい位置で再生成
        for i in range(len(self.particles)):
            if self.particles[i].is_dead():
                self.particles[i] = Particle(self.emitter_pos.x, self.emitter_pos.y)
        # 不足分を追加
        while len(self.particles) < self.num_particles:
            self.particles.append(Particle(self.emitter_pos.x, self.emitter_pos.y))
        
        for p in self.particles:
            p.update()
    
    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)

class GazeParticles:
    """視線に追従するパーティクルエフェクト"""
    def __init__(self, screen, num_particles=3000):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.center_x, self.center_y = self.width // 2, self.height // 2
        self.particle_system = ParticleSystem(num_particles)
        
        # 視線方向の安定性チェッカー
        self.previous_direction = "center"
        self.current_streak = 0
        self.last_valid_direction = "center"

        # 方向と座標のマッピング
        self.movement_map = {
            "up": (self.center_x, self.center_y - 180), "down": (self.center_x, self.center_y + 190),
            "left": (self.center_x - 400, self.center_y + 180), "right": (self.center_x + 400, self.center_y + 180),
            "up-right": (self.center_x + 400, self.center_y - 200), "up-left": (self.center_x - 400, self.center_y - 200),
            "down-right": (self.center_x + 400, self.center_y + 200), "down-left": (self.center_x - 400, self.center_y + 200),
        }

    def _update_direction_stability(self, new_direction):
        if new_direction == self.previous_direction:
            self.current_streak += 1
        else:
            self.previous_direction = new_direction
            self.current_streak = 1

        if new_direction != "center":
            self.last_valid_direction = new_direction

        return self.current_streak >= 3 # 3フレーム連続で安定

    def update(self, gaze_direction):
        is_stable = self._update_direction_stability(gaze_direction)
        target_pos = None

        if is_stable:
            if gaze_direction != "center":
                target_pos = self.movement_map.get(gaze_direction)
            else: # "center"だが安定している場合、最後に見ていた位置を使う
                target_pos = self.movement_map.get(self.last_valid_direction)
        
        if target_pos:
            self.particle_system.set_emitter(target_pos[0], target_pos[1])

        self.particle_system.update()

    def draw(self):
        self.particle_system.draw(self.screen)