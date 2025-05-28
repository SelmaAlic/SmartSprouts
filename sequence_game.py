import tkinter as tk
from PIL import Image, ImageTk
import random
import os
from datetime import datetime
import sqlite3


DB_PATH = "database.db"

def connect_db():
    return sqlite3.connect(DB_PATH)

def create_progress_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            game_name TEXT NOT NULL,
            best_level INTEGER DEFAULT 0,
            best_time REAL DEFAULT NULL,
            mistakes INTEGER DEFAULT 0,
            last_played DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(username, game_name)
            -- FOREIGN KEY(username) REFERENCES login_info(username) ON DELETE CASCADE
            -- Assuming login_info table exists or remove FK constraint if not
        )
    ''')
    conn.commit()
    conn.close()

def get_progress(username, game_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT best_level, best_time, mistakes, last_played
        FROM progress_tracking
        WHERE username=? AND game_name=?
    ''', (username, game_name))
    result = cursor.fetchone()
    conn.close()
    return result  # returns tuple or None

def update_progress(username, game_name, level, time_sec, mistakes):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT best_level, best_time FROM progress_tracking WHERE username=? AND game_name=?', (username, game_name))
    row = cursor.fetchone()

    if row:
        best_level, best_time = row
        if (level > best_level) or (level == best_level and (best_time is None or time_sec < best_time)):
            cursor.execute('''
                UPDATE progress_tracking
                SET best_level=?, best_time=?, mistakes=?, last_played=?
                WHERE username=? AND game_name=?
            ''', (level, time_sec, mistakes, datetime.now(), username, game_name))
    else:
        cursor.execute('''
            INSERT INTO progress_tracking (username, game_name, best_level, best_time, mistakes)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, game_name, level, time_sec, mistakes))

    conn.commit()
    conn.close()

def sequence_easy(root, username):
    class SequenceGameEasy:
        def __init__(self, root, username):
            self.root = root
            self.username = username
            self.game_name = "SequenceGameEasy"

            self.root.title("Sequence Game - Age 3–5")
            self.root.configure(bg="#88B04B")
            self.root.state("zoomed")

            icon_path = "logo2.ico"
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)

            self.sequence = []
            self.user_sequence = []
            self.round = 1
            self.max_rounds = 10
            self.mistakes = 0
            self.buttons = {}
            self.colors = ["red", "green", "blue", "yellow"]
            self.flash_speed = 1000
            self.sticker_images = {}
            self.unlocked_stickers = set()
            self.start_time = None

            self.load_sticker_images()
            self.build_ui()
            self.ask_continue_or_restart()

        def ask_continue_or_restart(self):
            progress = get_progress(self.username, self.game_name)
            if progress:
                self.continue_popup = tk.Toplevel(self.root)
                self.continue_popup.title("Continue or Restart?")
                self.continue_popup.configure(bg="#f7e7ce")
                self.continue_popup.geometry("400x200")
                self.continue_popup.transient(self.root)
                self.continue_popup.grab_set()

                lbl = tk.Label(
                    self.continue_popup,
                    text="Do you want to continue where you left off\nor restart from the beginning?",
                    font=("Comic Sans MS", 14),
                    bg="#f7e7ce",
                    fg="#172255"
                )
                lbl.pack(pady=20)

                btn_frame = tk.Frame(self.continue_popup, bg="#f7e7ce")
                btn_frame.pack()

                continue_btn = tk.Button(
                    btn_frame,
                    text="Continue",
                    font=("Comic Sans MS", 12, "bold"),
                    bg="#88B04B",
                    fg="white",
                    width=12,
                    command=lambda: self.handle_user_choice("continue")
                )
                continue_btn.pack(side=tk.LEFT, padx=10)

                restart_btn = tk.Button(
                    btn_frame,
                    text="Restart",
                    font=("Comic Sans MS", 12, "bold"),
                    bg="#B0413E",
                    fg="white",
                    width=12,
                    command=lambda: self.handle_user_choice("restart")
                )
                restart_btn.pack(side=tk.LEFT, padx=10)
            else:
                self.round = 1
                self.mistakes = 0
                self.show_start_button()

        def handle_user_choice(self, choice):
            self.continue_popup.destroy()
            if choice == "continue":
                self.load_progress()
            else:
                self.round = 1
                self.mistakes = 0
            self.show_start_button()

        def load_sticker_images(self):
            for name in ["you_did_it", "wow", "pro"]:
                filename = f"{name}.png"
                if os.path.exists(filename):
                    pil_img = Image.open(filename).resize((100, 100), Image.Resampling.LANCZOS)
                    tk_img = ImageTk.PhotoImage(pil_img)
                    self.sticker_images[name] = tk_img
                else:
                    print(f"Warning: Sticker image {filename} not found!")
                    self.sticker_images[name] = None

        def build_ui(self):
            self.okvir = tk.Frame(self.root, bg="#88B04B", padx=8, pady=8)
            self.okvir.pack(expand=True, fill="both", padx=20, pady=20)

            self.frame = tk.Frame(self.okvir, bg="#f7e7ce")
            self.frame.pack(expand=True, fill="both")

            self.title_label = tk.Label(
                self.frame,
                text="Remember the Sequence!",
                font=("Comic Sans MS", 28, "bold"),
                bg="#f7e7ce",
                fg="#172255"
            )
            self.title_label.pack(pady=20)

            self.button_frame = tk.Frame(self.frame, bg="#f7e7ce")
            self.button_frame.pack(pady=20)

            color_map = {
                "red": "#FF6F61",
                "green": "#88B04B",
                "blue": "#92A8D1",
                "yellow": "#F9C74F"
            }

            for color in self.colors:
                btn = tk.Button(
                    self.button_frame,
                    bg=color_map[color],
                    activebackground="white",
                    width=10,
                    height=4,
                    relief="raised",
                    bd=3,
                    command=lambda c=color: self.user_input(c)
                )
                btn.pack(side=tk.LEFT, padx=20)
                self.buttons[color] = btn

            self.message_label = tk.Label(
                self.frame,
                text="",
                font=("Comic Sans MS", 22),
                bg="#f7e7ce",
                fg="#172255"
            )
            self.message_label.pack(pady=20)

            self.sticker_frame = tk.Frame(self.frame, bg="#f7e7ce")
            self.sticker_frame.pack(pady=10)

            self.root.bind("<Escape>", lambda e: self.root.destroy())

        def show_start_button(self):
            self.start_button = tk.Button(
                self.frame,
                text="Start Game",
                font=("Comic Sans MS", 18, "bold"),
                bg="#88B04B",
                fg="white",
                width=14,
                command=self.start_game
            )
            self.start_button.pack(pady=20)

        def load_progress(self):
            progress = get_progress(self.username, self.game_name)
            if progress:
                best_level, best_time, mistakes, last_played = progress
                self.round = best_level + 1 if best_level < self.max_rounds else self.max_rounds
                self.mistakes = mistakes
                self.message_label.config(text=f"Resuming at round {self.round}")
            else:
                self.round = 1
                self.mistakes = 0

        def start_game(self):
            if hasattr(self, 'start_button'):
                self.start_button.destroy()
            self.sequence = []
            self.user_sequence = []
            self.mistakes = 0
            self.unlocked_stickers.clear()
            self.clear_stickers_display()
            self.message_label.config(text=f"Round {self.round}")
            self.start_time = datetime.now()
            self.next_round()

        def next_round(self):
            if self.round > self.max_rounds:
                self.message_label.config(text="Great Job! You finished all levels!")
                self.save_progress(final=True)
                return

            self.message_label.config(text=f"Round {self.round}")
            self.user_sequence = []
            self.sequence.append(random.choice(self.colors))
            self.root.after(1000, self.play_sequence)

        def play_sequence(self):
            for i, color in enumerate(self.sequence):
                self.root.after(i * self.flash_speed, lambda c=color: self.flash_button(c))

        def flash_button(self, color):
            btn = self.buttons[color]
            original_color = btn.cget("bg")
            btn.config(bg="white")
            self.root.after(400, lambda: btn.config(bg=original_color))

        def user_input(self, color):
            if not self.sequence:
                return
            self.user_sequence.append(color)
            self.flash_button(color)

            if self.user_sequence[len(self.user_sequence) - 1] != self.sequence[len(self.user_sequence) - 1]:
                self.mistakes += 1
                self.message_label.config(text="Oops! Wrong sequence. Try again.")
                self.prompt_restart()
                return

            if len(self.user_sequence) == len(self.sequence):
                self.round += 1
                self.message_label.config(text="Correct! Get ready for next round.")
                self.check_for_stickers()
                self.save_progress()
                self.root.after(1500, self.next_round)

        def check_for_stickers(self):
            if self.round == 5:
                self.unlock_sticker("you_did_it")
            elif self.round == 8:
                self.unlock_sticker("wow")
            elif self.round == 11:
                self.unlock_sticker("pro")

        def unlock_sticker(self, sticker_name):
            if sticker_name not in self.unlocked_stickers:
                self.unlocked_stickers.add(sticker_name)
                self.show_sticker_popup(sticker_name)

        def show_sticker_popup(self, sticker_name):
            popup = tk.Toplevel(self.root)
            popup.title("Sticker Unlocked!")
            popup.configure(bg="#f7e7ce")
            popup.geometry("250x250")
            popup.transient(self.root)
            popup.grab_set()

            lbl = tk.Label(
                popup,
                text=f"You unlocked a sticker: {sticker_name.replace('_', ' ').title()}!",
                font=("Comic Sans MS", 14),
                bg="#f7e7ce",
                fg="#172255"
            )
            lbl.pack(pady=10)

            img = self.sticker_images.get(sticker_name)
            if img:
                img_label = tk.Label(popup, image=img, bg="#f7e7ce")
                img_label.pack()

            btn_close = tk.Button(
                popup,
                text="Close",
                font=("Comic Sans MS", 12),
                bg="#88B04B",
                fg="white",
                command=popup.destroy
            )
            btn_close.pack(pady=10)

        def clear_stickers_display(self):
            for widget in self.sticker_frame.winfo_children():
                widget.destroy()

        def save_progress(self, final=False):
            time_played = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
            update_progress(self.username, self.game_name, self.round-1 if final else self.round, time_played, self.mistakes)

        def prompt_restart(self):
            response = tk.messagebox.askyesno("Game Over", "You made a mistake! Do you want to restart?")
            if response:
                self.round = 1
                self.sequence = []
                self.user_sequence = []
                self.mistakes = 0
                self.message_label.config(text="Restarting game...")
                self.start_game()
            else:
                self.root.destroy()

    create_progress_table()
    game = SequenceGameEasy(root, username)
    root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    username = "demo_user"  
    sequence_easy(root, username)
