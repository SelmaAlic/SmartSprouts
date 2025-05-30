import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import os
from datetime import datetime
import sqlite3
from database import get_progress, upsert_progress, unlock_sticker, get_unlocked_stickers

DB_PATH = "database.db"
GAME_NAME = "sequence_easy"
MAX_ROUNDS = 10
FLASH_SPEED = 1000
COLORS = ["red", "green", "blue", "yellow"]

sequence = []
user_sequence = []
current_round = 1
mistakes = 0
sticker_images = {}
unlocked_stickers = set()
start_time = None
current_username= None

root = None
message_label = None
button_frame = None
start_button= None
try_again_button= None
sticker_frame = None
color_buttons = {}

def build_ui():
    global root, message_label, button_frame, start_button, sticker_frame, color_buttons
    root.title("Sequence Game - Easy")
    root.configure(bg="#88B04B")
    root.state("zoomed")
    root.resizable(True,True)

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

def show_start_button():
    global start_button
    if start_button:
        try:
            start_button.destroy()
        except:
            pass
    start_button = tk.Button(root, text="Start Game", font=("Arial", 18), bg="#88B04B", command=start_game)
    start_button.pack(pady=20)

def start_game():
    global sequence, user_sequence, mistakes, start_time, current_round
    if start_button:
        try: start_button.pack_forget()
        except: pass
    
    current_round=1
    mistakes=0
    sequence.clear()
    user_sequence.clear()
    start_time = datetime.now()
    next_round()

def next_round():
    global current_round
    if current_round > MAX_ROUNDS:
        message_label.config(text="Great Job! Finished all rounds.")
        duration = (datetime.now() - start_time).total_seconds()
        score=current_round-1
        upsert_progress(current_username, GAME_NAME, score)
        _unlock_sequence_stickers(current_round-1)
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

    #User makes a mistake
    if user_sequence[idx] != sequence[idx]:
        mistakes += 1
        message_label.config(text="Wrong sequence!")
        show_try_again()
        return
    
    if len(user_sequence) == len(sequence):
        duration = (datetime.now() - start_time).total_seconds()
        upsert_progress(current_username, GAME_NAME, current_round, duration, mistakes)
        _unlock_sequence_stickers(current_round)
        current_round += 1
        root.after(500, next_round)

def show_try_again():
    global try_again_button
    if try_again_button is not None:
        try:
            try_again_button.destroy()
        except:
            pass

    try_again_button = tk.Button(
        root,
        text="Try Again",
        font=("Arial", 18),
        bg="#D26155",
        fg="white",
        command=reset_to_start
    )
    try_again_button.pack(side=tk.BOTTOM, pady=20)

def reset_to_start():
    global try_again_button
    if try_again_button is not None:
        try:
            try_again_button.destroy()
        except:
            pass
    start_game()

def _unlock_sequence_stickers (score):
    ACHIEVEMENTS={
    1: "sequence1",
    3: "sequence2",
    5: "sequence3"
    }

    for lvl, sticker in ACHIEVEMENTS.items():
        if score>=lvl and sticker not in unlocked_stickers:
            unlock_sticker(current_username, sticker)
            unlocked_stickers.add(sticker)
            show_sticker_popup(sticker, lvl)

def show_sticker_popup(name, lvl):
    popup = tk.Toplevel(root)
    popup.title("Sticker Unlocked!")
    popup.configure(bg="#f7e7ce")
    lbl = tk.Label(popup, text=f"Finish {lvl}. level!", bg="#f7e7ce")
    lbl.pack(pady=10)
    tk.Button(popup, text="Close", command=popup.destroy).pack(pady=5)

def sequence_easy(username_param):
    global root, current_username, unlocked_stickers
    current_username=username_param
    unlocked_stickers=set(get_unlocked_stickers(current_username))

    root = tk.Tk()
    build_ui()
    show_start_button()
    root.mainloop()