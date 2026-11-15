from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle, Polygon
from kivy.utils import get_color_from_hex
import random

# ==========================================
# ИГРОВОЕ ПОЛЕ (Только рисование, без тяжелой математики)
# ==========================================
class GameArea(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.seal_x = 200
        self.items = []
        self.score = 0
        self.lives = 3
        self.spawn_timer = 0
        self.game_over = False
        self.current_mode = "normal"
        self.parent_game = None
        
        # Статичные пузырьки для фона
        self.bg_bubbles = [(random.randint(50, 400), random.randint(150, 800), random.randint(5, 15)) for _ in range(10)]

        # 30 кадров в секунду (вместо 60) - это в 2 раза меньше нагрузки на телефон!
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def start(self, mode, parent):
        self.parent_game = parent
        self.current_mode = mode
        self.seal_x = self.width / 2 if self.width else 200
        self.items = []
        self.score = 0
        self.lives = 1 if mode == "hard" else 3
        self.spawn_timer = 0
        self.game_over = False

    def on_touch_move(self, touch):
        if not self.game_over:
            self.seal_x = max(50, min(self.width - 50, touch.x))
        return True

    def update(self, dt):
        if self.game_over or self.width == 0:
            return

        self.spawn_timer += dt
        rate = 0.8 if self.current_mode == "normal" else 0.5 if self.current_mode == "lol" else 0.4
        
        if self.spawn_timer > rate:
            self.spawn_timer = 0
            x = random.uniform(50, self.width - 50)
            kind = "fish"
            r = random.random()
            if self.current_mode == "normal" and r > 0.8: kind = "trash"
            elif self.current_mode == "lol" and r > 0.6: kind = "demon"
            elif self.current_mode == "hard" and r > 0.5: kind = "bomb"
            
            speed = random.uniform(self.height * 0.2, self.height * 0.35)
            if self.current_mode == "hard": speed *= 1.3
            
            self.items.append({"x": x, "y": self.height + 50, "kind": kind, "speed": speed})

        for item in self.items[:]:
            item["y"] -= item["speed"] * dt
            
            if item["y"] < 150 and item["y"] > 50:
                if abs(item["x"] - self.seal_x) < 70:
                    self.items.remove(item)
                    if item["kind"] == "fish": 
                        self.score += 1
                        if self.parent_game: self.parent_game.update_score(self.score)
                    else: 
                        self.lose_life()
                    continue
            
            if item["y"] < -50:
                if item["kind"] == "fish": 
                    self.lose_life()
                self.items.remove(item)

        self.redraw()

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
            if self.parent_game:
                self.parent_game.end_game(self.score)

    def redraw(self):
        self.canvas.clear()
        with self.canvas:
            # === КРАСИВЫЙ, НО ЛЕГКИЙ ФОН ===
            Color(0.05, 0.2, 0.4) 
            Rectangle(pos=(0, 0), size=self.size)
            Color(0.1, 0.4, 0.7) 
            Rectangle(pos=(0, self.height * 0.4), size=(self.width, self.height * 0.6))
            
            # Песок
            Color(0.8, 0.7, 0.5) 
            Ellipse(pos=(-50, -100), size=(self.width * 0.7, 200)) 
            Ellipse(pos=(self.width * 0.4, -120), size=(self.width * 0.8, 220))

            # Пузырьки
            Color(1, 1, 1, 0.2)
            for bx, by, br in self.bg_bubbles:
                Ellipse(pos=(bx, by), size=(br, br))

            # === ТЮЛЕНЬ ===
            sy = 110
            Color(0, 0, 0, 0.2) # Тень
            Ellipse(pos=(self.seal_x - 60, 70), size=(120, 30))

            Color(0.6, 0.7, 0.8) # Тело
            Ellipse(pos=(self.seal_x - 70, sy - 50), size=(140, 120))
            Color(0.9, 0.95, 1) # Живот
            Ellipse(pos=(self.seal_x - 40, sy - 40), size=(80, 80))
            Color(0.7, 0.8, 0.9) # Голова
            Ellipse(pos=(self.seal_x - 45, sy + 20), size=(90, 90))
            
            # Раны
            if self.lives < 3:
                Color(0.9, 0.8, 0.6) 
                Rectangle(pos=(self.seal_x + 10, sy + 75), size=(30, 12))

            # Глаза (крестики - это просто 4 маленьких квадратика, это очень легко для телефона)
            Color(0.1, 0.1, 0.1)
            if self.lives == 1:
                # Крестики
                Rectangle(pos=(self.seal_x - 30, sy + 60), size=(10, 10))
                Rectangle(pos=(self.seal_x - 20, sy + 60), size=(10, 10))
                Rectangle(pos=(self.seal_x + 10, sy + 60), size=(10, 10))
                Rectangle(pos=(self.seal_x + 20, sy + 60), size=(10, 10))
            else:
                Ellipse(pos=(self.seal_x - 25, sy + 60), size=(15, 15))
                Ellipse(pos=(self.seal_x + 10, sy + 60), size=(15, 15))

            # === ПРЕДМЕТЫ ===
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

# ==========================================
# ГЛАВНЫЙ ЭКРАН (Меню и Кнопки)
# ==========================================
class SealGame(FloatLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        
        # 1. Игровое поле
        self.game_area = GameArea(size_hint=(1, 1))
        self.add_widget(self.game_area)

        # 2. Текст счета
        self.score_label = Label(text="", font_size='30sp', bold=True, color=get_color_from_hex("#FFD700"), pos_hint={'x': 0.1, 'top': 0.95})
        self.add_widget(self.score_label)

        # 3. Меню
        self.menu_layout = FloatLayout()
        title = Label(text="ТЮЛЕНЬ ГЕЙМС", font_size='45sp', bold=True, color=get_color_from_hex("#00FFFF"), pos_hint={'center_x': 0.5, 'center_y': 0.8})
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

        # 4. Пасхалка (Золотая рыбка)
        self.egg_btn = Button(background_color=(0,0,0,0), background_normal='', size_hint=(None, None), size=(100, 100), pos=(20, 20))
        with self.egg_btn.canvas.after:
            Color(1, 0.8, 0.2)
            Ellipse(pos=(20, 30), size=(60, 35))
            Polygon(points=[20, 47.5, 0, 20, 0, 75])
        self.egg_btn.bind(on_release=self.show_egg)
        self.menu_layout.add_widget(self.egg_btn)

        self.egg_lbl = Label(text="Ты нашёл пасхалку!", font_size='20sp', color=get_color_from_hex("#FFF"), pos=(130, 40), opacity=0)
        self.menu_layout.add_widget(self.egg_lbl)
        
        self.add_widget(self.menu_layout)

        # 5. Экран Game Over
        self.go_layout = FloatLayout(opacity=0)
        self.go_lbl = Label(text="", font_size='35sp', bold=True, color=get_color_from_hex("#FFFFFF"), pos_hint={'center_x': 0.5, 'center_y': 0.6})
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

    def update_score(self, score):
        self.score_label.text = str(score)

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
