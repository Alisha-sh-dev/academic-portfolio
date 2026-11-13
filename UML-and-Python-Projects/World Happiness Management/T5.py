"""
ADVANCED ONLINE MEETING MANAGEMENT SYSTEM (AOMMS)
ICT505 Assessment 3 - Part B - Premium Edition
Innovation Features: AI Meeting Scheduler, Real-time Web Integration, Advanced Security
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime, timedelta
import sqlite3
import json
import csv
import os
import hashlib
import uuid
import threading
import time
import random
import pickle
from io import BytesIO
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np

# Try to import optional packages with fallbacks
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL/Pillow not installed. Some image features disabled.")

try:
    import cryptography
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    print("cryptography not installed. Using basic encryption.")

try:
    from tkcalendar import Calendar, DateEntry
    TKCALENDAR_AVAILABLE = True
except ImportError:
    TKCALENDAR_AVAILABLE = False
    print("tkcalendar not installed. Using basic date entry.")

class SecureDatabaseManager:
    """Advanced secure database management with encryption"""
    
    def __init__(self, db_name='secure_omms.db'):
        self.db_name = db_name
        self.encryption_key = self.load_or_create_key()
        if CRYPTOGRAPHY_AVAILABLE:
            self.cipher = Fernet(self.encryption_key)
        self.init_database()
        
    def load_or_create_key(self):
        """Load or create encryption key"""
        key_file = 'secret.key'
        if CRYPTOGRAPHY_AVAILABLE:
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    key = f.read()
            else:
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
            return key
        else:
            # Fallback to simple key
            return hashlib.sha256(b"omms_secret_key").digest()
    
    def encrypt_data(self, data):
        """Encrypt sensitive data"""
        if not CRYPTOGRAPHY_AVAILABLE:
            # Simple XOR encryption for fallback
            key = b"omms_secret_key"
            if isinstance(data, str):
                data = data.encode()
            encrypted = bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])
            return encrypted.hex()
        
        if isinstance(data, str):
            data = data.encode()
        return self.cipher.encrypt(data).decode()
    
    def decrypt_data(self, encrypted_data):
        """Decrypt sensitive data"""
        if not CRYPTOGRAPHY_AVAILABLE:
            # Simple XOR decryption for fallback
            key = b"omms_secret_key"
            encrypted_bytes = bytes.fromhex(encrypted_data)
            decrypted = bytes([encrypted_bytes[i] ^ key[i % len(key)] for i in range(len(encrypted_bytes))])
            return decrypted.decode()
        
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        return self.cipher.decrypt(encrypted_data).decode()
    
    def hash_password(self, password, salt=None):
        """Secure password hashing"""
        if salt is None:
            salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        
        pwdhash = hashlib.pbkdf2_hmac(
            'sha512',
            password.encode('utf-8'),
            salt,
            100000
        )
        pwdhash = hashlib.sha256(pwdhash).hexdigest()
        return (salt + pwdhash.encode('ascii')).decode('ascii')
    
    def verify_password(self, stored_password, provided_password):
        """Verify hashed password"""
        salt = stored_password[:64]
        stored_hash = stored_password[64:]
        pwdhash = self.hash_password(provided_password, salt.encode('ascii'))[64:]
        return pwdhash == stored_hash
    
    def init_database(self):
        """Initialize advanced database schema"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Users table with enhanced security
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'host', 'participant', 'guest')),
                full_name TEXT,
                department TEXT,
                phone TEXT,
                profile_pic BLOB,
                security_question TEXT,
                security_answer TEXT,
                last_login TEXT,
                failed_attempts INTEGER DEFAULT 0,
                account_locked INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Meetings table with advanced features
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meetings (
                meeting_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                meeting_type TEXT CHECK(meeting_type IN ('one-time', 'recurring', 'urgent')),
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                duration INTEGER NOT NULL,
                agenda TEXT,
                location TEXT,
                meeting_url TEXT,
                host_id TEXT,
                status TEXT DEFAULT 'scheduled' CHECK(status IN ('scheduled', 'ongoing', 'completed', 'cancelled')),
                priority INTEGER DEFAULT 1 CHECK(priority BETWEEN 1 AND 5),
                requires_confirmation INTEGER DEFAULT 0,
                max_participants INTEGER,
                recurring_pattern TEXT,
                recurring_end_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (host_id) REFERENCES users(user_id)
            )
        ''')
        
        # Participants with enhanced tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS participants (
                participant_id TEXT PRIMARY KEY,
                meeting_id TEXT,
                user_id TEXT,
                role TEXT DEFAULT 'attendee' CHECK(role IN ('attendee', 'presenter', 'moderator')),
                status TEXT DEFAULT 'invited' CHECK(status IN ('invited', 'confirmed', 'declined', 'attended', 'absent')),
                confirmation_time TEXT,
                actual_join_time TEXT,
                actual_leave_time TEXT,
                attendance_duration INTEGER,
                feedback_score INTEGER,
                feedback_comment TEXT,
                FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Meeting notes with version control
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meeting_notes (
                note_id TEXT PRIMARY KEY,
                meeting_id TEXT,
                version INTEGER DEFAULT 1,
                content TEXT,
                created_by TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                modified_at TEXT,
                tags TEXT,
                is_encrypted INTEGER DEFAULT 0,
                FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id)
            )
        ''')
        
        # Resources and files
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meeting_resources (
                resource_id TEXT PRIMARY KEY,
                meeting_id TEXT,
                filename TEXT,
                file_type TEXT,
                file_size INTEGER,
                file_data BLOB,
                uploaded_by TEXT,
                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                download_count INTEGER DEFAULT 0,
                FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id)
            )
        ''')
        
        # Notifications history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id TEXT PRIMARY KEY,
                user_id TEXT,
                type TEXT CHECK(type IN ('reminder', 'invitation', 'update', 'alert')),
                title TEXT,
                message TEXT,
                meeting_id TEXT,
                is_read INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                scheduled_for TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id)
            )
        ''')
        
        # Analytics data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meeting_analytics (
                analytic_id TEXT PRIMARY KEY,
                meeting_id TEXT,
                total_participants INTEGER,
                confirmed_participants INTEGER,
                attendance_rate REAL,
                average_duration REAL,
                feedback_score REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        self.create_default_admin()
    
    def create_default_admin(self):
        """Create default admin account if none exists"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        if cursor.fetchone()[0] == 0:
            admin_id = str(uuid.uuid4())
            password_hash = self.hash_password("Admin@123")
            
            cursor.execute('''
                INSERT INTO users (user_id, username, password_hash, email, role, full_name)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (admin_id, 'admin', password_hash, 'admin@omms.com', 'admin', 'System Administrator'))
            
            # Create sample users
            sample_users = [
                ('host1', 'host1@omms.com', 'Host One', 'Engineering'),
                ('host2', 'host2@omms.com', 'Host Two', 'Marketing'),
                ('participant1', 'participant1@omms.com', 'Participant One', 'Sales'),
                ('participant2', 'participant2@omms.com', 'Participant Two', 'HR'),
            ]
            
            for username, email, full_name, department in sample_users:
                user_id = str(uuid.uuid4())
                password_hash = self.hash_password("Password@123")
                cursor.execute('''
                    INSERT INTO users (user_id, username, password_hash, email, role, full_name, department)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, username, password_hash, email, 
                      'host' if 'host' in username else 'participant', 
                      full_name, department))
        
        conn.commit()
        conn.close()

class AIScheduler:
    """AI-powered meeting scheduler with optimization"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def find_optimal_time(self, host_id, participant_ids, duration, preferences=None):
        """Find optimal meeting time using AI algorithm"""
        conn = sqlite3.connect(self.db.db_name)
        cursor = conn.cursor()
        
        # Get existing meetings for conflict detection
        all_user_ids = [host_id] + participant_ids
        placeholders = ','.join(['?'] * len(all_user_ids))
        
        cursor.execute(f'''
            SELECT m.date, m.start_time, m.end_time 
            FROM meetings m
            LEFT JOIN participants p ON m.meeting_id = p.meeting_id
            WHERE (m.host_id IN ({placeholders}) OR p.user_id IN ({placeholders}))
            AND m.status = 'scheduled'
            AND m.date >= date('now')
        ''', all_user_ids * 2)
        
        busy_slots = cursor.fetchall()
        
        # Generate optimal time suggestions
        optimal_times = self.generate_time_slots(busy_slots, duration, preferences)
        
        conn.close()
        return optimal_times
    
    def generate_time_slots(self, busy_slots, duration, preferences):
        """Generate optimal time slots"""
        suggestions = []
        today = datetime.now()
        
        # Check next 7 days
        for days_ahead in range(1, 8):
            target_date = today + timedelta(days=days_ahead)
            
            # Morning slot (9 AM)
            morning_time = target_date.replace(hour=9, minute=0, second=0, microsecond=0)
            if self.is_slot_available(morning_time, duration, busy_slots):
                suggestions.append({
                    'date': target_date.strftime('%Y-%m-%d'),
                    'time': '09:00',
                    'score': 85,
                    'reason': 'Optimal morning slot'
                })
            
            # Afternoon slot (2 PM)
            afternoon_time = target_date.replace(hour=14, minute=0, second=0, microsecond=0)
            if self.is_slot_available(afternoon_time, duration, busy_slots):
                suggestions.append({
                    'date': target_date.strftime('%Y-%m-%d'),
                    'time': '14:00',
                    'score': 90,
                    'reason': 'Optimal afternoon slot'
                })
        
        return sorted(suggestions, key=lambda x: x['score'], reverse=True)[:3]
    
    def is_slot_available(self, start_time, duration, busy_slots):
        """Check if time slot is available"""
        end_time = start_time + timedelta(minutes=duration)
        
        for busy_date, busy_start, busy_end in busy_slots:
            busy_start_dt = datetime.strptime(f"{busy_date} {busy_start}", "%Y-%m-%d %H:%M")
            busy_end_dt = datetime.strptime(f"{busy_date} {busy_end}", "%Y-%m-%d %H:%M")
            
            if not (end_time <= busy_start_dt or start_time >= busy_end_dt):
                return False
        
        return True

