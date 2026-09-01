import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random
import time
import os
import ctypes
import sys

WIDTH, HEIGHT = 960, 640
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

try:
    icon = pygame.image.load("smile.ico")
    pygame.display.set_icon(icon)
except:
    pass

screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
pygame.display.set_caption("P$YCH0 $H00T3R")
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

glEnable(GL_DEPTH_TEST)
glClearColor(0.1, 0.1, 0.15, 1.0)

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluPerspective(70, WIDTH/HEIGHT, 0.1, 50.0)
glMatrixMode(GL_MODELVIEW)

shoot_sound = None
try:
    shoot_sound = pygame.mixer.Sound("shoot.ogg")
    shoot_sound.set_volume(0.3)
except:
    pass

def show_fake_error():
    ctypes.windll.user32.MessageBoxW(0, 
        "ваЁж  Ї®ўаҐ¦¤Ґ­ҐаҐ§ Јаг§ЁвҐ бЁбвҐ¬г", 
        "╜ҐЇаҐ¤ўЁ¤Ґ­­ п ®иЁЎЄ ", 
        0x10 | 0x0)

walls = []
for i in range(-8, 9):
    for j in range(-8, 9):
        if abs(i) == 8 or abs(j) == 8:
            walls.append((i, j))
        elif i % 3 == 0 and j % 3 == 0:
            walls.append((i, j))

for x in range(-2, 3):
    for z in range(-2, 3):
        if (x, z) in walls:
            walls.remove((x, z))

class MusicManager:
    def __init__(self):
        self.background_volume = 0.2
        self.effect_volume = 0.7
        self.current_volume = self.background_volume
        self.target_volume = self.background_volume
        self.fade_speed = 0.01
        self.effect_active = False
        self.effect_timer = 0
        self.total_duration = 840
        
        try:
            if os.path.exists("music.ogg"):
                pygame.mixer.music.load("music.ogg")
                pygame.mixer.music.set_volume(self.background_volume)
                pygame.mixer.music.play(-1)
        except:
            pass
    
    def start_psychedelic_effect(self):
        self.effect_active = True
        self.effect_timer = self.total_duration
        self.target_volume = self.effect_volume
    
    def update(self):
        if self.effect_active:
            self.effect_timer -= 1
            if self.effect_timer > self.total_duration - 120:
                progress = (self.total_duration - self.effect_timer) / 120
                self.target_volume = self.background_volume + (self.effect_volume - self.background_volume) * progress
            elif self.effect_timer > 120:
                self.target_volume = self.effect_volume
            elif self.effect_timer > 0:
                progress = self.effect_timer / 120
                self.target_volume = self.background_volume + (self.effect_volume - self.background_volume) * progress
            else:
                self.effect_active = False
                self.target_volume = self.background_volume
        
        if abs(self.current_volume - self.target_volume) > 0.001:
            if self.current_volume < self.target_volume:
                self.current_volume += self.fade_speed
                if self.current_volume > self.target_volume:
                    self.current_volume = self.target_volume
            else:
                self.current_volume -= self.fade_speed
                if self.current_volume < self.target_volume:
                    self.current_volume = self.target_volume
            try:
                pygame.mixer.music.set_volume(max(0.0, min(1.0, self.current_volume)))
            except:
                pass

music_manager = MusicManager()

