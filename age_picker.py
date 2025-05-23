import tkinter as tk
import subprocess
import sys

# Hover effects
def on_enter(e, btn, hover_color):
    btn.config(bg=hover_color)

def on_leave(e, btn, original_color):
    btn.config(bg=original_color)

class SequenceGameLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Sprouts - Sequence Game")
        self.root.configure(bg="#88B04B")
        self.root.resizable(True, True)  
        self.root.iconbitmap("logo2.ico")
        self.root.state("zoomed")

        self.build_ui()

    def build_ui(self):
      
        self.okvir = tk.Frame(self.root, bg="#88B04B", padx=6, pady=6)
        self.okvir.pack(expand=True, fill="both", padx=15, pady=15)
        self.frame = tk.Frame(self.okvir, bg="#f7e7ce")
        self.frame.pack(expand=True, fill="both", padx=10, pady=10)

        title = tk.Label(self.frame, text="Select Your Game", font=("Comic Sans MS", 36, "bold"),
                         bg="#f7e7ce", fg="#172255")
        title.pack(pady=60)

        btn_3_5 = tk.Button(self.frame, text="Age 3–5", font=("Arial", 18, "bold"), width=20, height=2,
                            bg="#88B04B", fg="white", command=self.launch_easy_game, bd=0)
        btn_3_5.pack(pady=30)
        btn_3_5.bind("<Enter>", lambda e: on_enter(e, btn_3_5, "#6dbf3d"))
        btn_3_5.bind("<Leave>", lambda e: on_leave(e, btn_3_5, "#88B04B"))

        btn_6_8 = tk.Button(self.frame, text="Age 6–8", font=("Arial", 18, "bold"), width=20, height=2,
                            bg="#172255", fg="white", command=self.launch_hard_game, bd=0)
        btn_6_8.pack(pady=30)
        btn_6_8.bind("<Enter>", lambda e: on_enter(e, btn_6_8, "#4a90e2"))
        btn_6_8.bind("<Leave>", lambda e: on_leave(e, btn_6_8, "#172255"))

        exit_btn = tk.Button(self.frame, text="Exit", font=("Arial", 16, "bold"), command=self.root.destroy,
                             bg="#FF6347", fg="white", width=14, bd=0)
        exit_btn.pack(pady=50)
        exit_btn.bind("<Enter>", lambda e: on_enter(e, exit_btn, "#e5533d"))
        exit_btn.bind("<Leave>", lambda e: on_leave(e, exit_btn, "#FF6347"))

        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def launch_easy_game(self):
        self.run_script("sequence_game_3_5.py")

    def launch_hard_game(self):
        self.run_script("sequence_game_6_8.py")

    def run_script(self, script_name):
        python_exe = sys.executable
        subprocess.Popen([python_exe, script_name])
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SequenceGameLauncher(root)
    root.mainloop()
