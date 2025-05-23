import tkinter as tk
from tkinter import PhotoImage
import subprocess
import sys

class HomeScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Sprouts - Home")
        self.root.configure(bg="#2C8102")
        self.root.resizable(True, True)
        self.root.iconbitmap("logo2.ico")
        self.root.state("zoomed")

        self.build_ui()

    def build_ui(self):
        self.okvir = tk.Frame(self.root, bg="#2C8102", padx=6, pady=6)
        self.okvir.pack(expand=True, fill="both", padx=5, pady=5)

        self.frame = tk.Frame(self.okvir, bg="#f7e7ce")
        self.frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.logo_img = PhotoImage(file="logo.png")
        big_logo = self.logo_img.zoom(1, 1) 
        logo_label = tk.Label(self.frame, image=big_logo, bg="#f7e7ce")
        logo_label.image = big_logo 
        logo_label.pack(pady=(40, 40))

        btn_files = ["btn1.png", "btn2.png", "btn3.png"]
        self.btn_imgs = []
        for f in btn_files:
            img = PhotoImage(file=f)
            small_img = img.subsample(3, 3)  
            self.btn_imgs.append(small_img)

        self.btn_cmds = [
            lambda: self.run_script("progress_tracking.py"),
            lambda: self.run_script("login.py"),
            lambda: self.run_script("sticker_collection.py"),
        ]

        btn_frame = tk.Frame(self.frame, bg="#f7e7ce")
        btn_frame.pack(pady=(10, 40))

        for i in range(3):
            btn = tk.Button(
                btn_frame,
                image=self.btn_imgs[i],
                bd=0,
                bg="#f7e7ce",
                activebackground="#d6c7b0",
                command=self.btn_cmds[i],
                cursor="hand2"
            )
            btn.grid(row=0, column=i, padx=40, pady=10)

    def run_script(self, script_name):
        python_exe = sys.executable
        subprocess.Popen([python_exe, script_name])
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = HomeScreen(root)
    root.mainloop()
