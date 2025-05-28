import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import os
import sqlite3
from datetime import datetime

# Constants and state
DB_PATH = "database.db"
current_username = None
GAME_NAME = "SequenceGameHard"
MAX_ROUNDS = 10
FLASH_SPEED = 650
COLORS = ["red", "green", "blue", "yellow", "purple", "orange"]

# State variables
sequence = []
user_sequence = []
current_round = 1
mistakes = 0
sticker_images = {}
unlocked_stickers = set()
start_time = None

# UI globals
tk_root = None
message_label = None
frame_buttons = None
start_button = None
label_best = None
frame_stickers = None
color_buttons = {}

# Database helpers
def connect_db():
    return sqlite3.connect(DB_PATH)

def create_progress_table():
    conn = connect_db(); c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS progress (
        username TEXT NOT NULL,
        highest_round INTEGER NOT NULL,
        PRIMARY KEY(username)
    )''')
    conn.commit(); conn.close()

def create_rewards_table():
    conn = connect_db(); c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rewards (
        username TEXT NOT NULL,
        name TEXT NOT NULL,
        unlocked INTEGER DEFAULT 0,
        PRIMARY KEY(username, name)
    )''')
    for name in ["you_did_it","wow","pro"]:
        c.execute("INSERT OR IGNORE INTO rewards (username,name,unlocked) VALUES (?,?,0)", (current_username, name))
    conn.commit(); conn.close()

def get_highest_round():
    conn = connect_db(); c = conn.cursor()
    c.execute("SELECT highest_round FROM progress WHERE username=?", (current_username,))
    row = c.fetchone(); conn.close()
    return row[0] if row else 0

def set_highest_round(rnd):
    conn = connect_db(); c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO progress (username,highest_round) VALUES (?,?)", (current_username, rnd))
    conn.commit(); conn.close()

def load_unlocked_stickers():
    conn = connect_db(); c = conn.cursor()
    c.execute("SELECT name FROM rewards WHERE username=? AND unlocked=1", (current_username,))
    rows = c.fetchall(); conn.close()
    return {r[0] for r in rows}

def unlock_sticker_db(name):
    conn = connect_db(); c = conn.cursor()
    c.execute("UPDATE rewards SET unlocked=1 WHERE username=? AND name=?", (current_username, name))
    conn.commit(); conn.close()

# UI setup
def load_sticker_images():
    global sticker_images
    for name in ["you_did_it","wow","pro"]:
        path = os.path.join("assets", f"{name}.png")
        if os.path.exists(path):
            img = Image.open(path).resize((100,100), Image.Resampling.LANCZOS)
            sticker_images[name] = ImageTk.PhotoImage(img)
        else:
            sticker_images[name] = None

def build_ui():
    global tk_root, message_label, frame_buttons, start_button, label_best, frame_stickers, color_buttons
    tk_root.title("Sequence Game - Age 6–8")
    tk_root.configure(bg="#88B04B")
    tk_root.state("zoomed")

    # initialize DB
    create_progress_table(); create_rewards_table()
    unlocked = load_unlocked_stickers()
    unlocked_stickers.clear(); unlocked_stickers.update(unlocked)

    frm = tk.Frame(tk_root, bg="#f7e7ce", padx=20, pady=20)
    frm.pack(expand=True, fill="both")

    tk.Label(frm, text="Remember the Sequence!", font=("Arial",24,"bold"), bg="#f7e7ce").pack(pady=10)
    label_best = tk.Label(frm, text=f"Best Round: {get_highest_round()}", font=("Arial",16), bg="#f7e7ce")
    label_best.pack(pady=5)

    message_label = tk.Label(frm, text="", font=("Arial",18), bg="#f7e7ce")
    message_label.pack(pady=10)

    frame_buttons = tk.Frame(frm, bg="#f7e7ce"); frame_buttons.pack(pady=10)
    color_buttons = {}
    for i,color in enumerate(COLORS):
        btn = tk.Button(frame_buttons, bg=color, width=8, height=4, command=lambda c=color: user_input(c))
        btn.grid(row=i//3, column=i%3, padx=15, pady=10)
        color_buttons[color] = btn

    frame_stickers = tk.Frame(frm, bg="#f7e7ce"); frame_stickers.pack(pady=10)

    start_button = tk.Button(frm, text="Start Game", font=("Arial",18), bg="#88B04B", command=start_game)
    start_button.pack(pady=20)

# Game logic
def start_game():
    global sequence, user_sequence, mistakes, current_round, start_time
    sequence.clear(); user_sequence.clear(); mistakes=0; current_round=1
    clear_stickers(); set_highest_round(get_highest_round()); update_best_label()
    start_time = datetime.now(); next_round()

def next_round():
    global current_round
    if current_round>MAX_ROUNDS:
        message_label.config(text="Great Job! Finished all rounds!")
        return
    message_label.config(text=f"Round {current_round}")
    user_sequence.clear(); sequence.append(random.choice(COLORS))
    tk_root.after(1000, play_sequence)

def play_sequence():
    for idx,color in enumerate(sequence): tk_root.after(idx*FLASH_SPEED, lambda c=color: flash_button(c))

def flash_button(color):
    btn=color_buttons[color]; orig=btn.cget("bg")
    btn.config(bg="white"); tk_root.after(400, lambda: btn.config(bg=orig))

def user_input(color):
    global mistakes, current_round
    flash_button(color)
    pos=len(user_sequence); user_sequence.append(color)
    if user_sequence[pos]!=sequence[pos]:
        mistakes+=1; message_label.config(text="Wrong!"); prompt_restart(); return
    if len(user_sequence)==len(sequence):
        if current_round>get_highest_round(): set_highest_round(current_round); update_best_label()
        check_unlock(current_round)


def check_unlock(rnd):
    if rnd==4 and "you_did_it" not in unlocked_stickers: unlock_and_popup("you_did_it")
    elif rnd==7 and "wow" not in unlocked_stickers: unlock_and_popup("wow")
    elif rnd==10 and "pro" not in unlocked_stickers: unlock_and_popup("pro")
    else: increment_round()

def unlock_and_popup(name):
    unlock_sticker_db(name); unlocked_stickers.add(name)
    popup=tk.Toplevel(tk_root); tk.Label(popup, text=f"Unlocked {name}").pack()
    popup.after(1000,popup.destroy); increment_round()

def increment_round():
    global current_round; current_round+=1; tk_root.after(500,next_round)

def clear_stickers():
    for w in frame_stickers.winfo_children(): w.destroy()

def update_best_label():
    label_best.config(text=f"Best Round: {get_highest_round()}")

def prompt_restart():
    if messagebox.askyesno("Game Over","Restart at round 1?"):
        start_game()
    else:
        tk_root.destroy()

# Entry point
def sequence_hard(username_param):
    global tk_root, current_username
    current_username = username_param  # set global for module
    tk_root = tk.Toplevel()
    tk_root.lift(); tk_root.attributes('-topmost',True); tk_root.after(10, lambda: tk_root.attributes('-topmost',False))
    load_sticker_images(); build_ui()
    tk_root.mainloop()
