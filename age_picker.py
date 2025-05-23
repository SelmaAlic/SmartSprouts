import tkinter as tk
from PIL import Image, ImageTk
import os
from game_picker import game_picker 

def age_picker():
    def select_difficulty(difficulty):
        root.destroy()
        game_picker(difficulty)

    root = tk.Tk()
    root.title("Smart Sprouts - Age picker")
    root.configure(bg="#2C8102")
    root.resizable(True, True)
    root.iconbitmap(os.path.join("assets", "logo2.ico"))
    root.state("zoomed")

    frame = tk.Frame(root, bg="#f7e7ce")
    frame.pack(expand=True, fill="both", padx=15, pady=15)

    title = tk.Label(frame, text="Select Your Age", font=("Arial", 36, "bold"),
                     bg="#f7e7ce", fg="#172255")
    title.pack(pady=60)

    btn_info = [
        {
            "img": "easy_btn.png",
            "hover_img": "easy_btn.png",
            "label": "Age 3–5",
            "difficulty": "easy"
        },
        {
            "img": "difficult_btn.png",
            "hover_img": "difficult_btn.png",
            "label": "Age 6–8",
            "difficulty": "hard"
        }
    ]

    btn_frame = tk.Frame(frame, bg="#f7e7ce")
    btn_frame.pack(pady=20)

    btn_imgs = []
    btn_hover_imgs = []

    def on_enter(e, btn, hover_img):
        btn.config(image=hover_img)
    def on_leave(e, btn, normal_img):
        btn.config(image=normal_img)

    for i, info in enumerate(btn_info):
        img_path = os.path.join("assets", info["img"])
        hover_img_path = os.path.join("assets", info["hover_img"])
        img = Image.open(img_path).resize((180, 180), Image.LANCZOS)
        hover_img = Image.open(hover_img_path).resize((220, 220), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        hover_img_tk = ImageTk.PhotoImage(hover_img)
        btn_imgs.append(img_tk)
        btn_hover_imgs.append(hover_img_tk)

        btn = tk.Button(
            btn_frame,
            image=img_tk,
            bd=0,
            bg="#f7e7ce",
            activebackground="#f7e7ce",
            command=lambda diff=info["difficulty"]: select_difficulty(diff),
            cursor="hand2"
        )
        btn.grid(row=0, column=i, padx=60, pady=(0, 5))
        btn.bind("<Enter>", lambda e, b=btn, h=hover_img_tk: on_enter(e, b, h))
        btn.bind("<Leave>", lambda e, b=btn, n=img_tk: on_leave(e, b, n))

        lbl = tk.Label(
            btn_frame,
            text=info["label"],
            font=("Arial", 16, "bold"),
            bg="#f7e7ce",
            fg="#172255"
        )
        lbl.grid(row=1, column=i, pady=(0, 10))



    root.bind("<Escape>", lambda e: root.destroy())
    root.mainloop()

age_picker()
