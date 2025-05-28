import tkinter as tk
from PIL import Image, ImageTk
import os

from login import show_login_window
from age_picker import age_picker
from inventory import show_inventory


current_username= ""

class HomeScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Sprouts - Home")
        self.root.configure(bg="#2C8102")
        self.root.resizable(True, True)
        self.root.iconbitmap(os.path.join("assets", "logo2.ico"))
        self.root.state("zoomed")
        self.build_ui()

    def build_ui(self):
        self.frame = tk.Frame(self.root, bg="#2C8102", padx=6, pady=6)
        self.frame.pack(expand=True, fill="both", padx=5, pady=5)

        self.inner_frame = tk.Frame(self.frame, bg="#f7e7ce")
        self.inner_frame.pack(expand=True, fill="both", padx=10, pady=10)

        logo_path = os.path.join("assets", "logo.png")
        logo_img = Image.open(logo_path).resize((630, 400), Image.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(self.inner_frame, image=logo_photo, bg="#f7e7ce")
        logo_label.image = logo_photo
        logo_label.pack(pady=(30, 30))

    
        btn_data = [
            ("progress.png", "Progress Tracking", self.on_progress),
            ("login.png", "Play", self.on_login),
            ("stickers.png", "Sticker Collection", self.on_sticker),
        ]

        btn_imgs = []
        for file, _, _ in btn_data:
            img_path = os.path.join("assets", file)
            img = Image.open(img_path).resize((150, 150), Image.LANCZOS)
            btn_imgs.append(ImageTk.PhotoImage(img))

        btn_frame = tk.Frame(self.inner_frame, bg="#f7e7ce")
        btn_frame.pack(pady=(10, 40))

        for i, (img, (file, label, cmd)) in enumerate(zip(btn_imgs, btn_data)):
            btn = tk.Button(
                btn_frame,
                image=img,
                bd=0,
                bg="#f7e7ce",
                activebackground="#d6c7b0",
                command=cmd,
                cursor="hand2"
            )
            btn.image = img  
            btn.grid(row=0, column=i, padx=40, pady=(0, 5))
            
            lbl = tk.Label(
                btn_frame,
                text=label,
                font=("Arial", 13, "bold"),
                bg="#f7e7ce",
                fg="#172255"
            )
            lbl.grid(row=1, column=i, pady=(0, 10))

    
    def on_progress(self):
        # add function call to progress tracking
        pass

    def on_login(self):
        age_picker(current_username)
        pass

    def on_sticker(self):
        show_inventory(current_username)
        pass

if __name__ == "__main__":
    current_username=show_login_window()
    root = tk.Tk()
    app = HomeScreen(root)
    root.mainloop()