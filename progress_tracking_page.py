import tkinter as tk
from PIL import Image, ImageTk
import sqlite3
import os
from utils import resource_path


GAMES = [
    ("Math Game",      "math",    "math_btn.png"),
    ("Sorting",        "sorting", "sorting_btn.png"),
    ("Sequences",      "sequence","sequence_btn.png"),
    ("Memory Cards",   "memory",  "memory_btn.png"),
]
DIFFICULTIES = [
    ("Easy", "easy"),
    ("Hard", "hard"),
]

def get_user_progress(username):
    conn = sqlite3.connect('database.db')
    cur  = conn.cursor()

    progress = {}
    for display_name, game_code, _icon in GAMES:
        for diff_label, diff_code in DIFFICULTIES:
            game_name = f"{game_code}_{diff_code}"  
            cur.execute('''
                SELECT best_level, mistakes, last_played
                  FROM progress_tracking
                 WHERE username=? AND game_name=?
            ''', (username, game_name))
            row = cur.fetchone() or (0, 0, None)

            progress[(game_code, diff_code)] = {
                "display_name":    f"{display_name} ({diff_label})",
                "max_level":       row[0],
                "total_mistakes":  row[1],
                "last_played":     row[2] or "Never",
            }

    conn.close()
    return progress

def progress_tracker(username, master=None):
    root = tk.Toplevel(master) if master else tk.Tk()
    root.title(f"{username}'s Progress")
    root.configure(bg="#2C8102")
    root.state("zoomed")

    ico =  resource_path(os.path.join("assets","logo2.ico"))
    if os.path.exists(ico):
        root.iconbitmap(ico)

    border = tk.Frame(root, bg="#2C8102", padx=5, pady=5)
    border.pack(expand=True, fill="both", padx=15, pady=15)
    content = tk.Frame(border, bg="#f7e7ce")
    content.pack(expand=True, fill="both")

    
    logo_path = resource_path(os.path.join("assets","logo.png"))
    if os.path.exists(logo_path):
        img = Image.open(logo_path).resize((220,120), Image.LANCZOS)
        ph = ImageTk.PhotoImage(img)
        lbl = tk.Label(content, image=ph, bg="#f7e7ce")
        lbl.image = ph
        lbl.grid(row=0, column=0, columnspan=4, pady=(20,5))
    else:
        lbl = tk.Label(content, text="Smart Sprouts", font=("Comic Sans MS",36,"bold"),
                       bg="#f7e7ce", fg="#172255")
        lbl.grid(row=0, column=0, columnspan=4, pady=(30,10))

    sub = tk.Label(content, text="Your Progress", font=("Arial",28,"bold"),
                   bg="#f7e7ce", fg="#2C8102")
    sub.grid(row=1, column=0, columnspan=4, pady=(0,20))

   
    data = get_user_progress(username)

    for col, (_display, game_code, icon_fn) in enumerate(GAMES):
        for row, (_label, diff_code) in enumerate(DIFFICULTIES):
            p = data[(game_code, diff_code)]
            frame = tk.Frame(content, bg="#f7e7ce", padx=12, pady=12,
                             borderwidth=3, relief="groove",
                             highlightbackground="#2C8102", highlightthickness=2)
            frame.grid(row=row+2, column=col, padx=30, pady=20, sticky="nsew")
            content.grid_rowconfigure(row+2, weight=1)
            content.grid_columnconfigure(col, weight=1)

            path = resource_path(os.path.join("assets", icon_fn))
            if os.path.exists(path):
                ico = Image.open(path).resize((48,48), Image.LANCZOS)
                ph = ImageTk.PhotoImage(ico)
                lbl = tk.Label(frame, image=ph, bg="#f7e7ce")
                lbl.image = ph
                lbl.pack(pady=(0,6))

            tk.Label(frame, text=p["display_name"], font=("Arial",16,"bold"),
                     bg="#f7e7ce", fg="#2C8102").pack(pady=(0,10))

            info_font = ("Arial",13)
            tk.Label(frame, text=f"Highest Level: {p['max_level']}",
                     font=info_font, bg="#f7e7ce", anchor="w").pack(anchor="w")
            tk.Label(frame, text=f"Total Mistakes: {p['total_mistakes']}",
                     font=info_font, bg="#f7e7ce", anchor="w").pack(anchor="w")
            tk.Label(frame, text=f"Last Played: {p['last_played']}",
                     font=info_font, bg="#f7e7ce", anchor="w").pack(anchor="w")

    root.mainloop()


if __name__ == "__main__":
    # For quick testing:
    uname = "Adna"
    progress_tracker(uname)
