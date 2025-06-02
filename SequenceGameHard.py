import tkinter as tk
from PIL import Image, ImageTk
import random
from datetime import datetime
from database import get_progress, upsert_progress, unlock_sticker, get_unlocked_stickers

DB_PATH = "database.db"
GAME_NAME = "sequence_hard"
MAX_ROUNDS = 10
FLASH_SPEED = 650
COLORS = ["red", "green", "blue", "yellow", "purple", "orange"]

sequence = []
user_sequence = []
current_round = 1
mistakes = 0
start_time = None

current_username = None
unlocked_stickers = set()

root = None
message_label = None
frame_buttons = None
start_button = None
try_again_button = None
label_best = None
color_buttons = {}

def build_ui():
    global root, message_label, frame_buttons, start_button, label_best, color_buttons

    root.title("Sequence Game - Hard")
    root.configure(bg="#88B04B")
    root.state("zoomed")
    root.resizable(True, True)

    frm = tk.Frame(root, bg="#f7e7ce", padx=20, pady=20)
    frm.pack(expand=True, fill="both")

    tk.Label(frm, text="Remember the Sequence!", font=("Arial",24,"bold"), bg="#f7e7ce")\
        .pack(pady=10)

    best = get_progress(current_username, GAME_NAME).get("best_level", 0)
    label_best = tk.Label(frm, text=f"Best Round: {best}", font=("Arial",16), bg="#f7e7ce")
    label_best.pack(pady=5)

    message_label = tk.Label(frm, text="", font=("Arial",18), bg="#f7e7ce")
    message_label.pack(pady=10)

    frame_buttons = tk.Frame(frm, bg="#f7e7ce")
    frame_buttons.pack(pady=10)
    color_buttons.clear()
    for i, color in enumerate(COLORS):
        btn = tk.Button(
            frame_buttons,
            bg=color,
            width=8,
            height=4,
            command=lambda c=color: user_input(c)
        )
        btn.grid(row=i//3, column=i%3, padx=15, pady=10)
        color_buttons[color] = btn

    start_button = tk.Button(frm, text="Start Game", font=("Arial",18), bg="#88B04B", command=start_game)
    start_button.pack(pady=20)

def start_game():
    global sequence, user_sequence, mistakes, current_round, start_time, try_again_button

    if try_again_button:
        try_again_button.destroy()

    sequence.clear()
    user_sequence.clear()
    mistakes = 0
    current_round = 1

    label_best.config(
        text=f"Best Round: {get_progress(current_username, GAME_NAME).get('best_level',0)}"
    )

    start_time = datetime.now()
    next_round()

def next_round():
    global current_round

    if current_round > MAX_ROUNDS:
        message_label.config(text="Great Job! Finished all rounds!")
        score = current_round - 1
        upsert_progress(current_username, GAME_NAME, score)
        _unlock_sequence_stickers(score)
        return

    message_label.config(text=f"Round {current_round}")
    user_sequence.clear()
    sequence.append(random.choice(COLORS))
    root.after(FLASH_SPEED, play_sequence)

def play_sequence():
    for i, color in enumerate(sequence):
        root.after(i * FLASH_SPEED, lambda c=color: flash_button(c))

def flash_button(color):
    btn = color_buttons[color]
    orig = btn.cget("bg")
    btn.config(bg="white")
    root.after(400, lambda: btn.config(bg=orig))

def user_input(color):
    global mistakes, current_round

    if not sequence:
        return

    flash_button(color)
    idx = len(user_sequence)
    user_sequence.append(color)

    if user_sequence[idx] != sequence[idx]:
        mistakes += 1
        message_label.config(text="Wrong sequence!")
        show_try_again()
        return

    if len(user_sequence) == len(sequence):
        upsert_progress(current_username, GAME_NAME, current_round)
        _unlock_sequence_stickers(current_round)
        current_round += 1
        root.after(500, next_round)

def show_try_again():
    global try_again_button
    if try_again_button:
        try:
            try_again_button.destroy()
        except:
            pass

    try_again_button = tk.Button(
        root,
        text="Try Again",
        font=("Arial",18),
        bg="#D26155",
        fg="white",
        command=start_game
    )
    try_again_button.pack(side=tk.BOTTOM, pady=20)

def _unlock_sequence_stickers(level):
    THRESHOLDS = {1:"sequence1", 3:"sequence2", 5:"sequence3"}
    for lvl, sticker in THRESHOLDS.items():
        if level >= lvl and sticker not in unlocked_stickers:
            unlock_sticker(current_username, sticker)
            unlocked_stickers.add(sticker)
            show_sticker_popup(sticker, lvl)

def show_sticker_popup(name, lvl):
    popup = tk.Toplevel(root)
    popup.title("Sticker Unlocked!")
    popup.configure(bg="#f7e7ce")
    tk.Label(popup, text=f"Finished {lvl}. level!", font=("Arial",14), bg="#f7e7ce")\
        .pack(pady=10)
    tk.Button(popup, text="Close", command=popup.destroy).pack(pady=5)

def sequence_hard(username_param):
    global root, current_username, unlocked_stickers, label_best

    current_username = username_param
    unlocked_stickers = set(get_unlocked_stickers(current_username))

    root = tk.Tk()
    build_ui()
    root.mainloop()
