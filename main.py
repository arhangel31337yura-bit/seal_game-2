from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.utils import get_color_from_hex
from kivy.core.text import Label as CoreLabel
import random

class SealGame(Widget):
    def __init__(self, **kw):
        super().__init__(**kw)
        
        self.seal_x = self.width / 2
        self.items = []
        self.score = 0
        self.lives = 3
        self.spawn_timer = 0
        self.game_over = False
        
        # Запускаем игровой цикл (60 кадров в секунду)
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def on_touch_move(self, touch):
        # Двигаем тюленя за пальцем/мышкой
        if not self.game_over:
            # Ограничиваем движение краями экрана (с учетом размера тюленя)
            seal_half = self.width * 0.15
            self.seal_x = max(seal_half, min(self.width - seal_half, touch.x))
        return True

    def on_touch_down(self, touch):
        # Перезапуск игры по клику, ТОЛЬКО если проиграл
        if self.game_over:
            self.reset_game()
            return True

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.items = []
        self.game_over = False
        self.spawn_timer = 0

    def update(self, dt):
        if self.game_over:
            return

        self.spawn_timer += dt
        
        # Спавним предметы каждые 0.7 секунды
        if self.spawn_timer > 0.7:
            self.spawn_timer = 0
            # Генерируем X в пределах экрана
            x = random.uniform(self.width * 0.1, self.width * 0.9)
            # 80% шанс, что выпадет рыбка, 20% - мусор
            kind = "fish" if random.random() < 0.8 else "trash"
            
            # Скорость падения зависит от высоты экрана (чтобы было комфортно на любом телефоне)
            speed = random.uniform(self.height * 0.2, self.height * 0.35)
            
            self.items.append({
                "x": x, 
                "y": self.height + 50, 
                "kind": kind, 
                "speed": speed
            })

        # Координаты тюленя (внизу экрана)
        self.seal_y = self.height * 0.15
        seal_half_width = self.width * 0.15
        
        # Двигаем предметы
        for item in self.items[:]:
            item["y"] -= item["speed"] * dt

            # Проверка столкновения с тюленем
            # Если предмет пролетает на уровне тюленя и попадает в его X-координаты
            if item["y"] < self.seal_y + (self.width * 0.15) and item["y"] > self.seal_y - (self.width * 0.15):
                if abs(item["x"] - self.seal_x) < seal_half_width:
                    self.items.remove(item)
                    if item["kind"] == "fish":
                        self.score += 1
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
        if self.lives <= 0:
            self.game_over = True

    def redraw(self):
        self.canvas.clear()
        with self.canvas:
            # 1. Фон (водный градиент)
            Color(0.12, 0.42, 0.62)
            Rectangle(pos=(0, 0), size=self.size)
            Color(0.15, 0.50, 0.72)
            Rectangle(pos=(0, self.height * 0.5), size=(self.width, self.height * 0.5))

            # Размеры для масштабирования
            seal_y = self.height * 0.15
            seal_w = self.width * 0.25  # Тюлень занимает 25% ширины экрана
            seal_h = seal_w * 0.8

            # 2. Тюлень
            Color(0.56, 0.64, 0.72) # Тело
            Ellipse(pos=(self.seal_x - seal_w/2, seal_y - seal_h/2), size=(seal_w, seal_h))
            Color(0.85, 0.90, 0.95) # Живот
            Ellipse(pos=(self.seal_x - seal_w*0.3, seal_y - seal_h*0.3), size=(seal_w*0.6, seal_h*0.6))
            Color(0.64, 0.71, 0.78) # Голова
            Ellipse(pos=(self.seal_x - seal_w*0.35, seal_y + seal_h*0.2), size=(seal_w*0.7, seal_w*0.7))
            
            # Глаза
            Color(0.12, 0.17, 0.21)
            Ellipse(pos=(self.seal_x - seal_w*0.2, seal_y + seal_h*0.5), size=(seal_w*0.1, seal_w*0.1))
            Ellipse(pos=(self.seal_x + seal_w*0.1, seal_y + seal_h*0.5), size=(seal_w*0.1, seal_w*0.1))
            
            # Нос
            Color(0.17, 0.23, 0.28)
            Ellipse(pos=(self.seal_x - seal_w*0.05, seal_y + seal_h*0.35), size=(seal_w*0.1, seal_w*0.08))

            # 3. Предметы
            item_w = self.width * 0.1 # Рыбка занимает 10% ширины
            for item in self.items:
                if item["kind"] == "fish":
                    Color(1.0, 0.66, 0.30)
                    Ellipse(pos=(item["x"] - item_w/2, item["y"] - item_w/3), size=(item_w, item_w*0.6))
                    Color(0.88, 0.48, 0.10)
                    Ellipse(pos=(item["x"] - item_w*0.7, item["y"] - item_w/5), size=(item_w*0.3, item_w*0.4))
                else:
                    Color(0.5, 0.5, 0.5)
                    Rectangle(pos=(item["x"] - item_w/2, item["y"] - item_w/2), size=(item_w, item_w))

            # 4. Счёт и Жизни (Рисуем прямо на холсте)
            score_label = CoreLabel(text=f"Счёт: {self.score}", font_size=int(self.width * 0.06), color=(1, 1, 1, 1))
            score_label.refresh()
            Rectangle(texture=score_label.texture, pos=(20, self.height - 80), size=score_label.texture.size)

            if self.game_over:
                # Экран поражения
                Color(0, 0, 0, 0.7)
                Rectangle(pos=(0, 0), size=self.size)
                
                txt = f"ИГРА ОКОНЧЕНА!\n\nПоймано рыбок: {self.score}\n\nКоснись экрана, чтобы играть снова"
                over_label = CoreLabel(text=txt, font_size=int(self.width * 0.07), color=(1, 1, 1, 1), halign="center")
                over_label.refresh()
                Rectangle(texture=over_label.texture, 
                          pos=(self.width/2 - over_label.texture.size[0]/2, self.height/2 - over_label.texture.size[1]/2), 
                          size=over_label.texture.size)
            else:
                # Жизни
                lives_txt = " ".join("❤" for _ in range(max(0, self.lives)))
                lives_label = CoreLabel(text=lives_txt, font_size=int(self.width * 0.06), color=get_color_from_hex("#ff8fab"))
                lives_label.refresh()
                Rectangle(texture=lives_label.texture, pos=(self.width - lives_label.texture.size[0] - 20, self.height - 80), size=lives_label.texture.size)

class SealApp(App):
    def build(self):
        return SealGame()

if __name__ == "__main__":
    SealApp().run()
