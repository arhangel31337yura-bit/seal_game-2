from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle, Line, Polygon
from settings import *
import random
import math

class GameArea(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.seal_x = 100
        self.items = []
        self.score = 0
        self.lives = 3
        self.spawn_timer = 0
        self.game_over = False
        self.current_mode = "normal"
        
        # Переменные для анимаций
        self.time_alive = 0
        self.hit_timer = 0
        self.particles = []
        self.is_blinking = False
        self.blink_timer = 0
        self.parent_game = None

        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def start(self, mode, parent):
        self.parent_game = parent
        self.current_mode = mode
        self.seal_x = self.width / 2 if self.width else 200
        self.items = []
        self.score = 0
        self.lives = 1 if mode == "hard" else 3
        self.spawn_timer = 0
        self.game_over = False
        self.time_alive = 0
        self.hit_timer = 0
        self.particles = []

    def on_touch_move(self, touch):
        if not self.game_over:
            self.seal_x = max(50, min(self.width - 50, touch.x))
        return True

    def update(self, dt):
        if self.game_over or self.width == 0:
            return

        self.time_alive += dt
        
        # Анимация моргания
        self.blink_timer += dt
        if self.blink_timer > 3:
            self.is_blinking = True
            if self.blink_timer > 3.2:
                self.is_blinking = False
                self.blink_timer = 0

        # Таймер красной вспышки при уроне
        if self.hit_timer > 0:
            self.hit_timer -= dt

        # Движение частиц (брызг)
        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] -= 400 * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

        # Спавн врагов и рыбок
        self.spawn_timer += dt
        rate = SPAWN_RATE_NORMAL if self.current_mode == "normal" else SPAWN_RATE_LOL if self.current_mode == "lol" else SPAWN_RATE_HARD
        
        if self.spawn_timer > rate:
            self.spawn_timer = 0
            x = random.uniform(50, self.width - 50)
            kind = "fish"
            r = random.random()
            
            if self.current_mode == "normal" and r > 0.8: kind = "trash"
            elif self.current_mode == "lol" and r > 0.6: kind = "demon"
            elif self.current_mode == "hard" and r > 0.5: kind = "bomb"
            
            speed = random.uniform(self.height * 0.2, self.height * 0.4)
            if self.current_mode == "hard": speed *= 1.4
            
            self.items.append({"x": x, "y": self.height + 50, "kind": kind, "speed": speed})

        # Логика столкновений
        for item in self.items[:]:
            item["y"] -= item["speed"] * dt
            
            # Если предмет на уровне тюленя
            if item["y"] < 150 and item["y"] > 50:
                if abs(item["x"] - self.seal_x) < 70:
                    self.items.remove(item)
                    if item["kind"] == "fish": 
                        self.score += 1
                        self.spawn_particles((0.2, 1.0, 0.2)) # Зеленые брызги
                    else: 
                        self.lose_life()
                    continue
            
            # Если предмет упал за экран
            if item["y"] < -50:
                if item["kind"] == "fish": 
                    self.lose_life()
                self.items.remove(item)

        self.redraw()

    def spawn_particles(self, color):
        for _ in range(10):
            self.particles.append({
                "x": self.seal_x, "y": 150,
                "vx": random.uniform(-200, 200),
                "vy": random.uniform(50, 250),
                "life": 0.5,
                "color": color
            })

    def lose_life(self):
        self.lives -= 1
        self.hit_timer = 0.4
        self.spawn_particles((1.0, 0.1, 0.1)) # Красные брызги
        if self.lives <= 0:
            self.game_over = True
            if self.parent_game:
                self.parent_game.end_game(self.score)

    def redraw(self):
        self.canvas.clear()
        with self.canvas:
            # Фон
            Color(*COLOR_BG_BOTTOM)
            Rectangle(pos=(0, 0), size=self.size)
            Color(*COLOR_BG_TOP)
            Rectangle(pos=(0, self.height * 0.5), size=(self.width, self.height * 0.5))

            # Тюлень (с анимацией дыхания)
            breath = math.sin(self.time_alive * 4) * 0.05 + 1.0
            sy = 100
            seal_w = 140 * breath
            seal_h = 120 * breath

            Color(*COLOR_SEAL)
            Ellipse(pos=(self.seal_x - seal_w/2, sy - seal_h/2), size=(seal_w, seal_h))
            Color(0.9, 0.95, 1)
            Ellipse(pos=(self.seal_x - 40 * breath, sy - 40 * breath), size=(80 * breath, 80 * breath))
            Color(0.7, 0.8, 0.9)
            Ellipse(pos=(self.seal_x - 45, sy + 20), size=(90, 90))
            
            # Состояния ранений
            if self.lives < 3:
                Color(0.9, 0.8, 0.6) # Пластырь
                Rectangle(pos=(self.seal_x - 20, sy + 80), size=(30, 12))
                Color(0.7, 0.6, 0.4)
                Rectangle(pos=(self.seal_x - 18, sy + 84), size=(26, 4))
                
            if self.lives == 1:
                Color(0.9, 0.8, 0.6) # Второй пластырь
                Rectangle(pos=(self.seal_x + 15, sy + 10), size=(20, 10))
                Color(0.8, 0.1, 0.1) # Шрам
                Line(points=[self.seal_x - 35, sy + 40, self.seal_x - 15, sy + 50], width=3)

            # Глаза (крестики, если осталась 1 жизнь)
            if not self.is_blinking:
                Color(0.1, 0.1, 0.1)
                if self.lives == 1:
                    Line(points=[self.seal_x - 25, sy + 55, self.seal_x - 15, sy + 65], width=3)
                    Line(points=[self.seal_x - 25, sy + 65, self.seal_x - 15, sy + 55], width=3)
                    Line(points=[self.seal_x + 10, sy + 55, self.seal_x + 20, sy + 65], width=3)
                    Line(points=[self.seal_x + 10, sy + 65, self.seal_x + 20, sy + 55], width=3)
                else:
                    Ellipse(pos=(self.seal_x - 25, sy + 60), size=(15, 15))
                    Ellipse(pos=(self.seal_x + 10, sy + 60), size=(15, 15))

            # Отрисовка предметов
            for item in self.items:
                ix, iy = item["x"], item["y"]
                if item["kind"] == "fish":
                    Color(1.0, 0.6, 0.2)
                    Ellipse(pos=(ix - 20, iy - 10), size=(40, 20))
                    Color(1.0, 0.8, 0.3)
                    Polygon(points=[ix - 20, iy, ix - 35, iy - 15, ix - 35, iy + 15])
                elif item["kind"] == "trash":
                    Color(0.4, 0.4, 0.4)
                    Rectangle(pos=(ix - 15, iy - 15), size=(30, 30))
                elif item["kind"] == "demon":
                    Color(0.8, 0.1, 0.1)
                    Ellipse(pos=(ix - 20, iy - 20), size=(40, 40))
                elif item["kind"] == "bomb":
                    Color(0.1, 0.1, 0.1)
                    Ellipse(pos=(ix - 20, iy - 20), size=(40, 40))

            # Отрисовка частиц
            for p in self.particles:
                Color(*p["color"], min(p["life"] * 2, 1.0))
                Ellipse(pos=(p["x"] - 5, p["y"] - 5), size=(10, 10))

            # Красная вспышка урона
            if self.hit_timer > 0:
                Color(1, 0, 0, self.hit_timer * 1.5)
                Rectangle(pos=(0, 0), size=self.size)