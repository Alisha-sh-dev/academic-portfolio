import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
import os
import csv

class LibraryManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Online Library Management System")
        self.root.geometry("1000x600")
        self.root.resizable(True, True)
        
        # Initialize database
        self.init_db()
        
        # Current user
        self.current_user = None
        
        # Create main frames
        self.create_login_frame()
        self.create_main_frame()
        
        # Show login frame initially
        self.show_frame("login")
    
    def init_db(self):
        """Initialize the database with required tables"""
        self.conn = sqlite3.connect('library.db')
        self.cursor = self.conn.cursor()
        
        # Create users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            )
        ''')
        
        # Create books table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                available INTEGER NOT NULL DEFAULT 1
            )
        ''')
        
        # Create transactions table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                issue_date TEXT NOT NULL,
                return_date TEXT,
                status TEXT NOT NULL DEFAULT 'borrowed',
                FOREIGN KEY (book_id) REFERENCES books (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create reservations table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                reservation_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'reserved',
                FOREIGN KEY (book_id) REFERENCES books (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Insert default admin user if not exists
        self.cursor.execute("SELECT * FROM users WHERE username='admin'")
        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ('admin', 'admin123', 'admin')
            )
        
        self.conn.commit()
    
    def create_login_frame(self):
        """Create the login frame"""
        self.login_frame = ttk.Frame(self.root, padding="20")
        
        ttk.Label(self.login_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(self.login_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(self.login_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(self.login_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, pady=5, padx=10)
        
        self.login_button = ttk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Bind Enter key to login
        self.username_entry.bind('<Return>', lambda event: self.login())
        self.password_entry.bind('<Return>', lambda event: self.login())
    
    def create_main_frame(self):
        """Create the main application frame with tabs"""
        self.main_frame = ttk.Frame(self.root)
        
        # Create notebook (tab control)
        self.notebook = ttk.Notebook(self.main_frame)
        
        # Create frames for each tab
        self.book_frame = ttk.Frame(self.notebook, padding="10")
        self.borrow_frame = ttk.Frame(self.notebook, padding="10")
        self.search_frame = ttk.Frame(self.notebook, padding="10")
        self.transaction_frame = ttk.Frame(self.notebook, padding="10")
        self.notification_frame = ttk.Frame(self.notebook, padding="10")
        self.backup_frame = ttk.Frame(self.notebook, padding="10")
        
        # Add tabs to notebook
        self.notebook.add(self.book_frame, text="Book Management")
        self.notebook.add(self.borrow_frame, text="Borrow/Return")
        self.notebook.add(self.search_frame, text="Search Books")
        self.notebook.add(self.transaction_frame, text="Transactions")
        self.notebook.add(self.notification_frame, text="Notifications")
        self.notebook.add(self.backup_frame, text="Backup/Restore")
        
        self.notebook.pack(expand=1, fill="both")
        
        # Create widgets for each tab
        self.create_book_management_tab()
        self.create_borrow_return_tab()
        self.create_search_tab()
        self.create_transaction_tab()
        self.create_notification_tab()
        self.create_backup_tab()
        
        # Add logout button
        self.logout_button = ttk.Button(self.main_frame, text="Logout", command=self.logout)
        self.logout_button.pack(pady=10)
    
    def create_book_management_tab(self):
        """Create book management tab widgets"""
        # Add book section
        ttk.Label(self.book_frame, text="Add New Book", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        ttk.Label(self.book_frame, text="Title:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(self.book_frame, width=30)
        self.title_entry.grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(self.book_frame, text="Author:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.author_entry = ttk.Entry(self.book_frame, width=30)
        self.author_entry.grid(row=2, column=1, pady=5, padx=10)
        
        ttk.Label(self.book_frame, text="ISBN:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.isbn_entry = ttk.Entry(self.book_frame, width=30)
        self.isbn_entry.grid(row=3, column=1, pady=5, padx=10)
        
        ttk.Label(self.book_frame, text="Category:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.category_entry = ttk.Entry(self.book_frame, width=30)
        self.category_entry.grid(row=4, column=1, pady=5, padx=10)
        
        ttk.Label(self.book_frame, text="Quantity:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.quantity_entry = ttk.Entry(self.book_frame, width=30)
        self.quantity_entry.grid(row=5, column=1, pady=5, padx=10)
        
        self.add_book_button = ttk.Button(self.book_frame, text="Add Book", command=self.add_book)
        self.add_book_button.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Book list section
        ttk.Label(self.book_frame, text="Book List", font=('Arial', 12, 'bold')).grid(row=7, column=0, columnspan=4, pady=10, sticky=tk.W)
        
        # Treeview for books
        columns = ("ID", "Title", "Author", "ISBN", "Category", "Quantity", "Available")
        self.book_tree = ttk.Treeview(self.book_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.book_tree.heading(col, text=col)
            self.book_tree.column(col, width=100)
        
        self.book_tree.grid(row=8, column=0, columnspan=4, pady=10, sticky="nsew")
        
        # Scrollbar for book tree
        scrollbar = ttk.Scrollbar(self.book_frame, orient=tk.VERTICAL, command=self.book_tree.yview)
        self.book_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=8, column=4, sticky="ns")
        
        # Buttons for book management
        self.edit_book_button = ttk.Button(self.book_frame, text="Edit Book", command=self.edit_book)
        self.edit_book_button.grid(row=9, column=0, pady=10, padx=5)
        
        self.delete_book_button = ttk.Button(self.book_frame, text="Delete Book", command=self.delete_book)
        self.delete_book_button.grid(row=9, column=1, pady=10, padx=5)
        
        self.refresh_book_button = ttk.Button(self.book_frame, text="Refresh", command=self.load_books)
        self.refresh_book_button.grid(row=9, column=2, pady=10, padx=5)
        
        # Configure grid weights
        self.book_frame.grid_rowconfigure(8, weight=1)
        self.book_frame.grid_columnconfigure(0, weight=1)
        
        # Load books
        self.load_books()
    
    def create_borrow_return_tab(self):
        """Create borrow/return tab widgets"""
        # Borrow section
        ttk.Label(self.borrow_frame, text="Borrow Book", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        ttk.Label(self.borrow_frame, text="Book ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.borrow_book_id_entry = ttk.Entry(self.borrow_frame, width=30)
        self.borrow_book_id_entry.grid(row=1, column=1, pady=5, padx=10)
        
        self.borrow_button = ttk.Button(self.borrow_frame, text="Borrow Book", command=self.borrow_book)
        self.borrow_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Return section
        ttk.Label(self.borrow_frame, text="Return Book", font=('Arial', 12, 'bold')).grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        ttk.Label(self.borrow_frame, text="Book ID:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.return_book_id_entry = ttk.Entry(self.borrow_frame, width=30)
        self.return_book_id_entry.grid(row=4, column=1, pady=5, padx=10)
        
        self.return_button = ttk.Button(self.borrow_frame, text="Return Book", command=self.return_book)
        self.return_button.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Current borrowings section
        ttk.Label(self.borrow_frame, text="Your Current Borrowings", font=('Arial', 12, 'bold')).grid(row=6, column=0, columnspan=4, pady=10, sticky=tk.W)
        
        # Treeview for current borrowings
        columns = ("ID", "Book ID", "Book Title", "Issue Date", "Due Date", "Status")
        self.borrow_tree = ttk.Treeview(self.borrow_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.borrow_tree.heading(col, text=col)
            self.borrow_tree.column(col, width=100)
        
        self.borrow_tree.grid(row=7, column=0, columnspan=4, pady=10, sticky="nsew")
        
        # Scrollbar for borrow tree
        scrollbar = ttk.Scrollbar(self.borrow_frame, orient=tk.VERTICAL, command=self.borrow_tree.yview)
        self.borrow_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=7, column=4, sticky="ns")
        
        # Configure grid weights
        self.borrow_frame.grid_rowconfigure(7, weight=1)
        self.borrow_frame.grid_columnconfigure(0, weight=1)
        
        # Load current borrowings
        self.load_current_borrowings()
    
    def create_search_tab(self):
        """Create search tab widgets"""
        # Search criteria
        ttk.Label(self.search_frame, text="Search Books", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=3, pady=10, sticky=tk.W)
        
        ttk.Label(self.search_frame, text="Search by:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.search_by = tk.StringVar(value="Title")
        search_options = ["Title", "Author", "Category", "Availability"]
        self.search_by_dropdown = ttk.Combobox(self.search_frame, textvariable=self.search_by, values=search_options, state="readonly")
        self.search_by_dropdown.grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(self.search_frame, text="Search term:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.search_term_entry = ttk.Entry(self.search_frame, width=30)
        self.search_term_entry.grid(row=2, column=1, pady=5, padx=10)
        
        self.search_button = ttk.Button(self.search_frame, text="Search", command=self.search_books)
        self.search_button.grid(row=2, column=2, pady=5, padx=10)
        
        # Search results
        ttk.Label(self.search_frame, text="Search Results", font=('Arial', 12, 'bold')).grid(row=3, column=0, columnspan=4, pady=10, sticky=tk.W)
        
        # Treeview for search results
        columns = ("ID", "Title", "Author", "ISBN", "Category", "Quantity", "Available")
        self.search_tree = ttk.Treeview(self.search_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.search_tree.heading(col, text=col)
            self.search_tree.column(col, width=100)
        
        self.search_tree.grid(row=4, column=0, columnspan=4, pady=10, sticky="nsew")
        
        # Scrollbar for search tree
        scrollbar = ttk.Scrollbar(self.search_frame, orient=tk.VERTICAL, command=self.search_tree.yview)
        self.search_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=4, column=4, sticky="ns")
        
        # Configure grid weights
        self.search_frame.grid_rowconfigure(4, weight=1)
        self.search_frame.grid_columnconfigure(0, weight=1)
    
    def create_transaction_tab(self):
        """Create transaction history tab widgets"""
        # Transaction history section
        ttk.Label(self.transaction_frame, text="Transaction History", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=4, pady=10, sticky=tk.W)
        
        # Treeview for transactions
        columns = ("ID", "Book ID", "User ID", "Issue Date", "Return Date", "Status")
        self.transaction_tree = ttk.Treeview(self.transaction_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.transaction_tree.heading(col, text=col)
            self.transaction_tree.column(col, width=100)
        
        self.transaction_tree.grid(row=1, column=0, columnspan=4, pady=10, sticky="nsew")
        
        # Scrollbar for transaction tree
        scrollbar = ttk.Scrollbar(self.transaction_frame, orient=tk.VERTICAL, command=self.transaction_tree.yview)
        self.transaction_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=4, sticky="ns")
        
        # Buttons for transaction management
        self.load_transactions_button = ttk.Button(self.transaction_frame, text="Load All Transactions", command=self.load_all_transactions)
        self.load_transactions_button.grid(row=2, column=0, pady=10, padx=5)
        
        self.load_user_transactions_button = ttk.Button(self.transaction_frame, text="Load My Transactions", command=self.load_user_transactions)
        self.load_user_transactions_button.grid(row=2, column=1, pady=10, padx=5)
        
        self.most_borrowed_button = ttk.Button(self.transaction_frame, text="Most Borrowed Books", command=self.show_most_borrowed)
        self.most_borrowed_button.grid(row=2, column=2, pady=10, padx=5)
        
        self.overdue_button = ttk.Button(self.transaction_frame, text="Overdue Items", command=self.show_overdue)
        self.overdue_button.grid(row=2, column=3, pady=10, padx=5)
        
        # Configure grid weights
        self.transaction_frame.grid_rowconfigure(1, weight=1)
        self.transaction_frame.grid_columnconfigure(0, weight=1)
        
        # Load transactions
        self.load_all_transactions()
    
    def create_notification_tab(self):
        """Create notifications tab widgets"""
        # Notifications section
        ttk.Label(self.notification_frame, text="Notifications", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        # Text widget for notifications
        self.notification_text = tk.Text(self.notification_frame, height=20, width=80)
        self.notification_text.grid(row=1, column=0, columnspan=2, pady=10, sticky="nsew")
        
        # Scrollbar for notification text
        scrollbar = ttk.Scrollbar(self.notification_frame, orient=tk.VERTICAL, command=self.notification_text.yview)
        self.notification_text.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky="ns")
        
        # Buttons for notifications
        self.check_notifications_button = ttk.Button(self.notification_frame, text="Check Notifications", command=self.check_notifications)
        self.check_notifications_button.grid(row=2, column=0, pady=10, padx=5)
        
        self.clear_notifications_button = ttk.Button(self.notification_frame, text="Clear Notifications", command=self.clear_notifications)
        self.clear_notifications_button.grid(row=2, column=1, pady=10, padx=5)
        
        # Configure grid weights
        self.notification_frame.grid_rowconfigure(1, weight=1)
        self.notification_frame.grid_columnconfigure(0, weight=1)
        
        # Check notifications
        self.check_notifications()
    
    def create_backup_tab(self):
        """Create backup/restore tab widgets"""
        # Backup section
        ttk.Label(self.backup_frame, text="Backup and Restore", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        self.backup_button = ttk.Button(self.backup_frame, text="Backup Database", command=self.backup_database, width=20)
        self.backup_button.grid(row=1, column=0, pady=20, padx=10)
        
        self.restore_button = ttk.Button(self.backup_frame, text="Restore Database", command=self.restore_database, width=20)
        self.restore_button.grid(row=1, column=1, pady=20, padx=10)
        
        self.export_csv_button = ttk.Button(self.backup_frame, text="Export to CSV", command=self.export_to_csv, width=20)
        self.export_csv_button.grid(row=2, column=0, pady=20, padx=10)
        
        self.import_csv_button = ttk.Button(self.backup_frame, text="Import from CSV", command=self.import_from_csv, width=20)
        self.import_csv_button.grid(row=2, column=1, pady=20, padx=10)
    
    def show_frame(self, frame_name):
        """Show the specified frame and hide others"""
        if frame_name == "login":
            self.login_frame.pack(fill="both", expand=True)
            self.main_frame.pack_forget()
        elif frame_name == "main":
            self.login_frame.pack_forget()
            self.main_frame.pack(fill="both", expand=True)
    
    def login(self):
        """Handle user login"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        self.cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = self.cursor.fetchone()
        
        if user:
            self.current_user = {
                "id": user[0],
                "username": user[1],
                "role": user[3]
            }
            self.show_frame("main")
            messagebox.showinfo("Success", f"Welcome {username}!")
            
            # Update UI based on user role
            if self.current_user["role"] == "user":
                # Hide book management tab for regular users
                self.notebook.hide(0)
            else:
                self.notebook.add(self.book_frame, text="Book Management")
                
            # Refresh data
            self.load_books()
            self.load_current_borrowings()
            self.check_notifications()
        else:
            messagebox.showerror("Error", "Invalid username or password")
    
    def logout(self):
        """Handle user logout"""
        self.current_user = None
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.show_frame("login")
    
    def add_book(self):
        """Add a new book to the library"""
        if not self.current_user or self.current_user["role"] != "admin":
            messagebox.showerror("Error", "Only admins can add books")
            return
        
        title = self.title_entry.get()
        author = self.author_entry.get()
        isbn = self.isbn_entry.get()
        category = self.category_entry.get()
        quantity = self.quantity_entry.get()
        
        if not all([title, author, isbn, category, quantity]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        try:
            quantity = int(quantity)
            if quantity < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive integer")
            return
        
        try:
            self.cursor.execute(
                "INSERT INTO books (title, author, isbn, category, quantity, available) VALUES (?, ?, ?, ?, ?, ?)",
                (title, author, isbn, category, quantity, quantity)
            )
            self.conn.commit()
            messagebox.showinfo("Success", "Book added successfully")
            self.clear_book_entries()
            self.load_books()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "A book with this ISBN already exists")
    
    def edit_book(self):
        """Edit selected book"""
        if not self.current_user or self.current_user["role"] != "admin":
            messagebox.showerror("Error", "Only admins can edit books")
            return
        
        selected_item = self.book_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a book to edit")
            return
        
        item = self.book_tree.item(selected_item[0])
        book_id = item['values'][0]
        
        # Open edit dialog
        self.edit_book_dialog(book_id)
    
    def edit_book_dialog(self, book_id):
        """Open dialog to edit book details"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Book")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Get book details
        self.cursor.execute("SELECT * FROM books WHERE id=?", (book_id,))
        book = self.cursor.fetchone()
        
        ttk.Label(dialog, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
        title_entry = ttk.Entry(dialog, width=30)
        title_entry.insert(0, book[1])
        title_entry.grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(dialog, text="Author:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        author_entry = ttk.Entry(dialog, width=30)
        author_entry.insert(0, book[2])
        author_entry.grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(dialog, text="ISBN:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=10)
        isbn_entry = ttk.Entry(dialog, width=30)
        isbn_entry.insert(0, book[3])
        isbn_entry.grid(row=2, column=1, pady=5, padx=10)
        
        ttk.Label(dialog, text="Category:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=10)
        category_entry = ttk.Entry(dialog, width=30)
        category_entry.insert(0, book[4])
        category_entry.grid(row=3, column=1, pady=5, padx=10)
        
        ttk.Label(dialog, text="Quantity:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=10)
        quantity_entry = ttk.Entry(dialog, width=30)
        quantity_entry.insert(0, book[5])
        quantity_entry.grid(row=4, column=1, pady=5, padx=10)
        
        def save_changes():
            title = title_entry.get()
            author = author_entry.get()
            isbn = isbn_entry.get()
            category = category_entry.get()
            quantity = quantity_entry.get()
            
            if not all([title, author, isbn, category, quantity]):
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            try:
                quantity = int(quantity)
                if quantity < 1:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Quantity must be a positive integer")
                return
            
            # Calculate new available count
            current_available = book[6]
            current_quantity = book[5]
            available = current_available + (quantity - current_quantity)
            
            if available < 0:
                messagebox.showerror("Error", "Cannot reduce quantity below borrowed copies")
                return
            
            try:
                self.cursor.execute(
                    "UPDATE books SET title=?, author=?, isbn=?, category=?, quantity=?, available=? WHERE id=?",
                    (title, author, isbn, category, quantity, available, book_id)
                )
                self.conn.commit()
                messagebox.showinfo("Success", "Book updated successfully")
                dialog.destroy()
                self.load_books()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "A book with this ISBN already exists")
        
        ttk.Button(dialog, text="Save", command=save_changes).grid(row=5, column=0, pady=20, padx=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=5, column=1, pady=20, padx=10)
    
    def delete_book(self):
        """Delete selected book"""
        if not self.current_user or self.current_user["role"] != "admin":
            messagebox.showerror("Error", "Only admins can delete books")
            return
        
        selected_item = self.book_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a book to delete")
            return
        
        item = self.book_tree.item(selected_item[0])
        book_id = item['values'][0]
        title = item['values'][1]
        
        # Check if book is currently borrowed
        self.cursor.execute("SELECT COUNT(*) FROM transactions WHERE book_id=? AND status='borrowed'", (book_id,))
        borrowed_count = self.cursor.fetchone()[0]
        
        if borrowed_count > 0:
            messagebox.showerror("Error", "Cannot delete book that is currently borrowed")
            return
        
        # Confirm deletion
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{title}'?"):
            self.cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
            self.conn.commit()
            messagebox.showinfo("Success", "Book deleted successfully")
            self.load_books()
    
    def clear_book_entries(self):
        """Clear book entry fields"""
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.isbn_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
    
    def load_books(self):
        """Load books into the book tree"""
        # Clear existing items
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)
        
        self.cursor.execute("SELECT * FROM books")
        books = self.cursor.fetchall()
        
        for book in books:
            self.book_tree.insert("", "end", values=book)
    
    def borrow_book(self):
        """Borrow a book"""
        if not self.current_user:
            messagebox.showerror("Error", "Please login first")
            return
        
        book_id = self.borrow_book_id_entry.get()
        
        if not book_id:
            messagebox.showerror("Error", "Please enter a book ID")
            return
        
        try:
            book_id = int(book_id)
        except ValueError:
            messagebox.showerror("Error", "Book ID must be a number")
            return
        
        # Check if book exists and is available
        self.cursor.execute("SELECT * FROM books WHERE id=?", (book_id,))
        book = self.cursor.fetchone()
        
        if not book:
            messagebox.showerror("Error", "Book not found")
            return
        
        if book[6] < 1:
            messagebox.showerror("Error", "Book is not available for borrowing")
            return
        
        # Check if user has already borrowed this book
        self.cursor.execute(
            "SELECT * FROM transactions WHERE book_id=? AND user_id=? AND status='borrowed'",
            (book_id, self.current_user["id"])
        )
        existing_borrowing = self.cursor.fetchone()
        
        if existing_borrowing:
            messagebox.showerror("Error", "You have already borrowed this book")
            return
        
        # Borrow the book
        issue_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.cursor.execute(
            "INSERT INTO transactions (book_id, user_id, issue_date, status) VALUES (?, ?, ?, ?)",
            (book_id, self.current_user["id"], issue_date, "borrowed")
        )
        
        # Update available count
        self.cursor.execute(
            "UPDATE books SET available = available - 1 WHERE id=?",
            (book_id,)
        )
        
        self.conn.commit()
        messagebox.showinfo("Success", f"Book '{book[1]}' borrowed successfully")
        self.borrow_book_id_entry.delete(0, tk.END)
        self.load_current_borrowings()
    
    def return_book(self):
        """Return a borrowed book"""
        if not self.current_user:
            messagebox.showerror("Error", "Please login first")
            return
        
        book_id = self.return_book_id_entry.get()
        
        if not book_id:
            messagebox.showerror("Error", "Please enter a book ID")
            return
        
        try:
            book_id = int(book_id)
        except ValueError:
            messagebox.showerror("Error", "Book ID must be a number")
            return
        
        # Check if user has borrowed this book
        self.cursor.execute(
            "SELECT * FROM transactions WHERE book_id=? AND user_id=? AND status='borrowed'",
            (book_id, self.current_user["id"])
        )
        borrowing = self.cursor.fetchone()
        
        if not borrowing:
            messagebox.showerror("Error", "You have not borrowed this book")
            return
        
        # Return the book
        return_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.cursor.execute(
            "UPDATE transactions SET return_date=?, status='returned' WHERE id=?",
            (return_date, borrowing[0])
        )
        
        # Update available count
        self.cursor.execute(
            "UPDATE books SET available = available + 1 WHERE id=?",
            (book_id,)
        )
        
        self.conn.commit()
        messagebox.showinfo("Success", "Book returned successfully")
        self.return_book_id_entry.delete(0, tk.END)
        self.load_current_borrowings()
    
    def load_current_borrowings(self):
        """Load current borrowings for the user"""
        # Clear existing items
        for item in self.borrow_tree.get_children():
            self.borrow_tree.delete(item)
        
        if not self.current_user:
            return
        
        self.cursor.execute('''
            SELECT t.id, t.book_id, b.title, t.issue_date, 
                   date(t.issue_date, '+14 days') as due_date, t.status
            FROM transactions t
            JOIN books b ON t.book_id = b.id
            WHERE t.user_id=? AND t.status='borrowed'
        ''', (self.current_user["id"],))
        
        borrowings = self.cursor.fetchall()
        
        for borrowing in borrowings:
            self.borrow_tree.insert("", "end", values=borrowing)
    
    def search_books(self):
        """Search for books based on criteria"""
        search_by = self.search_by.get()
        search_term = self.search_term_entry.get()
        
        # Clear existing items
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        if search_by == "Title":
            self.cursor.execute("SELECT * FROM books WHERE title LIKE ?", (f"%{search_term}%",))
        elif search_by == "Author":
            self.cursor.execute("SELECT * FROM books WHERE author LIKE ?", (f"%{search_term}%",))
        elif search_by == "Category":
            self.cursor.execute("SELECT * FROM books WHERE category LIKE ?", (f"%{search_term}%",))
        elif search_by == "Availability":
            if search_term.lower() in ["available", "yes", "true", "1"]:
                self.cursor.execute("SELECT * FROM books WHERE available > 0")
            else:
                self.cursor.execute("SELECT * FROM books WHERE available = 0")
        else:
            self.cursor.execute("SELECT * FROM books")
        
        books = self.cursor.fetchall()
        
        for book in books:
            self.search_tree.insert("", "end", values=book)
    
    def load_all_transactions(self):
        """Load all transactions (admin only)"""
        # Clear existing items
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)
        
        if not self.current_user:
            return
        
        if self.current_user["role"] == "admin":
            self.cursor.execute('''
                SELECT t.id, t.book_id, t.user_id, t.issue_date, t.return_date, t.status
                FROM transactions t
                ORDER BY t.issue_date DESC
            ''')
        else:
            self.cursor.execute('''
                SELECT t.id, t.book_id, t.user_id, t.issue_date, t.return_date, t.status
                FROM transactions t
                WHERE t.user_id=?
                ORDER BY t.issue_date DESC
            ''', (self.current_user["id"],))
        
        transactions = self.cursor.fetchall()
        
        for transaction in transactions:
            self.transaction_tree.insert("", "end", values=transaction)
    
    def load_user_transactions(self):
        """Load transactions for the current user"""
        # Clear existing items
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)
        
        if not self.current_user:
            return
        
        self.cursor.execute('''
            SELECT t.id, t.book_id, t.user_id, t.issue_date, t.return_date, t.status
            FROM transactions t
            WHERE t.user_id=?
            ORDER BY t.issue_date DESC
        ''', (self.current_user["id"],))
        
        transactions = self.cursor.fetchall()
        
        for transaction in transactions:
            self.transaction_tree.insert("", "end", values=transaction)
    
    def show_most_borrowed(self):
        """Show most borrowed books"""
        # Clear existing items
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)
        
        self.cursor.execute('''
            SELECT b.id, b.title, b.author, COUNT(t.id) as borrow_count
            FROM books b
            JOIN transactions t ON b.id = t.book_id
            GROUP BY b.id
            ORDER BY borrow_count DESC
            LIMIT 10
        ''')
        
        popular_books = self.cursor.fetchall()
        
        # Change column headings for this view
        self.transaction_tree["columns"] = ("ID", "Title", "Author", "Borrow Count")
        for col in self.transaction_tree["columns"]:
            self.transaction_tree.heading(col, text=col)
            self.transaction_tree.column(col, width=100)
        
        for book in popular_books:
            self.transaction_tree.insert("", "end", values=book)
    
    def show_overdue(self):
        """Show overdue items"""
        # Clear existing items
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)
        
        # Calculate due date (14 days from issue date)
        due_date_threshold = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")
        
        self.cursor.execute('''
            SELECT t.id, t.book_id, t.user_id, t.issue_date, t.return_date, t.status
            FROM transactions t
            WHERE t.status='borrowed' AND t.issue_date < ?
        ''', (due_date_threshold,))
        
        overdue_items = self.cursor.fetchall()
        
        # Restore original column headings
        self.transaction_tree["columns"] = ("ID", "Book ID", "User ID", "Issue Date", "Return Date", "Status")
        for col in self.transaction_tree["columns"]:
            self.transaction_tree.heading(col, text=col)
            self.transaction_tree.column(col, width=100)
        
        for item in overdue_items:
            self.transaction_tree.insert("", "end", values=item)
    
    def check_notifications(self):
        """Check for notifications (overdue books, reservations)"""
        self.notification_text.delete(1.0, tk.END)
        
        if not self.current_user:
            return
        
        # Check for overdue books
        due_date_threshold = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")
        
        self.cursor.execute('''
            SELECT b.title, t.issue_date
            FROM transactions t
            JOIN books b ON t.book_id = b.id
            WHERE t.user_id=? AND t.status='borrowed' AND t.issue_date < ?
        ''', (self.current_user["id"], due_date_threshold))
        
        overdue_books = self.cursor.fetchall()
        
        if overdue_books:
            self.notification_text.insert(tk.END, "OVERDUE BOOKS:\n")
            for book in overdue_books:
                self.notification_text.insert(tk.END, f"- {book[0]} (issued on {book[1]})\n")
            self.notification_text.insert(tk.END, "\n")
        
        # Check for reservations
        if self.current_user["role"] == "admin":
            self.cursor.execute('''
                SELECT r.id, b.title, u.username, r.reservation_date
                FROM reservations r
                JOIN books b ON r.book_id = b.id
                JOIN users u ON r.user_id = u.id
                WHERE r.status='reserved'
            ''')
            
            reservations = self.cursor.fetchall()
            
            if reservations:
                self.notification_text.insert(tk.END, "BOOK RESERVATIONS:\n")
                for res in reservations:
                    self.notification_text.insert(tk.END, f"- {res[1]} reserved by {res[2]} on {res[3]}\n")
        
        if not overdue_books and (not reservations or self.current_user["role"] != "admin"):
            self.notification_text.insert(tk.END, "No notifications at this time.")
    
    def clear_notifications(self):
        """Clear notifications"""
        self.notification_text.delete(1.0, tk.END)
        self.notification_text.insert(tk.END, "Notifications cleared.")
    
    def backup_database(self):
        """Backup the database to a file"""
        if not self.current_user or self.current_user["role"] != "admin":
            messagebox.showerror("Error", "Only admins can backup the database")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                # Close current connection
                self.conn.close()
                
                # Copy database file
                import shutil
                shutil.copy2('library.db', file_path)
                
                # Reopen connection
                self.conn = sqlite3.connect('library.db')
                self.cursor = self.conn.cursor()
                
                messagebox.showinfo("Success", f"Database backed up to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to backup database: {str(e)}")
                # Reopen connection if backup failed
                self.conn = sqlite3.connect('library.db')
                self.cursor = self.conn.cursor()
    
    def restore_database(self):
        """Restore the database from a backup"""
        if not self.current_user or self.current_user["role"] != "admin":
            messagebox.showerror("Error", "Only admins can restore the database")
            return
        
        file_path = filedialog.askopenfilename(
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                # Close current connection
                self.conn.close()
                
                # Copy backup file
                import shutil
                shutil.copy2(file_path, 'library.db')
                
                # Reopen connection
                self.conn = sqlite3.connect('library.db')
                self.cursor = self.conn.cursor()
                
                messagebox.showinfo("Success", "Database restored successfully")
                
                # Refresh data
                self.load_books()
                self.load_current_borrowings()
                self.check_notifications()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to restore database: {str(e)}")
                # Reopen connection if restore failed
                self.conn = sqlite3.connect('library.db')
                self.cursor = self.conn.cursor()
    
    def export_to_csv(self):
        """Export books to CSV"""
        if not self.current_user or self.current_user["role"] != "admin":
            messagebox.showerror("Error", "Only admins can export data")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                self.cursor.execute("SELECT * FROM books")
                books = self.cursor.fetchall()
                
                with open(file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    # Write header
                    writer.writerow(['ID', 'Title', 'Author', 'ISBN', 'Category', 'Quantity', 'Available'])
                    # Write data
                    writer.writerows(books)
                
                messagebox.showinfo("Success", f"Data exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def import_from_csv(self):
        """Import books from CSV"""
        if not self.current_user or self.current_user["role"] != "admin":
            messagebox.showerror("Error", "Only admins can import data")
            return
        
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)  # Skip header
                    
                    for row in reader:
                        # Check if book already exists
                        self.cursor.execute("SELECT * FROM books WHERE isbn=?", (row[3],))
                        existing = self.cursor.fetchone()
                        
                        if existing:
                            # Update existing book
                            self.cursor.execute(
                                "UPDATE books SET title=?, author=?, category=?, quantity=?, available=? WHERE isbn=?",
                                (row[1], row[2], row[4], row[5], row[6], row[3])
                            )
                        else:
                            # Insert new book
                            self.cursor.execute(
                                "INSERT INTO books (title, author, isbn, category, quantity, available) VALUES (?, ?, ?, ?, ?, ?)",
                                (row[1], row[2], row[3], row[4], row[5], row[6])
                            )
                    
                    self.conn.commit()
                
                messagebox.showinfo("Success", "Data imported successfully")
                self.load_books()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import data: {str(e)}")

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = LibraryManagementSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()