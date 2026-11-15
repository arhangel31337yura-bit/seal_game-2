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
        
        # Настройки игры
        self.seal_x = self.width / 2
        self.seal_y = 100
        self.items = []
        self.score = 0
        self.lives = 3
        self.spawn_timer = 0
        self.game_over = False
        
        # Текст на экране (Счёт и Жизни)
        self.score_label = Label(text="Счёт: 0", font_size='24sp', bold=True, 
                                 pos_hint={'x': 0.05, 'top': 0.95}, color=(1,1,1,1))
        self.lives_label = Label(text="❤ ❤ ❤", font_size='24sp', bold=True, 
                                 pos_hint={'right': 0.95, 'top': 0.95}, color=get_color_from_hex("#ff8fab"))
        
        self.game_over_label = Label(text="", font_size='30sp', bold=True, 
                                     pos_hint={'center_x': 0.5, 'center_y': 0.5}, 
                                     halign='center', color=(1,1,1,1))
        
        self.add_widget(self.score_label)
        self.add_widget(self.lives_label)
        self.add_widget(self.game_over_label)
        
        # Запускаем игровой цикл (60 кадров в секунду)
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def on_touch_move(self, touch):
        # Двигаем тюленя за пальцем/мышкой (только по горизонтали)
        if not self.game_over:
            self.seal_x = max(70, min(self.width - 70, touch.x))
        return True

    def on_touch_down(self, touch):
        # Перезапуск игры по клику, если проиграл
        if self.game_over:
            self.reset_game()
            return True

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.items = []
        self.game_over = False
        self.score_label.text = "Счёт: 0"
        self.lives_label.text = "❤ ❤ ❤"
        self.game_over_label.text = ""

    def update(self, dt):
        if self.game_over:
            return

        self.spawn_timer += dt
        
        # Спавним предметы каждые 0.6 секунды
        if self.spawn_timer > 0.6:
            self.spawn_timer = 0
            x = random.randint(50, int(self.width) - 50)
            # 80% шанс, что выпадет рыбка, 20% - мусор
            kind = "fish" if random.random() < 0.8 else "trash"
            self.items.append({
                "x": x, 
                "y": self.height, 
                "kind": kind, 
                "speed": random.uniform(250, 400)
            })

        # Двигаем предметы
        for item in self.items[:]:
            item["y"] -= item["speed"] * dt

            # Проверка столкновения с тюленем
            if item["y"] < self.seal_y + 70 and item["y"] > self.seal_y - 50:
                if abs(item["x"] - self.seal_x) < 60:
                    self.items.remove(item)
                    if item["kind"] == "fish":
                        self.score += 1
                        self.score_label.text = f"Счёт: {self.score}"
                    else:
                        self.lose_life()
                    continue

            # Если предмет упал за экран
            if item["y"] < -50:
                self.items.remove(item)
                # Если упустили рыбку - теряем жизнь
                if item["kind"] == "fish":
                    self.lose_life()

        self.redraw()

    def lose_life(self):
        self.lives -= 1
        self.lives_label.text = " ".join("❤" for _ in range(max(0, self.lives)))
        if self.lives <= 0:
            self.game_over = True
            self.game_over_label.text = f"ИГРА ОКОНЧЕНА!\nПоймано рыбок: {self.score}\n\nКоснись экрана, чтобы играть снова"

    def redraw(self):
        # Очищаем экран и рисуем всё заново
        self.canvas.clear()
        with self.canvas:
            # Фон (водный градиент)
            Color(0.12, 0.42, 0.62)
            Rectangle(pos=(0, 0), size=self.size)
            Color(0.15, 0.50, 0.72)
            Rectangle(pos=(0, self.height * 0.5), size=(self.width, self.height * 0.5))

            # Тюлень
            Color(0.56, 0.64, 0.72) # Тело
            Ellipse(pos=(self.seal_x - 70, self.seal_y - 50), size=(140, 120))
            Color(0.85, 0.90, 0.95) # Живот
            Ellipse(pos=(self.seal_x - 45, self.seal_y - 40), size=(90, 90))
            Color(0.64, 0.71, 0.78) # Голова
            Ellipse(pos=(self.seal_x - 45, self.seal_y + 20), size=(90, 90))
            Color(0.12, 0.17, 0.21) # Глаза
            Ellipse(pos=(self.seal_x - 30, self.seal_y + 60), size=(14, 14))
            Ellipse(pos=(self.seal_x + 16, self.seal_y + 60), size=(14, 14))
            Color(1, 1, 1) # Блики
            Ellipse(pos=(self.seal_x - 27, self.seal_y + 63), size=(5, 5))
            Ellipse(pos=(self.seal_x + 19, self.seal_y + 63), size=(5, 5))
            Color(0.17, 0.23, 0.28) # Нос
            Ellipse(pos=(self.seal_x - 8, self.seal_y + 40), size=(16, 12))

            # Предметы (рыбки и мусор)
            for item in self.items:
                if item["kind"] == "fish":
                    Color(1.0, 0.66, 0.30) # Оранжевая рыбка
                    Ellipse(pos=(item["x"] - 20, item["y"] - 15), size=(40, 30))
                    Color(0.88, 0.48, 0.10) # Хвост
                    Ellipse(pos=(item["x"] - 28, item["y"] - 8), size=(15, 16))
                else:
                    Color(0.5, 0.5, 0.5) # Мусор
                    Rectangle(pos=(item["x"] - 20, item["y"] - 20), size=(40, 40))

class SealApp(App):
    def build(self):
        return SealGame()

if __name__ == "__main__":
    SealApp().run()
