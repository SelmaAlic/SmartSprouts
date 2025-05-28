import tkinter as tk 
from tkinter import messagebox
import sqlite3
import bcrypt
from PIL import Image, ImageTk
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from auth import authenticate
from encryption import to_encrypt
from age_picker import age_picker

current_username=" "

def setup_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS login_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

setup_database()

def center_window(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

def clear_placeholder(event, entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, "end")
        entry.config(fg='black', show='*' if placeholder == "Password" else '')

def restore_placeholder(event, entry, placeholder):
    if entry.get() == "":
        entry.insert(0, placeholder)
        entry.config(fg='gray')
        if placeholder == "Password":
            entry.config(show='')

def on_enter(e, btn, hover_color):
    btn.config(bg=hover_color)

def on_leave(e, btn, original_color):
    btn.config(bg=original_color)

#Wrapping login GUI in a callable function
def show_login_window(parent=None): 
    global username_entry, password_entry, root, current_username 

    if parent:
        parent.destroy()

    root = tk.Tk()
    root.title("Smart Sprouts Login")
    root.state('zoomed')
    root.iconbitmap(os.path.join("assets", "logo2.ico"))

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    border_frame = tk.Frame(root, bg="#88B04B", width=screen_width, height=screen_height)
    border_frame.pack(fill="both", expand=True)

    content_frame = tk.Frame(border_frame, bg="#f7e7ce")
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    frame = tk.Frame(content_frame, bg="#f7e7ce")
    frame.place(relx=0.5, rely=0.5, anchor="center")

    try:
        logo_img = Image.open(os.path.join("assets", "logo.png"))
        logo_img = logo_img.resize((400, 250))
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(frame, image=logo_photo, bg="#f7e7ce")
        logo_label.image = logo_photo
        logo_label.pack(pady=(10, 0))
    except Exception as e:
        print("Logo not found:", e)

    username_entry = tk.Entry(frame, font=("Arial", 16), bd=2, relief="groove", fg="gray")
    username_entry.insert(0, "Username")
    username_entry.pack(pady=10)

    password_entry = tk.Entry(frame, font=("Arial", 16), bd=2, relief="groove", fg="gray", show="")
    password_entry.insert(0, "Password")
    password_entry.pack(pady=10)

    for e, p in [(username_entry, "Username"), (password_entry, "Password")]:
        e.bind("<FocusIn>", lambda e, ent=e, ph=p: clear_placeholder(e, ent, ph))
        e.bind("<FocusOut>", lambda e, ent=e, ph=p: restore_placeholder(e, ent, ph))

    button_frame = tk.Frame(frame, bg="#f7e7ce")
    button_frame.pack(pady=5)

    login_btn = tk.Button(button_frame, text="Login", font=("Arial", 14, "bold"), bg="#88B04B", fg="white", width=12, command=login)
    login_btn.pack(side="left", padx=10)
    login_btn.bind("<Enter>", lambda e: on_enter(e, login_btn, "#6dbf3d"))
    login_btn.bind("<Leave>", lambda e: on_leave(e, login_btn, "#88B04B"))

    create_account_btn = tk.Button(button_frame, text="Create Account", font=("Arial", 14, "bold"), bg="#172255", fg="white", width=16, command=open_create_account_window)
    create_account_btn.pack(side="left", padx=10)
    create_account_btn.bind("<Enter>", lambda e: on_enter(e, create_account_btn, "#4a90e2"))
    create_account_btn.bind("<Leave>", lambda e: on_leave(e, create_account_btn, "#172255"))

    forgot_password_btn = tk.Button(frame, text="Forgot Password?", font=("Arial", 12, "underline"), bg="#f7e7ce", fg="#172255", bd=0, command=forgot_password)
    forgot_password_btn.pack(pady=(0, 10))
    forgot_password_btn.bind("<Enter>", lambda e: on_enter(e, forgot_password_btn, "#cce7b0"))
    forgot_password_btn.bind("<Leave>", lambda e: on_leave(e, forgot_password_btn, "#f7e7ce"))

    root.mainloop()
    return current_username


def login():
    global current_username
    username = username_entry.get()
    password = password_entry.get()

    if username in ("", "Username") or password in ("", "Password"):
        messagebox.showwarning("Input Error", "Please enter both username and password.")
        return

    if authenticate(username, password):
        messagebox.showinfo("Login Successful", f"Welcome, {username}!")
        current_username=username
        root.destroy()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def open_create_account_window():
    win = tk.Toplevel(root)
    win.title("Create Account")
    win.iconbitmap(os.path.join("assets", "logo2.ico"))
    win.configure(bg="#88B04B")
    win.geometry("400x500")
    win.grab_set()

    frame = tk.Frame(win, bg="#f7e7ce", padx=20, pady=20)
    frame.pack(expand=True, fill="both", padx=10, pady=10)

    tk.Label(frame, text="Create Account", font=("Comic Sans MS", 18, "bold"), bg="#f7e7ce").pack(pady=10)

    new_user = tk.Entry(frame, font=("Arial", 14), fg="gray")
    new_user.insert(0, "Username")
    new_user.pack(pady=5)

    new_pass = tk.Entry(frame, font=("Arial", 14), fg="gray")
    new_pass.insert(0, "Password")
    new_pass.pack(pady=5)

    for e, p in [(new_user, "Username"), (new_pass, "Password")]:
        e.bind("<FocusIn>", lambda e, ent=e, ph=p: clear_placeholder(e, ent, ph))
        e.bind("<FocusOut>", lambda e, ent=e, ph=p: restore_placeholder(e, ent, ph))

    def create_account():
        username = new_user.get()
        password = new_pass.get()

        if username in ("", "Username") or password in ("", "Password"):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        hashed_pw = to_encrypt(password)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO login_info (username, password) VALUES (?, ?)", (username, hashed_pw))
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully!")
            win.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
        conn.close()

    tk.Button(frame, text="Create Account", bg="#4682B4", fg="white", font=("Arial", 14, "bold"), command=create_account).pack(pady=20)
    center_window(win)

def forgot_password():
    win = tk.Toplevel(root)
    win.title("Reset Password")
    win.iconbitmap(os.path.join("assets", "logo2.ico"))
    win.configure(bg="#88B04B")
    win.geometry("400x300")
    win.grab_set()

    frame = tk.Frame(win, bg="#f7e7ce", padx=20, pady=20)
    frame.pack(expand=True, fill="both", padx=10, pady=10)

    tk.Label(frame, text="Reset Password", font=("Comic Sans MS", 18, "bold"), bg="#f7e7ce").pack(pady=10)

    email_entry = tk.Entry(frame, font=("Arial", 14), fg="gray")
    email_entry.insert(0, "Enter your Email")
    email_entry.pack(pady=10)

    email_entry.bind("<FocusIn>", lambda e: clear_placeholder(e, email_entry, "Enter your Email"))
    email_entry.bind("<FocusOut>", lambda e: restore_placeholder(e, email_entry, "Enter your Email"))

    def send_reset_email():
        email = email_entry.get()
        if email == "" or email == "Enter your Email":
            messagebox.showwarning("Input Error", "Please enter your email.")
            return

        try:
            message = MIMEMultipart()
            message["From"] = "your_email@example.com"
            message["To"] = email
            message["Subject"] = "Password Reset Request"
            body = "Click the link to reset your password."
            message.attach(MIMEText(body, "plain"))

            with smtplib.SMTP("smtp.example.com", 587) as server:
                server.starttls()
                server.login("your_email@example.com", "your_password")
                server.sendmail(message["From"], message["To"], message.as_string())

            messagebox.showinfo("Success", "Password reset email sent!")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error sending email: {e}")

    tk.Button(frame, text="Reset", font=("Arial", 14, "bold"), bg="#FF6347", fg="white", command=send_reset_email).pack(pady=20)
    center_window(win)