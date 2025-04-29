import tkinter as tk
import random
import time
from tkinter import messagebox

class SequenceGame:
    def __init__(self, root, age_group):
        self.root = root
        self.age_group = age_group
        self.sequence = []
        self.user_sequence = []
        self.current_index = 0

        if age_group == "3-5":
            self.sequence_length = 3
            self.speed = 1000
        elif age_group == "6-8":
            self.sequence_length = 6
            self.speed = 600

        self.colors = ["red", "green", "blue", "yellow"]
        self.buttons = {}

        self.build_gui()
        self.root.after(1000, self.show_sequence)

    def build_gui(self):
        self.root.title("Sequence Game")
        self.root.geometry("400x400")

        tk.Label(self.root, text=f"Age group: {self.age_group}", font=("Arial", 14)).pack(pady=10)

        grid_frame = tk.Frame(self.root)
        grid_frame.pack(pady=20)

        for i, color in enumerate(self.colors):
            btn = tk.Button(grid_frame, bg=color, width=10, height=5,
                            command=lambda c=color: self.button_pressed(c))
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=10)
            self.buttons[color] = btn

    def show_sequence(self):
        self.sequence = [random.choice(self.colors) for _ in range(self.sequence_length)]
        self.user_sequence = []
        self.current_index = 0

        for i, color in enumerate(self.sequence):
            self.root.after(i * self.speed, self.highlight_button, color)

    def highlight_button(self, color):
        btn = self.buttons[color]
        original = btn.cget("bg")
        btn.config(bg="white")
        self.root.after(300, lambda: btn.config(bg=original))

    def button_pressed(self, color):
        self.user_sequence.append(color)
        if self.user_sequence[len(self.user_sequence) - 1] != self.sequence[len(self.user_sequence) - 1]:
            messagebox.showerror("Wrong!", "Oops! That was the wrong sequence.")
            self.ask_replay()
            return

        if len(self.user_sequence) == len(self.sequence):
            messagebox.showinfo("Correct!", "Well done! You remembered the sequence.")
            self.ask_replay()

    def ask_replay(self):
        replay = messagebox.askyesno("Play Again?", "Do you want to try again?")
        if replay:
            self.show_sequence()
        else:
            self.root.destroy()

# Entry window for age selection
def launch_game():
    selected_age = age_var.get()
    if selected_age not in ["3-5", "6-8"]:
        messagebox.showwarning("Select Age", "Please choose an age group.")
        return
    age_window.destroy()
    root = tk.Tk()
    game = SequenceGame(root, selected_age)
    root.mainloop()

age_window = tk.Tk()
age_window.title("Choose Age Group")
age_window.geometry("300x200")

tk.Label(age_window, text="Choose Age Group", font=("Arial", 14)).pack(pady=20)

age_var = tk.StringVar()

tk.Radiobutton(age_window, text="3-5 years", variable=age_var, value="3-5").pack(pady=5)
tk.Radiobutton(age_window, text="6-8 years", variable=age_var, value="6-8").pack(pady=5)

tk.Button(age_window, text="Start Game", command=launch_game).pack(pady=20)

age_window.mainloop()
