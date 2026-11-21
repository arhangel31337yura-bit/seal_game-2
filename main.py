from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle, Polygon
from kivy.core.text import Label as CoreLabel
import random

class SealGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.seal_x = 200
        self.items = []
        self.score = 0
        self.lives = 3
        self.spawn_timer = 0
        self.game_over = False
        
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def on_touch_move(self, touch):
        if not self.game_over:
            self.seal_x = max(70, min(self.width - 70, touch.x))
        return True

    def update(self, dt):
        if self.game_over or self.width == 0:
            return

        self.spawn_timer += dt
        if self.spawn_timer > 0.8:
            self.spawn_timer = 0
            x = random.uniform(50, self.width - 50)
            kind = "fish" if random.random() < 0.8 else "trash"
            speed = random.uniform(self.height * 0.2, self.height * 0.35)
            self.items.append({"x": x, "y": self.height + 50, "kind": kind, "speed": speed})

        for item in self.items[:]:
            item["y"] -= item["speed"] * dt
            
            # Столкновение с тюленем
            if item["y"] < 150 and item["y"] > 50:
                if abs(item["x"] - self.seal_x) < 70:
                    self.items.remove(item)
                    if item["kind"] == "fish": 
                        self.score += 1
                    else: 
                        self.lives -= 1
                        if self.lives <= 0: self.game_over = True
                    continue
            
            # Упал за экран
            if item["y"] < -50:
                if item["kind"] == "fish": 
                    self.lives -= 1
                    if self.lives <= 0: self.game_over = True
                self.items.remove(item)

        self.redraw()

    def redraw(self):
        self.canvas.clear()
        with self.canvas:
            # Фон
            Color(0.1, 0.4, 0.7)
            Rectangle(pos=(0, 0), size=self.size)
            Color(0.15, 0.5, 0.8)
            Rectangle(pos=(0, self.height * 0.5), size=(self.width, self.height * 0.5))

            # Тюлень
            sy = 110
            Color(0.6, 0.7, 0.8) # Тело
            Ellipse(pos=(self.seal_x - 70, sy - 50), size=(140, 120))
            Color(0.9, 0.95, 1) # Живот
            Ellipse(pos=(self.seal_x - 40, sy - 40), size=(80, 80))
            Color(0.7, 0.8, 0.9) # Голова
            Ellipse(pos=(self.seal_x - 45, sy + 20), size=(90, 90))
            
            # Глаза
            Color(0.1, 0.1, 0.1)
            Ellipse(pos=(self.seal_x - 25, sy + 60), size=(15, 15))
            Ellipse(pos=(self.seal_x + 10, sy + 60), size=(15, 15))

            # Предметы
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

            # Счёт (рисуем на холсте, чтобы не было виджетов)
            score_label = CoreLabel(text=f"Счёт: {self.score}", font_size=int(self.width * 0.06), color=(1, 1, 1, 1))
            score_label.refresh()
            Rectangle(texture=score_label.texture, pos=(20, self.height - 60), size=score_label.texture.size)

            # Жизни
            lives_text = " ".join("❤" for _ in range(max(0, self.lives)))
            lives_label = CoreLabel(text=lives_text, font_size=int(self.width * 0.06), color=(1, 0.3, 0.5, 1))
            lives_label.refresh()
            Rectangle(texture=lives_label.texture, pos=(self.width - lives_label.texture.size[0] - 20, self.height - 60), size=lives_label.texture.size)

            if self.game_over:
                Color(0, 0, 0, 0.7)
                Rectangle(pos=(0, 0), size=self.size)
                over_text = f"ИГРА ОКОНЧЕНА\nСчёт: {self.score}"
                over_label = CoreLabel(text=over_text, font_size=int(self.width * 0.08), color=(1, 1, 1, 1), halign="center")
                over_label.refresh()
                Rectangle(texture=over_label.texture, 
                          pos=(self.width/2 - over_label.texture.size[0]/2, self.height/2 - over_label.texture.size[1]/2), 
                          size=over_label.texture.size)

class SealApp(App):
    def build(self):
        return SealGame()

if __name__ == "__main__":
    SealApp().run()
