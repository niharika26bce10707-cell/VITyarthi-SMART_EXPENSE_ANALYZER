import tkinter as tk
from tkinter import messagebox
import sqlite3

# ---------------- DATABASE ----------------
conn = sqlite3.connect("expenses.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    amount REAL,
    category TEXT,
    note TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS budgets (
    username TEXT PRIMARY KEY,
    amount REAL
)
""")

conn.commit()

# ---------------- LOGIN ----------------
def register():
    username = user_entry.get().strip()
    password = pass_entry.get().strip()

    if not username or not password:
        messagebox.showerror("Error", "Enter username and password")
        return

    try:
        cur.execute("INSERT INTO users(username, password) VALUES (?, ?)",
                    (username, password))
        conn.commit()
        messagebox.showinfo("Success", "Registration successful")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists")


def login():
    username = user_entry.get().strip()
    password = pass_entry.get().strip()

    cur.execute("SELECT * FROM users WHERE username=? AND password=?",
                (username, password))

    if cur.fetchone():
        login_window.destroy()
        open_dashboard(username)
    else:
        messagebox.showerror("Error", "Invalid username or password")


# ---------------- EXPENSE FUNCTIONS ----------------
def add_expense(username, amount_box, category_box, note_box, output):
    amount = amount_box.get().strip()
    category = category_box.get().strip()
    note = note_box.get().strip()

    if not amount or not category:
        messagebox.showerror("Error", "Enter amount and category")
        return

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Amount must be a positive number")
        return

    cur.execute(
        "INSERT INTO expenses(username, amount, category, note) VALUES (?, ?, ?, ?)",
        (username, amount, category, note)
    )
    conn.commit()

    amount_box.delete(0, tk.END)
    category_box.delete(0, tk.END)
    note_box.delete(0, tk.END)

    messagebox.showinfo("Success", "Expense added")
    show_expenses(username, output)


def show_expenses(username, output):
    cur.execute(
        "SELECT id, amount, category, note FROM expenses WHERE username=?",
        (username,)
    )
    rows = cur.fetchall()

    output.delete("1.0", tk.END)

    if not rows:
        output.insert(tk.END, "No expenses found.\n")
        return

    total = 0
    for row in rows:
        total += row[1]
        output.insert(
            tk.END,
            f"ID: {row[0]} | Rs.{row[1]:.2f} | "
            f"{row[2]} | {row[3]}\n"
        )

    output.insert(tk.END, f"\nTotal Expense: Rs.{total:.2f}")


def delete_expense(username, id_box, output):
    expense_id = id_box.get().strip()

    if not expense_id.isdigit():
        messagebox.showerror("Error", "Enter a valid expense ID")
        return

    cur.execute(
        "DELETE FROM expenses WHERE id=? AND username=?",
        (int(expense_id), username)
    )
    conn.commit()

    if cur.rowcount == 0:
        messagebox.showerror("Error", "Expense not found")
    else:
        messagebox.showinfo("Success", "Expense deleted")

    id_box.delete(0, tk.END)
    show_expenses(username, output)


# ---------------- BUDGET ----------------
def set_budget(username, budget_box, budget_label):
    value = budget_box.get().strip()

    try:
        value = float(value)
        if value <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Enter a valid budget")
        return

    cur.execute(
        "INSERT OR REPLACE INTO budgets(username, amount) VALUES (?, ?)",
        (username, value)
    )
    conn.commit()

    budget_box.delete(0, tk.END)
    show_summary(username, budget_label)
    messagebox.showinfo("Success", "Budget saved")


def show_summary(username, label):
    cur.execute("SELECT SUM(amount) FROM expenses WHERE username=?", (username,))
    total = cur.fetchone()[0] or 0

    cur.execute("SELECT amount FROM budgets WHERE username=?", (username,))
    row = cur.fetchone()

    if row:
        budget = row[0]
        remaining = budget - total
        label.config(
            text=f"Budget: Rs.{budget:.2f}\n"
                 f"Spent: Rs.{total:.2f}\n"
                 f"Remaining: Rs.{remaining:.2f}"
        )
    else:
        label.config(
            text=f"Spent: Rs.{total:.2f}\nBudget not set"
        )


# ---------------- DASHBOARD ----------------
def open_dashboard(username):
    window = tk.Tk()
    window.title("Smart Expense Analyzer")
    window.geometry("700x650")

    tk.Label(
        window,
        text=f"Welcome, {username}",
        font=("Arial", 20, "bold")
    ).pack(pady=15)

    # Add expense
    frame = tk.LabelFrame(window, text="Add Expense", padx=10, pady=10)
    frame.pack(fill="x", padx=20)

    tk.Label(frame, text="Amount").grid(row=0, column=0, padx=5, pady=5)
    amount_box = tk.Entry(frame)
    amount_box.grid(row=0, column=1, padx=5)

    tk.Label(frame, text="Category").grid(row=1, column=0, padx=5, pady=5)
    category_box = tk.Entry(frame)
    category_box.grid(row=1, column=1, padx=5)

    tk.Label(frame, text="Note").grid(row=2, column=0, padx=5, pady=5)
    note_box = tk.Entry(frame, width=35)
    note_box.grid(row=2, column=1, padx=5)

    output = tk.Text(window, height=12, width=75)
    output.pack(pady=15)

    tk.Button(
        window, text="Add Expense",
        command=lambda: add_expense(
            username, amount_box, category_box, note_box, output
        )
    ).pack()

    tk.Button(
        window, text="Show Expenses",
        command=lambda: show_expenses(username, output)
    ).pack(pady=5)

    # Delete
    delete_frame = tk.Frame(window)
    delete_frame.pack(pady=5)

    tk.Label(delete_frame, text="Expense ID to delete:").pack(side="left")
    id_box = tk.Entry(delete_frame, width=10)
    id_box.pack(side="left", padx=5)

    tk.Button(
        delete_frame, text="Delete",
        command=lambda: delete_expense(username, id_box, output)
    ).pack(side="left")

    # Budget
    budget_frame = tk.LabelFrame(window, text="Budget", padx=10, pady=10)
    budget_frame.pack(fill="x", padx=20, pady=10)

    budget_box = tk.Entry(budget_frame)
    budget_box.pack(side="left", padx=5)

    budget_label = tk.Label(budget_frame, text="Budget not set")
    budget_label.pack(side="left", padx=20)

    tk.Button(
        budget_frame, text="Set Budget",
        command=lambda: set_budget(username, budget_box, budget_label)
    ).pack(side="left")

    tk.Button(
        window, text="Refresh Summary",
        command=lambda: show_summary(username, budget_label)
    ).pack(pady=5)

    show_summary(username, budget_label)
    window.mainloop()


# ---------------- START LOGIN WINDOW ----------------
login_window = tk.Tk()
login_window.title("Smart Expense Analyzer - Login")
login_window.geometry("400x300")

tk.Label(
    login_window,
    text="Smart Expense Analyzer",
    font=("Arial", 18, "bold")
).pack(pady=20)

tk.Label(login_window, text="Username").pack()
user_entry = tk.Entry(login_window)
user_entry.pack()

tk.Label(login_window, text="Password").pack(pady=(10, 0))
pass_entry = tk.Entry(login_window, show="*")
pass_entry.pack()

tk.Button(login_window, text="Login", command=login).pack(pady=15)
tk.Button(login_window, text="Register", command=register).pack()

login_window.mainloop()
conn.close()
