import tkinter as tk
from PIL import Image, ImageTk

# Sticker data
stickers = [
    ("Well Done", "well_done_gray.png", True),
    ("Wow", "wow_gray.png", True),
    ("You Did It", "you_did_it_color.png", False),
    ("Smart", "smart_gray.png", True),
    ("Crazy", "crazy_color.png", False),
    ("Pro", "pro_gray.png", True),
]

# Create main window
root = tk.Tk()
root.title("Sticker Achievements")
root.configure(bg="#f7e7ce")
root.geometry("800x600")

# Title label
title = tk.Label(root, text="Sticker Achievements", bg="#f7e7ce", fg="#333", font=("Arial", 24, "bold"))
title.pack(pady=20)

# Grid frame
frame = tk.Frame(root, bg="#f7e7ce")
frame.pack()

# Load and display stickers
images = []
for index, (name, image_file, is_locked) in enumerate(stickers):
    try:
        img = Image.open(image_file).resize((100, 100))
        if is_locked:
            img = img.convert("LA")  # Grayscale
        photo = ImageTk.PhotoImage(img)
        images.append(photo)  # Keep a reference to avoid garbage collection

        # Create container for each sticker
        container = tk.Frame(frame, bg="#88B04B", bd=3, relief="solid")
        container.grid(row=index // 3, column=index % 3, padx=15, pady=15)

        lbl_img = tk.Label(container, image=photo, bg="#88B04B")
        lbl_img.pack()

        lbl_text = tk.Label(container, text=name, bg="#88B04B", fg="white", font=("Arial", 12, "bold"))
        lbl_text.pack(pady=5)

    except Exception as e:
        print(f"Error loading {name}: {e}")

root.mainloop()