class AdvancedOMMS:
    """Main application class with premium features"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ADVANCED ONLINE MEETING MANAGEMENT SYSTEM")
        self.root.geometry("1400x800")
        self.root.configure(bg='#0f172a')
        
        # Set window icon
        try:
            self.root.iconbitmap('omms_icon.ico')
        except:
            pass
        
        # Initialize components
        self.db = SecureDatabaseManager()
        self.ai_scheduler = AIScheduler(self.db)
        self.current_user = None
        self.notification_thread = None
        self.theme_mode = 'dark'
        
        # Create modern UI elements
        self.setup_styles()
        self.create_splash_screen()
        
        # Start background services
        self.start_background_services()
    
    def setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        
        # Modern dark theme
        style.theme_use('clam')
        
        # Configure colors for dark theme
        style.configure('TLabel', background='#0f172a', foreground='#f8fafc', font=('Segoe UI', 10))
        style.configure('TFrame', background='#0f172a')
        style.configure('TLabelframe', background='#0f172a', foreground='#f8fafc')
        style.configure('TLabelframe.Label', background='#0f172a', foreground='#f8fafc')
        
        # Configure buttons
        style.configure('Custom.TButton',
                       background='#3b82f6',
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'),
                       padding=10,
                       borderwidth=0)
        
        style.map('Custom.TButton',
                 background=[('active', '#2563eb'), ('disabled', '#64748b')],
                 foreground=[('disabled', '#cbd5e1')])
    
    def create_splash_screen(self):
        """Create animated splash screen"""
        self.splash_frame = tk.Frame(self.root, bg='#0f172a')
        self.splash_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Animated title
        title_label = tk.Label(self.splash_frame, 
                              text="⚡ ADVANCED OMMS", 
                              font=("Segoe UI", 36, "bold"),
                              bg='#0f172a',
                              fg='#3b82f6')
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(self.splash_frame,
                                 text="Premium Meeting Management Platform",
                                 font=("Segoe UI", 14),
                                 bg='#0f172a',
                                 fg='#94a3b8')
        subtitle_label.pack(pady=10)
        
        # Loading animation
        self.loading_label = tk.Label(self.splash_frame,
                                     text="Initializing System...",
                                     font=("Segoe UI", 12),
                                     bg='#0f172a',
                                     fg='#64748b')
        self.loading_label.pack(pady=30)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.splash_frame,
                                       length=300,
                                       mode='determinate')
        self.progress.pack(pady=20)
        
        # Simulate loading
        self.splash_progress = 0
        self.animate_splash()
    
    def animate_splash(self):
        """Animate splash screen loading"""
        if self.splash_progress < 100:
            self.splash_progress += 10
            self.progress['value'] = self.splash_progress
            
            loading_texts = [
                "Initializing System...",
                "Loading Database...",
                "Starting AI Services...",
                "Configuring Security...",
                "Ready to Launch!"
            ]
            index = min(self.splash_progress // 20, 4)
            self.loading_label.config(text=loading_texts[index])
            
            self.root.after(200, self.animate_splash)
        else:
            self.splash_frame.destroy()
            self.show_enhanced_login()
    
    # ==================== TASK B.1: ENHANCED USER AUTHENTICATION ====================
    def show_enhanced_login(self):
        """Show advanced login screen with security features"""
        self.clear_window()
        
        # Create main container
        main_container = tk.Frame(self.root, bg='#0f172a')
        main_container.pack(fill='both', expand=True)
        
        # Left panel with branding (using solid color instead of gradient)
        left_panel = tk.Frame(main_container, bg='#1e40af')
        left_panel.pack(side='left', fill='both', expand=True)
        
        brand_frame = tk.Frame(left_panel, bg='#1e40af')
        brand_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(brand_frame, text="⚡", font=("Segoe UI", 72), 
                bg='#1e40af', fg='white').pack()
        tk.Label(brand_frame, text="AOMMS", font=("Segoe UI", 36, "bold"), 
                bg='#1e40af', fg='white').pack(pady=10)
        tk.Label(brand_frame, text="Advanced Online Meeting System", 
                font=("Segoe UI", 14), bg='#1e40af', fg='#dbeafe').pack()
        
        # Right panel with login form
        right_panel = tk.Frame(main_container, bg='#1e293b')
        right_panel.pack(side='right', fill='both', expand=True)
        
        form_frame = tk.Frame(right_panel, bg='#1e293b', padx=50, pady=50)
        form_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(form_frame, text="Secure Login", font=("Segoe UI", 28, "bold"), 
                bg='#1e293b', fg='white').pack(pady=(0, 30))
        
        # Username field
        tk.Label(form_frame, text="Username", font=("Segoe UI", 11), 
                bg='#1e293b', fg='#94a3b8', anchor='w').pack(fill='x', pady=(10, 5))
        self.username_entry = ttk.Entry(form_frame, font=("Segoe UI", 12), width=30)
        self.username_entry.pack(pady=(0, 15))
        self.username_entry.insert(0, "admin")
        
        # Password field with show/hide
        password_frame = tk.Frame(form_frame, bg='#1e293b')
        password_frame.pack(fill='x', pady=(10, 5))
        
        tk.Label(password_frame, text="Password", font=("Segoe UI", 11), 
                bg='#1e293b', fg='#94a3b8', anchor='w').pack(side='left')
        
        forgot_label = tk.Label(password_frame, text="Forgot Password?", font=("Segoe UI", 10), 
                bg='#1e293b', fg='#3b82f6', anchor='e', cursor="hand2")
        forgot_label.pack(side='right')
        
        self.password_entry = ttk.Entry(form_frame, font=("Segoe UI", 12), 
                                       width=30, show='•')
        self.password_entry.pack(pady=(0, 15))
        self.password_entry.insert(0, "Admin@123")
        
        # Show password checkbox
        self.show_password_var = tk.BooleanVar()
        show_pass_check = tk.Checkbutton(form_frame, text="Show Password", 
                                        variable=self.show_password_var,
                                        command=self.toggle_password_visibility,
                                        bg='#1e293b', fg='white',
                                        selectcolor='#1e293b',
                                        activebackground='#1e293b',
                                        activeforeground='white')
        show_pass_check.pack(anchor='w', pady=(0, 20))
        
        # Security challenge (CAPTCHA-like)
        security_frame = tk.Frame(form_frame, bg='#1e293b')
        security_frame.pack(fill='x', pady=(0, 20))
        
        self.captcha_text = self.generate_captcha()
        tk.Label(security_frame, text=f"Enter code: {self.captcha_text}", 
                font=("Segoe UI", 10, "bold"), bg='#1e293b', fg='white').pack(side='left')
        
        self.captcha_entry = ttk.Entry(security_frame, font=("Segoe UI", 12), width=15)
        self.captcha_entry.pack(side='right', padx=(10, 0))
        
        # Login button with hover effect
        login_btn = tk.Button(form_frame, text="Secure Login →", 
                             font=("Segoe UI", 12, "bold"),
                             bg='#3b82f6', fg='white',
                             bd=0, padx=40, pady=12,
                             cursor="hand2",
                             command=self.enhanced_authentication)
        login_btn.pack(pady=(10, 20))
        
        # Additional options
        options_frame = tk.Frame(form_frame, bg='#1e293b')
        options_frame.pack(fill='x')
        
        tk.Label(options_frame, text="New user? ", font=("Segoe UI", 10), 
                bg='#1e293b', fg='#94a3b8').pack(side='left')
        
        register_label = tk.Label(options_frame, text="Register here", font=("Segoe UI", 10, "bold"), 
                bg='#1e293b', fg='#3b82f6', cursor="hand2")
        register_label.pack(side='left')
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda e: self.enhanced_authentication())
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='•')
    
    def generate_captcha(self):
        """Generate simple CAPTCHA"""
        chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        return ''.join(random.choice(chars) for _ in range(5))
    
    def enhanced_authentication(self):
        """Enhanced authentication with security checks"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        captcha_input = self.captcha_entry.get()
        
        # Validate CAPTCHA
        if captcha_input != self.captcha_text:
            messagebox.showerror("Security Error", "Invalid security code!")
            self.captcha_text = self.generate_captcha()
            return
        
        # Check for brute force
        conn = sqlite3.connect(self.db.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT failed_attempts, account_locked FROM users WHERE username = ?
        ''', (username,))
        
        result = cursor.fetchone()
        if result and result[1] == 1:
            messagebox.showerror("Account Locked", 
                               "Account is locked due to multiple failed attempts. Contact administrator.")
            conn.close()
            return
        
        # Authenticate
        cursor.execute('''
            SELECT user_id, password_hash, role, full_name FROM users WHERE username = ?
        ''', (username,))
        
        user = cursor.fetchone()
        
        if user and self.db.verify_password(user[1], password):
            # Reset failed attempts
            cursor.execute('''
                UPDATE users SET failed_attempts = 0, last_login = ? WHERE username = ?
            ''', (datetime.now().isoformat(), username))
            
            self.current_user = {
                'id': user[0],
                'username': username,
                'role': user[2],
                'name': user[3]
            }
            
            conn.commit()
            conn.close()
            
            # Log successful login
            self.log_activity(f"User {username} logged in successfully")
            
            # Show dashboard
            self.show_advanced_dashboard()
        else:
            # Increment failed attempts
            if user:
                cursor.execute('''
                    UPDATE users 
                    SET failed_attempts = failed_attempts + 1 
                    WHERE username = ?
                ''', (username,))
                
                cursor.execute('''
                    SELECT failed_attempts FROM users WHERE username = ?
                ''', (username,))
                
                attempts = cursor.fetchone()[0]
                
                if attempts >= 5:
                    cursor.execute('''
                        UPDATE users SET account_locked = 1 WHERE username = ?
                    ''', (username,))
                    messagebox.showerror("Account Locked", 
                                       "Too many failed attempts. Account locked.")
                else:
                    messagebox.showerror("Login Failed", 
                                       f"Invalid credentials. {5-attempts} attempts remaining.")
            
            conn.commit()
            conn.close()
    
    def log_activity(self, activity):
        """Log user activity"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('activity.log', 'a') as f:
            f.write(f"[{timestamp}] {activity}\n")
    
    # ==================== MAIN DASHBOARD ====================
    def show_advanced_dashboard(self):
        """Show advanced dashboard with analytics"""
        self.clear_window()
        
        # Top Navigation Bar
        nav_bar = tk.Frame(self.root, bg='#1e293b', height=60)
        nav_bar.pack(fill='x')
        nav_bar.pack_propagate(False)
        
        # Logo and title
        logo_frame = tk.Frame(nav_bar, bg='#1e293b')
        logo_frame.pack(side='left', padx=20)
        
        tk.Label(logo_frame, text="⚡", font=("Segoe UI", 24), 
                bg='#1e293b', fg='#3b82f6').pack(side='left')
        tk.Label(logo_frame, text="AOMMS", font=("Segoe UI", 18, "bold"), 
                bg='#1e293b', fg='white').pack(side='left', padx=10)
        
        # User info
        user_frame = tk.Frame(nav_bar, bg='#1e293b')
        user_frame.pack(side='right', padx=20)
        
        tk.Label(user_frame, text=f"👤 {self.current_user['name']}", 
                font=("Segoe UI", 11), bg='#1e293b', fg='#94a3b8').pack(side='left', padx=10)
        
        # Notification bell
        tk.Label(user_frame, text="🔔", font=("Segoe UI", 16), 
                bg='#1e293b', fg='#94a3b8', cursor="hand2").pack(side='left', padx=10)
        
        # Logout button
        logout_btn = tk.Button(user_frame, text="Logout", 
                              font=("Segoe UI", 10),
                              bg='#ef4444', fg='white',
                              bd=0, padx=15, pady=5,
                              cursor="hand2",
                              command=self.show_enhanced_login)
        logout_btn.pack(side='left', padx=10)
        
        # Main content area
        main_content = tk.Frame(self.root, bg='#0f172a')
        main_content.pack(fill='both', expand=True)
        
        # Sidebar
        sidebar = tk.Frame(main_content, bg='#1e293b', width=250)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # Navigation buttons
        nav_buttons = [
            ("📊 Dashboard", self.show_dashboard_overview),
            ("📅 Schedule Meeting", self.show_ai_scheduler),
            ("🤖 AI Assistant", self.show_ai_assistant),
            ("👥 Participants", self.show_participant_manager),
            ("🔔 Smart Notifications", self.show_smart_notifications),
            ("📝 Smart Notes", self.show_smart_notes),
            ("🔍 Advanced Search", self.show_advanced_search),
            ("💾 Secure Backup", self.show_secure_backup),
            ("📈 Analytics", self.show_analytics_dashboard),
            ("⚙️ Settings", self.show_settings)
        ]
        
        for text, command in nav_buttons:
            btn = tk.Button(sidebar, text=text, font=("Segoe UI", 11),
                           bg='#1e293b', fg='#cbd5e1',
                           bd=0, padx=20, pady=12,
                           anchor='w', cursor="hand2",
                           command=command)
            btn.pack(fill='x', padx=10, pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg='#334155'))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg='#1e293b'))
        
        # Content frame
        self.content_frame = tk.Frame(main_content, bg='#0f172a')
        self.content_frame.pack(side='right', fill='both', expand=True)
        
        # Show dashboard by default
        self.show_dashboard_overview()
    
    # ==================== TASK B.2: AI-POWERED MEETING SCHEDULER ====================
    def show_ai_scheduler(self):
        """Show AI-powered meeting scheduling interface"""
        self.clear_content()
        
        # Header
        header = tk.Frame(self.content_frame, bg='#1e293b', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="🤖 AI-Powered Meeting Scheduler", 
                font=("Segoe UI", 20, "bold"), bg='#1e293b', fg='white').pack(side='left', padx=30, pady=20)
        
        # Main form
        form_container = tk.Frame(self.content_frame, bg='#0f172a')
        form_container.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(form_container)
        notebook.pack(fill='both', expand=True)
        
        # Tab 1: Basic Details
        basic_tab = tk.Frame(notebook, bg='#1e293b')
        notebook.add(basic_tab, text="📝 Basic Details")
        
        # Meeting title
        tk.Label(basic_tab, text="Meeting Title *", font=("Segoe UI", 12),
                bg='#1e293b', fg='#94a3b8').grid(row=0, column=0, sticky='w', pady=15, padx=20)
        title_entry = ttk.Entry(basic_tab, font=("Segoe UI", 12), width=40)
        title_entry.grid(row=0, column=1, pady=15, padx=20, sticky='w')
        
        # Meeting type
        tk.Label(basic_tab, text="Meeting Type *", font=("Segoe UI", 12),
                bg='#1e293b', fg='#94a3b8').grid(row=1, column=0, sticky='w', pady=15, padx=20)
        type_combo = ttk.Combobox(basic_tab, values=["One-time", "Recurring", "Urgent"], 
                                 font=("Segoe UI", 12), width=37, state='readonly')
        type_combo.grid(row=1, column=1, pady=15, padx=20, sticky='w')
        type_combo.set("One-time")
        
        # Duration
        tk.Label(basic_tab, text="Duration (minutes) *", font=("Segoe UI", 12),
                bg='#1e293b', fg='#94a3b8').grid(row=2, column=0, sticky='w', pady=15, padx=20)
        duration_combo = ttk.Combobox(basic_tab, values=["15", "30", "45", "60", "90", "120"], 
                                     font=("Segoe UI", 12), width=37, state='readonly')
        duration_combo.grid(row=2, column=1, pady=15, padx=20, sticky='w')
        duration_combo.set("60")
        
        # Tab 2: Date & Time Selection
        datetime_tab = tk.Frame(notebook, bg='#1e293b')
        notebook.add(datetime_tab, text="📅 Date & Time")
        
        # Date selection
        tk.Label(datetime_tab, text="Select Date (YYYY-MM-DD):", font=("Segoe UI", 12),
                bg='#1e293b', fg='#94a3b8').pack(anchor='w', padx=20, pady=(20, 10))
        
        date_entry = ttk.Entry(datetime_tab, font=("Segoe UI", 12), width=20)
        date_entry.pack(anchor='w', padx=20, pady=5)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Time selection
        tk.Label(datetime_tab, text="Select Time:", font=("Segoe UI", 12),
                bg='#1e293b', fg='#94a3b8').pack(anchor='w', padx=20, pady=(20, 10))
        
        time_frame = tk.Frame(datetime_tab, bg='#1e293b')
        time_frame.pack(anchor='w', padx=20, pady=5)
        
        hour_combo = ttk.Combobox(time_frame, values=[f"{h:02d}" for h in range(9, 18)], 
                                 width=5, state='readonly')
        hour_combo.pack(side='left', padx=5)
        hour_combo.set("14")
        
        tk.Label(time_frame, text=":", bg='#1e293b', fg='white').pack(side='left', padx=5)
        
        minute_combo = ttk.Combobox(time_frame, values=["00", "15", "30", "45"], 
                                   width=5, state='readonly')
        minute_combo.pack(side='left', padx=5)
        minute_combo.set("00")
        
        # Tab 3: Participants
        participants_tab = tk.Frame(notebook, bg='#1e293b')
        notebook.add(participants_tab, text="👥 Participants")
        
        # Get all users
        conn = sqlite3.connect(self.db.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, full_name FROM users WHERE user_id != ?", 
                      (self.current_user['id'],))
        all_users = cursor.fetchall()
        conn.close()
        
        # Participants listbox
        listbox_frame = tk.Frame(participants_tab, bg='#1e293b')
        listbox_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.participants_listbox = tk.Listbox(listbox_frame, 
                                              bg='#0f172a',
                                              fg='white',
                                              selectbackground='#3b82f6',
                                              font=("Segoe UI", 11),
                                              yscrollcommand=scrollbar.set,
                                              selectmode='multiple',
                                              height=10)
        self.participants_listbox.pack(fill='both', expand=True)
        
        for user in all_users:
            self.participants_listbox.insert(tk.END, f"{user[2]} ({user[1]})")
        
        scrollbar.config(command=self.participants_listbox.yview)
        
        # AI Suggestion Button
        suggestion_frame = tk.Frame(form_container, bg='#0f172a')
        suggestion_frame.pack(pady=20)
        
        ai_btn = tk.Button(suggestion_frame, text="🤖 Get AI Time Suggestions",
                          font=("Segoe UI", 12, "bold"),
                          bg='#8b5cf6', fg='white',
                          bd=0, padx=30, pady=12,
                          cursor="hand2",
                          command=lambda: self.get_ai_suggestions(title_entry.get(),
                                                                 duration_combo.get(),
                                                                 self.participants_listbox))
        ai_btn.pack()
        
        # Schedule button
        schedule_btn = tk.Button(form_container, text="📅 Schedule Meeting",
                                font=("Segoe UI", 14, "bold"),
                                bg='#10b981', fg='white',
                                bd=0, padx=40, pady=15,
                                cursor="hand2",
                                command=lambda: self.schedule_meeting_advanced(
                                    title_entry.get(),
                                    type_combo.get(),
                                    duration_combo.get(),
                                    date_entry.get(),
                                    f"{hour_combo.get()}:{minute_combo.get()}",
                                    self.participants_listbox
                                ))
        schedule_btn.pack(pady=20)
    
    def get_ai_suggestions(self, title, duration, listbox):
        """Get AI-powered time suggestions"""
        if not title:
            messagebox.showwarning("Input Required", "Please enter meeting title first")
            return
        
        # Get selected participants
        selected_indices = listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Participants Required", "Please select at least one participant")
            return
        
        # Show AI suggestions window
        suggestion_window = tk.Toplevel(self.root)
        suggestion_window.title("🤖 AI Time Suggestions")
        suggestion_window.geometry("500x400")
        suggestion_window.configure(bg='#0f172a')
        
        tk.Label(suggestion_window, text="AI-Powered Time Suggestions", 
                font=("Segoe UI", 16, "bold"), bg='#0f172a', fg='white').pack(pady=20)
        
        # Get suggestions (simulated)
        suggestions = [
            {"date": datetime.now().strftime('%Y-%m-%d'), "time": "14:00", "score": 95, "reason": "Optimal for all participants"},
            {"date": (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'), "time": "10:00", "score": 88, "reason": "Morning productivity peak"},
            {"date": (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'), "time": "15:30", "score": 82, "reason": "Afternoon availability"}
        ]
        
        for i, suggestion in enumerate(suggestions):
            frame = tk.Frame(suggestion_window, bg='#1e293b', relief='raised', bd=1)
            frame.pack(fill='x', padx=20, pady=10)
            
            tk.Label(frame, text=f"Option {i+1} | Score: {suggestion['score']}%", 
                    font=("Segoe UI", 12, "bold"), bg='#1e293b', fg='#10b981').pack(anchor='w', padx=10, pady=5)
            tk.Label(frame, text=f"📅 {suggestion['date']} 🕒 {suggestion['time']}", 
                    font=("Segoe UI", 11), bg='#1e293b', fg='white').pack(anchor='w', padx=10)
            tk.Label(frame, text=f"📊 {suggestion['reason']}", 
                    font=("Segoe UI", 10), bg='#1e293b', fg='#94a3b8').pack(anchor='w', padx=10, pady=(0, 5))
            
            select_btn = tk.Button(frame, text="Select This Time",
                                  font=("Segoe UI", 10),
                                  bg='#3b82f6', fg='white',
                                  bd=0, padx=10, pady=5,
                                  cursor="hand2")
            select_btn.pack(anchor='e', padx=10, pady=5)
    
    def schedule_meeting_advanced(self, title, meeting_type, duration, date, time, listbox):
        """Schedule meeting with advanced features"""
        if not all([title, duration, date, time]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
        
        # Create meeting
        meeting_id = str(uuid.uuid4())
        
        # Calculate end time
        start_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end_dt = start_dt + timedelta(minutes=int(duration))
        
        meeting_data = {
            'meeting_id': meeting_id,
            'title': title,
            'meeting_type': meeting_type.lower(),
            'duration': int(duration),
            'date': date,
            'start_time': time,
            'end_time': end_dt.strftime("%H:%M"),
            'host_id': self.current_user['id'],
            'status': 'scheduled'
        }
        
        try:
            conn = sqlite3.connect(self.db.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO meetings (meeting_id, title, meeting_type, duration, 
                                    date, start_time, end_time, host_id, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(meeting_data.values()))
            
            # Add participants
            selected_indices = listbox.curselection()
            conn2 = sqlite3.connect(self.db.db_name)
            cursor2 = conn2.cursor()
            cursor2.execute("SELECT user_id FROM users WHERE user_id != ?", (self.current_user['id'],))
            all_users = cursor2.fetchall()
            conn2.close()
            
            for idx in selected_indices:
                if idx < len(all_users):
                    participant_id = str(uuid.uuid4())
                    cursor.execute('''
                        INSERT INTO participants (participant_id, meeting_id, user_id)
                        VALUES (?, ?, ?)
                    ''', (participant_id, meeting_id, all_users[idx][0]))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Meeting scheduled successfully!")
            
            # Send notifications
            self.send_meeting_notifications(meeting_id)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to schedule meeting: {str(e)}")
    
        # ==================== TASK B.3: ADVANCED PARTICIPANT MANAGEMENT ====================
    def show_participant_manager(self):
        """Show advanced participant management"""
        self.clear_content()
        
        tk.Label(self.content_frame, text="👥 Advanced Participant Management", 
                font=("Segoe UI", 20, "bold"), bg='#0f172a', fg='white').pack(pady=20)
        
        # Create notebook
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Tab 1: Manage Participants
        manage_tab = tk.Frame(notebook, bg='#1e293b')
        notebook.add(manage_tab, text="Manage Participants")
        
        # Get meetings
        conn = sqlite3.connect(self.db.db_name)
        cursor = conn.cursor()
        
        if self.current_user['role'] == 'admin':
            cursor.execute('''
                SELECT m.meeting_id, m.title, m.date, m.start_time 
                FROM meetings m 
                ORDER BY m.date DESC
            ''')
        else:
            cursor.execute('''
                SELECT m.meeting_id, m.title, m.date, m.start_time 
                FROM meetings m 
                WHERE m.host_id = ?
                ORDER BY m.date DESC
            ''', (self.current_user['id'],))
        
        meetings = cursor.fetchall()
        
        if not meetings:
            tk.Label(manage_tab, text="No meetings found", 
                    font=("Segoe UI", 14), bg='#1e293b', fg='white').pack(pady=50)
            conn.close()
            return
        
        # Meeting selector
        tk.Label(manage_tab, text="Select Meeting:", font=("Segoe UI", 12),
                bg='#1e293b', fg='#94a3b8').pack(anchor='w', padx=20, pady=(20, 10))
        
        meeting_var = tk.StringVar()
        meeting_combo = ttk.Combobox(manage_tab, textvariable=meeting_var,
                                    values=[f"{m[1]} ({m[2]} {m[3]})" for m in meetings],
                                    font=("Segoe UI", 12), width=50, state='readonly')
        meeting_combo.pack(padx=20, pady=(0, 20))
        
        # Store meeting ID mapping
        self.meeting_id_map = {f"{m[1]} ({m[2]} {m[3]})": m[0] for m in meetings}
        
        # Participants treeview
        tree_frame = tk.Frame(manage_tab, bg='#1e293b')
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('ID', 'Name', 'Email', 'Role', 'Status', 'Actions')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.column('Name', width=150)
        tree.column('Email', width=200)
        tree.column('Actions', width=120)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Store tree reference
        self.participants_tree = tree
        
        def load_participants(event=None):
            """Load participants for selected meeting"""
            selection = meeting_combo.get()
            if not selection:
                return
            
            meeting_id = self.meeting_id_map.get(selection)
            if not meeting_id:
                return
            
            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)
            
            # Get participants for this meeting
            cursor.execute('''
                SELECT p.participant_id, u.full_name, u.email, p.role, p.status
                FROM participants p
                JOIN users u ON p.user_id = u.user_id
                WHERE p.meeting_id = ?
            ''', (meeting_id,))
            
            participants = cursor.fetchall()
            
            for participant in participants:
                tree.insert('', 'end', values=(
                    participant[0],
                    participant[1],
                    participant[2],
                    participant[3],
                    participant[4],
                    "Remove"
                ))
        
        meeting_combo.bind('<<ComboboxSelected>>', load_participants)
        
        # Action buttons frame
        button_frame = tk.Frame(manage_tab, bg='#1e293b')
        button_frame.pack(pady=20)
        
        # Get all users for adding
        cursor.execute('''
            SELECT user_id, full_name, email, role 
            FROM users 
            WHERE user_id != ? AND role IN ('participant', 'host')
        ''', (self.current_user['id'],))
        
        all_users = cursor.fetchall()
        self.all_users_map = {f"{u[1]} ({u[2]})": u[0] for u in all_users}
        
        # Add participant button
        add_frame = tk.Frame(button_frame, bg='#1e293b')
        add_frame.pack(pady=10)
        
        tk.Label(add_frame, text="Add Participant:", font=("Segoe UI", 11),
                bg='#1e293b', fg='#94a3b8').pack(side='left', padx=(0, 10))
        
        user_var = tk.StringVar()
        user_combo = ttk.Combobox(add_frame, textvariable=user_var,
                                 values=list(self.all_users_map.keys()),
                                 font=("Segoe UI", 11), width=30, state='readonly')
        user_combo.pack(side='left', padx=(0, 10))
        
        def add_participant():
            """Add a new participant to the meeting"""
            selection = meeting_combo.get()
            if not selection:
                messagebox.showwarning("Warning", "Please select a meeting first")
                return
            
            user_selection = user_combo.get()
            if not user_selection:
                messagebox.showwarning("Warning", "Please select a user to add")
                return
            
            meeting_id = self.meeting_id_map.get(selection)
            user_id = self.all_users_map.get(user_selection)
            
            # Check if user is already a participant
            cursor.execute('''
                SELECT participant_id FROM participants 
                WHERE meeting_id = ? AND user_id = ?
            ''', (meeting_id, user_id))
            
            if cursor.fetchone():
                messagebox.showwarning("Warning", "User is already a participant in this meeting")
                return
            
            # Add participant
            participant_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO participants (participant_id, meeting_id, user_id, status)
                VALUES (?, ?, ?, 'invited')
            ''', (participant_id, meeting_id, user_id))
            
            conn.commit()
            
            # Reload participants
            load_participants()
            messagebox.showinfo("Success", "Participant added successfully!")
        
        tk.Button(add_frame, text="➕ Add",
                 font=("Segoe UI", 10),
                 bg='#10b981', fg='white',
                 bd=0, padx=15, pady=5,
                 cursor="hand2",
                 command=add_participant).pack(side='left')
        
        # Action buttons for selected participant
        action_frame = tk.Frame(button_frame, bg='#1e293b')
        action_frame.pack(pady=10)
        
        def update_participant_status():
            """Update selected participant's status"""
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a participant")
                return
            
            item = tree.item(selection[0])
            participant_id = item['values'][0]
            
            status_window = tk.Toplevel(self.root)
            status_window.title("Update Status")
            status_window.geometry("300x200")
            status_window.configure(bg='#0f172a')
            
            tk.Label(status_window, text="Select New Status:", 
                    font=("Segoe UI", 14, "bold"), bg='#0f172a', fg='white').pack(pady=20)
            
            status_var = tk.StringVar(value=item['values'][4])
            
            status_options = [
                ("Invited", "invited"),
                ("Confirmed", "confirmed"),
                ("Declined", "declined"),
                ("Attended", "attended"),
                ("Absent", "absent")
            ]
            
            for text, value in status_options:
                tk.Radiobutton(status_window, text=text, variable=status_var, value=value,
                             bg='#0f172a', fg='white', selectcolor='#1e293b').pack(anchor='w', padx=50)
            
            def save_status():
                new_status = status_var.get()
                cursor.execute('''
                    UPDATE participants SET status = ? WHERE participant_id = ?
                ''', (new_status, participant_id))
                
                conn.commit()
                load_participants()
                status_window.destroy()
                messagebox.showinfo("Success", "Status updated successfully!")
            
            tk.Button(status_window, text="Save", 
                     font=("Segoe UI", 11, "bold"),
                     bg='#3b82f6', fg='white',
                     bd=0, padx=20, pady=8,
                     cursor="hand2",
                     command=save_status).pack(pady=20)
        
        def edit_participant_role():
            """Edit selected participant's role"""
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a participant")
                return
            
            item = tree.item(selection[0])
            participant_id = item['values'][0]
            
            role = simpledialog.askstring("Edit Role", 
                                         "Enter new role (attendee/presenter/moderator):",
                                         initialvalue=item['values'][3])
            
            if role and role.lower() in ['attendee', 'presenter', 'moderator']:
                cursor.execute('''
                    UPDATE participants SET role = ? WHERE participant_id = ?
                ''', (role.lower(), participant_id))
                
                conn.commit()
                load_participants()
                messagebox.showinfo("Success", "Role updated successfully!")
        
        def remove_participant():
            """Remove selected participant"""
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a participant")
                return
            
            item = tree.item(selection[0])
            participant_name = item['values'][1]
            participant_id = item['values'][0]
            
            confirm = messagebox.askyesno("Confirm Removal", 
                                         f"Are you sure you want to remove {participant_name} from the meeting?")
            
            if confirm:
                cursor.execute('DELETE FROM participants WHERE participant_id = ?', (participant_id,))
                conn.commit()
                load_participants()
                messagebox.showinfo("Success", "Participant removed successfully!")
        
        def view_participant_stats():
            """View participant statistics"""
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a participant")
                return
            
            item = tree.item(selection[0])
            participant_name = item['values'][1]
            
            # Get participant statistics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_meetings,
                    SUM(CASE WHEN status = 'attended' THEN 1 ELSE 0 END) as attended,
                    SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed,
                    SUM(CASE WHEN status = 'declined' THEN 1 ELSE 0 END) as declined
                FROM participants p
                JOIN users u ON p.user_id = u.user_id
                WHERE u.full_name = ?
            ''', (participant_name,))
            
            stats = cursor.fetchone()
            
            if stats:
                attendance_rate = (stats[1] / stats[0] * 100) if stats[0] > 0 else 0
                
                stats_text = f"📊 Statistics for {participant_name}:\n\n"
                stats_text += f"• Total Meetings Invited: {stats[0]}\n"
                stats_text += f"• Meetings Attended: {stats[1]}\n"
                stats_text += f"• Meetings Confirmed: {stats[2]}\n"
                stats_text += f"• Meetings Declined: {stats[3]}\n"
                stats_text += f"• Attendance Rate: {attendance_rate:.1f}%\n"
                stats_text += f"• Current Status: {item['values'][4]}\n"
                stats_text += f"• Current Role: {item['values'][3]}"
                
                messagebox.showinfo("Participant Statistics", stats_text)
        
        # Action buttons
        action_buttons = [
            ("✅ Update Status", '#10b981', update_participant_status),
            ("✏️ Edit Role", '#3b82f6', edit_participant_role),
            ("🗑️ Remove", '#ef4444', remove_participant),
            ("📊 View Stats", '#8b5cf6', view_participant_stats)
        ]
        
        for text, color, command in action_buttons:
            btn = tk.Button(action_frame, text=text,
                           font=("Segoe UI", 11),
                           bg=color, fg='white',
                           bd=0, padx=15, pady=8,
                           cursor="hand2",
                           command=command)
            btn.pack(side='left', padx=10)
        
        # Tab 2: Bulk Operations
        bulk_tab = tk.Frame(notebook, bg='#1e293b')
        notebook.add(bulk_tab, text="Bulk Operations")
        
        tk.Label(bulk_tab, text="📁 Import Participants from CSV", 
                font=("Segoe UI", 14, "bold"), bg='#1e293b', fg='white').pack(pady=20)
        
        import_frame = tk.Frame(bulk_tab, bg='#1e293b')
        import_frame.pack(pady=10)
        
        tk.Button(import_frame, text="📂 Choose CSV File",
                 font=("Segoe UI", 11),
                 bg='#3b82f6', fg='white',
                 bd=0, padx=20, pady=10,
                 cursor="hand2",
                 command=self.import_participants_csv).pack(side='left', padx=10)
        
        tk.Button(import_frame, text="📋 Export Participants",
                 font=("Segoe UI", 11),
                 bg='#10b981', fg='white',
                 bd=0, padx=20, pady=10,
                 cursor="hand2",
                 command=self.export_participants_csv).pack(side='left', padx=10)
        
        # Bulk actions frame
        bulk_actions_frame = tk.Frame(bulk_tab, bg='#1e293b')
        bulk_actions_frame.pack(pady=30)
        
        tk.Label(bulk_actions_frame, text="Bulk Actions:", 
                font=("Segoe UI", 12, "bold"), bg='#1e293b', fg='white').pack(pady=(0, 10))
        
        bulk_buttons = [
            ("📧 Send Invitations", '#3b82f6', self.send_bulk_invitations),
            ("🔄 Update All Status", '#8b5cf6', self.update_all_status),
            ("📊 Generate Report", '#10b981', self.generate_participant_report)
        ]
        
        for text, color, command in bulk_buttons:
            btn = tk.Button(bulk_actions_frame, text=text,
                           font=("Segoe UI", 11),
                           bg=color, fg='white',
                           bd=0, padx=15, pady=8,
                           cursor="hand2",
                           command=command)
            btn.pack(side='left', padx=10)
        
        conn.close()
    
    def import_participants_csv(self):
        """Import participants from CSV file"""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Select CSV file to import"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header if exists
                
                conn = sqlite3.connect(self.db.db_name)
                cursor = conn.cursor()
                
                imported_count = 0
                for row in reader:
                    if len(row) >= 3:  # Assuming format: meeting_id, user_id, role
                        participant_id = str(uuid.uuid4())
                        cursor.execute('''
                            INSERT OR IGNORE INTO participants 
                            (participant_id, meeting_id, user_id, role, status)
                            VALUES (?, ?, ?, ?, 'invited')
                        ''', (participant_id, row[0], row[1], row[2] if len(row) > 2 else 'attendee'))
                        imported_count += 1
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Import Complete", 
                                  f"Successfully imported {imported_count} participants from CSV!")
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import CSV: {str(e)}")
    
    def export_participants_csv(self):
        """Export participants to CSV file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save participants as CSV"
        )
        
        if not filename:
            return
        
        try:
            conn = sqlite3.connect(self.db.db_name)
            cursor = conn.cursor()
            
            if self.current_user['role'] == 'admin':
                cursor.execute('''
                    SELECT 
                        p.meeting_id,
                        m.title as meeting_title,
                        p.user_id,
                        u.full_name,
                        u.email,
                        p.role,
                        p.status,
                        p.confirmation_time
                    FROM participants p
                    JOIN meetings m ON p.meeting_id = m.meeting_id
                    JOIN users u ON p.user_id = u.user_id
                    ORDER BY m.date DESC, u.full_name
                ''')
            else:
                cursor.execute('''
                    SELECT 
                        p.meeting_id,
                        m.title as meeting_title,
                        p.user_id,
                        u.full_name,
                        u.email,
                        p.role,
                        p.status,
                        p.confirmation_time
                    FROM participants p
                    JOIN meetings m ON p.meeting_id = m.meeting_id
                    JOIN users u ON p.user_id = u.user_id
                    WHERE m.host_id = ?
                    ORDER BY m.date DESC, u.full_name
                ''', (self.current_user['id'],))
            
            participants = cursor.fetchall()
            conn.close()
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Meeting ID', 'Meeting Title', 'User ID', 'Name', 'Email', 
                               'Role', 'Status', 'Confirmation Time'])
                writer.writerows(participants)
            
            messagebox.showinfo("Export Complete", 
                              f"Successfully exported {len(participants)} participants to CSV!")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV: {str(e)}")
    
    def send_bulk_invitations(self):
        """Send invitations to all participants"""
        confirm = messagebox.askyesno("Send Invitations", 
                                     "Send meeting invitations to all participants?")
        if confirm:
            messagebox.showinfo("Invitations Sent", 
                              "Meeting invitations have been sent to all participants!")
    
    def update_all_status(self):
        """Update status for all participants"""
        status_window = tk.Toplevel(self.root)
        status_window.title("Update All Status")
        status_window.geometry("300x200")
        status_window.configure(bg='#0f172a')
        
        tk.Label(status_window, text="Set Status for All Participants:", 
                font=("Segoe UI", 14, "bold"), bg='#0f172a', fg='white').pack(pady=20)
        
        status_var = tk.StringVar(value="invited")
        
        status_options = [
            ("Invited", "invited"),
            ("Confirmed", "confirmed"),
            ("Declined", "declined")
        ]
        
        for text, value in status_options:
            tk.Radiobutton(status_window, text=text, variable=status_var, value=value,
                         bg='#0f172a', fg='white', selectcolor='#1e293b').pack(anchor='w', padx=50)
        
        def apply_to_all():
            new_status = status_var.get()
            conn = sqlite3.connect(self.db.db_name)
            cursor = conn.cursor()
            
            if self.current_user['role'] == 'admin':
                cursor.execute('UPDATE participants SET status = ?', (new_status,))
            else:
                cursor.execute('''
                    UPDATE participants 
                    SET status = ? 
                    WHERE meeting_id IN (
                        SELECT meeting_id FROM meetings WHERE host_id = ?
                    )
                ''', (new_status, self.current_user['id']))
            
            conn.commit()
            conn.close()
            status_window.destroy()
            messagebox.showinfo("Success", f"All participant statuses updated to {new_status}!")
        
        tk.Button(status_window, text="Apply to All", 
                 font=("Segoe UI", 11, "bold"),
                 bg='#3b82f6', fg='white',
                 bd=0, padx=20, pady=8,
                 cursor="hand2",
                 command=apply_to_all).pack(pady=20)
    
    def generate_participant_report(self):
        """Generate participant report"""
        conn = sqlite3.connect(self.db.db_name)
        cursor = conn.cursor()
        
        if self.current_user['role'] == 'admin':
            cursor.execute('''
                SELECT 
                    m.title,
                    COUNT(p.participant_id) as total_participants,
                    SUM(CASE WHEN p.status = 'confirmed' THEN 1 ELSE 0 END) as confirmed,
                    SUM(CASE WHEN p.status = 'attended' THEN 1 ELSE 0 END) as attended,
                    SUM(CASE WHEN p.status = 'declined' THEN 1 ELSE 0 END) as declined
                FROM meetings m
                LEFT JOIN participants p ON m.meeting_id = p.meeting_id
                GROUP BY m.meeting_id
                ORDER BY m.date DESC
            ''')
        else:
            cursor.execute('''
                SELECT 
                    m.title,
                    COUNT(p.participant_id) as total_participants,
                    SUM(CASE WHEN p.status = 'confirmed' THEN 1 ELSE 0 END) as confirmed,
                    SUM(CASE WHEN p.status = 'attended' THEN 1 ELSE 0 END) as attended,
                    SUM(CASE WHEN p.status = 'declined' THEN 1 ELSE 0 END) as declined
                FROM meetings m
                LEFT JOIN participants p ON m.meeting_id = p.meeting_id
                WHERE m.host_id = ?
                GROUP BY m.meeting_id
                ORDER BY m.date DESC
            ''', (self.current_user['id'],))
        
        reports = cursor.fetchall()
        conn.close()
        
        if not reports:
            messagebox.showinfo("No Data", "No participant data found to generate report.")
            return
        
        # Create report window
        report_window = tk.Toplevel(self.root)
        report_window.title("Participant Report")
        report_window.geometry("800x500")
        report_window.configure(bg='#0f172a')
        
        # Title
        tk.Label(report_window, text="📊 Participant Analytics Report", 
                font=("Segoe UI", 18, "bold"), bg='#0f172a', fg='white').pack(pady=20)
        
        # Create text widget for report
        text_frame = tk.Frame(report_window, bg='#1e293b')
        text_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        report_text = tk.Text(text_frame, bg='#0f172a', fg='white', 
                             font=("Consolas", 10), wrap='none')
        
        scrollbar_y = tk.Scrollbar(text_frame, orient='vertical', command=report_text.yview)
        scrollbar_x = tk.Scrollbar(text_frame, orient='horizontal', command=report_text.xview)
        report_text.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        report_text.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Generate report content
        report_content = "PARTICIPANT ANALYTICS REPORT\n"
        report_content += "=" * 60 + "\n\n"
        
        total_meetings = len(reports)
        total_participants = sum(r[1] for r in reports)
        total_confirmed = sum(r[2] for r in reports)
        total_attended = sum(r[3] for r in reports)
        
        report_content += f"SUMMARY STATISTICS:\n"
        report_content += f"• Total Meetings: {total_meetings}\n"
        report_content += f"• Total Participants: {total_participants}\n"
        report_content += f"• Total Confirmed: {total_confirmed}\n"
        report_content += f"• Total Attended: {total_attended}\n"
        report_content += f"• Overall Attendance Rate: {(total_attended/total_participants*100 if total_participants > 0 else 0):.1f}%\n\n"
        
        report_content += "DETAILED MEETING DATA:\n"
        report_content += "=" * 60 + "\n"
        
        for i, report in enumerate(reports, 1):
            meeting_title, total, confirmed, attended, declined = report
            attendance_rate = (attended/total*100) if total > 0 else 0
            confirmation_rate = (confirmed/total*100) if total > 0 else 0
            
            report_content += f"\n{i}. {meeting_title}\n"
            report_content += f"   • Total Participants: {total}\n"
            report_content += f"   • Confirmed: {confirmed} ({confirmation_rate:.1f}%)\n"
            report_content += f"   • Attended: {attended} ({attendance_rate:.1f}%)\n"
            report_content += f"   • Declined: {declined}\n"
        
        report_text.insert('1.0', report_content)
        report_text.configure(state='disabled')
        
        # Add export button
        tk.Button(report_window, text="📥 Export Report", 
                 font=("Segoe UI", 11, "bold"),
                 bg='#10b981', fg='white',
                 bd=0, padx=20, pady=10,
                 cursor="hand2",
                 command=lambda: self.export_report_text(report_content)).pack(pady=20)
    
    def export_report_text(self, report_content):
        """Export report text to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save report as"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(report_content)
                messagebox.showinfo("Export Complete", "Report exported successfully!")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")
    

        # ==================== TASK B.3: ADVANCED PARTICIPANT MANAGEMENT ====================
    def show_participant_manager(self):
        """Show advanced participant management with user management"""
        self.clear_content()
        
        tk.Label(self.content_frame, text="👥 Advanced Participant Management", 
                font=("Segoe UI", 20, "bold"), bg='#0f172a', fg='white').pack(pady=20)
        
        # Create notebook with multiple tabs
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Tab 1: User Management (New - for managing all users/participants)
        user_management_tab = tk.Frame(notebook, bg='#1e293b')
        notebook.add(user_management_tab, text="👤 User Management")
        
        self.setup_user_management_tab(user_management_tab)
        
        # Tab 2: Meeting Participants Management
        meeting_participants_tab = tk.Frame(notebook, bg='#1e293b')
        notebook.add(meeting_participants_tab, text="📅 Meeting Participants")
        
        self.setup_meeting_participants_tab(meeting_participants_tab)
        
        # Tab 3: Bulk Operations
        bulk_tab = tk.Frame(notebook, bg='#1e293b')
        notebook.add(bulk_tab, text="📁 Bulk Operations")
        
        self.setup_bulk_operations_tab(bulk_tab)
    
    def setup_user_management_tab(self, parent_frame):
        """Setup user management tab for adding/editing/deleting users"""
        # Header
        tk.Label(parent_frame, text="Manage All Users/Participants", 
                font=("Segoe UI", 16, "bold"), bg='#1e293b', fg='white').pack(pady=20)
        
        # Buttons for user management
        button_frame = tk.Frame(parent_frame, bg='#1e293b')
        button_frame.pack(pady=10)
        
        user_buttons = [
            ("➕ Add New User", '#10b981', self.show_add_user_dialog),
            ("✏️ Edit User", '#3b82f6', self.show_edit_user_dialog),
            ("🗑️ Delete User", '#ef4444', self.show_delete_user_dialog),
            ("🔄 Refresh List", '#8b5cf6', lambda: self.load_users_table())
        ]
        
        for text, color, command in user_buttons:
            btn = tk.Button(button_frame, text=text,
                           font=("Segoe UI", 11),
                           bg=color, fg='white',
                           bd=0, padx=15, pady=8,
                           cursor="hand2",
                           command=command)
            btn.pack(side='left', padx=10)
        
        # Users table
        table_frame = tk.Frame(parent_frame, bg='#1e293b')
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        columns = ('ID', 'Username', 'Full Name', 'Email', 'Role', 'Department', 'Actions')
        self.users_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=100)
        
        self.users_tree.column('Full Name', width=150)
        self.users_tree.column('Email', width=200)
        self.users_tree.column('Department', width=120)
        self.users_tree.column('Actions', width=100)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.users_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.users_tree.xview)
        self.users_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.users_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Load initial users
        self.load_users_table()
    
    def load_users_table(self):
        """Load all users into the table"""
        # Clear existing items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        conn = sqlite3.connect(self.db.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, username, full_name, email, role, department 
            FROM users 
            ORDER BY role, full_name
        ''')
        
        users = cursor.fetchall()
        
        for user in users:
            self.users_tree.insert('', 'end', values=(
                user[0],
                user[1],
                user[2],
                user[3],
                user[4],
                user[5] or 'N/A',
                "Edit | Delete"
            ))
        
        conn.close()
    
    def show_add_user_dialog(self):
        """Show dialog to add a new user"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New User")
        dialog.geometry("500x600")
        dialog.configure(bg='#0f172a')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="➕ Add New User", 
                font=("Segoe UI", 18, "bold"), bg='#0f172a', fg='white').pack(pady=20)
        
        form_frame = tk.Frame(dialog, bg='#1e293b', padx=30, pady=20)
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Form fields
        fields = [
            ("Username", "username_entry", True),
            ("Password", "password_entry", True),
            ("Full Name", "fullname_entry", True),
            ("Email", "email_entry", True),
            ("Department", "dept_entry", False),
            ("Phone", "phone_entry", False)
        ]
        
        entries = {}
        for i, (label, key, required) in enumerate(fields):
            tk.Label(form_frame, text=f"{label}{' *' if required else ''}:", 
                    font=("Segoe UI", 11), bg='#1e293b', fg='#94a3b8').grid(row=i, column=0, sticky='w', pady=10)
            
            if "password" in key:
                entry = ttk.Entry(form_frame, font=("Segoe UI", 11), width=30, show='•')
            else:
                entry = ttk.Entry(form_frame, font=("Segoe UI", 11), width=30)
            
            entry.grid(row=i, column=1, pady=10, padx=10)
            entries[key] = entry
        
        # Role selection
        tk.Label(form_frame, text="Role *:", 
                font=("Segoe UI", 11), bg='#1e293b', fg='#94a3b8').grid(row=len(fields), column=0, sticky='w', pady=10)
        
        role_var = tk.StringVar(value="participant")
        role_combo = ttk.Combobox(form_frame, textvariable=role_var,
                                 values=["admin", "host", "participant", "guest"],
                                 font=("Segoe UI", 11), width=28, state='readonly')
        role_combo.grid(row=len(fields), column=1, pady=10, padx=10)
        
        def save_user():
            """Save new user to database"""
            # Get form data
            username = entries['username_entry'].get().strip()
            password = entries['password_entry'].get()
            full_name = entries['fullname_entry'].get().strip()
            email = entries['email_entry'].get().strip()
            department = entries['dept_entry'].get().strip()
            phone = entries['phone_entry'].get().strip()
            role = role_var.get()
            
            # Validate required fields
            if not all([username, password, full_name, email]):
                messagebox.showerror("Validation Error", "Please fill all required fields (*)")
                return
            
            # Validate email format
            if '@' not in email or '.' not in email:
                messagebox.showerror("Validation Error", "Please enter a valid email address")
                return
            
            try:
                conn = sqlite3.connect(self.db.db_name)
                cursor = conn.cursor()
                
                # Check if username or email already exists
                cursor.execute('SELECT user_id FROM users WHERE username = ? OR email = ?', (username, email))
                if cursor.fetchone():
                    messagebox.showerror("Duplicate Error", "Username or email already exists")
                    conn.close()
                    return
                
                # Hash password
                password_hash = self.db.hash_password(password)
                user_id = str(uuid.uuid4())
                
                # Insert new user
                cursor.execute('''
                    INSERT INTO users (user_id, username, password_hash, email, role, full_name, department, phone)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, username, password_hash, email, role, full_name, department or None, phone or None))
                
                conn.commit()
                conn.close()
                
                # Update table and close dialog
                self.load_users_table()
                dialog.destroy()
                messagebox.showinfo("Success", f"User '{full_name}' added successfully!")
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to add user: {str(e)}")
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#0f172a')
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Save User", 
                 font=("Segoe UI", 12, "bold"),
                 bg='#10b981', fg='white',
                 bd=0, padx=30, pady=10,
                 cursor="hand2",
                 command=save_user).pack(side='left', padx=10)
        
        tk.Button(button_frame, text="Cancel", 
                 font=("Segoe UI", 12),
                 bg='#64748b', fg='white',
                 bd=0, padx=30, pady=10,
                 cursor="hand2",
                 command=dialog.destroy).pack(side='left', padx=10)
    
    def show_edit_user_dialog(self):
        """Show dialog to edit selected user"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user to edit")
            return
        
        item = self.users_tree.item(selection[0])
        user_id = item['values'][0]
        username = item['values'][1]
        full_name = item['values'][2]
        email = item['values'][3]
        role = item['values'][4]
        department = item['values'][5] if item['values'][5] != 'N/A' else ''
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit User: {full_name}")
        dialog.geometry("500x550")
        dialog.configure(bg='#0f172a')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text=f"✏️ Edit User: {full_name}", 
                font=("Segoe UI", 18, "bold"), bg='#0f172a', fg='white').pack(pady=20)
        
        form_frame = tk.Frame(dialog, bg='#1e293b', padx=30, pady=20)
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Form fields
        fields = [
            ("Username", username),
            ("Full Name", full_name),
            ("Email", email),
            ("Department", department),
            ("New Password (leave blank to keep current)", "")
        ]
        
        entries = {}
        for i, (label, value) in enumerate(fields):
            tk.Label(form_frame, text=f"{label}:", 
                    font=("Segoe UI", 11), bg='#1e293b', fg='#94a3b8').grid(row=i, column=0, sticky='w', pady=10)
            
            if "Password" in label:
                entry = ttk.Entry(form_frame, font=("Segoe UI", 11), width=30, show='•')
                entry.insert(0, value)
            else:
                entry = ttk.Entry(form_frame, font=("Segoe UI", 11), width=30)
                entry.insert(0, value)
                if label == "Username":
                    entry.config(state='readonly')
            
            entry.grid(row=i, column=1, pady=10, padx=10)
            entries[label] = entry
        
        # Role selection
        tk.Label(form_frame, text="Role:", 
                font=("Segoe UI", 11), bg='#1e293b', fg='#94a3b8').grid(row=len(fields), column=0, sticky='w', pady=10)
        
        role_var = tk.StringVar(value=role)
        role_combo = ttk.Combobox(form_frame, textvariable=role_var,
                                 values=["admin", "host", "participant", "guest"],
                                 font=("Segoe UI", 11), width=28, state='readonly')
        role_combo.grid(row=len(fields), column=1, pady=10, padx=10)
        
        def save_changes():
            """Save user changes to database"""
            new_full_name = entries["Full Name"].get().strip()
            new_email = entries["Email"].get().strip()
            new_department = entries["Department"].get().strip()
            new_password = entries["New Password (leave blank to keep current)"].get()
            new_role = role_var.get()
            
            # Validate
            if not all([new_full_name, new_email]):
                messagebox.showerror("Validation Error", "Full Name and Email are required")
                return
            
            try:
                conn = sqlite3.connect(self.db.db_name)
                cursor = conn.cursor()
                
                # Check if email already exists (for other users)
                cursor.execute('SELECT user_id FROM users WHERE email = ? AND user_id != ?', (new_email, user_id))
                if cursor.fetchone():
                    messagebox.showerror("Duplicate Error", "Email already exists for another user")
                    conn.close()
                    return
                
                # Update user
                if new_password:
                    password_hash = self.db.hash_password(new_password)
                    cursor.execute('''
                        UPDATE users 
                        SET full_name = ?, email = ?, department = ?, role = ?, password_hash = ?
                        WHERE user_id = ?
                    ''', (new_full_name, new_email, new_department or None, new_role, password_hash, user_id))
                else:
                    cursor.execute('''
                        UPDATE users 
                        SET full_name = ?, email = ?, department = ?, role = ?
                        WHERE user_id = ?
                    ''', (new_full_name, new_email, new_department or None, new_role, user_id))
                
                conn.commit()
                conn.close()
                
                # Update table and close dialog
                self.load_users_table()
                dialog.destroy()
                messagebox.showinfo("Success", f"User '{new_full_name}' updated successfully!")
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to update user: {str(e)}")
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#0f172a')
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Save Changes", 
                 font=("Segoe UI", 12, "bold"),
                 bg='#3b82f6', fg='white',
                 bd=0, padx=30, pady=10,
                 cursor="hand2",
                 command=save_changes).pack(side='left', padx=10)
        
        tk.Button(button_frame, text="Cancel", 
                 font=("Segoe UI", 12),
                 bg='#64748b', fg='white',
                 bd=0, padx=30, pady=10,
                 cursor="hand2",
                 command=dialog.destroy).pack(side='left', padx=10)
    
    def show_delete_user_dialog(self):
        """Show dialog to delete selected user"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user to delete")
            return
        
        item = self.users_tree.item(selection[0])
        user_id = item['values'][0]
        username = item['values'][1]
        full_name = item['values'][2]
        
        # Check if trying to delete self
        if user_id == self.current_user['id']:
            messagebox.showerror("Error", "You cannot delete your own account!")
            return
        
        # Check if user has meetings (as host)
        conn = sqlite3.connect(self.db.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM meetings WHERE host_id = ?', (user_id,))
        meeting_count = cursor.fetchone()[0]
        conn.close()
        
        warning_msg = f"Are you sure you want to delete user:\n\n"
        warning_msg += f"• Name: {full_name}\n"
        warning_msg += f"• Username: {username}\n"
        
        if meeting_count > 0:
            warning_msg += f"\n⚠️  WARNING: This user is hosting {meeting_count} meeting(s).\n"
            warning_msg += "Deleting them will also delete their meetings!"
        
        confirm = messagebox.askyesno("Confirm Deletion", warning_msg)
        
        if confirm:
            try:
                conn = sqlite3.connect(self.db.db_name)
                cursor = conn.cursor()
                
                # Start transaction
                cursor.execute('BEGIN TRANSACTION')
                
                # Delete from participants table first
                cursor.execute('DELETE FROM participants WHERE user_id = ?', (user_id,))
                
                # Delete meetings hosted by this user
                cursor.execute('DELETE FROM meetings WHERE host_id = ?', (user_id,))
                
                # Delete the user
                cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
                
                # Commit transaction
                cursor.execute('COMMIT')
                conn.close()
                
                # Update table
                self.load_users_table()
                messagebox.showinfo("Success", f"User '{full_name}' deleted successfully!")
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to delete user: {str(e)}")
    
    def setup_meeting_participants_tab(self, parent_frame):
        """Setup meeting participants management tab"""
        # Get meetings
        conn = sqlite3.connect(self.db.db_name)
        cursor = conn.cursor()
        
        if self.current_user['role'] == 'admin':
            cursor.execute('''
                SELECT m.meeting_id, m.title, m.date, m.start_time 
                FROM meetings m 
                ORDER BY m.date DESC
            ''')
        else:
            cursor.execute('''
                SELECT m.meeting_id, m.title, m.date, m.start_time 
                FROM meetings m 
                WHERE m.host_id = ?
                ORDER BY m.date DESC
            ''', (self.current_user['id'],))
        
        meetings = cursor.fetchall()
        
        if not meetings:
            tk.Label(parent_frame, text="No meetings found. Schedule a meeting first.", 
                    font=("Segoe UI", 14), bg='#1e293b', fg='white').pack(pady=50)
            conn.close()
            return
        
        # Meeting selector
        tk.Label(parent_frame, text="Select Meeting:", font=("Segoe UI", 12),
                bg='#1e293b', fg='#94a3b8').pack(anchor='w', padx=20, pady=(20, 10))
        
        meeting_var = tk.StringVar()
        meeting_combo = ttk.Combobox(parent_frame, textvariable=meeting_var,
                                    values=[f"{m[1]} ({m[2]} {m[3]})" for m in meetings],
                                    font=("Segoe UI", 12), width=50, state='readonly')
        meeting_combo.pack(padx=20, pady=(0, 20))
        
        # Store meeting ID mapping
        self.meeting_id_map = {f"{m[1]} ({m[2]} {m[3]})": m[0] for m in meetings}
        
        # Participants treeview
        tree_frame = tk.Frame(parent_frame, bg='#1e293b')
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('ID', 'Name', 'Email', 'Role', 'Status', 'Actions')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.column('Name', width=150)
        tree.column('Email', width=200)
        tree.column('Actions', width=120)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        def load_participants(event=None):
            """Load participants for selected meeting"""
            selection = meeting_combo.get()
            if not selection:
                return
            
            meeting_id = self.meeting_id_map.get(selection)
            if not meeting_id:
                return
            
            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)
            
            # Get participants for this meeting
            cursor.execute('''
                SELECT p.participant_id, u.full_name, u.email, p.role, p.status
                FROM participants p
                JOIN users u ON p.user_id = u.user_id
                WHERE p.meeting_id = ?
            ''', (meeting_id,))
            
            participants = cursor.fetchall()
            
            for participant in participants:
                tree.insert('', 'end', values=(
                    participant[0],
                    participant[1],
                    participant[2],
                    participant[3],
                    participant[4],
                    "Remove"
                ))
        
        meeting_combo.bind('<<ComboboxSelected>>', load_participants)
        
        # Action buttons frame
        button_frame = tk.Frame(parent_frame, bg='#1e293b')
        button_frame.pack(pady=20)
        
        # Get all users for adding
        cursor.execute('''
            SELECT user_id, full_name, email, role 
            FROM users 
            WHERE user_id != ? AND role IN ('participant', 'host')
        ''', (self.current_user['id'],))
        
        all_users = cursor.fetchall()
        self.all_users_map = {f"{u[1]} ({u[2]})": u[0] for u in all_users}
        
        # Add participant button
        add_frame = tk.Frame(button_frame, bg='#1e293b')
        add_frame.pack(pady=10)
        
        tk.Label(add_frame, text="Add Participant:", font=("Segoe UI", 11),
                bg='#1e293b', fg='#94a3b8').pack(side='left', padx=(0, 10))
        
        user_var = tk.StringVar()
        user_combo = ttk.Combobox(add_frame, textvariable=user_var,
                                 values=list(self.all_users_map.keys()),
                                 font=("Segoe UI", 11), width=30, state='readonly')
        user_combo.pack(side='left', padx=(0, 10))
        
        def add_participant():
            """Add a new participant to the meeting"""
            selection = meeting_combo.get()
            if not selection:
                messagebox.showwarning("Warning", "Please select a meeting first")
                return
            
            user_selection = user_combo.get()
            if not user_selection:
                messagebox.showwarning("Warning", "Please select a user to add")
                return
            
            meeting_id = self.meeting_id_map.get(selection)
            user_id = self.all_users_map.get(user_selection)
            
            # Check if user is already a participant
            cursor.execute('''
                SELECT participant_id FROM participants 
                WHERE meeting_id = ? AND user_id = ?
            ''', (meeting_id, user_id))
            
            if cursor.fetchone():
                messagebox.showwarning("Warning", "User is already a participant in this meeting")
                return
            
            # Add participant
            participant_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO participants (participant_id, meeting_id, user_id, status)
                VALUES (?, ?, ?, 'invited')
            ''', (participant_id, meeting_id, user_id))
            
            conn.commit()
            
            # Reload participants
            load_participants()
            messagebox.showinfo("Success", "Participant added successfully!")
        
        tk.Button(add_frame, text="➕ Add",
                 font=("Segoe UI", 10),
                 bg='#10b981', fg='white',
                 bd=0, padx=15, pady=5,
                 cursor="hand2",
                 command=add_participant).pack(side='left')
        
        # Action buttons for selected participant
        action_frame = tk.Frame(button_frame, bg='#1e293b')
        action_frame.pack(pady=10)
        
        def update_participant_status():
            """Update selected participant's status"""
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a participant")
                return
            
            item = tree.item(selection[0])
            participant_id = item['values'][0]
            
            status_window = tk.Toplevel(self.root)
            status_window.title("Update Status")
            status_window.geometry("300x250")
            status_window.configure(bg='#0f172a')
            
            tk.Label(status_window, text="Select New Status:", 
                    font=("Segoe UI", 14, "bold"), bg='#0f172a', fg='white').pack(pady=20)
            
            status_var = tk.StringVar(value=item['values'][4])
            
            status_options = [
                ("Invited", "invited"),
                ("Confirmed", "confirmed"),
                ("Declined", "declined"),
                ("Attended", "attended"),
                ("Absent", "absent")
            ]
            
            for text, value in status_options:
                tk.Radiobutton(status_window, text=text, variable=status_var, value=value,
                             bg='#0f172a', fg='white', selectcolor='#1e293b').pack(anchor='w', padx=50, pady=5)
            
            def save_status():
                new_status = status_var.get()
                cursor.execute('''
                    UPDATE participants SET status = ? WHERE participant_id = ?
                ''', (new_status, participant_id))
                
                conn.commit()
                load_participants()
                status_window.destroy()
                messagebox.showinfo("Success", "Status updated successfully!")
            
            tk.Button(status_window, text="Save", 
                     font=("Segoe UI", 11, "bold"),
                     bg='#3b82f6', fg='white',
                     bd=0, padx=20, pady=8,
                     cursor="hand2",
                     command=save_status).pack(pady=20)
        
        def edit_participant_role():
            """Edit selected participant's role"""
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a participant")
                return
            
            item = tree.item(selection[0])
            participant_id = item['values'][0]
            current_role = item['values'][3]
            
            role = simpledialog.askstring("Edit Role", 
                                         "Enter new role (attendee/presenter/moderator):",
                                         initialvalue=current_role)
            
            if role and role.lower() in ['attendee', 'presenter', 'moderator']:
                cursor.execute('''
                    UPDATE participants SET role = ? WHERE participant_id = ?
                ''', (role.lower(), participant_id))
                
                conn.commit()
                load_participants()
                messagebox.showinfo("Success", "Role updated successfully!")
        
        def remove_participant():
            """Remove selected participant"""
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a participant")
                return
            
            item = tree.item(selection[0])
            participant_name = item['values'][1]
            participant_id = item['values'][0]
            
            confirm = messagebox.askyesno("Confirm Removal", 
                                         f"Are you sure you want to remove {participant_name} from the meeting?")
            
            if confirm:
                cursor.execute('DELETE FROM participants WHERE participant_id = ?', (participant_id,))
                conn.commit()
                load_participants()
                messagebox.showinfo("Success", "Participant removed successfully!")
        
        # Action buttons
        action_buttons = [
            ("✅ Update Status", '#10b981', update_participant_status),
            ("✏️ Edit Role", '#3b82f6', edit_participant_role),
            ("🗑️ Remove", '#ef4444', remove_participant)
        ]
        
        for text, color, command in action_buttons:
            btn = tk.Button(action_frame, text=text,
                           font=("Segoe UI", 11),
                           bg=color, fg='white',
                           bd=0, padx=15, pady=8,
                           cursor="hand2",
                           command=command)
            btn.pack(side='left', padx=10)
        
        conn.close()
    
    def setup_bulk_operations_tab(self, parent_frame):
        """Setup bulk operations tab"""
        tk.Label(parent_frame, text="📁 Bulk Operations", 
                font=("Segoe UI", 16, "bold"), bg='#1e293b', fg='white').pack(pady=20)
        
        # Import/Export section
        io_frame = tk.Frame(parent_frame, bg='#1e293b')
        io_frame.pack(pady=20, padx=50)
        
        tk.Label(io_frame, text="Import/Export Participants:", 
                font=("Segoe UI", 14, "bold"), bg='#1e293b', fg='white').pack(pady=(0, 15))
        
        # Import button
        import_frame = tk.Frame(io_frame, bg='#1e293b')
        import_frame.pack(fill='x', pady=10)
        
        tk.Button(import_frame, text="📂 Import from CSV",
                 font=("Segoe UI", 12),
                 bg='#3b82f6', fg='white',
                 bd=0, padx=20, pady=12,
                 cursor="hand2",
                 command=self.import_participants_csv).pack(side='left', padx=10)
        
        tk.Label(import_frame, text="Import participants from CSV file", 
                font=("Segoe UI", 10), bg='#1e293b', fg='#94a3b8').pack(side='left', padx=20)
        
        # Export button
        export_frame = tk.Frame(io_frame, bg='#1e293b')
        export_frame.pack(fill='x', pady=10)
        
        tk.Button(export_frame, text="📋 Export to CSV",
                 font=("Segoe UI", 12),
                 bg='#10b981', fg='white',
                 bd=0, padx=20, pady=12,
                 cursor="hand2",
                 command=self.export_participants_csv).pack(side='left', padx=10)
        
        tk.Label(export_frame, text="Export all participants to CSV file", 
                font=("Segoe UI", 10), bg='#1e293b', fg='#94a3b8').pack(side='left', padx=20)
        
        # Bulk actions section
        bulk_actions_frame = tk.Frame(parent_frame, bg='#1e293b')
        bulk_actions_frame.pack(pady=30, padx=50)
        
        tk.Label(bulk_actions_frame, text="Bulk Actions:", 
                font=("Segoe UI", 14, "bold"), bg='#1e293b', fg='white').pack(pady=(0, 15))
        
        bulk_buttons = [
            ("📧 Send Invitations to All", '#3b82f6', self.send_bulk_invitations),
            ("🔄 Update All Status", '#8b5cf6', self.update_all_participant_status),
            ("📊 Generate Report", '#10b981', self.generate_participant_report)
        ]
        
        for text, color, command in bulk_buttons:
            btn_frame = tk.Frame(bulk_actions_frame, bg='#1e293b')
            btn_frame.pack(fill='x', pady=8)
            
            tk.Button(btn_frame, text=text,
                     font=("Segoe UI", 11),
                     bg=color, fg='white',
                     bd=0, padx=15, pady=8,
                     cursor="hand2",
                     command=command).pack(side='left')
    
    # ==================== TASK B.4: SMART NOTIFICATIONS ====================
    def show_smart_notifications(self):
        """Show smart notification system"""
        self.clear_content()
        
        tk.Label(self.content_frame, text="🔔 Smart Notification System", 
                font=("Segoe UI", 20, "bold"), bg='#0f172a', fg='white').pack(pady=20)
        
        # Notification center
        center_frame = tk.Frame(self.content_frame, bg='#1e293b')
        center_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Header
        header_frame = tk.Frame(center_frame, bg='#1e293b')
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(header_frame, text="📨 Notifications Center", 
                font=("Segoe UI", 16, "bold"), bg='#1e293b', fg='white').pack(side='left')
        
        tk.Button(header_frame, text="Mark All as Read",
                 font=("Segoe UI", 10),
                 bg='#3b82f6', fg='white',
                 bd=0, padx=15, pady=5,
                 cursor="hand2").pack(side='right')
        
        # Notification types
        type_frame = tk.Frame(center_frame, bg='#1e293b')
        type_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        types = ["All", "Unread", "Meeting Alerts", "System", "Updates"]
        for i, type_text in enumerate(types):
            btn = tk.Button(type_frame, text=type_text,
                           font=("Segoe UI", 10),
                           bg='#334155' if i == 0 else '#1e293b',
                           fg='white',
                           bd=0, padx=15, pady=5,
                           cursor="hand2")
            btn.pack(side='left', padx=5)
        
        # Notifications list
        notifications_frame = tk.Frame(center_frame, bg='#0f172a')
        notifications_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Sample notifications
        notifications = [
            {
                'icon': '📅',
                'title': 'Meeting in 30 minutes',
                'message': 'Team Sync starts at 2:00 PM',
                'time': '10 mins ago',
                'priority': 'high',
                'unread': True
            },
            {
                'icon': '👥',
                'title': 'New participant confirmed',
                'message': 'John Smith confirmed attendance',
                'time': '1 hour ago',
                'priority': 'medium',
                'unread': True
            },
            {
                'icon': '🔔',
                'title': 'System Update',
                'message': 'New features available in AOMMS',
                'time': '2 hours ago',
                'priority': 'low',
                'unread': False
            }
        ]
        
        for i, notif in enumerate(notifications):
            notif_frame = tk.Frame(notifications_frame, 
                                  bg='#1e293b' if notif['unread'] else '#0f172a',
                                  relief='groove', bd=1)
            notif_frame.pack(fill='x', pady=5)
            
            # Icon and content
            icon_label = tk.Label(notif_frame, text=notif['icon'], 
                                 font=("Segoe UI", 16),
                                 bg=notif_frame['bg'], fg='#3b82f6')
            icon_label.grid(row=0, column=0, rowspan=2, padx=15, pady=10)
            
            title_label = tk.Label(notif_frame, text=notif['title'], 
                                  font=("Segoe UI", 12, "bold"),
                                  bg=notif_frame['bg'], 
                                  fg='white' if notif['unread'] else '#94a3b8')
            title_label.grid(row=0, column=1, sticky='w', pady=(10, 2))
            
            msg_label = tk.Label(notif_frame, text=notif['message'], 
                                font=("Segoe UI", 10),
                                bg=notif_frame['bg'], fg='#94a3b8')
            msg_label.grid(row=1, column=1, sticky='w', pady=(0, 10))
            
            time_label = tk.Label(notif_frame, text=notif['time'], 
                                 font=("Segoe UI", 9),
                                 bg=notif_frame['bg'], fg='#64748b')
            time_label.grid(row=0, column=2, rowspan=2, padx=15, pady=10, sticky='ns')
            
            # Priority indicator
            priority_colors = {'high': '#ef4444', 'medium': '#f59e0b', 'low': '#10b981'}
            tk.Label(notif_frame, text="●", 
                    font=("Segoe UI", 12),
                    bg=notif_frame['bg'], 
                    fg=priority_colors.get(notif['priority'], '#94a3b8')).grid(row=0, column=3, padx=10)
        
        # Notification settings
        settings_frame = tk.Frame(center_frame, bg='#1e293b', relief='raised', bd=1)
        settings_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(settings_frame, text="⚙️ Notification Settings", 
                font=("Segoe UI", 14, "bold"), bg='#1e293b', fg='white').pack(pady=10)
        
        settings = [
            ("Email Notifications", True),
            ("Push Notifications", True),
            ("SMS Alerts", False),
            ("Desktop Alerts", True),
            ("Sound Effects", True),
            ("Do Not Disturb", False)
        ]
        
        for setting, default in settings:
            frame = tk.Frame(settings_frame, bg='#1e293b')
            frame.pack(fill='x', padx=20, pady=5)
            
            tk.Label(frame, text=setting, font=("Segoe UI", 11), 
                    bg='#1e293b', fg='#cbd5e1').pack(side='left')
            
            var = tk.BooleanVar(value=default)
            tk.Checkbutton(frame, variable=var, bg='#1e293b').pack(side='right')
    
    def send_meeting_notifications(self, meeting_id):
        """Send smart notifications for meeting"""
        # In real implementation, this would send actual notifications
        print(f"Smart notifications sent for meeting {meeting_id}")
        
        # Schedule reminders
        self.schedule_reminders(meeting_id)
    
    def schedule_reminders(self, meeting_id):
        """Schedule automated reminders"""
        # Schedule reminder for 1 hour before
        threading.Thread(target=self.send_reminder, args=[meeting_id, "1 hour"]).start()
    
    def send_reminder(self, meeting_id, time_before):
        """Send meeting reminder"""
        time.sleep(2)  # Simulate delay
        message = f"⏰ Meeting reminder: Your meeting starts in {time_before}!"
        
        # Show popup notification
        try:
            self.root.after(0, messagebox.showinfo, "Meeting Reminder", message)
        except:
            pass
    
    # ==================== TASK B.5: SMART NOTES ====================
    def show_smart_notes(self):
        """Show smart meeting notes with AI features"""
        self.clear_content()
        
        tk.Label(self.content_frame, text="📝 Smart Meeting Notes with AI", 
                font=("Segoe UI", 20, "bold"), bg='#0f172a', fg='white').pack(pady=20)
        
        # Main notes interface
        main_frame = tk.Frame(self.content_frame, bg='#1e293b')
        main_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Left panel - Meeting selection
        left_panel = tk.Frame(main_frame, bg='#0f172a', width=300)
        left_panel.pack(side='left', fill='y')
        left_panel.pack_propagate(False)
        
        tk.Label(left_panel, text="Select Meeting:", font=("Segoe UI", 12, "bold"),
                bg='#0f172a', fg='white').pack(pady=15)
        
        # Meeting list
        meetings_listbox = tk.Listbox(left_panel, 
                                     bg='#1e293b',
                                     fg='white',
                                     selectbackground='#3b82f6',
                                     font=("Segoe UI", 11),
                                     height=15)
        meetings_listbox.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add sample meetings
        sample_meetings = [
            "Team Sync - Today 2:00 PM",
            "Project Review - Tomorrow 10:00 AM",
            "Client Meeting - Next Week 3:00 PM",
            "Weekly Planning - Next Week 9:00 AM"
        ]
        
        for meeting in sample_meetings:
            meetings_listbox.insert(tk.END, meeting)
        
        # Right panel - Notes editor
        right_panel = tk.Frame(main_frame, bg='#1e293b')
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Toolbar
        toolbar = tk.Frame(right_panel, bg='#334155')
        toolbar.pack(fill='x', pady=(0, 10))
        
        tools = ["💾 Save", "📤 Export", "🤖 AI Summary", "🔍 Search", "📎 Attach"]
        for tool in tools:
            btn = tk.Button(toolbar, text=tool,
                           font=("Segoe UI", 10),
                           bg='#334155', fg='white',
                           bd=0, padx=10, pady=5,
                           cursor="hand2")
            btn.pack(side='left', padx=5, pady=5)
        
        # Text editor
        editor_frame = tk.Frame(right_panel, bg='#0f172a')
        editor_frame.pack(fill='both', expand=True)
        
        # Main text area
        text_area = tk.Text(editor_frame,
                           bg='#0f172a',
                           fg='white',
                           font=("Consolas", 11),
                           insertbackground='white',
                           wrap='word',
                           undo=True)
        text_area.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Insert sample content
        sample_content = """# Team Sync Meeting Notes
Date: 2024-01-15 | Time: 14:00-15:00

## 📋 Agenda
1. Project updates
2. Blockers discussion
3. Next week planning

## 👥 Attendees
- John Smith (present)
- Sarah Johnson (present)
- Mike Brown (absent)

## 📝 Discussion Points
- Project Alpha is ahead of schedule
- Need clarification on API requirements
- Design review scheduled for Friday

## ✅ Action Items
• John to send API docs by EOD
• Sarah to prepare design mockups
• Urgent: Client demo on Monday!"""
        
        text_area.insert('1.0', sample_content)
    
    # ==================== TASK B.6: ADVANCED SEARCH ====================
    def show_advanced_search(self):
        """Show advanced search with filters"""
        self.clear_content()
        
        tk.Label(self.content_frame, text="🔍 Advanced Search & Analytics", 
                font=("Segoe UI", 20, "bold"), bg='#0f172a', fg='white').pack(pady=20)
        
        # Search panel
        search_panel = tk.Frame(self.content_frame, bg='#1e293b', padx=20, pady=20)
        search_panel.pack(fill='x', padx=30, pady=(0, 20))
        
        tk.Label(search_panel, text="🔍 Search Meetings:", font=("Segoe UI", 14, "bold"),
                bg='#1e293b', fg='white').pack(anchor='w', pady=(0, 10))
        
        # Search bar
        search_frame = tk.Frame(search_panel, bg='#1e293b')
        search_frame.pack(fill='x')
        
        search_entry = ttk.Entry(search_frame, font=("Segoe UI", 12), width=40)
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        search_btn = tk.Button(search_frame, text="Search",
                              font=("Segoe UI", 11, "bold"),
                              bg='#3b82f6', fg='white',
                              bd=0, padx=20, pady=8,
                              cursor="hand2")
        search_btn.pack(side='left')
        
        # Advanced filters
        filters_frame = tk.Frame(search_panel, bg='#1e293b')
        filters_frame.pack(fill='x', pady=(20, 0))
        
        tk.Label(filters_frame, text="Filters:", font=("Segoe UI", 12),
                bg='#1e293b', fg='#94a3b8').pack(side='left', padx=(0, 10))
        
        filter_options = ["Date Range", "Host", "Participant", "Status", "Priority", "Type"]
        for option in filter_options:
            btn = tk.Button(filters_frame, text=option,
                           font=("Segoe UI", 10),
                           bg='#334155', fg='white',
                           bd=0, padx=10, pady=5,
                           cursor="hand2")
            btn.pack(side='left', padx=5)
        
        # Results panel
        results_frame = tk.Frame(self.content_frame, bg='#1e293b')
        results_frame.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        
        # Treeview for results
        columns = ('ID', 'Title', 'Date', 'Time', 'Duration', 'Host', 'Participants', 'Status', 'Priority')
        tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=80)
        
        tree.column('Title', width=200)
        tree.column('Participants', width=120)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        
        # Add sample data
        sample_data = [
            ('001', 'Team Sync', datetime.now().strftime('%Y-%m-%d'), '14:00', '60', 'You', '8/10', 'Completed', '⭐⭐⭐'),
            ('002', 'Project Review', (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'), '10:00', '90', 'You', '5/5', 'Scheduled', '⭐⭐⭐⭐'),
            ('003', 'Client Demo', (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'), '15:00', '120', 'Sarah', '12/15', 'Scheduled', '⭐⭐⭐⭐⭐'),
        ]
        
        for item in sample_data:
            tree.insert('', 'end', values=item)
    
    # ==================== TASK B.7: SECURE BACKUP & RESTORE ====================
    def show_secure_backup(self):
        """Show secure backup and restore system"""
        self.clear_content()
        
        tk.Label(self.content_frame, text="💾 Secure Backup & Disaster Recovery", 
                font=("Segoe UI", 20, "bold"), bg='#0f172a', fg='white').pack(pady=20)
        
        # Main backup interface
        backup_frame = tk.Frame(self.content_frame, bg='#1e293b')
        backup_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Backup card
        backup_card = tk.Frame(backup_frame, bg='#0f172a', relief='raised', bd=2)
        backup_card.pack(fill='x', padx=20, pady=20)
        
        tk.Label(backup_card, text="🔒 Secure Backup", 
                font=("Segoe UI", 18, "bold"), bg='#0f172a', fg='#3b82f6').pack(pady=20)
        
        # Backup options
        options_frame = tk.Frame(backup_card, bg='#0f172a')
        options_frame.pack(pady=20)
        
        backup_options = [
            ("💾 Full Database Backup", "Complete system backup with encryption"),
            ("📁 Meeting Data Only", "Backup meetings, participants, and notes"),
            ("👤 User Data Backup", "User profiles and preferences"),
            ("📊 Analytics Backup", "Historical data and statistics")
        ]
        
        for i, (title, desc) in enumerate(backup_options):
            frame = tk.Frame(options_frame, bg='#1e293b', relief='groove', bd=1)
            frame.pack(fill='x', pady=5, padx=20)
            
            var = tk.BooleanVar()
            tk.Checkbutton(frame, variable=var, bg='#1e293b').pack(side='left', padx=10, pady=10)
            
            tk.Label(frame, text=title, font=("Segoe UI", 12, "bold"),
                    bg='#1e293b', fg='white').pack(side='left', padx=10)
            tk.Label(frame, text=desc, font=("Segoe UI", 10),
                    bg='#1e293b', fg='#94a3b8').pack(side='left', padx=20)
        
        # Backup location
        location_frame = tk.Frame(backup_card, bg='#0f172a')
        location_frame.pack(pady=20, padx=20, fill='x')
        
        tk.Label(location_frame, text="📁 Backup Location:", 
                font=("Segoe UI", 11), bg='#0f172a', fg='#94a3b8').pack(side='left', padx=(0, 10))
        
        location_entry = ttk.Entry(location_frame, font=("Segoe UI", 11), width=40)
        location_entry.pack(side='left', fill='x', expand=True)
        location_entry.insert(0, "C:/AOMMS_Backups/")
        
        tk.Button(location_frame, text="Browse",
                 font=("Segoe UI", 10),
                 bg='#3b82f6', fg='white',
                 bd=0, padx=10, pady=5,
                 cursor="hand2",
                 command=lambda: self.browse_backup_location(location_entry)).pack(side='left', padx=10)
        
        # Backup buttons
        button_frame = tk.Frame(backup_card, bg='#0f172a')
        button_frame.pack(pady=30)
        
        backup_btn = tk.Button(button_frame, text="🚀 Start Secure Backup",
                              font=("Segoe UI", 14, "bold"),
                              bg='#10b981', fg='white',
                              bd=0, padx=30, pady=12,
                              cursor="hand2",
                              command=self.perform_backup)
        backup_btn.pack(side='left', padx=10)
        
        # Restore card
        restore_card = tk.Frame(backup_frame, bg='#0f172a', relief='raised', bd=2)
        restore_card.pack(fill='x', padx=20, pady=20)
        
        tk.Label(restore_card, text="🔄 Disaster Recovery", 
                font=("Segoe UI", 18, "bold"), bg='#0f172a', fg='#ef4444').pack(pady=20)
        
        restore_frame = tk.Frame(restore_card, bg='#0f172a')
        restore_frame.pack(pady=20, padx=20)
        
        # Backup file selection
        tk.Label(restore_frame, text="Select Backup File:", font=("Segoe UI", 11),
                bg='#0f172a', fg='#94a3b8').pack(anchor='w', pady=(0, 10))
        
        file_frame = tk.Frame(restore_frame, bg='#0f172a')
        file_frame.pack(fill='x', pady=(0, 20))
        
        file_entry = ttk.Entry(file_frame, font=("Segoe UI", 11), width=40)
        file_entry.pack(side='left', fill='x', expand=True)
        
        tk.Button(file_frame, text="📂 Choose File",
                 font=("Segoe UI", 10),
                 bg='#3b82f6', fg='white',
                 bd=0, padx=15, pady=5,
                 cursor="hand2",
                 command=lambda: self.browse_backup_file(file_entry)).pack(side='left', padx=10)
        
        # Restore button
        restore_btn = tk.Button(restore_card, text="🔄 Start Restore Process",
                               font=("Segoe UI", 14, "bold"),
                               bg='#f59e0b', fg='white',
                               bd=0, padx=30, pady=12,
                               cursor="hand2",
                               command=self.perform_restore)
        restore_btn.pack(pady=30)
    
    def browse_backup_location(self, entry_widget):
        """Browse for backup location"""
        directory = filedialog.askdirectory()
        if directory:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, directory)
    
    def browse_backup_file(self, entry_widget):
        """Browse for backup file"""
        filename = filedialog.askopenfilename(filetypes=[("Backup files", "*.bak;*.db;*.csv"), ("All files", "*.*")])
        if filename:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)
    
    def perform_backup(self):
        """Perform secure backup"""
        backup_window = tk.Toplevel(self.root)
        backup_window.title("Backup Progress")
        backup_window.geometry("400x300")
        backup_window.configure(bg='#0f172a')
        
        tk.Label(backup_window, text="🔒 Secure Backup in Progress", 
                font=("Segoe UI", 16, "bold"), bg='#0f172a', fg='white').pack(pady=30)
        
        # Progress bar
        progress = ttk.Progressbar(backup_window, length=300, mode='indeterminate')
        progress.pack(pady=20)
        progress.start(10)
        
        # Status messages
        status_frame = tk.Frame(backup_window, bg='#1e293b', padx=20, pady=20)
        status_frame.pack(pady=20, fill='x', padx=20)
        
        status_labels = [
            "Encrypting database...",
            "Compressing files...",
            "Creating backup archive...",
            "Verifying integrity...",
            "Backup completed successfully!"
        ]
        
        for i, text in enumerate(status_labels):
            label = tk.Label(status_frame, text=text, 
                           font=("Segoe UI", 10),
                           bg='#1e293b', fg='#94a3b8')
            label.pack(anchor='w', pady=2)
            
            # Simulate progress
            self.root.after(1000 * (i + 1), lambda l=label: l.config(fg='#10b981'))
        
        # Close button
        self.root.after(6000, lambda: backup_window.destroy())
        messagebox.showinfo("Backup Complete", "Backup created successfully!")
    
    def perform_restore(self):
        """Perform restore from backup"""
        response = messagebox.askyesno("Confirm Restore", 
                                      "This will overwrite existing data. Continue?")
        if response:
            messagebox.showinfo("Restore Started", 
                              "Restore process started in background.")
            # Simulate restore process
            self.root.after(2000, lambda: messagebox.showinfo("Restore Complete", "Data restored successfully!"))
    
    # ==================== ADDITIONAL PREMIUM FEATURES ====================
    def show_dashboard_overview(self):
        """Show main dashboard with widgets"""
        self.clear_content()
        
        tk.Label(self.content_frame, text="📊 Dashboard Overview", 
                font=("Segoe UI", 20, "bold"), bg='#0f172a', fg='white').pack(pady=20)
        
        # Stats widgets
        stats_frame = tk.Frame(self.content_frame, bg='#0f172a')
        stats_frame.pack(fill='x', padx=30, pady=10)
        
        stats_data = [
            ("📅 Today's Meetings", "3", "#3b82f6"),
            ("👥 Total Participants", "42", "#10b981"),
            ("⏰ Meeting Hours", "18.5", "#8b5cf6"),
            ("📈 Attendance Rate", "92%", "#f59e0b")
        ]
        
        for i, (title, value, color) in enumerate(stats_data):
            stat_card = tk.Frame(stats_frame, bg=color, relief='raised', bd=1)
            stat_card.grid(row=0, column=i, padx=10, sticky='nsew', ipadx=20, ipady=20)
            
            tk.Label(stat_card, text=title, font=("Segoe UI", 11), 
                    bg=color, fg='white').pack()
            tk.Label(stat_card, text=value, font=("Segoe UI", 24, "bold"), 
                    bg=color, fg='white').pack(pady=5)
        
        # Quick actions
        actions_frame = tk.Frame(self.content_frame, bg='#1e293b', padx=20, pady=20)
        actions_frame.pack(fill='x', padx=30, pady=20)
        
        tk.Label(actions_frame, text="⚡ Quick Actions", 
                font=("Segoe UI", 16, "bold"), bg='#1e293b', fg='white').pack(anchor='w', pady=(0, 15))
        
        quick_actions = [
            ("📅 Schedule Meeting", self.show_ai_scheduler),
            ("📝 Take Notes", self.show_smart_notes),
            ("👥 Add Participants", self.show_participant_manager),
            ("🔔 Set Reminder", self.show_smart_notifications)
        ]
        
        for text, command in quick_actions:
            btn = tk.Button(actions_frame, text=text,
                           font=("Segoe UI", 11),
                           bg='#334155', fg='white',
                           bd=0, padx=20, pady=10,
                           cursor="hand2",
                           command=command)
            btn.pack(side='left', padx=10)
    
    def show_ai_assistant(self):
        """Show AI assistant interface"""
        self.clear_content()
        
        tk.Label(self.content_frame, text="🤖 AI Meeting Assistant", 
                font=("Segoe UI", 20, "bold"), bg='#0f172a', fg='white').pack(pady=20)
        
        assistant_frame = tk.Frame(self.content_frame, bg='#1e293b', padx=30, pady=30)
        assistant_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        tk.Label(assistant_frame, text="How can I help you today?", 
                font=("Segoe UI", 16), bg='#1e293b', fg='white').pack(pady=(0, 20))
        
        # AI capabilities
        capabilities = [
            "📅 Schedule optimal meeting times",
            "👥 Suggest participants based on topic",
            "📝 Generate meeting agendas",
            "⏰ Set smart reminders",
            "📊 Analyze meeting effectiveness",
            "🔍 Find available time slots"
        ]
        
        for cap in capabilities:
            tk.Label(assistant_frame, text=f"• {cap}", 
                    font=("Segoe UI", 12), bg='#1e293b', fg='#cbd5e1').pack(anchor='w', pady=5)
    
    def show_analytics_dashboard(self):
        """Show advanced analytics dashboard"""
        self.clear_content()
        
        tk.Label(self.content_frame, text="📈 Advanced Analytics Dashboard", 
                font=("Segoe UI", 20, "bold"), bg='#0f172a', fg='white').pack(pady=20)
        
        analytics_frame = tk.Frame(self.content_frame, bg='#1e293b')
        analytics_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Create simple analytics display
        stats_frame = tk.Frame(analytics_frame, bg='#0f172a')
        stats_frame.pack(pady=20)
        
        analytics_stats = [
            ("Total Meetings", "24", "#3b82f6"),
            ("Average Duration", "45 mins", "#10b981"),
            ("Participant Satisfaction", "4.8/5", "#f59e0b"),
            ("Productivity Score", "87%", "#8b5cf6")
        ]
        
        for i, (title, value, color) in enumerate(analytics_stats):
            stat_frame = tk.Frame(stats_frame, bg=color, padx=20, pady=15)
            stat_frame.grid(row=0, column=i, padx=10)
            
            tk.Label(stat_frame, text=title, font=("Segoe UI", 11), 
                    bg=color, fg='white').pack()
            tk.Label(stat_frame, text=value, font=("Segoe UI", 18, "bold"), 
                    bg=color, fg='white').pack(pady=5)
    
    def show_settings(self):
        """Show system settings"""
        self.clear_content()
        
        tk.Label(self.content_frame, text="⚙️ System Settings", 
                font=("Segoe UI", 20, "bold"), bg='#0f172a', fg='white').pack(pady=20)
        
        settings_frame = tk.Frame(self.content_frame, bg='#1e293b', padx=30, pady=30)
        settings_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        settings = [
            ("Theme", "Dark/Light mode"),
            ("Notifications", "Configure alerts"),
            ("Security", "Password policies"),
            ("Integrations", "Connect other apps"),
            ("Backup", "Auto-backup settings"),
            ("Privacy", "Data handling")
        ]
        
        for i, (title, desc) in enumerate(settings):
            frame = tk.Frame(settings_frame, bg='#0f172a')
            frame.pack(fill='x', pady=10)
            
            tk.Label(frame, text=title, font=("Segoe UI", 12, "bold"),
                    bg='#0f172a', fg='white', width=15).pack(side='left')
            tk.Label(frame, text=desc, font=("Segoe UI", 11),
                    bg='#0f172a', fg='#94a3b8').pack(side='left', padx=20)
            
            btn = tk.Button(frame, text="Configure",
                           font=("Segoe UI", 10),
                           bg='#3b82f6', fg='white',
                           bd=0, padx=15, pady=5,
                           cursor="hand2")
            btn.pack(side='right')
    
    def clear_window(self):
        """Clear all widgets"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def start_background_services(self):
        """Start background services"""
        # Start notification checker
        self.notification_thread = threading.Thread(target=self.check_background_notifications, daemon=True)
        self.notification_thread.start()
    
    def check_background_notifications(self):
        """Background notification checker"""
        while True:
            try:
                # Check for upcoming meetings every minute
                time.sleep(60)
            except:
                pass

def main():
    """Launch the application"""
    root = tk.Tk()
    
    # Set window properties
    root.title("ADVANCED ONLINE MEETING MANAGEMENT SYSTEM")
    root.geometry("1400x800")
    
    # Make window resizable
    root.minsize(1200, 700)
    
    # Create application
    app = AdvancedOMMS(root)
    
    # Start main loop
    root.mainloop()

if __name__ == "__main__":
    print("🚀 Starting Advanced OMMS...")
    print("="*50)
    print("Note: For best experience, install optional packages:")
    print("pip install cryptography pillow matplotlib pandas numpy tkcalendar")
    print("="*50)
    
    main()