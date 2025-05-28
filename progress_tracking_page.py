import tkinter as tk
from PIL import Image, ImageTk
import sqlite3
import os

GAMES = [
    ("Math Game", "math", "math_btn.png"),
    ("Sorting", "sorting", "sorting_btn.png"),
    ("Sequences", "sequence", "sequence_btn.png"),
    ("Memory Cards", "memory", "memory_btn.png")
]
DIFFICULTIES = [("Easy", "easy"), ("Hard", "hard")]

def get_user_progress(username):
    conn = sqlite3.connect('cognitive_games.db')
    cursor = conn.cursor()
    progress = {}
    for display_name, game_code, _ in GAMES:
        for diff_label, diff_code in DIFFICULTIES:
            table = f"{game_code}_{diff_code}"
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if cursor.fetchone() is None:
                progress[(game_code, diff_code)] = {
                    "display_name": f"{display_name} ({diff_label})",
                    "max_level": 0,
                    "total_mistakes": 0,
                    "last_played": "Never"
                }
                continue
            cursor.execute(f'''
                SELECT 
                    MAX(level) as max_level,
                    SUM(mistakes) as total_mistakes,
                    MAX(last_played) as last_played
                FROM {table}
                WHERE username=?
            ''', (username,))
            row = cursor.fetchone()
            progress[(game_code, diff_code)] = {
                "display_name": f"{display_name} ({diff_label})",
                "max_level": row[0] if row and row[0] is not None else 0,
                "total_mistakes": row[1] if row and row[1] is not None else 0,
                "last_played": row[2] if row and row[2] is not None else "Never"
            }
    conn.close()
    return progress

def progress_tracker(username, master=None):
    if master:
        root = tk.Toplevel(master)
    else:
        root = tk.Tk()
    root.title(f"{username}'s Progress")
    root.configure(bg="#2C8102")
    root.state("zoomed")
    icon_path = os.path.join("assets", "logo2.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)

    border = tk.Frame(root, bg="#2C8102", padx=5, pady=5)
    border.pack(expand=True, fill="both", padx=15, pady=15)

    content = tk.Frame(border, bg="#f7e7ce")
    content.pack(expand=True, fill="both")

    logo_path = os.path.join("assets", "logo.png")
    if os.path.exists(logo_path):
        logo_img = Image.open(logo_path).resize((220, 120))
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(content, image=logo_photo, bg="#f7e7ce")
        logo_label.image = logo_photo
        logo_label.grid(row=0, column=0, columnspan=4, pady=(20, 5))
    else:
        logo_label = tk.Label(content, text="Smart Sprouts", font=("Comic Sans MS", 36, "bold"), bg="#f7e7ce", fg="#172255")
        logo_label.grid(row=0, column=0, columnspan=4, pady=(30, 10))

    subtitle = tk.Label(content, text="Your Progress", font=("Arial", 28, "bold"), bg="#f7e7ce", fg="#2C8102")
    subtitle.grid(row=1, column=0, columnspan=4, pady=(0, 20))

    progress = get_user_progress(username)

    for col, (display_name, game_code, icon_filename) in enumerate(GAMES):
        for row, (diff_label, diff_code) in enumerate(DIFFICULTIES):
            frame = tk.Frame(
                content,
                bg="#f7e7ce",
                padx=12,
                pady=12,
                borderwidth=3,
                relief="groove", 
                highlightbackground="#2C8102",
                highlightthickness=2
            )
            frame.grid(row=row+2, column=col, padx=30, pady=20, sticky="nsew")
            content.grid_rowconfigure(row+2, weight=1)
            content.grid_columnconfigure(col, weight=1)
            icon_path = os.path.join("assets", icon_filename)
            if os.path.exists(icon_path):
                icon_img = Image.open(icon_path).resize((48, 48))
                icon_photo = ImageTk.PhotoImage(icon_img)
                icon_label = tk.Label(frame, image=icon_photo, bg="#f7e7ce")
                icon_label.image = icon_photo
                icon_label.pack(pady=(0, 6))

            tk.Label(frame, text=f"{display_name}\n({diff_label})", font=("Arial", 16, "bold"), bg="#f7e7ce", fg="#2C8102").pack(pady=(0, 10))

            p = progress[(game_code, diff_code)]
            info_font = ("Arial", 13)
            tk.Label(frame, text=f"Highest Level: {p['max_level']}", font=info_font, bg="#f7e7ce", anchor="w").pack(anchor="w")
            tk.Label(frame, text=f"Total Mistakes: {p['total_mistakes']}", font=info_font, bg="#f7e7ce", anchor="w").pack(anchor="w")
            tk.Label(frame, text=f"Last Played: {p['last_played']}", font=info_font, bg="#f7e7ce", anchor="w").pack(anchor="w")

    root.mainloop()


if __name__ == "__main__":
    progress_tracker("testuser")