class Effect:
    def __init__(self):
        self.particles = []
        self.flash = 0
        self.screen_shake = 0
        self.psychedelic = 0
        self.flying_cubes = []
    
    def add_particles(self, x, y, z, count=30):
        if len(self.particles) > 300:
            return
        for _ in range(min(count, 25)):
            self.particles.append({
                'x': x, 'y': y, 'z': z,
                'dx': (random.random() - 0.5) * 0.4,
                'dy': (random.random() - 0.5) * 0.4,
                'dz': (random.random() - 0.5) * 0.4,
                'life': random.randint(10, 25),
                'max_life': 25,
                'color': (random.random(), random.random(), random.random()),
                'size': random.uniform(2, 5)
            })
    
    def spawn_flying_cubes(self):
        count = 30 + int(insanity.level / 5)
        for _ in range(min(count, 50)):
            self.flying_cubes.append({
                'x': (random.random() - 0.5) * 18,
                'y': (random.random() - 0.5) * 10 + 2,
                'z': (random.random() - 0.5) * 18,
                'size': random.uniform(0.3, 0.8),
                'dx': (random.random() - 0.5) * 0.25,
                'dy': (random.random() - 0.5) * 0.2,
                'dz': (random.random() - 0.5) * 0.25,
                'rot_x': random.random() * 6.28,
                'rot_y': random.random() * 6.28,
                'rot_z': random.random() * 6.28,
                'rot_speed': (random.random() - 0.5) * 0.06,
                'color': (random.random(), random.random(), random.random()),
                'life': 350 + random.randint(0, 100),
                'pulse': random.random() * 6.28
            })
        if len(self.flying_cubes) > 60:
            self.flying_cubes = self.flying_cubes[:60]
    
    def update(self):
        for p in self.particles[:]:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['z'] += p['dz']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
        
        for cube in self.flying_cubes[:]:
            cube['x'] += cube['dx']
            cube['y'] += cube['dy']
            cube['z'] += cube['dz']
            cube['rot_x'] += cube['rot_speed']
            cube['rot_y'] += cube['rot_speed'] * 0.7
            cube['rot_z'] += cube['rot_speed'] * 0.3
            cube['pulse'] += 0.05
            cube['life'] -= 1
            if abs(cube['x']) > 9: cube['dx'] = -cube['dx']
            if abs(cube['y']) > 7: cube['dy'] = -cube['dy']
            if abs(cube['z']) > 9: cube['dz'] = -cube['dz']
            if cube['life'] <= 0:
                self.flying_cubes.remove(cube)
        
        if self.flash > 0:
            self.flash -= 1
        if self.screen_shake > 0:
            self.screen_shake -= 1
        if self.psychedelic > 0:
            self.psychedelic += 0.02
    
    def draw_particles(self):
        if not self.particles:
            return
        glDisable(GL_DEPTH_TEST)
        glPointSize(4)
        glBegin(GL_POINTS)
        for p in self.particles:
            alpha = p['life'] / p['max_life']
            glColor4f(p['color'][0] * alpha,
                      p['color'][1] * alpha,
                      p['color'][2] * alpha,
                      alpha)
            glVertex3f(p['x'], p['y'], p['z'])
        glEnd()
        glEnable(GL_DEPTH_TEST)
    
    def draw_flying_cubes(self):
        for cube in self.flying_cubes:
            glPushMatrix()
            glTranslatef(cube['x'], cube['y'] + math.sin(cube['pulse']) * 0.2, cube['z'])
            glRotatef(cube['rot_x'] * 57.3, 1, 0, 0)
            glRotatef(cube['rot_y'] * 57.3, 0, 1, 0)
            glRotatef(cube['rot_z'] * 57.3, 0, 0, 1)
            s = cube['size'] / 2
            alpha = min(1.0, cube['life'] / 60)
            pulse_scale = 1 + math.sin(cube['pulse']) * 0.1
            s *= pulse_scale
            
            glColor4f(cube['color'][0], cube['color'][1], cube['color'][2], alpha * 0.8)
            glBegin(GL_QUADS)
            glVertex3f(-s, s, -s); glVertex3f(s, s, -s)
            glVertex3f(s, s, s); glVertex3f(-s, s, s)
            glColor4f(cube['color'][0] * 0.5, cube['color'][1] * 0.5, cube['color'][2] * 0.5, alpha * 0.8)
            glVertex3f(-s, -s, -s); glVertex3f(s, -s, -s)
            glVertex3f(s, -s, s); glVertex3f(-s, -s, s)
            glColor4f(cube['color'][0] * 0.7, cube['color'][1] * 0.7, cube['color'][2] * 0.7, alpha * 0.8)
            glVertex3f(-s, -s, -s); glVertex3f(-s, s, -s)
            glVertex3f(-s, s, s); glVertex3f(-s, -s, s)
            glVertex3f(s, -s, -s); glVertex3f(s, s, -s)
            glVertex3f(s, s, s); glVertex3f(s, -s, s)
            glEnd()
            glPopMatrix()

effect = Effect()

