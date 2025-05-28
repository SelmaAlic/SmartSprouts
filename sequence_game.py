import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import os
from datetime import datetime
import sqlite3

# Constants
DB_PATH = "database.db"
GAME_NAME = "SequenceGameEasy"
MAX_ROUNDS = 10
FLASH_SPEED = 1000
COLORS = ["red", "green", "blue", "yellow"]

# State variables
sequence = []
user_sequence = []
current_round = 1
mistakes = 0
sticker_images = {}
unlocked_stickers = set()
start_time = None

# UI globals
root = None
message_label = None
button_frame = None
start_button = None
sticker_frame = None
color_buttons = {}

# Database helpers
def connect_db():
    return sqlite3.connect(DB_PATH)

def create_progress_table():
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS progress_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            game_name TEXT NOT NULL,
            best_level INTEGER DEFAULT 0,
            best_time REAL DEFAULT NULL,
            mistakes INTEGER DEFAULT 0,
            last_played DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(username, game_name)
        )
    ''')
    conn.commit()
    conn.close()

def get_progress(username, game_name):
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "SELECT best_level, best_time, mistakes, last_played"
        " FROM progress_tracking"
        " WHERE username=? AND game_name=?",
        (username, game_name)
    )
    row = c.fetchone()
    conn.close()
    return row

def update_progress(username, game_name, level, time_sec, mistakes_count):
    conn = connect_db()
    c = conn.cursor()
    now = datetime.now()
    c.execute(
        "SELECT best_level, best_time FROM progress_tracking WHERE username=? AND game_name=?",
        (username, game_name)
    )
    row = c.fetchone()
    if row:
        best_level, best_time = row
        if level > best_level or (level == best_level and (best_time is None or time_sec < best_time)):
            c.execute(
                "UPDATE progress_tracking SET best_level=?, best_time=?, mistakes=?, last_played=?"
                " WHERE username=? AND game_name=?",
                (level, time_sec, mistakes_count, now, username, game_name)
            )
    else:
        c.execute(
            "INSERT INTO progress_tracking (username, game_name, best_level, best_time, mistakes)"
            " VALUES (?, ?, ?, ?, ?)",
            (username, game_name, level, time_sec, mistakes_count)
        )
    conn.commit()
    conn.close()

# UI setup
def load_sticker_images():
    global sticker_images
    for name in ["you_did_it", "wow", "pro"]:
        path = os.path.join("assets", f"{name}.png")
        if os.path.exists(path):
            img = Image.open(path).resize((100, 100), Image.Resampling.LANCZOS)
            sticker_images[name] = ImageTk.PhotoImage(img)
        else:
            sticker_images[name] = None

def build_ui():
    global root, message_label, button_frame, start_button, sticker_frame, color_buttons
    root.title("Sequence Game - Age 3–5")
    root.configure(bg="#88B04B")
    root.state("zoomed")

    frame = tk.Frame(root, bg="#f7e7ce", padx=20, pady=20)
    frame.pack(expand=True, fill="both")

    tk.Label(frame, text="Remember the Sequence!", font=("Arial", 24, "bold"), bg="#f7e7ce").pack(pady=10)
    message_label = tk.Label(frame, text="", font=("Arial", 18), bg="#f7e7ce")
    message_label.pack(pady=10)

    button_frame = tk.Frame(frame, bg="#f7e7ce")
    button_frame.pack(pady=10)
    color_buttons = {}
    for color in COLORS:
        btn = tk.Button(
            button_frame,
            bg=color,
            width=8,
            height=4,
            command=lambda c=color: user_input(c)
        )
        btn.pack(side=tk.LEFT, padx=15)
        color_buttons[color] = btn

    sticker_frame = tk.Frame(frame, bg="#f7e7ce")
    sticker_frame.pack(pady=10)

# Game control functions
def ask_continue_or_restart():
    global current_round, mistakes
    progress = get_progress(current_username, GAME_NAME)
    if progress:
        best_level, _, _, _ = progress
        current_round = best_level + 1 if best_level < MAX_ROUNDS else MAX_ROUNDS
        if not messagebox.askyesno("Continue?", "Continue where you left off?"):
            current_round = 1
            mistakes = 0
    show_start_button()

def show_start_button():
    global start_button
    try:
        start_button.destroy()
    except:
        pass
    start_button = tk.Button(root, text="Start Game", font=("Arial", 18), bg="#88B04B", command=start_game)
    start_button.pack(pady=20)

def start_game():
    global sequence, user_sequence, mistakes, unlocked_stickers, start_time
    start_button.destroy()
    sequence.clear()
    user_sequence.clear()
    mistakes = 0
    unlocked_stickers.clear()
    clear_stickers_display()
    start_time = datetime.now()
    next_round()

def next_round():
    global current_round
    if current_round > MAX_ROUNDS:
        message_label.config(text="Great Job! Finished all rounds.")
        duration = (datetime.now() - start_time).total_seconds()
        update_progress(current_username, GAME_NAME, current_round-1, duration, mistakes)
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
        prompt_restart()
        return
    if len(user_sequence) == len(sequence):
        duration = (datetime.now() - start_time).total_seconds()
        update_progress(current_username, GAME_NAME, current_round, duration, mistakes)
        current_round += 1
        check_for_stickers()
        root.after(500, next_round)

def check_for_stickers():
    if current_round == 5:
        unlock_sticker("you_did_it")
    elif current_round == 8:
        unlock_sticker("wow")
    elif current_round == 11:
        unlock_sticker("pro")

def unlock_sticker(name):
    if name not in unlocked_stickers:
        unlocked_stickers.add(name)
        show_sticker_popup(name)

def show_sticker_popup(name):
    popup = tk.Toplevel(root)
    popup.title("Sticker Unlocked!")
    popup.configure(bg="#f7e7ce")
    lbl = tk.Label(popup, text=f"Unlocked: {name}", font=("Arial",14), bg="#f7e7ce")
    lbl.pack(pady=10)
    img = sticker_images.get(name)
    if img:
        tk.Label(popup, image=img, bg="#f7e7ce").pack()
    tk.Button(popup, text="Close", command=popup.destroy).pack(pady=5)

def clear_stickers_display():
    for w in sticker_frame.winfo_children():
        w.destroy()

def prompt_restart():
    global current_round
    if messagebox.askyesno("Game Over", "Mistake! Do you want to restart?"):
        current_round = 1
        start_game()
    else:
        root.destroy()

# Entry point
def sequence_easy(username_param):
    global root, current_username
    current_username = username_param
    create_progress_table()
    root = tk.Toplevel()
    root.lift(); root.attributes('-topmost',True)
    root.after(10, lambda: root.attributes('-topmost',False))
    load_sticker_images()
    build_ui()
    ask_continue_or_restart()
    root.mainloop()
