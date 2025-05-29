# inventory.py

import sys
import os
import io
import urllib.request
from PIL import Image, ImageTk
import tkinter as tk
import database  # assumes your database.py from earlier

# global that will be set by show_inventory()
current_username = None

def show_inventory(username):
    global current_username
    current_username = username

    # ensure our tables exist
    conn = database.connect_db()
    conn.close()

    # (optional) ensure user row exists in login_info
    # you could insert here if you need:
    # database.add_user(current_username, some_hashed_pw)

    games_config = {
        "sequence_game": {
            "name": "Sequence Game",
            "stickers": {
                1: {"file": "sequence1", "name": "Sequence Star"},
                2: {"file": "sequence2", "name": "Pattern Master"},
                3: {"file": "sequence3", "name": "Sequence Champion"}
            }
        },
        "sorting_game": {
            "name": "Sorting Game",
            "stickers": {
                1: {"file": "sorting1", "name": "Sort Star"},
                2: {"file": "sorting2", "name": "Organization Pro"},
                3: {"file": "sorting3", "name": "Sorting Master"}
            }
        },
        "memory_card_game": {
            "name": "Memory Card Game",
            "stickers": {
                1: {"file": "memory1", "name": "Memory Spark"},
                2: {"file": "memory2", "name": "Brain Power"},
                3: {"file": "memory3", "name": "Memory Champion"}
            }
        },
        "math_game": {
            "name": "Math Game",
            "stickers": {
                1: {"file": "math1", "name": "Number Star"},
                2: {"file": "math2", "name": "Math Wizard"},
                3: {"file": "math3", "name": "Calculator Master"}
            }
        }
    }

    root = tk.Tk()
    root.title("Smart Sprouts - Sticker Collection")
    root.state('zoomed')
    root.configure(bg='#88b04b')

    # Header
    header = tk.Frame(root, bg='#f7e7ce', padx=20, pady=10)
    header.pack(fill='x')
    tk.Label(header,
             text="🌟 Sticker Collection 🌟",
             font=('Arial', 22, 'bold'),
             bg='#f7e7ce',
             fg='#172255').pack()
    tk.Label(header,
             text=f"Player: {current_username}",
             font=('Arial', 12),
             bg='#f7e7ce',
             fg='#172255').pack()

    # Game selector
    selector_frame = tk.Frame(root, bg='#f7e7ce', pady=10)
    selector_frame.pack()
    game_var = tk.StringVar(value="sequence_game")

    def reload_stickers():
        # clear existing
        for w in stickers_frame.winfo_children():
            w.destroy()

        # make a centered container
        container = tk.Frame(stickers_frame, bg='#f7e7ce')
        container.place(relx=0.5, rely=0.5, anchor='center')

        game_key = game_var.get()
        cfg = games_config[game_key]
#THIS PART FETCHES BEST LEVEL FROM DATABASE AND ACCORDING TO IT, UNLOCKS STICKER
        # fetch progress
        prog = database.get_progress(current_username, game_key)
        level = prog.get('best_level', 0)

        # award stickers
        if level >= 2:
            database.unlock_sticker(current_username, f"{game_key}_level_1")
        if level >= 3:
            database.unlock_sticker(current_username, f"{game_key}_level_2")
        if level >= 4:
            database.unlock_sticker(current_username, f"{game_key}_level_3")

        unlocked = set(database.get_unlocked_stickers(current_username))

        # section title
        tk.Label(container,
                 text=f"{cfg['name']} Stickers",
                 font=('Arial', 18, 'bold'),
                 bg='#f7e7ce',
                 fg='#172255')\
          .grid(row=0, column=0, columnspan=3, pady=(0, 15))

        # each sticker
        for idx in range(1, 4):
            key = f"{game_key}_level_{idx}"
            is_unlocked = key in unlocked
            sticker = cfg['stickers'][idx]

            frame = tk.Frame(container,
                             bg='white',
                             bd=3,
                             highlightbackground='#6FA547' if is_unlocked else '#bdc3c7',
                             highlightthickness=3 if is_unlocked else 1)
            frame.grid(row=1, column=idx - 1, padx=15, pady=10)

            variant = 'color' if is_unlocked else 'gray'
            filename = f"{sticker['file']}_{variant}.png"
            local_path = os.path.join("assets", filename)
            if os.path.exists(local_path):
                img = Image.open(local_path).resize((80, 80), Image.LANCZOS)
            else:
                img = Image.new('RGBA', (80, 80), (200, 200, 200, 255))

            photo = ImageTk.PhotoImage(img)
            lbl_img = tk.Label(frame, image=photo, bg='white')
            lbl_img.image = photo
            lbl_img.pack(pady=10)

            tk.Label(frame,
                     text=sticker['name'],
                     font=('Arial', 12, 'bold'),
                     bg='white',
                     fg='#6FA547' if is_unlocked else '#95a5a6').pack()
            status = '✅ UNLOCKED' if is_unlocked else f'🔒 Reach Level {idx+1}'
            tk.Label(frame,
                     text=status,
                     font=('Arial', 10, 'bold'),
                     bg='white',
                     fg='#6FA547' if is_unlocked else '#95a5a6').pack(pady=(0,5))

    # build radio buttons
    for key, cfg in games_config.items():
        rb = tk.Radiobutton(selector_frame,
                            text=cfg['name'],
                            variable=game_var,
                            value=key,
                            command=reload_stickers,
                            font=('Arial',12,'bold'),
                            bg='#f7e7ce',
                            fg='#333333',
                            indicatoron=0,
                            width=18,
                            pady=8,
                            selectcolor='#6FA547',
                            activebackground='#e6d4b7',
                            activeforeground='#6FA547',
                            relief='raised',
                            bd=2)
        rb.pack(side='left', padx=5)

    # area where stickers appear
    stickers_frame = tk.Frame(root, bg='#f7e7ce')
    stickers_frame.pack(expand=True, fill='both', padx=20, pady=20)

    # initial load
    reload_stickers()

    root.mainloop()

