"""
PassGuard - A Password Security Toolkit (GUI)
Lab 1 - Python (Level 200)
Author: Adjei Dodo-Mensah Alexander | Index No: 2526405108
"""

import string
import secrets
import hashlib
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

LOG_FILE = "passguard_log.txt"
USERS_FILE = "passguard_users.txt"
COMMON_PASSWORDS = [
    "123456", "password", "123456789", "12345678", "12345",
    "qwerty", "abc123", "111111", "123123", "admin",
    "letmein", "welcome", "iloveyou", "monkey", "football",
    "password1", "000000", "ghana123", "accra123", "god123",
    "0987654321", "222333", "iamaboy", "goaway", "mynameis",
]

COLOURS = {"VERY WEAK": "#b71c1c", "WEAK": "#e53935",
           "MEDIUM": "#fb8c00", "STRONG": "#2e7d32", "VERY STRONG": "#00e676"}



# LOGIC FUNCTIONS
def has_repeats(password):
    """Return True if any character appears 3 or more times in a row."""
    for i in range(len(password) - 2):
        if password[i] == password[i + 1] == password[i + 2]:
            return True
    return False


def contains_name(password, name):
    """Return True if the password contains the user's name (or any part
    of it that is at least 3 letters long)."""
    pw = password.lower()
    for part in name.lower().split():
        if len(part) >= 3 and part in pw:
            return True
    return False


def check_strength(password, name=""):
    """Return (score, label, tips) for password."""
    score = 0
    tips = []

    if password.lower() in COMMON_PASSWORDS:
        return 0, "VERY WEAK", ["This is one of the most common passwords.Dont use it."]
    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1
        tips.append("For extra strength use 12 characters or more.")
    else:
        tips.append("Too short.Use at least 8 characters.")

    if any(ch.isupper() for ch in password):
        score += 1
    else:
        tips.append("Add an uppercase letter(A-Z).")

    if any(ch.islower() for ch in password):
        score += 1
    else:
        tips.append("Add an lowercase letter(a-z).")

    if any(ch.isdigit() for ch in password):
        score += 1
    else:
        tips.append("Add a digit(0-9).")

    if any(ch in string.punctuation for ch in password):
        score += 1
    else:
        tips.append("Add a punctuation character such as ! @ # $ %.")

#feature 3: no repeats rule
    if has_repeats(password):
        score -= 1
        tips.append("Avoid 3 identical characters in a row (e.g. 111, aaa).")

#feature 4: personal info check
    if name.strip() and contains_name(password, name):
        score -= 1
        tips.append("Your password contains your name. Don't use personal info.")

    score = max(score, 0)


    if score <= 2:
        label = "VERY WEAK"
    elif score == 3:
        label = "WEAK"
    elif score == 4:
        label = "MEDIUM"
    elif score <= 6:
        label = "STRONG"
    else:
        label = "VERY STRONG"

    return score, label, tips

def generate_password(length=16):
    """Generate a password."""
    if length < 8:
        length = 8
    all_chars = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = "".join(secrets.choice(all_chars) for _ in range(length))
        score, label, tips = check_strength(password)
        if label == "STRONG":
            return password


