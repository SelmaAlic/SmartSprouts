import tkinter as tk
from PIL import Image, ImageTk
import os
import database

current_username = None

def show_inventory(username):
    global current_username
    current_username = username

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
        },
    }

    root = tk.Tk()
    root.title("Smart Sprouts — Sticker Collection")
    root.state('zoomed')
    root.configure(bg='#88b04b')

    hdr = tk.Frame(root, bg='#f7e7ce', pady=10)
    hdr.pack(fill='x')
    tk.Label(
        hdr,
        text="🌟 Sticker Collection 🌟",
        font=('Arial', 22, 'bold'),
        bg='#f7e7ce', fg='#172255'
    ).pack()
    tk.Label(
        hdr,
        text=f"Player: {current_username}",
        font=('Arial', 12),
        bg='#f7e7ce', fg='#172255'
    ).pack()

    selector = tk.Frame(root, bg='#f7e7ce', pady=10)
    selector.pack()
    game_var = tk.StringVar(value='sequence_game')

    sticker_area = tk.Frame(root, bg='#f7e7ce')
    sticker_area.pack(expand=True, fill='both', padx=20, pady=20)

    def reload_stickers():
        for w in sticker_area.winfo_children():
            w.destroy()

        container = tk.Frame(sticker_area, bg='#f7e7ce')
        container.pack(expand=True)

        key = game_var.get()
        cfg = games_config[key]
        unlocked = set(database.get_unlocked_stickers(current_username))

        title = tk.Label(
            container,
            text=f"{cfg['name']} Stickers",
            font=('Arial', 18, 'bold'),
            bg='#f7e7ce', fg='#172255'
        )
        title.grid(row=0, column=0, columnspan=3, pady=(0,15))

        for idx in range(1, 4):
            base = cfg['stickers'][idx]
            sticker_key = base['file']
            is_unlocked = sticker_key in unlocked

            frame = tk.Frame(
                container,
                bg='white',
                bd=3,
                highlightbackground='#6FA547' if is_unlocked else '#bdc3c7',
                highlightthickness=3 if is_unlocked else 1
            )
            frame.grid(row=1, column=idx-1, padx=15, pady=10)

            if is_unlocked:
                filename = f"{base['file']}.png"
            else:
                filename = f"{base['file']}_gray.png"

            local = os.path.join('assets', filename)
            if os.path.exists(local):
                img = Image.open(local).resize((80,80), Image.LANCZOS)
            else:
                img = Image.new('RGBA', (80,80), (200,200,200,255))

            photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(frame, image=photo, bg='white')
            lbl.image = photo
            lbl.pack(pady=10)

            tk.Label(
                frame,
                text=base['name'],
                font=('Arial',12,'bold'),
                bg='white',
                fg='#6FA547' if is_unlocked else '#95a5a6'
            ).pack()

            if is_unlocked:
                status = '✅ UNLOCKED'
                tk.Label(
                    frame,
                    text=status,
                    font=('Arial',10,'bold'),
                    bg='white',
                    fg='#6FA547'
                ).pack(pady=(0,5))

    for game_key, cfg in games_config.items():
        rb = tk.Radiobutton(
            selector,
            text=cfg['name'],
            variable=game_var,
            value=game_key,
            command=reload_stickers,
            font=('Arial',12,'bold'),
            bg='#f7e7ce',
            fg='#333333',
            indicatoron=0,
            width=18,
            pady=8
        )
        rb.pack(side='left', padx=5)

    reload_stickers()
    root.mainloop()
