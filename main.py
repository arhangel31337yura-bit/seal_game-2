from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle, Polygon
from kivy.utils import get_color_from_hex
import random

class SealGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = "menu"
        self.score = 0
        self.lives = 3
        self.items = []
        self.spawn_timer = 0
        self.seal_x = 200
        self.time_alive = 0
        
        # Кнопки меню (x, y, ширина, высота, цвет)
        self.btn_w = 300
        self.btn_h = 60
        self.btn_x = 250
        
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def on_touch_down(self, touch):
        if self.state == "menu":
            if self.btn_x < touch.x < self.btn_x + self.btn_w:
                if 400 < touch.y < 460: self.start_game("normal")
                elif 320 < touch.y < 380: self.start_game("lol")
                elif 240 < touch.y < 300: self.start_game("hard")
            
            # Пасхалка (рыбка в левом нижнем углу)
            if 20 < touch.x < 100 and 20 < touch.y < 100:
                self.state = "easter_egg"
                Clock.schedule_once(self.go_to_menu, 2.0)
                
        elif self.state == "game_over":
            if 250 < touch.x < 550 and 200 < touch.y < 260:
                self.state = "menu"
        return True

    def on_touch_move(self, touch):
        if self.state in ["normal", "lol", "hard"]:
            self.seal_x = max(70, min(self.width - 70, touch.x))
        return True

    def start_game(self, mode):
        self.state = mode
        self.seal_x = self.width / 2 if self.width else 400
        self.score = 0
        self.lives = 1 if mode == "hard" else 3
        self.items = []
        self.spawn_timer = 0
        self.time_alive = 0

    def go_to_menu(self, dt):
        self.state = "menu"

    def update(self, dt):
        self.time_alive += dt
        
        if self.state in ["normal", "lol", "hard"]:
            self.spawn_timer += dt
            rate = 0.8 if self.state == "normal" else 0.5 if self.state == "lol" else 0.4
            
            if self.spawn_timer > rate:
                self.spawn_timer = 0
                x = random.uniform(50, self.width - 50)
                kind = "fish"
                r = random.random()
                if self.state == "normal" and r > 0.8: kind = "trash"
                elif self.state == "lol" and r > 0.6: kind = "demon"
                elif self.state == "hard" and r > 0.5: kind = "bomb"
                
                speed = random.uniform(self.height * 0.2, self.height * 0.35)
                if self.state == "hard": speed *= 1.4
                
                self.items.append({"x": x, "y": self.height + 50, "kind": kind, "speed": speed})

            for item in self.items[:]:
                item["y"] -= item["speed"] * dt
                
                if item["y"] < 150 and item["y"] > 50:
                    if abs(item["x"] - self.seal_x) < 70:
                        self.items.remove(item)
                        if item["kind"] == "fish": self.score += 1
                        else: self.lives -= 1
                        continue
                
                if item["y"] < -50:
                    if item["kind"] == "fish": self.lives -= 1
                    self.items.remove(item)
            
            if self.lives <= 0:
                self.state = "game_over"

        self.redraw()

    def redraw(self):
        self.canvas.clear()
        with self.canvas:
            # ФОН
            Color(0.05, 0.2, 0.4) 
            Rectangle(pos=(0, 0), size=self.size)
            Color(0.1, 0.4, 0.7) 
            Rectangle(pos=(0, self.height * 0.4), size=(self.width, self.height * 0.6))
            
            # Песок
            Color(0.8, 0.7, 0.5) 
            Ellipse(pos=(-50, -100), size=(self.width * 0.7, 200)) 
            Ellipse(pos=(self.width * 0.4, -120), size=(self.width * 0.8, 220))

            if self.state == "menu" or self.state == "easter_egg":
                self.draw_menu()
            elif self.state == "game_over":
                self.draw_game_over()
            else:
                self.draw_game()

    def draw_menu(self):
        # Вместо текста рисуем красивые полоски (заголовок)
        Color(0, 1, 1)
        Rectangle(pos=(250, 500), size=(300, 40))
        Rectangle(pos=(200, 460), size=(400, 20))

        # Кнопки (просто цветные прямоугольники)
        Color(0.2, 0.6, 0.8) 
        Rectangle(pos=(self.btn_x, 400), size=(self.btn_w, self.btn_h))
        Color(0.9, 0.2, 0.1) 
        Rectangle(pos=(self.btn_x, 320), size=(self.btn_w, self.btn_h))
        Color(0.5, 0.2, 0.6) 
        Rectangle(pos=(self.btn_x, 240), size=(self.btn_w, self.btn_h))

        # Пасхалка (рыбка)
        Color(1, 0.8, 0.2)
        Ellipse(pos=(30, 40), size=(60, 35))
        Polygon(points=[30, 57.5, 10, 30, 10, 85])
        
        if self.state == "easter_egg":
            Color(1, 1, 1)
            Rectangle(pos=(110, 30), size=(250, 60))

    def draw_game_over(self):
        Color(0, 0, 0, 0.7)
        Rectangle(pos=(0, 0), size=self.size)
        
        Color(0.3, 0.8, 0.2)
        Rectangle(pos=(250, 200), size=(300, 60))
        
        Color(1, 1, 1)
        Rectangle(pos=(300, 400), size=(200, 20))

    def draw_game(self):
        # ТЮЛЕНЬ
        sy = 110
        Color(0, 0, 0, 0.2) 
        Ellipse(pos=(self.seal_x - 60, 70), size=(120, 30))

        Color(0.6, 0.7, 0.8) 
        Ellipse(pos=(self.seal_x - 70, sy - 50), size=(140, 120))
        Color(0.9, 0.95, 1) 
        Ellipse(pos=(self.seal_x - 40, sy - 40), size=(80, 80))
        Color(0.7, 0.8, 0.9) 
        Ellipse(pos=(self.seal_x - 45, sy + 20), size=(90, 90))
        
        # Глаза
        Color(0.1, 0.1, 0.1)
        if self.lives == 1:
            Rectangle(pos=(self.seal_x - 30, sy + 60), size=(10, 10))
            Rectangle(pos=(self.seal_x - 20, sy + 60), size=(10, 10))
            Rectangle(pos=(self.seal_x + 10, sy + 60), size=(10, 10))
            Rectangle(pos=(self.seal_x + 20, sy + 60), size=(10, 10))
        else:
            Ellipse(pos=(self.seal_x - 25, sy + 60), size=(15, 15))
            Ellipse(pos=(self.seal_x + 10, sy + 60), size=(15, 15))

        # ПРЕДМЕТЫ
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

        # СЧЕТ И ЖИЗНИ (вместо текста - полоски)
        Color(1, 0.8, 0.2)
        Ellipse(pos=(20, self.height - 50), size=(30, 15))
        
        Color(1, 1, 1)
        for i in range(min(self.score, 10)):
            Rectangle(pos=(60 + i * 15, self.height - 45), size=(10, 20))

        Color(1, 0.3, 0.5)
        for i in range(max(0, self.lives)):
            hx = self.width - 40 - i * 40
            hy = self.height - 40
            Ellipse(pos=(hx, hy), size=(15, 15))
            Ellipse(pos=(hx+15, hy), size=(15, 15))
            Polygon(points=[hx, hy+10, hx+15, hy+30, hx+30, hy+10])

class SealApp(App):
    def build(self):
        return SealGame()

if __name__ == "__main__":
    SealApp().run()
