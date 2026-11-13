from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry
from tkinter import messagebox
import sqlite3 as db
import csv

# --- Database Setup ---
def init_db():
    conn = db.connect("shopManagement.db")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS stocks (
        date TEXT,
        product TEXT PRIMARY KEY,
        price INTEGER,
        quantity INTEGER
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS sales (
        date TEXT,
        product TEXT,
        quantity INTEGER,
        price INTEGER,
        total INTEGER
    )''')
    cur.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?)", ("admin", "admin123", "admin"))
    conn.commit()
    conn.close()

# --- Global Styles ---
def setup_style():
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TLabel", font=("Segoe UI", 11))
    style.configure("TButton", font=("Segoe UI Semibold", 10), padding=6)
    style.configure("TEntry", font=("Segoe UI", 10))
    style.configure("TCombobox", font=("Segoe UI", 10))
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)
    style.configure("Treeview.Heading", font=("Segoe UI Semibold", 11), background="#007acc", foreground="white")
    style.map('TButton', background=[('active', '#005f99'), ('!active', '#007acc')])

# --- Login Window ---
def login_screen():
    def attempt_login():
        username = user_var.get()
        password = pass_var.get()
        conn = db.connect("shopManagement.db")
        cur = conn.cursor()
        cur.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        result = cur.fetchone()
        conn.close()

        if result:
            root.destroy()
            if result[0] == 'admin':
                open_admin_panel()
            else:
                open_customer_panel()
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password")

    global root
    root = Tk()
    root.title("Login Panel - Inventory Management")
    root.geometry("350x250")
    root.resizable(False, False)
    setup_style()

    frame = ttk.Frame(root, padding=20)
    frame.pack(expand=True, fill=BOTH)

    ttk.Label(frame, text="Login to Continue", font=("Segoe UI Semibold", 14)).pack(pady=10)

    user_var = StringVar()
    pass_var = StringVar()

    ttk.Label(frame, text="Username:").pack(anchor=W, pady=5)
    ttk.Entry(frame, textvariable=user_var).pack(fill=X)

    ttk.Label(frame, text="Password:").pack(anchor=W, pady=5)
    ttk.Entry(frame, textvariable=pass_var, show="*").pack(fill=X)

    ttk.Button(frame, text="Login", command=attempt_login).pack(pady=20, fill=X)

    root.mainloop()

# --- Admin Panel ---
def open_admin_panel():
    def addStock():
        product = product_var.get().strip()
        try:
            price = int(price_var.get())
            quantity = int(quantity_var.get())
        except ValueError:
            messagebox.showerror("Input Error", "Price and Quantity must be numbers")
            return
        date = date_var.get()

        if not product:
            messagebox.showerror("Input Error", "Product name is required")
            return

        conn = db.connect("shopManagement.db")
        cur = conn.cursor()
        cur.execute("SELECT quantity FROM stocks WHERE product=?", (product,))
        result = cur.fetchone()

        if result:
            new_quantity = result[0] + quantity
            cur.execute("UPDATE stocks SET quantity=?, price=?, date=? WHERE product=?",
                        (new_quantity, price, date, product))
        else:
            cur.execute("INSERT INTO stocks VALUES (?, ?, ?, ?)", (date, product, price, quantity))

        conn.commit()
        conn.close()
        viewStock()
        messagebox.showinfo("Success", f"Stock for '{product}' added/updated")

    def viewStock():
        for i in stock_tree.get_children():
            stock_tree.delete(i)

        conn = db.connect("shopManagement.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM stocks")
        for row in cur.fetchall():
            stock_tree.insert('', END, values=row)
        conn.close()

    def deleteProduct():
        selected = stock_tree.selection()
        if not selected:
            messagebox.showwarning("Select Product", "No product selected")
            return
        product = stock_tree.item(selected)['values'][1]
        conn = db.connect("shopManagement.db")
        cur = conn.cursor()
        cur.execute("DELETE FROM stocks WHERE product=?", (product,))
        conn.commit()
        conn.close()
        viewStock()
        messagebox.showinfo("Deleted", f"Product '{product}' deleted")

    def searchProduct():
        product = product_var.get().strip()
        for i in stock_tree.get_children():
            stock_tree.delete(i)

        conn = db.connect("shopManagement.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM stocks WHERE product LIKE ?", ('%' + product + '%',))
        for row in cur.fetchall():
            stock_tree.insert('', END, values=row)
        conn.close()

    def downloadReport():
        conn = db.connect("shopManagement.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM stocks")
        rows = cur.fetchall()
        with open("stock_report.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Product", "Price", "Quantity"])
            writer.writerows(rows)
        conn.close()
        messagebox.showinfo("Report Downloaded", "Stock report saved as stock_report.csv")

    def downloadSales():
        conn = db.connect("shopManagement.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM sales")
        rows = cur.fetchall()
        with open("sales_report.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Product", "Quantity", "Price", "Total"])
            writer.writerows(rows)
        conn.close()
        messagebox.showinfo("Report Downloaded", "Sales report saved as sales_report.csv")

    global date_var, product_var, price_var, quantity_var, stock_tree

    root2 = Tk()
    root2.title("Admin Panel")
    root2.geometry("850x600")
    setup_style()

    main_frame = ttk.Frame(root2, padding=15)
    main_frame.pack(fill=BOTH, expand=True)

    input_frame = ttk.LabelFrame(main_frame, text="Manage Stock", padding=10)
    input_frame.pack(fill=X, pady=10)

    date_var = StringVar()
    product_var = StringVar()
    price_var = StringVar()
    quantity_var = StringVar()

    ttk.Label(input_frame, text="Date:").grid(row=0, column=0)
    date_entry = DateEntry(input_frame, textvariable=date_var, width=12, date_pattern='yyyy-mm-dd')
    date_entry.grid(row=0, column=1, padx=5)
    date_var.set(date_entry.get_date().strftime('%Y-%m-%d'))

    ttk.Label(input_frame, text="Product:").grid(row=1, column=0)
    ttk.Entry(input_frame, textvariable=product_var).grid(row=1, column=1, padx=5)

    ttk.Label(input_frame, text="Price:").grid(row=2, column=0)
    ttk.Entry(input_frame, textvariable=price_var).grid(row=2, column=1, padx=5)

    ttk.Label(input_frame, text="Quantity:").grid(row=3, column=0)
    ttk.Entry(input_frame, textvariable=quantity_var).grid(row=3, column=1, padx=5)

    ttk.Button(input_frame, text="Add/Update", command=addStock).grid(row=4, column=0, columnspan=2, pady=10)

    ttk.Button(input_frame, text="Search", command=searchProduct).grid(row=4, column=2, padx=5)
    ttk.Button(input_frame, text="Delete", command=deleteProduct).grid(row=4, column=3, padx=5)

    tree_frame = ttk.Frame(main_frame)
    tree_frame.pack(fill=BOTH, expand=True)

    stock_tree = ttk.Treeview(tree_frame, columns=("Date", "Product", "Price", "Quantity"), show="headings")
    for col in ("Date", "Product", "Price", "Quantity"):
        stock_tree.heading(col, text=col)
        stock_tree.column(col, width=150, anchor=CENTER)
    stock_tree.pack(side=LEFT, fill=BOTH, expand=True)

    scroll = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=stock_tree.yview)
    stock_tree.configure(yscrollcommand=scroll.set)
    scroll.pack(side=RIGHT, fill=Y)

    report_btns = ttk.Frame(main_frame)
    report_btns.pack(pady=10)

    ttk.Button(report_btns, text="View All", command=viewStock).pack(side=LEFT, padx=10)
    ttk.Button(report_btns, text="Download Stock Report", command=downloadReport).pack(side=LEFT, padx=10)
    ttk.Button(report_btns, text="Download Sales Report", command=downloadSales).pack(side=LEFT, padx=10)

    viewStock()
    root2.mainloop()

# --- Customer Panel ---
def open_customer_panel():
    def sell():
        product = product_var.get().strip()
        try:
            quantity = int(quantity_var.get())
        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be numeric")
            return
        date = date_var.get()

        conn = db.connect("shopManagement.db")
        cur = conn.cursor()
        cur.execute("SELECT price, quantity FROM stocks WHERE product=?", (product,))
        result = cur.fetchone()

        if not result:
            messagebox.showerror("Error", "Product not found")
            conn.close()
            return

        price, stock_qty = result
        if quantity > stock_qty:
            messagebox.showerror("Error", "Not enough stock available")
            conn.close()
            return

        total = price * quantity
        cur.execute("INSERT INTO sales VALUES (?, ?, ?, ?, ?)", (date, product, quantity, price, total))
        cur.execute("UPDATE stocks SET quantity=? WHERE product=?", (stock_qty - quantity, product))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Sold {quantity} of '{product}'")
        product_var.set('')
        quantity_var.set('')

    rootC = Tk()
    rootC.title("Customer Panel")
    rootC.geometry("400x300")
    setup_style()

    frame = ttk.Frame(rootC, padding=20)
    frame.pack(fill=BOTH, expand=True)

    date_var = StringVar()
    product_var = StringVar()
    quantity_var = StringVar()

    ttk.Label(frame, text="Date:").pack(anchor=W)
    date_entry = DateEntry(frame, textvariable=date_var, date_pattern='yyyy-mm-dd')
    date_entry.pack(fill=X)
    date_var.set(date_entry.get_date().strftime('%Y-%m-%d'))

    ttk.Label(frame, text="Product Name:").pack(anchor=W)
    ttk.Entry(frame, textvariable=product_var).pack(fill=X)

    ttk.Label(frame, text="Quantity:").pack(anchor=W)
    ttk.Entry(frame, textvariable=quantity_var).pack(fill=X)

    ttk.Button(frame, text="Sell", command=sell).pack(pady=20, fill=X)

    rootC.mainloop()

# --- Start App ---
if __name__ == "__main__":
    init_db()
    login_screen()
