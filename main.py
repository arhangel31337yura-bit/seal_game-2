from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.utils import get_color_from_hex
import random

class SealGame(Widget):
    def __init__(self, **kw):
        super().__init__(**kw)
        
        self.seal_x = 200
        self.items = []
        self.score = 0
        self.lives = 3
        self.spawn_timer = 0
        
        # Используем стандартный Label, как в самом первом МВП
        self.score_label = Label(text="Счёт: 0", font_size='20sp', bold=True, color=(1,1,1,1))
        self.score_label.pos_hint = {'x': 0.05, 'y': 0.95}
        self.add_widget(self.score_label)

        self.lives_label = Label(text="❤ ❤ ❤", font_size='20sp', bold=True, color=get_color_from_hex("#ff8fab"))
        self.lives_label.pos_hint = {'right': 0.95, 'y': 0.95}
        self.add_widget(self.lives_label)

        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def on_touch_move(self, touch):
        if self.width > 0:
            self.seal_x = max(70, min(self.width - 70, touch.x))

    def update(self, dt):
        if self.width == 0: return
        
        self.spawn_timer += dt
        if self.spawn_timer > 0.8:
            self.spawn_timer = 0
            x = random.randint(50, int(self.width) - 50)
            kind = "fish" if random.random() < 0.8 else "trash"
            self.items.append({"x": x, "y": self.height, "kind": kind, "speed": random.uniform(300, 450)})

        for item in self.items[:]:
            item["y"] -= item["speed"] * dt
            
            # Столкновение
            if item["y"] < 200 and item["y"] > 100:
                if abs(item["x"] - self.seal_x) < 70:
                    self.items.remove(item)
                    if item["kind"] == "fish":
                        self.score += 1
                        self.score_label.text = f"Счёт: {self.score}"
                    else:
                        self.lives -= 1
                        self.lives_label.text = " ".join("❤" for _ in range(max(0, self.lives)))
                    continue
            
            # Упал за экран
            if item["y"] < -50:
                if item["kind"] == "fish":
                    self.lives -= 1
                    self.lives_label.text = " ".join("❤" for _ in range(max(0, self.lives)))
                self.items.remove(item)

        self.redraw()

    def redraw(self):
        self.canvas.clear()
        with self.canvas:
            # Фон
            Color(0.1, 0.4, 0.7)
            Rectangle(pos=(0, 0), size=self.size)
            
            # Тюлень
            Color(0.6, 0.7, 0.8)
            Ellipse(pos=(self.seal_x - 70, 100), size=(140, 120))
            Color(0.9, 0.95, 1)
            Ellipse(pos=(self.seal_x - 40, 110), size=(80, 80))
            Color(0.7, 0.8, 0.9)
            Ellipse(pos=(self.seal_x - 45, 170), size=(90, 90))

            # Глаза
            Color(0.1, 0.1, 0.1)
            Ellipse(pos=(self.seal_x - 25, 210), size=(15, 15))
            Ellipse(pos=(self.seal_x + 10, 210), size=(15, 15))

            # Предметы
            for item in self.items:
                if item["kind"] == "fish":
                    Color(1.0, 0.6, 0.2)
                    Ellipse(pos=(item["x"] - 20, item["y"] - 10), size=(40, 20))
                else:
                    Color(0.4, 0.4, 0.4)
                    Rectangle(pos=(item["x"] - 15, item["y"] - 15), size=(30, 30))

class SealApp(App):
    def build(self):
        return SealGame()

if __name__ == "__main__":
    SealApp().run()
