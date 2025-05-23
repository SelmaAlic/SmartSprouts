import tkinter as tk
from PIL import Image, ImageTk
import os

def game_picker(difficulty):

    def on_math():
       
        if difficulty==easy:
            math_game_easy()
        else:
            math_game_hard()
    

    def on_sorting():
        if difficulty==easy:
            sorting_game_easy()
        else:
            sorting_game_hard()


    def on_sequence():
        if difficulty==easy:
            sequence_game_easy()
        else:
            sequence_game_hard()
    

    def on_memory():
        if difficulty==easy:
            memory_card_easy()
        else:
            math_card_hard()
        
    def on_cloud_sync():
        cloud_sync(username)
        pass

    root = tk.Tk()
    root.title("Smart Sprouts - Game Picker")
    root.configure(bg="#2C8102")
    root.resizable(True, True)
    root.iconbitmap(os.path.join("assets", "logo2.ico"))
    root.state("zoomed")

    content = tk.Frame(root, bg="#f7e7ce", padx=15, pady=15)
    content.pack(expand=True, fill="both", padx=15, pady=15)

    cloud_icon_path = os.path.join("assets", "cloud_sync_btn.png")
    if os.path.exists(cloud_icon_path):
        cloud_img = Image.open(cloud_icon_path).resize((80, 80), Image.LANCZOS) 
        cloud_photo = ImageTk.PhotoImage(cloud_img)
        cloud_btn = tk.Button(
            content,
            image=cloud_photo,
            bd=0,
            bg="#f7e7ce",
            activebackground="#b2d8b2",
            command=on_cloud_sync,
            cursor="hand2",
            highlightthickness=0
        )
        cloud_btn.image = cloud_photo
    else:
        cloud_btn = tk.Button(
            content,
            text="Cloud Sync",
            font=("Arial", 14, "bold"),
            bd=0,
            bg="#f7e7ce",
            fg="#172255",
            activebackground="#b2d8b2",
            command=on_cloud_sync,
            cursor="hand2",
            highlightthickness=0
        )
    cloud_btn.place(relx=1.0, y=10, anchor="ne")  

    logo_img = Image.open(os.path.join("assets", "logo.png"))
    logo_img = logo_img.resize((480, 280), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(content, image=logo_photo, bg="#f7e7ce")
    logo_label.image = logo_photo
    logo_label.pack(pady=(20, 25))

    btn_files = [
        ("math_btn.png", "Math Game", on_math),
        ("sorting_btn.png", "Sorting", on_sorting),
        ("sequence_btn.png", "Sequences", on_sequence),
        ("memory_btn.png", "Memory Cards", on_memory),
    ]

    btn_imgs = []
    for file, _, _ in btn_files:
        img = Image.open(os.path.join("assets", file))
        img = img.resize((140, 140), Image.LANCZOS)
        btn_imgs.append(ImageTk.PhotoImage(img))

    btn_frame = tk.Frame(content, bg="#f7e7ce")
    btn_frame.pack(pady=(10, 40))

    for i in range(2):
        for j in range(2):
            idx = i * 2 + j
            img, label, func = btn_imgs[idx], btn_files[idx][1], btn_files[idx][2]
            btn = tk.Button(
                btn_frame,
                image=img,
                bd=0,
                bg="#f7e7ce",
                activebackground="#d6c7b0",
                command=func,
                cursor="hand2",
                borderwidth=0,
                highlightthickness=0
            )
            btn.grid(row=i*2, column=j, padx=50, pady=(0, 5))
            lbl = tk.Label(
                btn_frame,
                text=label,
                font=("Arial", 14, "bold"),
                bg="#f7e7ce",
                fg="#172255"
            )
            lbl.grid(row=i*2+1, column=j, pady=(0, 20))

    root.bind("<Escape>", lambda e: root.destroy())
    root.mainloop()

if __name__ == "__main__":
    game_picker()
