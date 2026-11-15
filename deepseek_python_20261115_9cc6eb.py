import tkinter as tk
import random

W, H = 820, 600
SEAL_HALF = 72          # половина ширины тюленя
SEAL_TOP, SEAL_BOTTOM = 410, 585   # вертикальные границы тюленя


class SealGame:
    def __init__(self, root):
        self.root = root
        root.title("Тюлень ловит рыбу 🦭")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=W, height=H,
                                bg="#1b6c9e", highlightthickness=0)
        self.canvas.pack()

        # управление
        root.bind("<Left>",  lambda e: setattr(self, "left", True))
        root.bind("<Right>", lambda e: setattr(self, "right", True))
        root.bind("<KeyRelease-Left>",  lambda e: setattr(self, "left", False))
        root.bind("<KeyRelease-Right>", lambda e: setattr(self, "right", False))
        root.bind("<space>", lambda e: self.restart())
        root.bind("<Motion>", self.on_mouse)

        self.left = self.right = False
        self.after_id = None
        self.reset()

    # ---------- управление ----------
    def on_mouse(self, e):
        if self.game_over:
            return
        new_x = max(SEAL_HALF, min(W - SEAL_HALF, e.x))
        dx = new_x - self.seal_x
        if dx:
            self.seal_x = new_x
            self.canvas.move("seal", dx, 0)

    def restart(self):
        if self.game_over:
            self.reset()

    # ---------- подготовка ----------
    def reset(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.canvas.delete("all")
        self.draw_background()

        self.seal_x = W // 2
        self.draw_seal()

        self.items = []
        self.score = 0
        self.lives = 3
        self.frame = 0
        self.spawn_every = 40     # кадров между появлением предметов
        self.fall_speed = 2.5
        self.game_over = False

        self.score_text = self.canvas.create_text(
            22, 26, anchor="w", text="Счёт: 0", fill="white",
            font=("Segoe UI", 18, "bold"), tags="hud")
        self.lives_text = self.canvas.create_text(
            W - 22, 26, anchor="e", text="❤ ❤ ❤", fill="#ff8fab",
            font=("Segoe UI", 18, "bold"), tags="hud")

        self.loop()

    def draw_background(self):
        colors = ["#4fb3e0", "#3a9ed0", "#2a86bb", "#1f6f9e", "#175c85"]
        band = H // len(colors)
        for i, c in enumerate(colors):
            self.canvas.create_rectangle(0, i * band, W, (i + 1) * band + 1,
                                         fill=c, outline="")
        for _ in range(45):
            x = random.randint(0, W)
            y = random.randint(0, H)
            r = random.randint(2, 6)
            self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                    outline="#bfe6fa", width=1)

    def draw_seal(self):
        x, t = self.seal_x, "seal"
        self.canvas.create_oval(x-72, 470, x+72, 585, fill="#8fa3b8",
                                outline="#6e8499", width=3, tags=t)   # тело
        self.canvas.create_oval(x-46, 500, x+46, 580, fill="#d9e6f2",
                                outline="", tags=t)                  # живот
        self.canvas.create_oval(x-48, 410, x+48, 506, fill="#a3b6c8",
                                outline="#6e8499", width=3, tags=t)   # голова
        for ex in (-26, 12):                                        # глаза
            self.canvas.create_oval(x+ex, 446, x+ex+14, 460,
                                    fill="#1e2b36", outline="", tags=t)
            self.canvas.create_oval(x+ex+2, 447, x+ex+7, 452,
                                    fill="white", outline="", tags=t)
        self.canvas.create_oval(x-9, 470, x+9, 484, fill="#2b3a47",
                                outline="", tags=t)                  # нос

    # ---------- предметы ----------
    def spawn_item(self):
        x, y = random.randint(60, W - 60), -60
        if random.random() < 0.78:
            ids, kind = self.draw_fish(x, y), "fish"
        else:
            ids, kind = self.draw_trash(x, y), "trash"
        self.items.append({
            "ids": ids, "y": y, "kind": kind,
            "speed": self.fall_speed + random.uniform(0, 1.2),
        })

    def draw_fish(self, x, y):
        body = self.canvas.create_oval(x, y, x+46, y+28, fill="#ffa94d",
                                       outline="#e07b1a", width=2)
        tail = self.canvas.create_polygon(x, y+14, x-16, y, x-16, y+28,
                                          fill="#ffa94d", outline="#e07b1a", width=2)
        eye  = self.canvas.create_oval(x+30, y+8, x+37, y+15,
                                       fill="#22313d", outline="")
        return [body, tail, eye]

    def draw_trash(self, x, y):
        bag = self.canvas.create_polygon(
            x, y+30, x+8, y+4, x+22, y, x+36, y+4, x+44, y+30,
            fill="#9aa5ad", outline="#6b7680", width=2)
        blob = self.canvas.create_oval(x+10, y+12, x+34, y+28,
                                       fill="#b6c0c7", outline="")
        return [bag, blob]

    # ---------- игровой цикл ----------
    def loop(self):
        if not self.game_over:
            self.update_game()
        self.after_id = self.root.after(20, self.loop)

    def update_game(self):
        self.frame += 1

        # движение клавишами
        dx = (9 if self.right else 0) - (9 if self.left else 0)
        if dx:
            new_x = max(SEAL_HALF, min(W - SEAL_HALF, self.seal_x + dx))
            real_dx = new_x - self.seal_x
            if real_dx:
                self.seal_x = new_x
                self.canvas.move("seal", real_dx, 0)

        if self.frame % self.spawn_every == 0:
            self.spawn_item()

        # постепенное усложнение
        if self.frame % 600 == 0:
            self.spawn_every = max(16, self.spawn_every - 4)
            self.fall_speed += 0.4

        for item in self.items[:]:
            for i in item["ids"]:
                self.canvas.move(i, 0, item["speed"])
            item["y"] += item["speed"]

            if self.hits_seal(item):
                self.items.remove(item)
                self.delete_item(item)
                if item["kind"] == "fish":
                    self.score += 1
                    self.canvas.itemconfig(self.score_text,
                                           text=f"Счёт: {self.score}")
                else:
                    self.lose_life()
            elif item["y"] > H + 20:
                self.items.remove(item)
                self.delete_item(item)
                if item["kind"] == "fish":
                    self.lose_life()

        self.canvas.tag_raise("hud")

    def hits_seal(self, item):
        b = self.canvas.bbox(item["ids"][0])
        if not b:
            return False
        x1, y1, x2, y2 = b
        return not (x2 < self.seal_x - SEAL_HALF
                    or x1 > self.seal_x + SEAL_HALF
                    or y2 < SEAL_TOP or y1 > SEAL_BOTTOM)

    def delete_item(self, item):
        for i in item["ids"]:
            self.canvas.delete(i)

    def lose_life(self):
        self.lives -= 1
        self.canvas.itemconfig(self.lives_text,
                               text=" ".join("❤" for _ in range(self.lives)))
        if self.lives <= 0:
            self.end_game()

    def end_game(self):
        self.game_over = True
        for item in self.items:
            self.delete_item(item)
        self.items.clear()

        self.canvas.create_rectangle(0, 0, W, H, fill="#0b2d45",
                                     stipple="gray50", outline="")
        self.canvas.create_text(W//2, H//2 - 70, text="Игра окончена!",
                                fill="white", font=("Segoe UI", 40, "bold"))
        self.canvas.create_text(W//2, H//2 + 5, text=f"Поймано рыбок: {self.score}",
                                fill="#ffd166", font=("Segoe UI", 24, "bold"))
        self.canvas.create_text(W//2, H//2 + 75,
                                text="Нажмите ПРОБЕЛ, чтобы сыграть ещё",
                                fill="#cde9f7", font=("Segoe UI", 18))


def main():
    root = tk.Tk()
    SealGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()