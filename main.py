from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Polygon
from kivy.utils import get_color_from_hex
from game import GameArea
from settings import *

class SealGame(FloatLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        
        self.game_area = GameArea(size_hint=(1, 1))
        self.add_widget(self.game_area)

        self.score_label = Label(text="", font_size='30sp', bold=True, color=COLOR_TEXT_SCORE, pos_hint={'x': 0.1, 'top': 0.95})
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
