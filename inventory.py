import sys
import os
import io
import urllib.request
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
import database


class MultiGameStickerSystem:
    def __init__(self, username=None):

        database.init_db(drop_existing=False)


        self.username = username or "test_user"
        database.ensure_user(self.username)



        self.root = tk.Tk()
        self.root.title("Smart Sprouts - Sticker Collection")
        self.root.geometry("900x700")

        self.root.configure(bg='#88b04b', highlightbackground='#88b04b', highlightthickness=0,
                            bd=0)


        self.games_config = {
            "sequence_game": {
                "name": "Sequence Game",
                "color": "#6FA547",
                "stickers": {
                    1: {"file": "sequence1", "name": "Sequence Star"},
                    2: {"file": "sequence2", "name": "Pattern Master"},
                    3: {"file": "sequence3", "name": "Sequence Champion"}
                }
            },
            "sorting_game": {
                "name": "Sorting Game",
                "color": "#6FA547",
                "stickers": {
                    1: {"file": "sorting1", "name": "Sort Star"},
                    2: {"file": "sorting2", "name": "Organization Pro"},
                    3: {"file": "sorting3", "name": "Sorting Master"}
                }
            },
            "memory_card_game": {
                "name": "Memory Card Game",
                "color": "#6FA547",
                "stickers": {
                    1: {"file": "memory1", "name": "Memory Spark"},
                    2: {"file": "memory2", "name": "Brain Power"},
                    3: {"file": "memory3", "name": "Memory Champion"}
                }
            },
            "math_game": {
                "name": "Math Game",
                "color": "#6FA547",
                "stickers": {
                    1: {"file": "math1", "name": "Number Star"},
                    2: {"file": "math2", "name": "Math Wizard"},
                    3: {"file": "math3", "name": "Calculator Master"}
                }
            }
        }


        self.setup_ui()
        self.load_stickers_ui()

    def setup_ui(self):

        main_content_frame = tk.Frame(self.root, bg='#f7e7ce', relief='flat', bd=0)
        main_content_frame.pack(fill='both', expand=True, padx=20, pady=20)


        title_frame = tk.Frame(main_content_frame, bg='#f7e7ce')
        title_frame.pack(pady=10)


        tk.Label(
            title_frame,
            text="🌟 Sticker Collection 🌟",
            font=('Arial', 22, 'bold'),
            bg='#f7e7ce',
            fg='#172255'
        ).pack()

        tk.Label(
            title_frame,
            text=f"Player: {self.username}",
            font=('Arial', 12),
            bg='#f7e7ce',
            fg='#172255'
        ).pack()


        selector_frame = tk.Frame(main_content_frame, bg='#f7e7ce')
        selector_frame.pack(pady=10)
        self.game_var = tk.StringVar(value="sequence_game")

        for key, cfg in self.games_config.items():
            btn = tk.Radiobutton(
                selector_frame,
                text=cfg['name'],
                variable=self.game_var,
                value=key,
                command=self.load_stickers_ui,
                font=('Arial', 12, 'bold'),
                bg='#f7e7ce',
                fg='#333333',
                selectcolor='#6FA547',
                activebackground='#e6d4b7',
                activeforeground='#6FA547',
                indicatoron=0,
                width=18,
                pady=8,
                relief='raised',
                bd=2
            )
            btn.pack(side=tk.LEFT, padx=5)


        self.stickers_frame = tk.Frame(main_content_frame, bg='#f7e7ce')
        self.stickers_frame.pack(expand=True, fill='both', padx=20, pady=20)

    def load_stickers_ui(self):

        for w in self.stickers_frame.winfo_children():
            w.destroy()


        game = self.game_var.get()
        cfg = self.games_config[game]


        prog = database.get_progress(self.username, game)
        level = prog['best_level']
        if level >= 2:
            database.unlock_sticker(self.username, f"{game}_level_1")
        if level >= 3:
            database.unlock_sticker(self.username, f"{game}_level_2")
        if level >= 4:
            database.unlock_sticker(self.username, f"{game}_level_3")

        unlocked = set(database.get_unlocked_stickers(self.username))


        container = tk.Frame(self.stickers_frame, bg='#f7e7ce')
        container.place(relx=0.5, rely=0.5, anchor='center')


        tk.Label(
            container,
            text=f"{cfg['name']} Stickers",
            font=('Arial', 18, 'bold'),
            bg='#f7e7ce',
            fg='#172255'
        ).grid(row=0, column=0, columnspan=3, pady=(0, 15))


        for idx in range(1, 4):
            sticker_key = f"{game}_level_{idx}"
            is_unlocked = (sticker_key in unlocked)


            frame = tk.Frame(
                container,
                bg='#ffffff',
                relief='raised',
                bd=3,
                highlightbackground='#6FA547' if is_unlocked else '#bdc3c7',
                highlightthickness=3 if is_unlocked else 1
            )
            frame.grid(row=1, column=idx - 1, padx=15, pady=10)


            base = cfg['stickers'][idx]
            variant = 'color' if is_unlocked else 'gray'
            img_url = f"https://raw.githubusercontent.com/SelmaAlic/SmartSprouts/sorting-game/{base}_{variant}.png"
            try:
                data = urllib.request.urlopen(img_url).read()
                img = Image.open(io.BytesIO(data)).resize((80, 80), Image.LANCZOS)
            except:
                img = Image.new('RGBA', (80, 80), (200, 200, 200, 255))

            photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(frame, image=photo, bg='white')
            lbl.image = photo
            lbl.pack(pady=10)


            tk.Label(
                frame,
                text=cfg['stickers'][idx]['name'] if isinstance(cfg['stickers'][idx], dict) else cfg['stickers'][idx],
                font=('Arial', 12, 'bold'),
                bg='white',
                fg='#6FA547' if is_unlocked else '#95a5a6'
            ).pack()

            status_text = '✅ UNLOCKED' if is_unlocked else f'🔒 Reach Level {idx + 1}'
            tk.Label(
                frame,
                text=status_text,
                font=('Arial', 10, 'bold'),
                bg='white',
                fg='#6FA547' if is_unlocked else '#95a5a6'
            ).pack(pady=(0, 5))

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    database.init_db(drop_existing=False)
    user = sys.argv[1] if len(sys.argv) > 1 else 'test_user'
    app = MultiGameStickerSystem(username=user)
    app.run()