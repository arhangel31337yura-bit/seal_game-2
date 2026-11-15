from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle, Line, Polygon
from kivy.utils import get_color_from_hex
import random
import math

# ==========================================
# ИГРОВОЕ ПОЛЕ (Вся логика и графика)
# ==========================================
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
        
        self.blink_timer += dt
        if self.blink_timer > 3:
            self.is_blinking = True
            if self.blink_timer > 3.2:
                self.is_blinking = False
                self.blink_timer = 0

        if self.hit_timer > 0:
            self.hit_timer -= dt

        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] -= 400 * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

        self.spawn_timer += dt
        rate = 0.6 if self.current_mode == "normal" else 0.4 if self.current_mode == "lol" else 0.3
        
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

        for item in self.items[:]:
            item["y"] -= item["speed"] * dt
            
            if item["y"] < 150 and item["y"] > 50:
                if abs(item["x"] - self.seal_x) < 70:
                    self.items.remove(item)
                    if item["kind"] == "fish": 
                        self.score += 1
                        self.spawn_particles((0.2, 1.0, 0.2))
                    else: 
                        self.lose_life()
                    continue
            
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
        self.spawn_particles((1.0, 0.1, 0.1))
        if self.lives <= 0:
            self.game_over = True
            if self.parent_game:
                self.parent_game.end_game(self.score)

    def redraw(self):
        self.canvas.clear()
        with self.canvas:
            # Фон
            Color(0.1, 0.4, 0.7)
            Rectangle(pos=(0, 0), size=self.size)
            Color(0.15, 0.5, 0.8)
            Rectangle(pos=(0, self.height * 0.5), size=(self.width, self.height * 0.5))

            # Тюлень
            breath = math.sin(self.time_alive * 4) * 0.05 + 1.0
            sy = 100
            seal_w = 140 * breath
            seal_h = 120 * breath

            Color(0.6, 0.7, 0.8)
            Ellipse(pos=(self.seal_x - seal_w/2, sy - seal_h/2), size=(seal_w, seal_h))
            Color(0.9, 0.95, 1)
            Ellipse(pos=(self.seal_x - 40 * breath, sy - 40 * breath), size=(80 * breath, 80 * breath))
            Color(0.7, 0.8, 0.9)
            Ellipse(pos=(self.seal_x - 45, sy + 20), size=(90, 90))
            
            if self.lives < 3:
                Color(0.9, 0.8, 0.6)
                Rectangle(pos=(self.seal_x - 20, sy + 80), size=(30, 12))
                Color(0.7, 0.6, 0.4)
                Rectangle(pos=(self.seal_x - 18, sy + 84), size=(26, 4))
                
            if self.lives == 1:
                Color(0.9, 0.8, 0.6)
                Rectangle(pos=(self.seal_x + 15, sy + 10), size=(20, 10))
                Color(0.8, 0.1, 0.1)
                Line(points=[self.seal_x - 35, sy + 40, self.seal_x - 15, sy + 50], width=3)

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

            for p in self.particles:
                Color(*p["color"], min(p["life"] * 2, 1.0))
                Ellipse(pos=(p["x"] - 5, p["y"] - 5), size=(10, 10))

            if self.hit_timer > 0:
                Color(1, 0, 0, self.hit_timer * 1.5)
                Rectangle(pos=(0, 0), size=self.size)

# ==========================================
# ГЛАВНЫЙ ЭКРАН (Меню и UI)
# ==========================================
class SealGame(FloatLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        
        self.game_area = GameArea(size_hint=(1, 1))
        self.add_widget(self.game_area)

        self.score_label = Label(text="", font_size='30sp', bold=True, color=get_color_from_hex("#FFD700"), pos_hint={'x': 0.1, 'top': 0.95})
        self.add_widget(self.score_label)

        # МЕНЮ
        self.menu_layout = FloatLayout()
        title = Label(text="ТЮЛЕНЬ ГЕЙМС", font_size='50sp', bold=True, color=get_color_from_hex("#00FFFF"), pos_hint={'center_x': 0.5, 'center_y': 0.8})
        self.menu_layout.add_widget(title)

        btn1 = Button(text="РЫБАЛКА", size_hint=(0.7, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.6}, background_color=get_color_from_hex("#3498db"))
        btn1.bind(on_release=lambda x: self.start_game("normal"))
        
        btn2 = Button(text="ЛОЛ-МОД", size_hint=(0.7, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.45}, background_color=get_color_from_hex("#e84118"))
        btn2.bind(on_release=lambda x: self.start_game("lol"))
        
        btn3 = Button(text="ХАРДМОД", size_hint=(0.7, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.3}, background_color=get_color_from_hex("#8e44ad"))
        btn3.bind(on_release=lambda x: self.start_game("hard"))

        self.menu_layout.add_widget(btn1)
        self.menu_layout.add_widget(btn2)
        self.menu_layout.add_widget(btn3)

        # Пасхалка
        self.egg_btn = Button(background_color=(0,0,0,0), background_normal='', size_hint=(None, None), size=(100, 100), pos=(20, 20))
        with self.egg_btn.canvas.after:
            Color(1, 0.8, 0.2)
            Ellipse(pos=(20, 30), size=(60, 35))
            Polygon(points=[20, 47.5, 0, 20, 0, 75])
        self.egg_btn.bind(on_release=self.show_egg)
        self.menu_layout.add_widget(self.egg_btn)

        self.egg_lbl = Label(text="Секрет!", font_size='20sp', color=get_color_from_hex("#FFF"), pos=(130, 40), opacity=0)
        self.menu_layout.add_widget(self.egg_lbl)
        self.add_widget(self.menu_layout)

        # GAME OVER
        self.go_layout = FloatLayout(opacity=0)
        self.go_lbl = Label(text="", font_size='40sp', bold=True, color=get_color_from_hex("#FFFFFF"), pos_hint={'center_x': 0.5, 'center_y': 0.6})
        btn_restart = Button(text="В МЕНЮ", size_hint=(0.6, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.4}, background_color=get_color_from_hex("#4cd137"))
        btn_restart.bind(on_release=self.to_menu)
        self.go_layout.add_widget(self.go_lbl)
        self.go_layout.add_widget(btn_restart)
        self.add_widget(self.go_layout)

    def show_egg(self, instance):
        self.egg_lbl.opacity = 1
        Clock.schedule_once(lambda dt: setattr(self.egg_lbl, 'opacity', 0), 2.0)

    def start_game(self, mode):
        self.menu_layout.opacity = 0
        self.go_layout.opacity = 0
        self.game_area.start(mode, self)
        self.score_label.text = "0"

    def end_game(self, score):
        self.go_lbl.text = f"ИГРА ОКОНЧЕНА\nСчёт: {score}"
        self.go_layout.opacity = 1

    def to_menu(self, instance):
        self.go_layout.opacity = 0
        self.menu_layout.opacity = 1
        self.score_label.text = ""

class SealApp(App):
    def build(self):
        return SealGame()

if __name__ == "__main__":
    SealApp().run()
