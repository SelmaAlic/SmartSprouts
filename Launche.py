import tkinter as tk
import subprocess
import sys

class SequenceGameLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Sequence Game Launcher")
        self.root.geometry("800x600")
        self.root.configure(bg="#FFF0F5")
        self.build_ui()

    def build_ui(self):
        self.okvir = tk.Frame(self.root, bg="green", padx=6, pady=6)
        self.okvir.pack(expand=True, fill="both", padx=30, pady=30)

        self.frame = tk.Frame(self.okvir, bg="#FFF3E0")
        self.frame.pack(expand=True, fill="both")

        title = tk.Label(self.frame, text="Select Your Game", font=("Comic Sans MS", 36, "bold"), bg="#FFF3E0", fg="#E65100")
        title.pack(pady=60)

        btn_3_5 = tk.Button(self.frame, text="Age 3–5 (Easier)", font=("Comic Sans MS", 20), width=25, height=2,
                            bg="#FFCC80", command=self.launch_easy_game)
        btn_3_5.pack(pady=30)

        btn_6_8 = tk.Button(self.frame, text="Age 6–8 (Harder)", font=("Comic Sans MS", 20), width=25, height=2,
                            bg="#FFB74D", command=self.launch_hard_game)
        btn_6_8.pack(pady=30)

        exit_btn = tk.Button(self.frame, text="Exit", font=("Comic Sans MS", 16), command=self.root.destroy,
                             bg="#FF8A65", width=15)
        exit_btn.pack(pady=50)

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
