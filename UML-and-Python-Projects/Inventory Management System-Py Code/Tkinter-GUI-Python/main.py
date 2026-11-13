import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import shutil
import os
import csv

def create_input_pair(frame, label_text, row):
    label = ttk.Label(frame, text=label_text, style='Custom.TLabel')
    entry = ttk.Entry(frame, style='Custom.TEntry')
    label.grid(row=row, column=0, padx=5, pady=5, sticky="w")
    entry.grid(row=row, column=1, padx=5, pady=5)
    return label, entry

# Function to handle login
def login():
    username = username_entry.get()
    password = password_entry.get()

    if username == "Admin987" and password == "pwdguess-123":
        # Close the login window and open the inventory management dashboard
        login_window.destroy()
        open_dashboard()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

def on_enter(event):
    # Change button color on hover
    login_button.config(style='CustomHover.TButton')

def on_leave(event):
    # Restore button color when leaving hover
    login_button.config(style='Custom.TButton')

# Function to open the inventory management dashboard
def open_dashboard():
    # Create the main inventory management window
    root = tk.Tk()
    root.title("Home Page")

    # Function to create the products table in the database
    def create_product_table():
        connection = sqlite3.connect('inventory.db')
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                quantity INTEGER,
                price REAL,
                category TEXT
            )
        ''')
        connection.commit()
        connection.close()

    # Function to add a new product to the database
    def add_product():
        name = product_name_entry.get()
        quantity = int(product_quantity_entry.get())
        price = float(product_price_entry.get())
        category = product_category_entry.get()

        connection = sqlite3.connect('inventory.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO products (name, quantity, price, category) VALUES (?, ?, ?, ?)',
                       (name, quantity, price, category))
        connection.commit()
        connection.close()
        messagebox.showinfo("Product Added", f"Product {name} has been added to the inventory.")

    # Function to check for low stock items and display notifications
    def check_low_stock():
        connection = sqlite3.connect('inventory.db')
        cursor = connection.cursor()
        cursor.execute('SELECT name, quantity FROM products WHERE quantity < ?', (5,))  # Change the threshold as needed
        low_stock_items = cursor.fetchall()
        connection.close()

        if low_stock_items:
            message = "Low stock items:\n"
            for item in low_stock_items:
                message += f"{item[0]} - {item[1]} units\n"
            messagebox.showwarning("Low Stock Alert", message)
        else:
            messagebox.showinfo("No Low Stock", "No products are currently low in stock.")

    # Function to create a backup of the database
    def create_backup():
        try:
            backup_file = 'inventory_backup.db'
            shutil.copy('inventory.db', backup_file)
            messagebox.showinfo("Backup Created", "Database backup created successfully.")
        except Exception as e:
            messagebox.showerror("Backup Error", f"Error creating backup: {str(e)}")

    # Function to restore data from a backup
    def restore_data():
        try:
            backup_file = 'inventory_backup.db'
            if os.path.isfile(backup_file):
                shutil.copy(backup_file, 'inventory.db')
                messagebox.showinfo("Restore Successful", "Database restored successfully.")
            else:
                messagebox.showerror("Restore Error", "Backup file not found.")
        except Exception as e:
            messagebox.showerror("Restore Error", f"Error restoring backup: {str(e)}")

    # Function to export product data to a CSV file
    def export_to_csv():
        connection = sqlite3.connect('inventory.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM products')
        data = cursor.fetchall()
        connection.close()

        if data:
            with open('inventory.csv', 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(['ID', 'Name', 'Quantity', 'Price', 'Category'])
                csvwriter.writerows(data)
            messagebox.showinfo("Export Successful", "Product data exported to 'inventory.csv'.")
        else:
            messagebox.showwarning("Export Warning", "No product data to export.")

    # Function to display products in a separate window
    def display_products():
        display_window = tk.Toplevel(root)
        display_window.title("Products List")

        connection = sqlite3.connect('inventory.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM products')
        data = cursor.fetchall()
        connection.close()

        if data:
            for row_index, row_data in enumerate(data):
                for col_index, cell_data in enumerate(row_data):
                    tk.Label(display_window, text=str(cell_data)).grid(row=row_index, column=col_index, padx=5, pady=5)
        else:
            tk.Label(display_window, text="No products in the inventory").pack(padx=10, pady=10)

    def search_and_filter():
        search_name = search_name_entry.get()
        search_category = search_category_entry.get()

        # Build the SQL query based on the provided criteria
        query = "SELECT * FROM products WHERE 1=1"

        if search_name:
            query += f" AND name LIKE '%{search_name}%'"
        if search_category:
            query += f" AND category LIKE '%{search_category}%'"

        connection = sqlite3.connect('inventory.db')
        cursor = connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        connection.close()

        display_search_results(data)

    # Function to record sales transactions
    def record_sale():
        sale_product_name = sale_product_name_entry.get()
        sale_quantity = int(sale_quantity_entry.get())

        connection = sqlite3.connect('inventory.db')
        cursor = connection.cursor()
        cursor.execute('SELECT quantity FROM products WHERE name = ?', (sale_product_name,))
        current_quantity = cursor.fetchone()[0]

        if current_quantity >= sale_quantity:
            new_quantity = current_quantity - sale_quantity
            cursor.execute('UPDATE products SET quantity = ? WHERE name = ?', (new_quantity, sale_product_name))

            connection.commit()
            messagebox.showinfo("Sale Recorded", f"{sale_quantity} units of {sale_product_name} sold.")
        else:
            messagebox.showerror("Sale Error", "Not enough quantity available for sale.")
        connection.close()

    # Function to display search results in a separate window
    def display_search_results(data):
        result_window = tk.Toplevel(root)
        result_window.title("Search Results")

        if data:
            for row_index, row_data in enumerate(data):
                for col_index, cell_data in enumerate(row_data):
                    tk.Label(result_window, text=str(cell_data)).grid(row=row_index, column=col_index, padx=5, pady=5)
        else:
            tk.Label(result_window, text="No matching products found").pack(padx=10, pady=10)

    style = ttk.Style()
    style.configure('Custom.TLabel', foreground='#2C3E50', font=('Arial', 10, 'bold'))
    style.configure('Custom.TEntry', fieldbackground='#D5DBDB', foreground='#34495E', font=('Arial', 10))
    style.configure('Custom.TButton', foreground='#2C3E50', background='#3498DB', font=('Arial', 10, 'bold'))

    # Sales Recording Section
    sales_section = tk.Frame(root)
    sales_section.pack(padx=20, pady=20)

    sale_product_name_label = ttk.Label(sales_section, text="Product Name:", style='Custom.TLabel')
    sale_product_name_entry = ttk.Entry(sales_section, style='Custom.TEntry')
    sale_quantity_label = ttk.Label(sales_section, text="Quantity Sold:", style='Custom.TLabel')
    sale_quantity_entry = ttk.Entry(sales_section, style='Custom.TEntry')
    record_sale_button = ttk.Button(sales_section, text="Record Sale", command=record_sale, style='Custom.TButton')

    sale_product_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    sale_product_name_entry.grid(row=0, column=1, padx=5, pady=5)
    sale_quantity_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    sale_quantity_entry.grid(row=1, column=1, padx=5, pady=5)
    record_sale_button.grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

    # Search and Filter Section
    search_section = tk.Frame(root)
    search_section.pack(padx=20, pady=20)

    search_label = ttk.Label(search_section, text="Search by Name:", style='Custom.TLabel')
    search_name_entry = ttk.Entry(search_section, style='Custom.TEntry')
    search_category_label = ttk.Label(search_section, text="Search by Category:", style='Custom.TLabel')
    search_category_entry = ttk.Entry(search_section, style='Custom.TEntry')
    search_button = ttk.Button(search_section, text="Search and Filter", command=search_and_filter,
                               style='Custom.TButton')

    search_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    search_name_entry.grid(row=0, column=1, padx=10, pady=5)
    search_category_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
    search_category_entry.grid(row=1, column=1, padx=10, pady=5)
    search_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    # Product Details Section
    product_section = tk.Frame(root)
    product_section.pack(padx=20, pady=20)

    product_name_label = ttk.Label(product_section, text="Product Name:", style='Custom.TLabel')
    product_name_entry = ttk.Entry(product_section, style='Custom.TEntry')
    product_quantity_label = ttk.Label(product_section, text="Quantity:", style='Custom.TLabel')
    product_quantity_entry = ttk.Entry(product_section, style='Custom.TEntry')
    product_price_label = ttk.Label(product_section, text="Price:", style='Custom.TLabel')
    product_price_entry = ttk.Entry(product_section, style='Custom.TEntry')
    product_category_label = ttk.Label(product_section, text="Category:", style='Custom.TLabel')
    product_category_entry = ttk.Entry(product_section, style='Custom.TEntry')
    add_product_button = ttk.Button(product_section, text="Add Product", command=add_product, style='Custom.TButton')

    product_name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    product_name_entry.grid(row=0, column=1, padx=10, pady=5)
    product_quantity_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
    product_quantity_entry.grid(row=1, column=1, padx=10, pady=5)
    product_price_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
    product_price_entry.grid(row=2, column=1, padx=10, pady=5)
    product_category_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
    product_category_entry.grid(row=3, column=1, padx=10, pady=5)
    add_product_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    # Management Section
    management_section = tk.Frame(root)
    management_section.pack(padx=20, pady=20)

    create_table_button = ttk.Button(management_section, text="Create Products Table", command=create_product_table,
                                     style='Custom.TButton')
    display_products_button = ttk.Button(management_section, text="Display Products", command=display_products,
                                         style='Custom.TButton')
    check_low_stock_button = ttk.Button(management_section, text="Check Low Stock", command=check_low_stock,
                                        style='Custom.TButton')
    backup_button = ttk.Button(management_section, text="Create Backup", command=create_backup, style='Custom.TButton')
    restore_button = ttk.Button(management_section, text="Restore Data", command=restore_data, style='Custom.TButton')
    export_csv_button = ttk.Button(management_section, text="Export to CSV", command=export_to_csv,
                                   style='Custom.TButton')

    create_table_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")
    display_products_button.grid(row=0, column=1, padx=10, pady=10, sticky="w")
    check_low_stock_button.grid(row=1, column=0, padx=10, pady=10, sticky="w")
    backup_button.grid(row=1, column=1, padx=10, pady=10, sticky="w")
    restore_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")
    export_csv_button.grid(row=2, column=1, padx=10, pady=10, sticky="w")

    root.mainloop()

# Create the login window
login_window = tk.Tk()
login_window.title("Login")

login_window.geometry('400x300')  # Set window dimensions

# Configure the background color for the login window
login_window.configure(bg='#E0E0E0')  # Light gray background

# Define and configure styles
style = ttk.Style()
style.configure('TLabel', background='#E0E0E0', foreground='#333333', font=('Arial', 12))
style.configure('TEntry', fieldbackground='#FFFFFF', font=('Arial', 12))
style.configure('Custom.TButton', foreground='#2C3E50', background='#3498DB', font=('Arial', 10, 'bold'))
style.configure('CustomHover.TButton', foreground='#2C3E50', background='#3498DB', font=('Arial', 10, 'bold'))

# Create a frame for better organization with a configured style
login_frame = ttk.Frame(login_window, style='TFrame')
login_frame.pack(padx=20, pady=40, fill='both', expand=True)  # Expand frame to window size

# Define and place widgets within the login frame
username_label = ttk.Label(login_frame, text="Username:")
username_entry = ttk.Entry(login_frame, style='TEntry')

password_label = ttk.Label(login_frame, text="Password:")
password_entry = ttk.Entry(login_frame, show="*", style='TEntry')

login_button = ttk.Button(login_frame, text="Login", command=login, style='Custom.TButton')
login_button.bind('<Enter>', on_enter)
login_button.bind('<Leave>', on_leave)

# Grid layout for login widgets within the login frame
username_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
username_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
password_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
password_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
login_button.grid(row=2, columnspan=2, pady=15)


login_window.mainloop()