def hash_password(password):
    """Return the SHA-256 hash of a password as hex text."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def on_hash():
    password = password_entry.get()
    if password == "":
        messagebox.showwarning("PassGuard", "Please enter a password.")
        return
    hash_var.set(hash_password(password))


def save_to_log(password, score, label):
    """Save a check. Only part of the HASH is stored, never the password."""
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    short_hash = hash_password(password)[:10]
    record = f"{time_now} | {short_hash}... | {score}/6 | {label}"
    with open(LOG_FILE, "a") as file:
        file.write(record + "\n")
    return record


def load_log():
    """Return a list of saved records (empty list if no file yet)."""
    try:
        with open(LOG_FILE, "r") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        return []


def load_users():
        """Return {username: hash} from the users file (empty if no file yet)."""
        users = {}
        try:
            with open(USERS_FILE, "r") as file:
                for line in file:
                    line = line.strip()
                    if "|" in line:
                        name, stored_hash = line.split("|", 1)
                        users[name] = stored_hash
        except FileNotFoundError:
            pass
        return users



# GUI HANDLERS
def live_check(event=None):
    """Update the strength bar every time a key is pressed."""
    password = password_entry.get()
    if password == "":
        strength_bar["value"] = 0
        bar_style.configure("Strength.Horizontal.TProgressbar",
                            background="grey")
        result_label.config(text="Type a password...", fg="grey")
        tips_label.config(text="")
        return
    score, label, tips = check_strength(password, name_entry.get())
    strength_bar["value"] = score
    bar_style.configure("Strength.Horizontal.TProgressbar",
                        background=COLOURS[label])
    result_label.config(text=f"{label}  ({score}/6)", fg=COLOURS[label])
    tips_label.config(text="\n".join("- " + tip for tip in tips))

def toggle_show():
    if show_var.get():
        password_entry.config(show="")
    else:
        password_entry.config(show="*")


def on_hash():
    password = password_entry.get()
    if password == "":
        messagebox.showwarning("PassGuard", "Please enter a password.")
        return
    hash_var.set(hash_password(password))


def on_generate():
    new_password = generate_password(length_var.get())
    generated_var.set(new_password)


def on_copy():
    root.clipboard_clear()
    root.clipboard_append(generated_var.get())
    messagebox.showinfo("PassGuard","Password copied to clipboard.")


def on_use_generated():
    """Feature 2: move the generated password into the checkbox."""
    new_password = generated_var.get()
    if new_password == "":
        messagebox.showwarning("PassGuard", "Generate a password first.")
        return
    password_entry.delete(0, tk.END)
    password_entry.insert(0, new_password)
    live_check()


def on_check():
    password = password_entry.get()
    if password == "":
        messagebox.showwarning("PassGuard", "Please enter a password first.")
        return
    score, label, tips = check_strength(password)
    record = save_to_log(password, score, label)
    history_list.insert(tk.END, record)
    messagebox.showinfo("PassGuard",f"{label}  ({score}/6)\nSaved to history")


def on_clear_history():
    """Feature 1: confirm, then empty the file and the list box."""
    if not messagebox.askyesno("PassGuard",
                            "Are you sure you want to clear the history?"):
        return
    try:
        open(LOG_FILE, "w").close()
    except OSError as error:
        messagebox.showerror("PassGuard", f"Could not clear the file:\n{error}")
        return
    history_list.delete(0, tk.END)



#GUI LAYOUT
root = tk.Tk()
root.title("Password Security Toolkit")
bar_style = ttk.Style()
bar_style.theme_use("clam")
bar_style.configure("Strength.Horizontal.TProgressbar",
                    troughcolor="#dddddd", background="grey",
                    bordercolor="#dddddd", thickness=14)
root.geometry("580x690")
root.minsize(580, 560)
root.resizable(False, False)

title_label = tk.Label(root, text="PassGuard", font=("Segoe UI", 22, "bold"),
fg="#0d47a1")
title_label.pack(pady=(15, 0))
tk.Label(root, text="Check, generate and hash passwords safely").pack()



# SECTION 1
check_frame = tk.LabelFrame(root, text="1. Check password strength",
padx=10, pady=10)
check_frame.pack(fill="x", padx=15, pady=10)

tk.Label(check_frame, text="Your name (optional):").pack(anchor="w")
name_entry = tk.Entry(check_frame, font=("Segoe UI", 11))
name_entry.pack(fill="x", pady=(0, 8))
name_entry.bind("<KeyRelease>", live_check)

tk.Label(check_frame, text="Password:").pack(anchor="w")
password_entry = tk.Entry(check_frame, show="*", font=("Segoe UI", 12),
width=35)
password_entry.pack(fill="x")
password_entry.bind("<KeyRelease>", live_check)

show_var = tk.BooleanVar()
tk.Checkbutton(check_frame, text="Show password", variable=show_var,
               command=toggle_show).pack(anchor="w")

strength_bar = ttk.Progressbar(check_frame, maximum=6, length=400,
                               style="Strength.Horizontal.TProgressbar")
strength_bar.pack(fill="x", pady=5)

result_label = tk.Label(check_frame, text="Start typing password...",
                        font=("Segoe UI", 12, "bold"), fg="grey")
result_label.pack(anchor="w")

tips_label = tk.Label(check_frame, text="", justify="left", fg="#444")
tips_label.pack(anchor="w")

button_row = tk.Frame(check_frame)
button_row.pack(anchor="w", pady=(5, 0))
tk.Button(button_row, text="Hash it", command=on_hash,
          width=12).pack(side="left", padx=5)
tk.Button(button_row, text="Save check", command=on_check,
          width=12).pack(side="left", padx=5)

hash_var = tk.StringVar()
tk.Entry(check_frame, textvariable=hash_var, state="readonly",
         font=("Consolas",8)).pack(fill="x", pady=(5, 0))


#SECTION 2
gen_frame = tk.LabelFrame(root, text="2.Generate strong passwords",
padx=10, pady=10)
gen_frame.pack(fill="x", padx=15, pady=5)

gen_top = tk.Frame(gen_frame)
gen_top.pack(fill="x")
tk.Label(gen_top, text="Length:").pack(side="left")
length_var = tk.IntVar(value=16)
tk.Spinbox(gen_top, from_=8, to=32, width=4, textvariable=length_var,
           state="readonly").pack(side="left", padx=5)
tk.Button(gen_top, text="Generate", command=on_generate).pack(side="left",
padx=5)

generated_var = tk.StringVar()
tk.Entry(gen_top, textvariable=generated_var, state="readonly",
         font=("Consolas", 11), width=22).pack(side="left", padx=5)
tk.Button(gen_top, text="Copy", command=on_copy).pack(side="left")

tk.Button(gen_frame, text="Use generated password",
          command=on_use_generated).pack(anchor="w", pady=(8, 0))


#SECTION 3
hist_frame = tk.LabelFrame(root, text=" 3. Check history(hashes only)",
padx=10, pady=10)
hist_frame.pack(fill="both", expand=True, padx=15, pady=10)

history_list = tk.Listbox(hist_frame, font=("Consolas", 9), height=4,)
history_list.pack(side="top", fill="both", expand=True)


tk.Button(hist_frame, text="Clear history",
          command=on_clear_history).pack(anchor="e", pady=(5, 0))


for saved_record in load_log():
    history_list.insert(tk.END, saved_record)


root.mainloop()