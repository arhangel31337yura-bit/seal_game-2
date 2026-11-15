from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle, Line, Polygon, RoundedRectangle
from kivy.utils import get_color_from_hex
import random
import math

# Отдельный холст для рисования игры (он будет на заднем плане)
class GameCanvas(Widget):
    pass

class SealGame(FloatLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.state = "menu"
        self.score = 0
        self.lives = 3
        self.items = []
        self.bubbles = []
        self.spawn_timer = 0
        self.boss_timer = 0
        self.blink_timer = 0
        self.is_blinking = False
        self.lasers = []
        self.gun_cooldown = 0
        self.seal_x = 200 # По умолчанию, чтобы не было ошибки при старте

        # 1. Слой для рисования игры (самый нижний)
        self.game_canvas = GameCanvas()
        self.add_widget(self.game_canvas)

        # 2. HUD (Счёт)
        self.score_label = Label(
            text="0", font_size='28sp', bold=True, 
            color=get_color_from_hex("#FFD700"), 
            pos_hint={'x': 0.15, 'top': 0.95}, halign='left'
        )
        self.add_widget(self.score_label)

        # 3. Меню
        self.menu_layout = FloatLayout()
        self.create_menu()
        self.add_widget(self.menu_layout)

        # 4. Экран Game Over
        self.game_over_layout = FloatLayout(opacity=0)
        self.game_over_label = Label(
            text="", font_size='40sp', bold=True, 
            color=get_color_from_hex("#FFFFFF"),
            pos_hint={'center_x': 0.5, 'center_y': 0.7}, halign='center'
        )
        self.restart_btn = Button(
            text="ИГРАТЬ СНОВА", font_size='24sp', bold=True,
            size_hint=(0.6, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.35},
            background_color=get_color_from_hex("#4cd137")
        )
        self.restart_btn.bind(on_release=self.go_to_menu)
        self.game_over_layout.add_widget(self.game_over_label)
        self.game_over_layout.add_widget(self.restart_btn)
        self.add_widget(self.game_over_layout)

        # 5. Пасхалка (Рыбка-кнопка)
        self.easter_egg_btn = Button(
            background_color=(0,0,0,0), background_normal='', background_down='', 
            size_hint=(None, None), size=(100, 100), pos=(30, 30)
        )
        # Рисуем рыбку прямо на кнопке
        with self.easter_egg_btn.canvas.after:
            Color(1, 0.8, 0.2)
            Ellipse(pos=(20, 30), size=(60, 35))
            Polygon(points=[20, 47.5, 0, 20, 0, 75])
            Color(0, 0, 0)
            Ellipse(pos=(65, 42), size=(8, 8))
            Color(1, 1, 1)
            Ellipse(pos=(67, 44), size=(3, 3))

        self.easter_egg_btn.bind(on_release=self.show_easter_egg)
        
        self.easter_egg_bubble = Label(
            text="Ты нашёл пасхалку, молодец!",
            font_size='20sp', bold=True, color=get_color_from_hex("#0b2d45"),
            size_hint=(None, None), size=(300, 80), pos=(140, 40),
            opacity=0, halign='center', valign='middle'
        )
        self.easter_egg_bubble.bind(size=self.easter_egg_bubble.setter('text_size'))

        self.menu_layout.add_widget(self.easter_egg_btn)
        self.menu_layout.add_widget(self.easter_egg_bubble)

        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def create_menu(self):
        cx, cy = 0.5, 0.5
        self.menu_title = Label(text="ТЮЛЕНЬ ГЕЙМС", font_size='50sp', bold=True, 
                                color=get_color_from_hex("#00FFFF"), pos_hint={'center_x': cx, 'center_y': 0.85})
        
        btn_normal = Button(text="ОБЫЧНАЯ РЫБАЛКА", size_hint=(0.7, 0.1), pos_hint={'center_x': cx, 'center_y': cy + 0.1},
                            background_color=get_color_from_hex("#3498db"))
        btn_normal.bind(on_release=lambda x: self.start_game("normal"))
        
        btn_lol = Button(text="ЛОЛ-МОД: АННИГИЛЯТОР", size_hint=(0.7, 0.1), pos_hint={'center_x': cx, 'center_y': cy - 0.05},
                         background_color=get_color_from_hex("#e84118"))
        btn_lol.bind(on_release=lambda x: self.start_game("lol"))
        
        btn_hard = Button(text="ХАРДМОД: ИСПЫТАНИЕ", size_hint=(0.7, 0.1), pos_hint={'center_x': cx, 'center_y': cy - 0.2},
                          background_color=get_color_from_hex("#8e44ad"))
        btn_hard.bind(on_release=lambda x: self.start_game("hard"))

        self.menu_layout.add_widget(self.menu_title)
        self.menu_layout.add_widget(btn_normal)
        self.menu_layout.add_widget(btn_lol)
        self.menu_layout.add_widget(btn_hard)

    def show_easter_egg(self, instance):
        self.easter_egg_bubble.opacity = 1
        Clock.schedule_once(self.hide_easter_egg, 3.0)

    def hide_easter_egg(self, dt):
        self.easter_egg_bubble.opacity = 0

    def start_game(self, mode):
        self.state = mode
        self.score = 0
        self.lives = 1 if mode == "hard" else 3
        self.items = []
        self.bubbles = []
        self.lasers = []
        self.spawn_timer = 0
        self.boss_timer = 0
        self.seal_x = self.width / 2
        
        self.score_label.text = "0"
        self.menu_layout.opacity = 0
        self.game_over_layout.opacity = 0

    def go_to_menu(self, instance):
        self.state = "menu"
        self.game_over_layout.opacity = 0
        self.menu_layout.opacity = 1

    def on_touch_down(self, touch):
        if self.state in ["normal", "lol", "hard"]:
            if self.state == "lol" and self.gun_cooldown <= 0:
                self.lasers.append({"x": self.seal_x, "y": self.height * 0.2, "time": 0.15})
                self.gun_cooldown = 0.3
                self.check_hit(touch.x, touch.y)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.state in ["normal", "lol", "hard"]:
            self.seal_x = max(self.width * 0.15, min(self.width * 0.85, touch.x))
        return super().on_touch_move(touch)

    def check_hit(self, tx, ty):
        for item in self.items[:]:
            if item["kind"] in ["demon", "boss"]:
                if math.hypot(item["x"] - tx, item["y"] - ty) < 70:
                    self.items.remove(item)
                    self.score += 5 if item["kind"] == "demon" else 50
                    self.score_label.text = str(self.score)

    def update(self, dt):
        if self.state == "menu" or self.state == "game_over":
            self.redraw()
            return

        # Если ширина еще не определилась, ставим тюленя по центру
        if self.seal_x == 0 and self.width > 0:
            self.seal_x = self.width / 2

        self.gun_cooldown -= dt
        self.blink_timer += dt

        if self.blink_timer > 3:
            self.is_blinking = True
            if self.blink_timer > 3.2:
                self.is_blinking = False
                self.blink_timer = 0

        if random.random() < 0.1:
            self.bubbles.append({"x": random.randint(0, int(self.width) if self.width > 0 else 800), "y": -20, "r": random.randint(5, 15), "speed": random.uniform(50, 150)})
        for b in self.bubbles[:]:
            b["y"] += b["speed"] * dt
            if b["y"] > self.height + 50: self.bubbles.remove(b)

        self.spawn_timer += dt
        rate = 0.6 if self.state == "normal" else 0.4 if self.state == "lol" else 0.3
        
        if self.spawn_timer > rate:
            self.spawn_timer = 0
            x = random.uniform(self.width * 0.1, self.width * 0.9)
            kind = "fish"
            r = random.random()
            if self.state == "normal":
                if r > 0.8: kind = "trash"
                elif r > 0.9: kind = "star"
                elif r > 0.95: kind = "medkit"
            elif self.state == "lol":
                if r > 0.6: kind = "demon"
                elif r > 0.9: kind = "star"
            elif self.state == "hard":
                if r > 0.5: kind = "bomb"
                elif r > 0.8: kind = "star"
                elif r > 0.9: kind = "medkit"

            speed = random.uniform(self.height * 0.2, self.height * 0.4)
            if self.state == "hard": speed *= 1.4
            self.items.append({"x": x, "y": self.height + 50, "kind": kind, "speed": speed})

        self.boss_timer += dt
        if self.boss_timer > 15 and not any(i["kind"] == "boss" for i in self.items) and self.state != "hard":
            self.boss_timer = 0
            self.items.append({"x": self.width/2, "y": self.height + 100, "kind": "boss", "speed": 100, "dir": 1})

        for item in self.items[:]:
            item["y"] -= item["speed"] * dt
            if item["kind"] == "boss":
                item["x"] += item["dir"] * 150 * dt
                if item["x"] < 100 or item["x"] > self.width - 100: item["dir"] *= -1

            if item["y"] < self.height * 0.15 + 60 and item["y"] > self.height * 0.15 - 60:
                if abs(item["x"] - self.seal_x) < self.width * 0.15:
                    if item["kind"] == "fish": 
                        self.score += 1
                        self.score_label.text = str(self.score)
                    elif item["kind"] == "star": 
                        self.score += 3
                        self.score_label.text = str(self.score)
                    elif item["kind"] in ["trash", "demon", "bomb"]: self.lose_life()
                    elif item["kind"] == "medkit": self.lives += 1
                    
                    if item["kind"] != "boss": self.items.remove(item)
                    continue

            if item["y"] < -100:
                if item["kind"] == "fish": self.lose_life()
                self.items.remove(item)

        for l in self.lasers[:]:
            l["time"] -= dt
            if l["time"] <= 0: self.lasers.remove(l)

        self.redraw()

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0: self.end_game()

    def end_game(self):
        self.state = "game_over"
        self.game_over_label.text = f"ИГРА ОКОНЧЕНА!\n\nТвой счёт: {self.score}"
        self.game_over_layout.opacity = 1

    def draw_heart(self, x, y, size):
        Color(1, 0.3, 0.5)
        Ellipse(pos=(x, y + size*0.25), size=(size*0.55, size*0.55))
        Ellipse(pos=(x + size*0.45, y + size*0.25), size=(size*0.55, size*0.55))
        Polygon(points=[x, y + size*0.4, x + size*0.5, y + size, x + size, y + size*0.4])

    def draw_fish_icon(self, x, y, size):
        Color(1, 0.8, 0.2)
        Ellipse(pos=(x, y), size=(size*1.2, size*0.7))
        Polygon(points=[x, y + size*0.35, x - size*0.4, y, x - size*0.4, y + size*0.7])
        Color(0, 0, 0)
        Ellipse(pos=(x + size*0.8, y + size*0.4), size=(size*0.15, size*0.15))

    def draw_star(self, x, y, size):
        Color(1, 0.9, 0.2)
        pts = []
        for i in range(10):
            angle = math.pi / 5 * i - math.pi / 2
            r = size if i % 2 == 0 else size * 0.4
            pts.extend([x + r * math.cos(angle), y + r * math.sin(angle)])
        Polygon(points=pts)

    def redraw(self):
        # Очищаем ТОЛЬКО холст игры, не трогая кнопки
        self.game_canvas.canvas.clear()
        
        with self.game_canvas.canvas:
            Color(0.1, 0.4, 0.7)
            Rectangle(pos=(0, 0), size=self.size)
            Color(0.15, 0.5, 0.8)
            Rectangle(pos=(0, self.height * 0.5), size=(self.width, self.height * 0.5))

            for b in self.bubbles:
                Color(1, 1, 1, 0.3)
                Ellipse(pos=(b["x"] - b["r"], b["y"] - b["r"]), size=(b["r"]*2, b["r"]*2))

            if self.state == "menu":
                if self.easter_egg_bubble.opacity > 0:
                    Color(1, 1, 1, 0.9)
                    RoundedRectangle(pos=(140, 40), size=(300, 80), radius=[15,])
                    Color(0.1, 0.4, 0.7)
                    Line(points=[140, 80, 120, 60, 140, 60], width=2)

            if self.state in ["menu", "game_over"]:
                return 

            seal_w = self.width * 0.25
            seal_h = seal_w * 0.8
            sy = self.height * 0.15
            sx = self.seal_x

            Color(0, 0, 0, 0.2)
            Ellipse(pos=(sx - seal_w/2, sy - seal_h/2 - 10), size=(seal_w, 20))
            Color(0.6, 0.7, 0.8)
            Ellipse(pos=(sx - seal_w/2, sy - seal_h/2), size=(seal_w, seal_h))
            Color(0.9, 0.95, 1)
            Ellipse(pos=(sx - seal_w*0.3, sy - seal_h*0.3), size=(seal_w*0.6, seal_h*0.6))
            Color(0.7, 0.8, 0.9)
            Ellipse(pos=(sx - seal_w*0.35, sy + seal_h*0.2), size=(seal_w*0.7, seal_w*0.7))
            
            if self.state == "lol":
                Color(0.3, 0.3, 0.3)
                Rectangle(pos=(sx - 10, sy + seal_h/2), size=(20, 50))
                Color(0.9, 0.2, 0.1)
                Rectangle(pos=(sx - 20, sy + seal_h/2 + 30), size=(40, 20))
                Color(0, 1, 1)
                for l in self.lasers:
                    Line(points=[sx, sy + seal_h/2 + 50, sx, self.height], width=4)

            if not self.is_blinking:
                Color(0.1, 0.1, 0.1)
                Ellipse(pos=(sx - seal_w*0.2, sy + seal_h*0.5), size=(seal_w*0.1, seal_w*0.1))
                Ellipse(pos=(sx + seal_w*0.1, sy + seal_h*0.5), size=(seal_w*0.1, seal_w*0.1))

            item_w = self.width * 0.12
            for item in self.items:
                ix, iy = item["x"], item["y"]
                if item["kind"] == "fish":
                    Color(1.0, 0.6, 0.2)
                    Ellipse(pos=(ix - item_w/2, iy - item_w/4), size=(item_w, item_w/2))
                    Polygon(points=[ix - item_w/2, iy, ix - item_w, iy - item_w/3, ix - item_w, iy + item_w/3])
                elif item["kind"] == "star":
                    self.draw_star(ix, iy, item_w/1.5)
                elif item["kind"] == "trash":
                    Color(0.4, 0.4, 0.4)
                    Rectangle(pos=(ix - item_w/2, iy - item_w/2), size=(item_w, item_w))
                elif item["kind"] == "demon":
                    Color(0.8, 0.1, 0.1)
                    Polygon(points=[ix, iy + item_w/2, ix + item_w/2, iy, ix, iy - item_w/2, ix - item_w/2, iy])
                    Color(1, 1, 0)
                    Ellipse(pos=(ix - 5, iy - 5), size=(10, 10))
                elif item["kind"] == "bomb":
                    Color(0.1, 0.1, 0.1)
                    Ellipse(pos=(ix - item_w/2, iy - item_w/2), size=(item_w, item_w))
                    Color(1, 0.5, 0)
                    Line(points=[ix, iy + item_w/2, ix + 10, iy + item_w/2 + 15], width=3)
                elif item["kind"] == "medkit":
                    Color(1, 1, 1)
                    Rectangle(pos=(ix - item_w/2, iy - item_w/2), size=(item_w, item_w))
                    Color(1, 0, 0)
                    Rectangle(pos=(ix - 5, iy - 15), size=(10, 30))
                    Rectangle(pos=(ix - 15, iy - 5), size=(30, 10))
                elif item["kind"] == "boss":
                    Color(0.6, 0, 0)
                    Ellipse(pos=(ix - 80, iy - 80), size=(160, 160))
                    Color(1, 0, 0)
                    Ellipse(pos=(ix - 30, iy), size=(20, 20))
                    Ellipse(pos=(ix + 10, iy), size=(20, 20))

            # --- HUD ---
            self.draw_fish_icon(20, self.height - 60, 30)
            for i in range(max(0, self.lives)):
                self.draw_heart(self.width - 60 - (i * 40), self.height - 55, 30)

class SealApp(App):
    def build(self):
        return SealGame()

if __name__ == "__main__":
    SealApp().run()
