import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# Constants for encryption
SALT = b'\xf8\xae\xd5$\xab\x1f"\xd6hw80\xd0e_&e\x90(\x89}s\x97\xd5\xc3|[\x8d\x9aP\xdb\x95'
FIXED_IV = b'\x00' * 16  # 16 bytes

# Encrypt the password consistently
def to_encrypt(password):
    key = PBKDF2(password, SALT, dkLen=32)
    cipher = AES.new(key, AES.MODE_CBC, FIXED_IV)
    encrypted = cipher.encrypt(pad(password.encode(), AES.block_size))
    return encrypted

# Authentication logic
def authenticate(username, encrypted_password):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        stored_encrypted_password = result[0]
        if encrypted_password == stored_encrypted_password:
            return True
    return False

# Placeholder utilities
def clear_placeholder(event, entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, "end")

def restore_placeholder(event, entry, placeholder):
    if entry.get() == "":
        entry.insert(0, placeholder)

# Login handler
def login():
    username = username_entry.get()
    raw_password = password_entry.get()

    if username == "Username" or raw_password == "Password" or not username or not raw_password:
        messagebox.showwarning("Input Error", "Please enter both username and password.")
        return

    encrypted_password = to_encrypt(raw_password)

    if authenticate(username, encrypted_password):
        if remember_me_var.get():
            print("User wants to be remembered.")
        messagebox.showinfo("Login Successful", f"Welcome, {username}!")
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

# Create account handler
def open_create_account_window():
    create_window = tk.Toplevel(root)
    create_window.title("Create Account")
    create_window.geometry("400x500")
    create_window.configure(bg="#FFFAF0")

    tk.Label(create_window, text="Create Your Account", font=("Comic Sans MS", 18, "bold"), bg="#FFFAF0").pack(pady=20)

    new_username_entry = tk.Entry(create_window, font=("Arial", 14), bd=2, relief="groove")
    new_username_entry.insert(0, "Username")
    new_username_entry.pack(pady=5)

    new_password_entry = tk.Entry(create_window, font=("Arial", 14), bd=2, relief="groove")
    new_password_entry.insert(0, "Password")
    new_password_entry.pack(pady=5)

    email_entry = tk.Entry(create_window, font=("Arial", 14), bd=2, relief="groove")
    email_entry.insert(0, "Email")
    email_entry.pack(pady=5)

    new_username_entry.bind("<FocusIn>", lambda e: clear_placeholder(e, new_username_entry, "Username"))
    new_password_entry.bind("<FocusIn>", lambda e: clear_placeholder(e, new_password_entry, "Password"))
    email_entry.bind("<FocusIn>", lambda e: clear_placeholder(e, email_entry, "Email"))

    new_username_entry.bind("<FocusOut>", lambda e: restore_placeholder(e, new_username_entry, "Username"))
    new_password_entry.bind("<FocusOut>", lambda e: restore_placeholder(e, new_password_entry, "Password"))
    email_entry.bind("<FocusOut>", lambda e: restore_placeholder(e, email_entry, "Email"))

    def create_account_in_db():
        username = new_username_entry.get()
        raw_password = new_password_entry.get()
        email = email_entry.get()

        if username in ("", "Username") or raw_password in ("", "Password") or email in ("", "Email"):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        encrypted_password = to_encrypt(raw_password)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists. Please choose another one.")
        else:
            cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, encrypted_password, email))
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully!")
            create_window.destroy()
        conn.close()

    create_btn = tk.Button(create_window, text="Create Account", font=("Arial", 14, "bold"), bg="#4682B4", fg="white", command=create_account_in_db)
    create_btn.pack(pady=20)

    create_btn.bind("<Enter>", lambda e: create_btn.config(bg="#5a9bd5"))
    create_btn.bind("<Leave>", lambda e: create_btn.config(bg="#4682B4"))

