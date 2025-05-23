import tkinter as tk
import random
import os
from PIL import Image, ImageTk
import sqlite3

def sequence_hard(root):
    class SequenceGameHard:
        def __init__(self, root):
            self.root = root
            self.root.title("Sequence Game - Age 6–8")
            self.root.configure(bg="#88B04B")
            self.root.state("zoomed")

            icon_path = "logo2.ico"
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)

            self.create_progress_table()
            self.create_rewards_table()

            self.sequence = []
            self.user_sequence = []
            self.round = 1
            self.max_rounds = 10
            self.buttons = {}
            self.colors = ["red", "green", "blue", "yellow", "purple", "orange"]
            self.flash_speed = 650

            self.sticker_images = {}
            self.unlocked_stickers = self.load_unlocked_stickers()
            self.load_sticker_images()

            self.build_ui()
            self.show_start_button()

        def create_progress_table(self):
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                highest_round INTEGER NOT NULL)''')
            c.execute("SELECT COUNT(*) FROM progress")
            if c.fetchone()[0] == 0:
                c.execute("INSERT INTO progress (highest_round) VALUES (0)")
            conn.commit()
            conn.close()

        def create_rewards_table(self):
            conn = sqlite3.connect("database.db")
            c = conn.cursor()

            try:
                c.execute("SELECT name FROM rewards LIMIT 1")
            except sqlite3.OperationalError:
                c.execute("DROP TABLE IF EXISTS rewards")
                c.execute('''CREATE TABLE IF NOT EXISTS rewards (
                                name TEXT PRIMARY KEY,
                                unlocked INTEGER DEFAULT 0
                            )''')

            stickers = ["you_did_it", "wow", "pro"]
            for name in stickers:
                c.execute("INSERT OR IGNORE INTO rewards (name, unlocked) VALUES (?, 0)", (name,))

            conn.commit()
            conn.close()

        def load_unlocked_stickers(self):
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute("SELECT name FROM rewards WHERE unlocked = 1")
            rows = c.fetchall()
            conn.close()
            return {row[0] for row in rows}

        def unlock_sticker(self, name):
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute("UPDATE rewards SET unlocked = 1 WHERE name = ?", (name,))
            conn.commit()
            conn.close()
            self.unlocked_stickers.add(name)

        def get_highest_round(self):
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute("SELECT highest_round FROM progress WHERE id=1")
            result = c.fetchone()
            conn.close()
            return result[0] if result else 0

        def set_highest_round(self, round_number):
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute("UPDATE progress SET highest_round = ? WHERE id=1", (round_number,))
            conn.commit()
            conn.close()
            self.best_score_label.config(text=f"Best Round: {round_number}")

        def load_sticker_images(self):
            for name in ["you_did_it", "wow", "pro"]:
                for version in ["", " siva"]:
                    file = f"{name}{version}.png"
                    if os.path.exists(file):
                        img = Image.open(file)
                        self.sticker_images[file] = ImageTk.PhotoImage(img)
                    else:
                        self.sticker_images[file] = None

        def build_ui(self):
            self.okvir = tk.Frame(self.root, bg="#88B04B", padx=8, pady=8)
            self.okvir.pack(expand=True, fill="both", padx=20, pady=20)

            self.frame = tk.Frame(self.okvir, bg="#f7e7ce")
            self.frame.pack(expand=True, fill="both")

            self.title_label = tk.Label(self.frame, text="Remember the Sequence!", font=("Comic Sans MS", 28, "bold"),
                                        bg="#f7e7ce", fg="#172255")
            self.title_label.pack(pady=20)

            self.best_score_label = tk.Label(self.frame, text=f"Best Round: {self.get_highest_round()}",
                                             font=("Comic Sans MS", 16), bg="#f7e7ce", fg="#172255")
            self.best_score_label.pack(pady=10)

            self.button_frame = tk.Frame(self.frame, bg="#f7e7ce")
            self.button_frame.pack(pady=20)

            color_map = {
                "red": "#FF6F61",
                "green": "#88B04B",
                "blue": "#92A8D1",
                "yellow": "#F9C74F",
                "purple": "#9B59B6",
                "orange": "#F39C12"
            }

            row = col = 0
            for i, color in enumerate(self.colors):
                btn = tk.Button(self.button_frame, bg=color_map[color], activebackground="white",
                                width=10, height=4, relief="raised", bd=3, command=lambda c=color: self.user_input(c))
                btn.grid(row=row, column=col, padx=15, pady=10)
                self.buttons[color] = btn
                col += 1
                if (i + 1) % 3 == 0:
                    row += 1
                    col = 0

            self.message_label = tk.Label(self.frame, text="", font=("Comic Sans MS", 22),
                                          bg="#f7e7ce", fg="#172255")
            self.message_label.pack(pady=20)

            self.inventory_btn = tk.Button(self.frame, text="Inventory", font=("Comic Sans MS", 14, "bold"),
                                           bg="#88B04B", fg="white", command=self.show_inventory)
            self.inventory_btn.pack(pady=10)

            self.sticker_frame = tk.Frame(self.frame, bg="#f7e7ce")
            self.sticker_frame.pack(pady=10)

            self.root.bind("<Escape>", lambda e: self.root.destroy())

        def show_start_button(self):
            self.start_button = tk.Button(self.frame, text="Start Game", font=("Comic Sans MS", 18, "bold"),
                                          bg="#88B04B", fg="white", width=14, command=self.start_game)
            self.start_button.pack(pady=20)

        def start_game(self):
            self.start_button.destroy()
            self.sequence.clear()
            self.user_sequence.clear()
            self.round = 1
            self.clear_stickers_display()
            self.best_score_label.config(text=f"Best Round: {self.get_highest_round()}")
            self.next_round()

        def next_round(self):
            if self.round > self.max_rounds:
                self.message_label.config(text="Great Job! You finished all levels!")
                return
            self.message_label.config(text=f"Round {self.round}")
            self.user_sequence.clear()
            self.sequence.append(random.choice(self.colors))
            self.root.after(1000, self.play_sequence)

        def play_sequence(self):
            for i, color in enumerate(self.sequence):
                self.root.after(i * self.flash_speed, lambda c=color: self.flash_button(c))
            self.root.after(len(self.sequence) * self.flash_speed, lambda: self.message_label.config(text="Your turn now!"))

        def flash_button(self, color):
            btn = self.buttons[color]
            original = btn["bg"]
            btn.config(bg="white")
            self.root.after(400, lambda: btn.config(bg=original))

        def user_input(self, color):
            self.user_sequence.append(color)
            if self.user_sequence == self.sequence[:len(self.user_sequence)]:
                if len(self.user_sequence) == len(self.sequence):
                    self.check_unlock_sticker(self.round)
            else:
                self.show_restart_screen()

        def check_unlock_sticker(self, round_number):
            sticker = None
            if round_number == 4 and "you_did_it" not in self.unlocked_stickers:
                sticker = "you_did_it"
            elif round_number == 7 and "wow" not in self.unlocked_stickers:
                sticker = "wow"
            elif round_number == 10 and "pro" not in self.unlocked_stickers:
                sticker = "pro"

            if round_number > self.get_highest_round():
                self.set_highest_round(round_number)

            if sticker:
                self.unlock_sticker(sticker)
                self.show_sticker_popup(sticker)
            else:
                self.round += 1
                self.root.after(1000, self.next_round)

        def show_sticker_popup(self, sticker_name):
            popup = tk.Toplevel(self.root)
            popup.title("You earned a sticker!")
            popup.geometry("300x300")
            popup.configure(bg="#f7e7ce")
            popup.transient(self.root)
            popup.grab_set()

            icon_path = "logo2.ico"
            if os.path.exists(icon_path):
                popup.iconbitmap(icon_path)

            img = self.sticker_images.get(f"{sticker_name}.png")
            if img:
                lbl = tk.Label(popup, image=img, bg="#f7e7ce")
                lbl.image = img
                lbl.pack(pady=20)

            btn = tk.Button(popup, text="Collect Sticker", font=("Comic Sans MS", 14, "bold"),
                            bg="#88B04B", fg="white", command=lambda: self.collect_sticker(popup))
            btn.pack(pady=20)

        def collect_sticker(self, popup):
            popup.destroy()
            self.display_stickers()
            self.round += 1
            self.root.after(500, self.next_round)

        def display_stickers(self):
            self.clear_stickers_display()
            for name in ["you_did_it", "wow", "pro"]:
                file = f"{name}.png" if name in self.unlocked_stickers else f"{name} siva.png"
                img = self.sticker_images.get(file)
                if img:
                    lbl = tk.Label(self.sticker_frame, image=img, bg="#f7e7ce")
                    lbl.image = img
                    lbl.pack(side="left", padx=5)

        def clear_stickers_display(self):
            for widget in self.sticker_frame.winfo_children():
                widget.destroy()

        def show_inventory(self):
            inv = tk.Toplevel(self.root)
            inv.title("Sticker Inventory")
            inv.geometry("350x150")
            inv.configure(bg="#f7e7ce")
            inv.transient(self.root)
            inv.grab_set()

            icon_path = "logo2.ico"
            if os.path.exists(icon_path):
                inv.iconbitmap(icon_path)

            for name in ["you_did_it", "wow", "pro"]:
                file = f"{name}.png" if name in self.unlocked_stickers else f"{name} siva.png"
                img = self.sticker_images.get(file)
                if img:
                    lbl = tk.Label(inv, image=img, bg="#f7e7ce")
                    lbl.image = img
                    lbl.pack(side="left", padx=10, pady=10)

        def show_restart_screen(self):
            self.message_label.config(text="Incorrect sequence! Game over.")
            for btn in self.buttons.values():
                btn.config(state="disabled")
            popup = tk.Toplevel(self.root)
            popup.title("Game Over")
            popup.geometry("300x200")
            popup.configure(bg="#f7e7ce")
            popup.transient(self.root)
            popup.grab_set()

            icon_path = "logo2.ico"
            if os.path.exists(icon_path):
                popup.iconbitmap(icon_path)

            msg = tk.Label(popup, text="Oops! You made a mistake.\nDo you want to restart?", font=("Comic Sans MS", 14),
                           bg="#f7e7ce", fg="#172255")
            msg.pack(pady=20)

            btn_frame = tk.Frame(popup, bg="#f7e7ce")
            btn_frame.pack(pady=10)

            restart_btn = tk.Button(btn_frame, text="Restart", bg="#88B04B", fg="white",
                                    command=lambda: [popup.destroy(), self.restart_game()])
            restart_btn.pack(side="left", padx=10)

            exit_btn = tk.Button(btn_frame, text="Exit", bg="#FF6F61", fg="white", command=self.root.destroy)
            exit_btn.pack(side="right", padx=10)

        def restart_game(self):
            for btn in self.buttons.values():
                btn.config(state="normal")
            self.start_game()

    game = SequenceGameHard(root)
    return game
if __name__ == "__main__":
    root = tk.Tk()
    game = sequence_hard(root)
    root.mainloop()
