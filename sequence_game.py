import tkinter as tk 
import random
import os

class SequenceGameEasy:
    def __init__(self, root):
        self.root = root
        self.root.title("Sequence Game - Age 3–5")
        self.root.configure(bg="#88B04B")
        self.root.state("zoomed")

        icon_path = "logo2.ico"
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        self.sequence = []
        self.user_sequence = []
        self.round = 1
        self.max_rounds = 6
        self.buttons = {}
        self.colors = ["red", "green", "blue", "yellow"]
        self.flash_speed = 1000

        self.build_ui()
        self.show_start_button()

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

    def start_game(self):
        self.start_button.destroy()
        self.next_round()

    def next_round(self):
        if self.round > self.max_rounds:
            self.message_label.config(text="Great Job!")
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
        original = btn["bg"]
        btn.config(bg="white")
        self.root.after(300, lambda: btn.config(bg=original))

    def user_input(self, color):
        self.user_sequence.append(color)
        if self.user_sequence == self.sequence[:len(self.user_sequence)]:
            if len(self.user_sequence) == len(self.sequence):
                self.round += 1
                self.root.after(1000, self.next_round)
        else:
            self.message_label.config(text="Try Again!")
            self.sequence = []
            self.round = 1
            self.root.after(2000, self.start_game)

if __name__ == "__main__":
    root = tk.Tk()
    app = SequenceGameEasy(root)
    root.mainloop()
