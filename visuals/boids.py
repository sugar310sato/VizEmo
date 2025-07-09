import pygame
import math
import random

class Boid:
    """群れを構成する個々のオブジェクト"""
    def __init__(self, x, y, width, height, shape):
        self.pos = pygame.Vector2(x, y)
        angle = random.uniform(0, 2 * math.pi)
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle))
        self.acc = pygame.Vector2(0, 0)
        self.width, self.height = width, height
        self.shape = shape
        self.max_speed = 4
        self.max_force = 0.1
        self.size = random.randint(15, 25)
        self.rotation_angle = 0

    def update(self):
        self.vel += self.acc
        self.vel.scale_to_length(min(self.vel.length(), self.max_speed))
        self.pos += self.vel
        self.acc *= 0

        # 壁でのループ
        if self.pos.x > self.width: self.pos.x = 0
        if self.pos.x < 0: self.pos.x = self.width
        if self.pos.y > self.height: self.pos.y = 0
        if self.pos.y < 0: self.pos.y = self.height

    def apply_force(self, force):
        self.acc += force

    def flock(self, boids, params):
        separation = self.separate(boids, params['repulsion_radius'])
        alignment = self.align(boids, params['attraction_radius'])
        cohesion = self.cohere(boids, params['attraction_radius'])
        
        separation *= params['repulsion_force']
        alignment *= params['attraction_force']
        cohesion *= params['attraction_force']
        
        self.apply_force(separation)
        self.apply_force(alignment)
        self.apply_force(cohesion)

    def seek(self, target):
        desired = target - self.pos
        desired.scale_to_length(self.max_speed)
        steer = desired - self.vel
        if steer.length() > self.max_force:
            steer.scale_to_length(self.max_force)
        return steer

    def separate(self, boids, radius):
        steer = pygame.Vector2(0, 0)
        total = 0
        for other in boids:
            d = self.pos.distance_to(other.pos)
            if 0 < d < radius:
                diff = self.pos - other.pos
                diff /= d # 距離で割る
                steer += diff
                total += 1
        if total > 0:
            steer /= total
            if steer.length() > 0:
                steer.scale_to_length(self.max_speed)
            steer -= self.vel
            if steer.length() > self.max_force:
                steer.scale_to_length(self.max_force)
        return steer

    def align(self, boids, radius):
        avg_vel = pygame.Vector2(0, 0)
        total = 0
        for other in boids:
            d = self.pos.distance_to(other.pos)
            if 0 < d < radius:
                avg_vel += other.vel
                total += 1
        if total > 0:
            avg_vel /= total
            if avg_vel.length() > 0:
                avg_vel.scale_to_length(self.max_speed)
            steer = avg_vel - self.vel
            if steer.length() > self.max_force:
                steer.scale_to_length(self.max_force)
            return steer
        return pygame.Vector2(0, 0)

    def cohere(self, boids, radius):
        avg_pos = pygame.Vector2(0, 0)
        total = 0
        for other in boids:
            d = self.pos.distance_to(other.pos)
            if 0 < d < radius:
                avg_pos += other.pos
                total += 1
        if total > 0:
            avg_pos /= total
            return self.seek(avg_pos)
        return pygame.Vector2(0, 0)

    def draw(self, screen, color):
        if self.shape == 'circle':
            pygame.draw.circle(screen, color, (int(self.pos.x), int(self.pos.y)), int(self.size / 2))
        elif self.shape == 'triangle':
            self.rotation_angle = self.vel.angle_to(pygame.Vector2(1, 0))
            points = [
                pygame.Vector2(self.size, 0).rotate(-self.rotation_angle),
                pygame.Vector2(-self.size/2, self.size/2).rotate(-self.rotation_angle),
                pygame.Vector2(-self.size/2, -self.size/2).rotate(-self.rotation_angle),
            ]
            points = [(p + self.pos) for p in points]
            pygame.draw.polygon(screen, color, points)

class Boids:
    """感情に連動する群衆シミュレーション"""
    def __init__(self, screen, shape='circle', num_boids=50):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.shape = shape
        self.boids = [Boid(random.uniform(0, self.width), random.uniform(0, self.height), self.width, self.height, self.shape) for _ in range(num_boids)]
        self.current_emotion = 'Neutral'
        self.target_params = None
        self.current_params = None
        self.GROUP_PARAMS = {
            'Neutral': {'color':(173, 216, 230), 'attraction_radius': 100, 'repulsion_radius': 25, 'attraction_force': 0.02, 'repulsion_force': 0.15},
            'Angry':   {'color':(240, 0, 0),   'attraction_radius': 80,  'repulsion_radius': 40, 'attraction_force': 0.1,  'repulsion_force': 0.3},
            'Fear':    {'color':(144, 58, 178),'attraction_radius': 60,  'repulsion_radius': 15, 'attraction_force': 0.04, 'repulsion_force': 0.25},
            'Happy':   {'color':(255, 255, 108),'attraction_radius': 130, 'repulsion_radius': 20, 'attraction_force': 0.05,  'repulsion_force': 0.1},
            'Sad':     {'color':(0, 108, 153), 'attraction_radius': 90,  'repulsion_radius': 30, 'attraction_force': 0.01, 'repulsion_force': 0.05},
            'Surprise':{'color':(255, 255, 255),'attraction_radius': 150, 'repulsion_radius': 50, 'attraction_force': 0.15, 'repulsion_force': 0.2}
        }
        self.GROUP_PARAMS['Disgust'] = self.GROUP_PARAMS['Fear'] # DisgustはFearと同じ挙動
        self.current_params = self.GROUP_PARAMS['Neutral'].copy()
        
    def lerp_color(self, c1, c2, t):
        return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))
    
    def lerp(self, v1, v2, t):
        return v1 + (v2 - v1) * t

    def update(self, emotion):
        if emotion != self.current_emotion:
            self.current_emotion = emotion
            self.target_params = self.GROUP_PARAMS.get(emotion, self.GROUP_PARAMS['Neutral'])
        
        # パラメータを滑らかに変化させる
        if self.target_params:
            t = 0.05 # 補間係数
            self.current_params['color'] = self.lerp_color(self.current_params['color'], self.target_params['color'], t)
            for key in ['attraction_radius', 'repulsion_radius', 'attraction_force', 'repulsion_force']:
                self.current_params[key] = self.lerp(self.current_params[key], self.target_params[key], t)

        for boid in self.boids:
            boid.flock(self.boids, self.current_params)
            boid.update()

    def draw(self):
        color = self.current_params['color']
        for boid in self.boids:
            boid.draw(self.screen, color)