from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle, Polygon
from kivy.utils import get_color_from_hex
import random

class SealGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Состояние игры
        self.state = "menu"  # menu, normal, lol, hard, game_over, easter_egg
        self.score = 0
        self.lives = 3
        self.items = []
        self.spawn_timer = 0
        self.seal_x = 200
        
        # --- HUD (Счёт и Жизни) ---
        # В МВП использовались Label, и они работали.
        self.score_label = Label(text="0", font_size='28sp', bold=True, color=get_color_from_hex("#FFD700"), pos_hint={'x': 0.1, 'top': 0.95})
        self.lives_label = Label(text="❤ ❤ ❤", font_size='28sp', bold=True, color=get_color_from_hex("#FF4D85"), pos_hint={'right': 0.9, 'top': 0.95})
        self.add_widget(self.score_label)
        self.add_widget(self.lives_label)
        self.hide_hud()

        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def hide_hud(self):
        self.score_label.opacity = 0
        self.lives_label.opacity = 0

    def show_hud(self):
        self.score_label.opacity = 1
        self.lives_label.opacity = 1

    def on_touch_down(self, touch):
        if self.state == "menu":
            # Кнопки меню (координаты клика)
            if 250 < touch.x < 550:
                if 350 < touch.y < 410: self.start_game("normal")
                elif 250 < touch.y < 310: self.start_game("lol")
                elif 150 < touch.y < 210: self.start_game("hard")
            
            # Пасхалка (рыбка в левом нижнем углу)
            if 20 < touch.x < 100 and 20 < touch.y < 100:
                self.state = "easter_egg"
                Clock.schedule_once(self.go_to_menu, 2.0)
                
        elif self.state == "game_over":
            # Кнопка "В меню"
            if 250 < touch.x < 550 and 150 < touch.y < 210:
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
        
        self.score_label.text = "0"
        self.lives_label.text = " ".join("❤" for _ in range(self.lives))
        self.show_hud()

    def go_to_menu(self, dt):
        self.state = "menu"
        self.hide_hud()

    def update(self, dt):
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
                        if item["kind"] == "fish": 
                            self.score += 1
                            self.score_label.text = str(self.score)
                        else: 
                            self.lives -= 1
                            self.lives_label.text = " ".join("❤" for _ in range(max(0, self.lives)))
                        continue
                
                if item["y"] < -50:
                    if item["kind"] == "fish": 
                        self.lives -= 1
                        self.lives_label.text = " ".join("❤" for _ in range(max(0, self.lives)))
                    self.items.remove(item)
            
            if self.lives <= 0:
                self.state = "game_over"

        self.redraw()

    def redraw(self):
        self.canvas.clear()
        with self.canvas:
            # === КРАСИВЫЙ И БЕЗОПАСНЫЙ ФОН ===
            # Градиент воды
            Color(0.05, 0.2, 0.4) 
            Rectangle(pos=(0, 0), size=self.size)
            Color(0.1, 0.4, 0.7) 
            Rectangle(pos=(0, self.height * 0.4), size=(self.width, self.height * 0.6))
            
            # Лучи света
            Color(1, 1, 1, 0.05)
            Polygon(points=[self.width*0.2, self.height, self.width*0.4, 0, self.width*0.1, 0])
            Polygon(points=[self.width*0.8, self.height, self.width*0.9, 0, self.width*0.6, 0])

            # Песчаное дно
            Color(0.8, 0.7, 0.5) 
            Ellipse(pos=(-50, -100), size=(self.width * 0.7, 200)) 
            Ellipse(pos=(self.width * 0.4, -120), size=(self.width * 0.8, 220))

            # Статичные пузырьки
            Color(1, 1, 1, 0.15)
            for i in range(10):
                bx = (i * 73) % int(self.width)
                by = (i * 157) % int(self.height)
                br = 10 + (i * 5) % 20
                Ellipse(pos=(bx, by), size=(br, br))

            if self.state == "menu" or self.state == "easter_egg":
                self.draw_menu()
            elif self.state == "game_over":
                self.draw_game_over()
            else:
                self.draw_game()

    def draw_menu(self):
        # Заголовок (полоски вместо текста)
        Color(0, 1, 1)
        Rectangle(pos=(self.width/2 - 150, self.height - 100), size=(300, 40))
        Rectangle(pos=(self.width/2 - 200, self.height - 140), size=(400, 20))

        # Кнопки (просто цветные прямоугольники)
        Color(0.2, 0.6, 0.8) 
        Rectangle(pos=(250, 350), size=(300, 60))
        Color(0.9, 0.2, 0.1) 
        Rectangle(pos=(250, 250), size=(300, 60))
        Color(0.5, 0.2, 0.6) 
        Rectangle(pos=(250, 150), size=(300, 60))

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
        Rectangle(pos=(250, 150), size=(300, 60))
        
        Color(1, 1, 1)
        Rectangle(pos=(self.width/2 - 100, self.height/2 + 50), size=(200, 20))

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

class SealApp(App):
    def build(self):
        return SealGame()

if __name__ == "__main__":
    SealApp().run()
        return SealGame()

if __name__ == "__main__":
    import traceback
    try:
        SealApp().run()
    except Exception:
        # Если произошла ошибка, сохраняем её в файл
        error_text = traceback.format_exc()
        try:
            # Пытаемся сохранить в папку Загрузки
            with open("/sdcard/Download/seal_error.txt", "w", encoding="utf-8") as f:
                f.write(error_text)
        except:
            pass # Если не получилось, просто молчим
