import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3

# Define clear_placeholder function globally
def clear_placeholder(event, entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, "end")

def login():
    username = username_entry.get()
    password = password_entry.get()

    if username == "Username" or password == "Password" or not username or not password:
        messagebox.showwarning("Input Error", "Please enter both username and password.")
        return

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()

    if result:
        if remember_me_var.get():
            print("User wants to be remembered.")
        messagebox.showinfo("Login Successful", f"Welcome, {username}!")
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

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

    def create_account_in_db():
        username = new_username_entry.get()
        password = new_password_entry.get()
        email = email_entry.get()

        if username in ("", "Username") or password in ("", "Password") or email in ("", "Email"):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists. Please choose another one.")
        else:
            cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, password, email))
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully!")
            create_window.destroy()
        conn.close()

    create_btn = tk.Button(create_window, text="Create Account", font=("Arial", 14, "bold"), bg="#4682B4", fg="white", command=create_account_in_db)
    create_btn.pack(pady=20)

    create_btn.bind("<Enter>", lambda e: create_btn.config(bg="#5a9bd5"))
    create_btn.bind("<Leave>", lambda e: create_btn.config(bg="#4682B4"))

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
root.configure(bg="#add8e6")

# Set the window icon
root.iconbitmap("logo2.ico")  # Ensure logo.ico is in the same directory

# Main Frame
frame = tk.Frame(root, bg="white", bd=5, relief="ridge")
frame.place(relx=0.5, rely=0.5, anchor="center")

# Logo (use a .png image if you don't have .ico format)
try:
    logo_image = Image.open("logo.png")
    logo_image = logo_image.resize((300, 300))
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(frame, image=logo_photo, bg="white")
    logo_label.pack(pady=(10, 0))
except Exception as e:
    print("Logo not found:", e)

# Username Entry
username_entry = tk.Entry(frame, font=("Arial", 16), bd=2, relief="groove")
username_entry.insert(0, "Username")
username_entry.pack(pady=10)
username_entry.bind("<FocusIn>", lambda e: clear_placeholder(e, username_entry, "Username"))

# Password Entry
password_entry = tk.Entry(frame, font=("Arial", 16), bd=2, relief="groove")
password_entry.insert(0, "Password")
password_entry.pack(pady=10)
password_entry.bind("<FocusIn>", lambda e: clear_placeholder(e, password_entry, "Password"))

# Remember Me
remember_me_var = tk.BooleanVar()
remember_me_check = tk.Checkbutton(frame, text="Remember Me", variable=remember_me_var, font=("Arial", 14), bg="white", activebackground="#90ee90")
remember_me_check.pack(pady=10)

# Buttons
buttons_frame = tk.Frame(frame, bg="white")
buttons_frame.pack(pady=20)

login_button = tk.Button(buttons_frame, text="Login", font=("Arial", 16, "bold"), bg="#32cd32", fg="white", width=12, command=login)
login_button.grid(row=0, column=0, padx=10)

create_account_button = tk.Button(buttons_frame, text="Create Account", font=("Arial", 16, "bold"), bg="#4682B4", fg="white", width=16, command=open_create_account_window)
create_account_button.grid(row=0, column=1, padx=10)

# Hover Effects
login_button.bind("<Enter>", lambda e: login_button.config(bg="#3ee63e"))
login_button.bind("<Leave>", lambda e: login_button.config(bg="#32cd32"))

create_account_button.bind("<Enter>", lambda e: create_account_button.config(bg="#5a9bd5"))
create_account_button.bind("<Leave>", lambda e: create_account_button.config(bg="#4682B4"))

# Forgot Password
forgot_password_button = tk.Button(frame, text="Forgot Password?", font=("Arial", 12, "underline"), bg="white", fg="blue", bd=0, command=forgot_password)
forgot_password_button.pack(pady=(0, 10))

root.mainloop()