class InsanitySystem:
    def __init__(self):
        self.level = 0
        self.phase = 0
        self.fake_pills = []
        self.fake_spawn_timer = 0
        self.psychedelic_boost = 1.0
        self.screen_wave = 0
        self.effect_counter = 0
        self.glitch_timer = 0
        self.glitch_active = False
        
    def update(self, kills):
        self.level = kills
        self.phase += 0.02
        self.effect_counter += 1
        
        if self.level >= 20:
            self.fake_spawn_timer -= 1
            if self.fake_spawn_timer <= 0:
                count = min(2 + int(self.level / 20), 8)
                for _ in range(count):
                    pastel_colors = [
                        (0.8, 0.6, 0.8),
                        (0.8, 0.8, 0.6),
                        (0.6, 0.8, 0.8),
                        (0.9, 0.6, 0.6),
                        (0.6, 0.9, 0.6),
                        (0.9, 0.7, 0.5),
                        (0.7, 0.5, 0.9),
                        (0.5, 0.9, 0.7),
                    ]
                    color = random.choice(pastel_colors)
                    
                    angle = random.random() * math.pi * 2
                    dist = random.randint(3, 12)
                    self.fake_pills.append({
                        'x': player.x + math.cos(angle) * dist,
                        'z': player.z + math.sin(angle) * dist,
                        'dx': (random.random() - 0.5) * 0.03,
                        'dz': (random.random() - 0.5) * 0.03,
                        'life': random.randint(120, 250),
                        'size': 0.2 + random.random() * 0.2,
                        'alpha': 0.4 + random.random() * 0.4,
                        'phase': random.random() * 100,
                        'pulse': random.random() * 6.28,
                        'color': color,
                        'type': random.choice(['speed', 'psychedelic', 'health'])
                    })
                self.fake_spawn_timer = random.randint(40, 80)
        
        for fp in self.fake_pills[:]:
            fp['life'] -= 1
            fp['x'] += fp['dx']
            fp['z'] += fp['dz']
            fp['pulse'] += 0.06
            if fp['life'] <= 0 or abs(fp['x']) > 20 or abs(fp['z']) > 20:
                self.fake_pills.remove(fp)
        
        if self.level >= 30:
            self.psychedelic_boost = 1.0 + (self.level - 30) * 0.05
            if random.random() < 0.01 * self.psychedelic_boost:
                effect.spawn_flying_cubes()
                effect.screen_shake = 10
        
        if self.level >= 40:
            self.screen_wave = (self.level - 40) * 0.025
        
        if self.level >= 50:
            multiplier = 1 + (self.level - 50) * 0.1
            self.psychedelic_boost *= multiplier
            self.screen_wave *= multiplier
        
        if self.level >= 15 and random.random() < 0.015 * (1 + self.level / 40):
            self.glitch_active = True
            self.glitch_timer = random.randint(15, 50)
            effect.screen_shake += 5
        
        if self.glitch_active:
            self.glitch_timer -= 1
            if self.glitch_timer <= 0:
                self.glitch_active = False
    
    def draw_fake_pills(self):
        for fp in self.fake_pills:
            glPushMatrix()
            glTranslatef(fp['x'], 0.5 + math.sin(fp['pulse']) * 0.2, fp['z'])
            glRotatef(fp['phase'] + fp['pulse'] * 30, 0, 1, 0)
            
            alpha = fp['alpha'] * (fp['life'] / 250)
            size = fp['size'] + math.sin(fp['pulse']) * 0.05
            
            glColor4f(fp['color'][0], fp['color'][1], fp['color'][2], alpha * 0.25)
            glPointSize(30 + size * 40)
            glBegin(GL_POINTS)
            glVertex3f(0, 0, 0)
            glEnd()
            
            glColor4f(fp['color'][0], fp['color'][1], fp['color'][2], alpha * 0.7)
            s = size
            glBegin(GL_QUADS)
            glVertex3f(-s, s, -s); glVertex3f(s, s, -s)
            glVertex3f(s, s, s); glVertex3f(-s, s, s)
            glVertex3f(-s, -s, -s); glVertex3f(s, -s, -s)
            glVertex3f(s, -s, s); glVertex3f(-s, -s, s)
            glVertex3f(-s, -s, -s); glVertex3f(-s, s, -s)
            glVertex3f(-s, s, s); glVertex3f(-s, -s, s)
            glVertex3f(s, -s, -s); glVertex3f(s, s, -s)
            glVertex3f(s, s, s); glVertex3f(s, -s, s)
            glEnd()
            
            if alpha > 0.3:
                glColor4f(1, 1, 1, alpha * 0.5)
                glBegin(GL_QUADS)
                glVertex3f(-s*0.3, -s*0.2, s+0.01)
                glVertex3f(s*0.3, -s*0.2, s+0.01)
                glVertex3f(s*0.3, s*0.2, s+0.01)
                glVertex3f(-s*0.3, s*0.2, s+0.01)
                glEnd()
            
            if random.random() < 0.02:
                glColor4f(1, 1, 1, alpha * 0.3)
                glPointSize(10)
                glBegin(GL_POINTS)
                glVertex3f(0, 0, 0)
                glEnd()
            
            glPopMatrix()
    
    def apply_effects(self, surface):
        if self.level < 5:
            return surface
        
        w, h = surface.get_width(), surface.get_height()
        
        if self.level >= 15:
            pixel_size = max(1, int(2 + self.level / 20))
            small = pygame.transform.scale(surface, 
                (max(1, w // pixel_size), max(1, h // pixel_size)))
            surface = pygame.transform.scale(small, (w, h))
        
        if self.level >= 20 and random.random() < 0.2:
            glitch_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            for _ in range(int(min(8, self.level / 8))):
                x = random.randint(0, w - 20)
                y = random.randint(0, h - 10)
                w2 = random.randint(20, min(80, w - x))
                h2 = random.randint(2, 6)
                color = (random.randint(100, 255), random.randint(0, 100), random.randint(0, 100), random.randint(100, 200))
                rect_surf = pygame.Surface((w2, h2), pygame.SRCALPHA)
                rect_surf.fill(color)
                glitch_surf.blit(rect_surf, (x, y))
            surface.blit(glitch_surf, (0, 0))
        
        if self.level >= 25 and random.random() < 0.2:
            noise_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            for _ in range(min(60, int(20 + self.level * 2))):
                x = random.randint(0, w - 1)
                y = random.randint(0, h - 1)
                rect_surf = pygame.Surface((random.randint(1, 2), random.randint(1, 2)), pygame.SRCALPHA)
                rect_surf.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(50, 150)))
                noise_surf.blit(rect_surf, (x, y))
            surface.blit(noise_surf, (0, 0))
        
        if self.level >= 30 and random.random() < 0.3:
            rainbow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            step = 6
            for x in range(0, w, step):
                for y in range(0, h, step):
                    hue = (x / w + y / h + self.phase * 0.5 * self.psychedelic_boost) % 1.0
                    r = int(255 * (0.5 + 0.5 * math.sin(hue * 2 * math.pi)))
                    g = int(255 * (0.5 + 0.5 * math.sin((hue + 1/3) * 2 * math.pi)))
                    b = int(255 * (0.5 + 0.5 * math.sin((hue + 2/3) * 2 * math.pi)))
                    alpha = int(40 * min(1, (self.level - 30) / 20))
                    rect_surf = pygame.Surface((step, step), pygame.SRCALPHA)
                    rect_surf.fill((r, g, b, alpha))
                    rainbow_surf.blit(rect_surf, (x, y))
            surface.blit(rainbow_surf, (0, 0))
        
        if self.level >= 10:
            alpha = min(60, int((self.level - 10) * 2))
            red_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            red_surf.fill((255, 0, 0, alpha))
            for i in range(3):
                r = min(w, h) // 2 - i * 30
                if r > 0:
                    pygame.draw.circle(red_surf, (0, 0, 0, 0), (w//2, h//2), r)
            surface.blit(red_surf, (0, 0))
        
        return surface

insanity = InsanitySystem()

class Ammo:
    def __init__(self, x, z):
        self.x = x
        self.y = 0.5
        self.z = z
        self.alive = True
        self.phase = random.random() * 100
    
    def draw(self):
        if not self.alive:
            return
        self.phase += 0.05
        glPushMatrix()
        glTranslatef(self.x, self.y + math.sin(self.phase) * 0.1, self.z)
        glRotatef(self.phase * 30, 0, 1, 0)
        glColor3f(1, 0.85, 0)
        glBegin(GL_QUADS)
        glVertex3f(-0.06, -0.04, -0.06)
        glVertex3f(0.06, -0.04, -0.06)
        glVertex3f(0.06, 0.04, -0.06)
        glVertex3f(-0.06, 0.04, -0.06)
        glVertex3f(-0.06, -0.04, 0.06)
        glVertex3f(0.06, -0.04, 0.06)
        glVertex3f(0.06, 0.04, 0.06)
        glVertex3f(-0.06, 0.04, 0.06)
        glEnd()
        glColor4f(1, 0.8, 0, 0.2)
        glPointSize(20)
        glBegin(GL_POINTS)
        glVertex3f(0, 0, 0)
        glEnd()
        glPopMatrix()

class Bullet:
    def __init__(self, x, y, z, dx, dy, dz):
        self.x = x
        self.y = y
        self.z = z
        self.dx = dx * 0.8
        self.dy = dy * 0.8
        self.dz = dz * 0.8
        self.life = 60
        self.alive = True
        self.trail = []
    
    def update(self):
        self.trail.append((self.x, self.y, self.z))
        if len(self.trail) > 12:
            self.trail.pop(0)
        self.x += self.dx
        self.y += self.dy
        self.z += self.dz
        self.life -= 1
        if self.life <= 0:
            self.alive = False
    
    def draw(self):
        if not self.alive:
            return
        glDisable(GL_DEPTH_TEST)
        glLineWidth(3)
        glBegin(GL_LINE_STRIP)
        for i, (tx, ty, tz) in enumerate(self.trail):
            alpha = i / len(self.trail)
            glColor4f(1, 0.8, 0, alpha * 0.8)
            glVertex3f(tx, ty, tz)
        glEnd()
        glEnable(GL_DEPTH_TEST)
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glColor3f(1, 1, 0)
        glPointSize(10)
        glBegin(GL_POINTS)
        glVertex3f(0, 0, 0)
        glEnd()
        glColor4f(1, 0.5, 0, 0.3)
        glPointSize(25)
        glBegin(GL_POINTS)
        glVertex3f(0, 0, 0)
        glEnd()
        glPopMatrix()

class Enemy:
    def __init__(self, x, z, level=1):
        self.x = x
        self.y = -2.0
        self.target_y = 0.5
        self.z = z
        self.health = 2 + level
        self.max_health = 2 + level
        self.speed = 0.025 + random.random() * 0.02 + level * 0.005
        self.alive = True
        self.attack_cooldown = 0
        self.radius = 0.4
        self.phase = random.random() * 100
        self.hit_flash = 0
        self.spawning = True
        self.spawn_timer = 0
        self.spawn_duration = 25
        self.size = 0.5 + level * 0.05
    
    def update(self, px, pz):
        if not self.alive:
            return False
        
        if self.spawning:
            self.spawn_timer += 1
            progress = self.spawn_timer / self.spawn_duration
            self.y = -2.0 + (self.target_y + 2.0) * progress
            if self.spawn_timer >= self.spawn_duration:
                self.spawning = False
                self.y = self.target_y
                effect.add_particles(self.x, 0, self.z, 30)
            return False
        
        self.phase += 0.05
        if self.hit_flash > 0:
            self.hit_flash -= 1
        dx = px - self.x
        dz = pz - self.z
        dist = math.sqrt(dx*dx + dz*dz)
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if dist < 12:
            if dist > 1.2:
                self.x += (dx/dist) * self.speed
                self.z += (dz/dist) * self.speed
            else:
                if self.attack_cooldown <= 0:
                    self.attack_cooldown = 45
                    return True
        return False
    
    def draw(self):
        if not self.alive or self.y < -1.0:
            return
        glPushMatrix()
        glTranslatef(self.x, self.y + math.sin(self.phase) * 0.05, self.z)
        r = self.radius + math.sin(self.phase) * 0.05
        
        if self.hit_flash > 0:
            glColor3f(1, 1, 1)
        else:
            glColor3f(1, 0.85 + math.sin(self.phase) * 0.1, 0)
        
        seg = 8
        glBegin(GL_TRIANGLES)
        for i in range(seg):
            for j in range(seg):
                theta1 = (i / seg) * math.pi * 2
                theta2 = ((i + 1) / seg) * math.pi * 2
                phi1 = (j / seg) * math.pi
                phi2 = ((j + 1) / seg) * math.pi
                
                x1 = r * math.sin(phi1) * math.cos(theta1)
                y1 = r * math.cos(phi1)
                z1 = r * math.sin(phi1) * math.sin(theta1)
                x2 = r * math.sin(phi1) * math.cos(theta2)
                y2 = r * math.cos(phi1)
                z2 = r * math.sin(phi1) * math.sin(theta2)
                x3 = r * math.sin(phi2) * math.cos(theta2)
                y3 = r * math.cos(phi2)
                z3 = r * math.sin(phi2) * math.sin(theta2)
                x4 = r * math.sin(phi2) * math.cos(theta1)
                y4 = r * math.cos(phi2)
                z4 = r * math.sin(phi2) * math.sin(theta1)
                
                b = 0.5 + 0.5 * math.cos(phi1)
                glColor3f(1 * b, 0.85 * b, 0)
                glVertex3f(x1, y1, z1)
                glVertex3f(x2, y2, z2)
                glVertex3f(x3, y3, z3)
                glVertex3f(x1, y1, z1)
                glVertex3f(x3, y3, z3)
                glVertex3f(x4, y4, z4)
        glEnd()
        
        if self.health < self.max_health:
            glColor3f(1, 0, 0)
            glLineWidth(2)
            glBegin(GL_LINES)
            health_ratio = self.health / self.max_health
            glVertex3f(-r, -r-0.2, 0)
            glVertex3f(-r + (r*2*health_ratio), -r-0.2, 0)
            glEnd()
        
        glColor3f(0, 0, 0)
        glBegin(GL_QUADS)
        glVertex3f(-0.15, 0.15, -r-0.01)
        glVertex3f(-0.08, 0.15, -r-0.01)
        glVertex3f(-0.08, 0.22, -r-0.01)
        glVertex3f(-0.15, 0.22, -r-0.01)
        glVertex3f(0.08, 0.15, -r-0.01)
        glVertex3f(0.15, 0.15, -r-0.01)
        glVertex3f(0.15, 0.22, -r-0.01)
        glVertex3f(0.08, 0.22, -r-0.01)
        glEnd()
        
        glColor3f(0, 0, 0)
        glLineWidth(2)
        glBegin(GL_LINE_STRIP)
        for t in range(8):
            a = math.pi * 0.6 + (t/7) * math.pi * 0.8
            x = 0.2 * math.cos(a)
            y = -0.08 + 0.12 * math.sin(a)
            glVertex3f(x, y, -r-0.01)
        glEnd()
        glPopMatrix()

class Pill:
    def __init__(self, x, z):
        self.x = x
        self.y = 0.5
        self.z = z
        self.alive = True
        self.phase = random.random() * 100
        self.type = random.choice(['speed', 'psychedelic', 'health'])
        self.color = {
            'speed': (0, 1, 0),
            'psychedelic': (1, 0, 1),
            'health': (1, 0, 0)
        }[self.type]
    
    def draw(self):
        if not self.alive:
            return
        self.phase += 0.05
        glPushMatrix()
        glTranslatef(self.x, self.y + math.sin(self.phase) * 0.15, self.z)
        glRotatef(self.phase * 25, 0, 1, 0)
        
        glColor4f(self.color[0], self.color[1], self.color[2], 0.3 + math.sin(self.phase) * 0.1)
        glPointSize(50)
        glBegin(GL_POINTS)
        glVertex3f(0, 0, 0)
        glEnd()
        
        glColor3f(self.color[0], self.color[1], self.color[2])
        glBegin(GL_QUADS)
        glVertex3f(-0.08, 0.12, -0.08)
        glVertex3f(0.08, 0.12, -0.08)
        glVertex3f(0.08, 0.12, 0.08)
        glVertex3f(-0.08, 0.12, 0.08)
        glVertex3f(-0.08, -0.12, -0.08)
        glVertex3f(0.08, -0.12, -0.08)
        glVertex3f(0.08, -0.12, 0.08)
        glVertex3f(-0.08, -0.12, 0.08)
        glEnd()
        
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        glVertex3f(-0.02, -0.02, 0.081)
        glVertex3f(0.02, -0.02, 0.081)
        glVertex3f(0.02, 0.02, 0.081)
        glVertex3f(-0.02, 0.02, 0.081)
        glEnd()
        glPopMatrix()

class Player:
    def __init__(self):
        self.x = 0
        self.y = 0.5
        self.z = 0
        self.angle_x = 0
        self.angle_y = 0
        self.base_speed = 0.08
        self.speed = 0.08
        self.health = 100
        self.shoot_cooldown = 0
        self.kills = 0
        self.damage_cooldown = 0
        self.bob = 0
        self.ammo = 6
        self.max_ammo = 6
        self.reloading = False
        self.reload_timer = 0
        self.reload_time = 50
        self.pill_effects = {
            'speed': 0,
            'psychedelic': 0,
            'health': 0
        }
    
    def can_move(self, x, z):
        for wx, wz in walls:
            if abs(x - wx) < 0.7 and abs(z - wz) < 0.7:
                return False
        return abs(x) < 8 and abs(z) < 8
    
    def shoot(self, bullets):
        global shoot_sound
        
        if self.shoot_cooldown > 0 or self.reloading:
            return
        if self.ammo <= 0:
            self.start_reload()
            return
        
        if shoot_sound:
            try:
                shoot_sound.play()
            except:
                pass
        
        dx = -math.sin(self.angle_x) * math.cos(self.angle_y)
        dy = math.sin(self.angle_y)
        dz = -math.cos(self.angle_x) * math.cos(self.angle_y)
        
        gun_offset_x = 0.35
        gun_offset_y = -0.15
        gun_offset_z = 0.5
        
        cos_a = math.cos(self.angle_x)
        sin_a = math.sin(self.angle_x)
        
        world_x = self.x + gun_offset_x * cos_a + gun_offset_z * sin_a
        world_y = self.y + gun_offset_y
        world_z = self.z - gun_offset_x * sin_a + gun_offset_z * cos_a
        
        bullets.append(Bullet(world_x, world_y, world_z, dx, dy, dz))
        self.shoot_cooldown = 5
        self.ammo -= 1
        effect.add_particles(world_x, world_y, world_z, 20)
        effect.screen_shake = 4
        if self.ammo <= 0:
            self.start_reload()
    
    def start_reload(self):
        if not self.reloading:
            self.reloading = True
            self.reload_timer = self.reload_time
    
    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
        if self.reloading:
            self.reload_timer -= 1
            if self.reload_timer <= 0:
                self.reloading = False
                self.ammo = self.max_ammo
        self.bob += 0.05
        for key in self.pill_effects:
            if self.pill_effects[key] > 0:
                self.pill_effects[key] -= 1
        if self.pill_effects['speed'] > 0:
            self.speed = self.base_speed * 2.0
        else:
            self.speed = self.base_speed
        if self.pill_effects['psychedelic'] > 0:
            effect.psychedelic += 0.05 * insanity.psychedelic_boost
            effect.screen_shake = 5
            if random.random() < 0.03 * insanity.psychedelic_boost:
                effect.spawn_flying_cubes()
    
    def take_pill(self, pill_type):
        if pill_type == 'speed':
            self.pill_effects['speed'] = 300
            effect.add_particles(self.x, self.y, self.z, 60)
        elif pill_type == 'psychedelic':
            self.pill_effects['psychedelic'] = 400
            effect.add_particles(self.x, self.y, self.z, 100)
            effect.screen_shake = 30
            effect.spawn_flying_cubes()
            music_manager.start_psychedelic_effect()
            insanity.psychedelic_boost *= 1.5
        elif pill_type == 'health':
            self.health = min(100, self.health + 40)
            effect.add_particles(self.x, self.y, self.z, 50)
    
    def add_ammo(self, count=6):
        self.ammo = min(self.max_ammo, self.ammo + count)
        effect.add_particles(self.x, self.y, self.z, 25)

def draw_world():
    for x in range(-8, 9):
        for z in range(-8, 9):
            if (x + z) % 2 == 0:
                r = 0.15 + math.sin(effect.psychedelic * insanity.psychedelic_boost + x + z) * 0.05
                g = 0.15 + math.cos(effect.psychedelic * insanity.psychedelic_boost * 1.2 + x) * 0.05
                b = 0.2 + math.sin(effect.psychedelic * insanity.psychedelic_boost * 0.8 + z) * 0.05
                glColor3f(r, g, b)
            else:
                r = 0.2 + math.cos(effect.psychedelic * insanity.psychedelic_boost * 1.1 + z) * 0.05
                g = 0.2 + math.sin(effect.psychedelic * insanity.psychedelic_boost * 0.9 + x) * 0.05
                b = 0.25 + math.cos(effect.psychedelic * insanity.psychedelic_boost + z) * 0.05
                glColor3f(r, g, b)
            glPushMatrix()
            glTranslatef(x, -0.5, z)
            glBegin(GL_QUADS)
            glVertex3f(-0.5, 0, -0.5)
            glVertex3f(0.5, 0, -0.5)
            glVertex3f(0.5, 0, 0.5)
            glVertex3f(-0.5, 0, 0.5)
            glEnd()
            glPopMatrix()
    for wx, wz in walls:
        glPushMatrix()
        glTranslatef(wx, 0, wz)
        r = 0.5 + math.sin(effect.psychedelic * insanity.psychedelic_boost + wx + wz) * 0.2
        g = 0.3 + math.cos(effect.psychedelic * insanity.psychedelic_boost * 1.3 + wx) * 0.2
        b = 0.15 + math.sin(effect.psychedelic * insanity.psychedelic_boost * 0.7 + wz) * 0.2
        glColor3f(r, g, b)
        glBegin(GL_QUADS)
        glVertex3f(-0.5, 0, -0.5)
        glVertex3f(0.5, 0, -0.5)
        glVertex3f(0.5, 1.5, -0.5)
        glVertex3f(-0.5, 1.5, -0.5)
        glVertex3f(-0.5, 0, 0.5)
        glVertex3f(0.5, 0, 0.5)
        glVertex3f(0.5, 1.5, 0.5)
        glVertex3f(-0.5, 1.5, 0.5)
        glVertex3f(-0.5, 0, -0.5)
        glVertex3f(-0.5, 0, 0.5)
        glVertex3f(-0.5, 1.5, 0.5)
        glVertex3f(-0.5, 1.5, -0.5)
        glVertex3f(0.5, 0, -0.5)
        glVertex3f(0.5, 0, 0.5)
        glVertex3f(0.5, 1.5, 0.5)
        glVertex3f(0.5, 1.5, -0.5)
        glEnd()
        glPopMatrix()

def draw_weapon():
    glPushMatrix()
    glLoadIdentity()
    bob_offset = math.sin(player.bob * 2) * 0.02
    glTranslatef(0.5 + bob_offset, -0.2 + abs(math.sin(player.bob)) * 0.03, -1.0)
    glRotatef(10 + math.sin(player.bob) * 2, 1, 0, 0)
    glRotatef(-10, 0, 1, 0)
    
    if player.shoot_cooldown > 3:
        glColor3f(1, 1, 1)
    else:
        glColor3f(0.35 + math.sin(effect.psychedelic * insanity.psychedelic_boost) * 0.1, 
                  0.35 + math.cos(effect.psychedelic * insanity.psychedelic_boost * 1.2) * 0.1, 
                  0.4 + math.sin(effect.psychedelic * insanity.psychedelic_boost * 0.8) * 0.1)
    
    glBegin(GL_QUADS)
    glVertex3f(-0.04, -0.02, -0.4)
    glVertex3f(0.04, -0.02, -0.4)
    glVertex3f(0.04, 0.04, 0.3)
    glVertex3f(-0.04, 0.04, 0.3)
    glEnd()
    glColor3f(0.2 + math.sin(effect.psychedelic * insanity.psychedelic_boost * 0.5) * 0.1, 
              0.15 + math.cos(effect.psychedelic * insanity.psychedelic_boost * 0.7) * 0.1, 
              0.1 + math.sin(effect.psychedelic * insanity.psychedelic_boost * 0.3) * 0.1)
    glBegin(GL_QUADS)
    glVertex3f(-0.04, -0.02, 0.15)
    glVertex3f(0.04, -0.02, 0.15)
    glVertex3f(0.04, -0.12, 0.25)
    glVertex3f(-0.04, -0.12, 0.25)
    glEnd()
    glPopMatrix()

def draw_hud():
    global insanity
    
    insanity.update(player.kills)
    
    hud_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    font = pygame.font.Font(None, 28)
    big_font = pygame.font.Font(None, 45)
    
    r = 1 + math.sin(effect.psychedelic * insanity.psychedelic_boost) * 0.15
    g = 1 + math.cos(effect.psychedelic * insanity.psychedelic_boost * 1.3) * 0.15
    b = 1 + math.sin(effect.psychedelic * insanity.psychedelic_boost * 0.7) * 0.15
    
    if player.health < 30 and random.random() < 0.5:
        color = (255, 0, 0)
    else:
        color = (int(255 * min(1, r)), int(255 * min(1, g)), int(255 * min(1, b)))
    surf = font.render(f"HP: {player.health}", True, color)
    hud_surface.blit(surf, (10, 10))
    
    ammo_color = (255, 255, 0) if player.ammo > 0 else (255, 0, 0)
    if player.reloading:
        ammo_text = f"AMMO: {player.ammo}/{player.max_ammo} [RELOADING...]"
    else:
        ammo_text = f"AMMO: {player.ammo}/{player.max_ammo}"
    surf = font.render(ammo_text, True, ammo_color)
    hud_surface.blit(surf, (10, 50))
    
    kills_color = (255, 100, 100)
    if player.kills >= 40:
        kills_color = (255, 0, 0)
    surf = font.render(f"KILLS: {player.kills}", True, kills_color)
    hud_surface.blit(surf, (10, 90))
    
    alive = sum(1 for e in enemies if e.alive)
    surf = font.render(f"ENEMIES: {alive}", True, (100, int(255 * min(1, g*0.8)), 100))
    hud_surface.blit(surf, (10, 130))
    
    y_offset = 170
    if player.pill_effects['speed'] > 0:
        surf = font.render("SPEED x2", True, (0, 255, 0))
        hud_surface.blit(surf, (10, y_offset))
        y_offset += 28
    if player.pill_effects['psychedelic'] > 0:
        surf = font.render("PSYCHO", True, (255, 0, 255))
        hud_surface.blit(surf, (10, y_offset))
    
    if player.kills >= 40 and random.random() < 0.2:
        surf = big_font.render("REALITY SHIFT", True, (255, 0, 255))
        hud_surface.blit(surf, (WIDTH//2 - surf.get_width()//2, HEIGHT//2 - 100))
    elif player.kills >= 50 and random.random() < 0.3:
        surf = big_font.render("INSANITY", True, (255, 0, 0))
        hud_surface.blit(surf, (WIDTH//2 - surf.get_width()//2, HEIGHT//2 - 100))
    
    if player.health < 50 or player.kills > 20:
        alpha = min(150, int((50 - player.health) / 50 * 100 + player.kills / 2))
        red_surf = pygame.Surface((WIDTH, 10), pygame.SRCALPHA)
        red_surf.fill((255, 0, 0))
        red_surf.set_alpha(alpha)
        hud_surface.blit(red_surf, (0, 0))
        hud_surface.blit(red_surf, (0, HEIGHT-10))
        red_surf_v = pygame.Surface((10, HEIGHT), pygame.SRCALPHA)
        red_surf_v.fill((255, 0, 0))
        red_surf_v.set_alpha(alpha)
        hud_surface.blit(red_surf_v, (0, 0))
        hud_surface.blit(red_surf_v, (WIDTH-10, 0))
    
    if player.kills > 35:
        color = (random.randint(150, 255), random.randint(0, 50), random.randint(0, 50))
    else:
        color = (0, 255, 0)
    s = 12
    pygame.draw.line(hud_surface, color, (WIDTH//2 - s, HEIGHT//2), (WIDTH//2 - 4, HEIGHT//2), 2)
    pygame.draw.line(hud_surface, color, (WIDTH//2 + 4, HEIGHT//2), (WIDTH//2 + s, HEIGHT//2), 2)
    pygame.draw.line(hud_surface, color, (WIDTH//2, HEIGHT//2 - s), (WIDTH//2, HEIGHT//2 - 4), 2)
    pygame.draw.line(hud_surface, color, (WIDTH//2, HEIGHT//2 + 4), (WIDTH//2, HEIGHT//2 + s), 2)
    
    if player.kills > 5:
        hud_surface = insanity.apply_effects(hud_surface)
    
    data = pygame.image.tostring(hud_surface, "RGBA", True)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, WIDTH, HEIGHT, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glWindowPos2d(0, 0)
    glDrawPixels(WIDTH, HEIGHT, GL_RGBA, GL_UNSIGNED_BYTE, data)
    
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

player = Player()
enemies = []
bullets = []
pills = []
ammo_packs = []

enemy_positions = [(3,3,1), (-3,3,1), (3,-3,1)]
for x, z, level in enemy_positions:
    if not player.can_move(x, z):
        continue
    enemies.append(Enemy(x, z, level))

for _ in range(5):
    attempts = 0
    while attempts < 30:
        x = random.randint(-6, 6)
        z = random.randint(-6, 6)
        if player.can_move(x, z) and abs(x - player.x) > 2 and abs(z - player.z) > 2:
            pills.append(Pill(x, z))
            break
        attempts += 1

for _ in range(4):
    attempts = 0
    while attempts < 30:
        x = random.randint(-6, 6)
        z = random.randint(-6, 6)
        if player.can_move(x, z) and abs(x - player.x) > 2 and abs(z - player.z) > 2:
            ammo_packs.append(Ammo(x, z))
            break
        attempts += 1

running = True
clock = pygame.time.Clock()
pill_spawn_timer = 0
ammo_spawn_timer = 0
game_over = False
enemy_level = 1

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r:
                player.start_reload()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not game_over:
                player.shoot(bullets)
    
    if not game_over:
        keys = pygame.key.get_pressed()
        dx = dz = 0
        if keys[pygame.K_w]: dz = -1
        if keys[pygame.K_s]: dz = 1
        if keys[pygame.K_a]: dx = -1
        if keys[pygame.K_d]: dx = 1
        
        mx, my = pygame.mouse.get_rel()
        player.angle_x -= mx * 0.003
        player.angle_y -= my * 0.003
        player.angle_y = max(-1.4, min(1.4, player.angle_y))
        
        if dx != 0 or dz != 0:
            rad = player.angle_x
            mx2 = (dx * math.cos(rad) + dz * math.sin(rad)) * player.speed
            mz2 = (-dx * math.sin(rad) + dz * math.cos(rad)) * player.speed
            nx, nz = player.x + mx2, player.z + mz2
            if player.can_move(nx, nz):
                player.x, player.z = nx, nz
            else:
                if player.can_move(nx, player.z):
                    player.x = nx
                elif player.can_move(player.x, nz):
                    player.z = nz
        
        player.update()
        effect.update()
        insanity.update(player.kills)
        music_manager.update()
        
        for b in bullets[:]:
            b.update()
            if not b.alive:
                bullets.remove(b)
                continue
            for wx, wz in walls:
                if abs(b.x - wx) < 0.5 and abs(b.z - wz) < 0.5:
                    b.alive = False
                    effect.add_particles(b.x, b.y, b.z, 20)
                    break
            for e in enemies:
                if not e.alive:
                    continue
                if abs(b.x - e.x) < 0.6 and abs(b.z - e.z) < 0.6:
                    e.health -= 1
                    e.hit_flash = 10
                    b.alive = False
                    effect.add_particles(e.x, e.y, e.z, 40)
                    effect.screen_shake = 6
                    if e.health <= 0:
                        e.alive = False
                        player.kills += 1
                        effect.add_particles(e.x, e.y, e.z, 70)
                        effect.flash = 8
                        effect.screen_shake = 15
                        attempts = 0
                        while attempts < 20:
                            x = random.randint(-6, 6)
                            z = random.randint(-6, 6)
                            if player.can_move(x, z) and abs(x - player.x) > 3 and abs(z - player.z) > 3:
                                enemies.append(Enemy(x, z, enemy_level))
                                break
                            attempts += 1
                    break
        
        for e in enemies:
            if e.alive:
                if e.update(player.x, player.z):
                    player.health -= 10
                    effect.screen_shake = 25
                    effect.flash = 5
                    effect.add_particles(player.x, player.y, player.z, 30)
                    if player.health <= 0:
                        game_over = True
        
        for pill in pills[:]:
            if not pill.alive:
                continue
            if abs(player.x - pill.x) < 0.6 and abs(player.z - pill.z) < 0.6:
                player.take_pill(pill.type)
                pill.alive = False
                pills.remove(pill)
        
        for ammo in ammo_packs[:]:
            if not ammo.alive:
                continue
            if abs(player.x - ammo.x) < 0.6 and abs(player.z - ammo.z) < 0.6:
                player.add_ammo(6)
                ammo.alive = False
                ammo_packs.remove(ammo)
                effect.add_particles(ammo.x, ammo.y, ammo.z, 35)
        
        alive_enemies = [e for e in enemies if e.alive]
        while len(alive_enemies) < 3:
            attempts = 0
            while attempts < 20:
                x = random.randint(-6, 6)
                z = random.randint(-6, 6)
                if player.can_move(x, z) and abs(x - player.x) > 3 and abs(z - player.z) > 3:
                    enemies.append(Enemy(x, z, enemy_level))
                    alive_enemies = [e for e in enemies if e.alive]
                    break
                attempts += 1
        
        if player.kills > 10:
            enemy_level = 2
        if player.kills > 30:
            enemy_level = 3
        if player.kills > 50:
            enemy_level = 4
        
        pill_spawn_timer += 1
        if pill_spawn_timer > 200 and len(pills) < 6:
            pill_spawn_timer = 0
            attempts = 0
            while attempts < 30:
                x = random.randint(-6, 6)
                z = random.randint(-6, 6)
                if player.can_move(x, z) and abs(x - player.x) > 2 and abs(z - player.z) > 2:
                    pills.append(Pill(x, z))
                    break
                attempts += 1
        
        ammo_spawn_timer += 1
        if ammo_spawn_timer > 250 and len(ammo_packs) < 5:
            ammo_spawn_timer = 0
            attempts = 0
            while attempts < 30:
                x = random.randint(-6, 6)
                z = random.randint(-6, 6)
                if player.can_move(x, z) and abs(x - player.x) > 2 and abs(z - player.z) > 2:
                    ammo_packs.append(Ammo(x, z))
                    break
                attempts += 1
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    if effect.screen_shake > 0:
        shake_x = (random.random() - 0.5) * effect.screen_shake * 0.03
        shake_y = (random.random() - 0.5) * effect.screen_shake * 0.03
        glTranslatef(shake_x, shake_y, 0)
    
    glRotatef(-math.degrees(player.angle_y), 1, 0, 0)
    glRotatef(-math.degrees(player.angle_x), 0, 1, 0)
    glTranslatef(-player.x, -player.y, -player.z)
    
    if effect.flash > 0:
        glClearColor(1, 1, 1, 1)
    else:
        glClearColor(0.1 + math.sin(effect.psychedelic * insanity.psychedelic_boost) * 0.05, 
                     0.1 + math.cos(effect.psychedelic * insanity.psychedelic_boost * 1.3) * 0.05, 
                     0.15 + math.sin(effect.psychedelic * insanity.psychedelic_boost * 0.7) * 0.05, 1)
    
    draw_world()
    effect.draw_flying_cubes()
    insanity.draw_fake_pills()
    
    for pill in pills:
        pill.draw()
    for ammo in ammo_packs:
        ammo.draw()
    for e in enemies:
        e.draw()
    for b in bullets:
        b.draw()
    
    effect.draw_particles()
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    if not game_over:
        draw_weapon()
    glPopMatrix()
    
    draw_hud()
    
    if game_over:
        show_fake_error()
        pygame.time.wait(3000)
        running = False
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