# Forgot password (not implemented fully)
def forgot_password():
    forgot_window = tk.Toplevel(root)
    forgot_window.title("Reset Password")
    forgot_window.geometry("400x300")
    forgot_window.configure(bg="#FFFAF0")

    tk.Label(forgot_window, text="Reset Your Password", font=("Comic Sans MS", 18, "bold"), bg="#FFFAF0").pack(pady=20)
    email_entry = tk.Entry(forgot_window, font=("Arial", 14), bd=2, relief="groove")
    email_entry.insert(0, "Enter your Email")
    email_entry.pack(pady=10)
    email_entry.bind("<FocusIn>", lambda e: clear_placeholder(e, email_entry, "Enter your Email"))
    tk.Button(forgot_window, text="Reset Password", font=("Arial", 14, "bold"), bg="#FF6347", fg="white").pack(pady=20)

# GUI Setup
root = tk.Tk()
root.title("Smart Sprouts Login")
root.state('zoomed')
root.iconbitmap("logo2.ico")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

border_frame = tk.Frame(root, bg="#88B04B", width=screen_width, height=screen_height)
border_frame.pack(fill="both", expand=True)

content_frame = tk.Frame(border_frame, bg="#f7e7ce")
content_frame.pack(fill="both", expand=True, padx=20, pady=20)

frame = tk.Frame(content_frame, bg="#f7e7ce")
frame.place(relx=0.5, rely=0.5, anchor="center")

try:
    logo_image = Image.open("logo.png")
    logo_image = logo_image.resize((int(screen_width * 0.5), int(screen_height * 0.5)))
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(frame, image=logo_photo, bg="#f7e7ce")
    logo_label.pack(pady=(10, 0))
except Exception as e:
    print("Logo not found:", e)

username_entry = tk.Entry(frame, font=("Arial", 16), bd=2, relief="groove", fg="#172255")
username_entry.insert(0, "Username")
username_entry.pack(pady=10)
username_entry.bind("<FocusIn>", lambda e: clear_placeholder(e, username_entry, "Username"))
username_entry.bind("<FocusOut>", lambda e: restore_placeholder(e, username_entry, "Username"))

password_entry = tk.Entry(frame, font=("Arial", 16), bd=2, relief="groove", fg="#172255")
password_entry.insert(0, "Password")
password_entry.pack(pady=10)
password_entry.bind("<FocusIn>", lambda e: clear_placeholder(e, password_entry, "Password"))
password_entry.bind("<FocusOut>", lambda e: restore_placeholder(e, password_entry, "Password"))

remember_me_var = tk.BooleanVar()
remember_me_check = tk.Checkbutton(frame, text="Remember Me", variable=remember_me_var, font=("Arial", 14), bg="#f7e7ce", activebackground="#f7e7ce", fg="#172255", selectcolor="#f7e7ce")
remember_me_check.pack(pady=10)

buttons_frame = tk.Frame(frame, bg="#f7e7ce")
buttons_frame.pack(pady=20)

login_button = tk.Button(buttons_frame, text="Login", font=("Arial", 16, "bold"), bg="#88B04B", fg="white", width=12, command=login)
login_button.grid(row=0, column=0, padx=10)

create_account_button = tk.Button(buttons_frame, text="Create Account", font=("Arial", 16, "bold"), bg="#172255", fg="white", width=16, command=open_create_account_window)
create_account_button.grid(row=0, column=1, padx=10)

login_button.bind("<Enter>", lambda e: login_button.config(bg="#7AA739"))
login_button.bind("<Leave>", lambda e: login_button.config(bg="#88B04B"))
create_account_button.bind("<Enter>", lambda e: create_account_button.config(bg="#1a3277"))
create_account_button.bind("<Leave>", lambda e: create_account_button.config(bg="#172255"))

forgot_password_button = tk.Button(frame, text="Forgot Password?", font=("Arial", 12, "underline"), bg="#f7e7ce", fg="#172255", bd=0, command=forgot_password)
forgot_password_button.pack(pady=(0, 10))

root.mainloop()
