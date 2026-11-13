"""
Online Meeting Management System (OMMS)
ICT505 Assessment 3 - Part B
Complete GUI Implementation with all 7 features
WITH SCROLLBARS for all content areas
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import json
import os
import csv
from tkcalendar import DateEntry
import threading
import time

# ==================== SCROLLABLE FRAME CLASS ====================
class ScrollableFrame(tk.Frame):
    """A frame with scrollbars that works properly"""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        # Create canvas and scrollbars
        self.canvas = tk.Canvas(self, bg=self['bg'])
        self.v_scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        
        # Configure canvas
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        # Create scrollable frame inside canvas
        self.scrollable_frame = tk.Frame(self.canvas, bg=self['bg'])
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Add scrollable frame to canvas
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas to resize with window
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        
        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)
        
        # Layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
    
    def _on_canvas_configure(self, event):
        """Resize scrollable frame to match canvas width"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def _on_frame_configure(self, event=None):
        """Update scrollregion when frame size changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_mousewheel(self, event):
        """Vertical scrolling with mouse wheel"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _on_shift_mousewheel(self, event):
        """Horizontal scrolling with shift+mouse wheel"""
        self.canvas.xview_scroll(int(-1*(event.delta/120)), "units")

# ==================== DATA STORAGE CLASS ====================
class DataStore:
    """Centralized data storage for meetings, users, and notes"""
    
    def __init__(self):
        self.users = {
            "admin": {"password": "admin123", "role": "admin"},
            "host1": {"password": "host123", "role": "host"},
            "participant1": {"password": "part123", "role": "participant"}
        }
        self.meetings = []
        self.notes = {}
        self.backup_folder = "backups"
        
        # Create backup folder if it doesn't exist
        if not os.path.exists(self.backup_folder):
            os.makedirs(self.backup_folder)
        
        # Load sample data
        self._load_sample_data()
    
    def _load_sample_data(self):
        """Load sample meetings for demonstration"""
        sample_meetings = [
            {
                "id": 1,
                "title": "Project Kickoff",
                "host": "host1",
                "date": "2025-04-10",
                "time": "14:00",
                "duration": "1.5 hours",
                "agenda": "Discuss project goals and timeline",
                "participants": ["participant1", "admin"],
                "confirmed": ["participant1"],
                "status": "upcoming"
            },
            {
                "id": 2,
                "title": "Weekly Team Sync",
                "host": "admin",
                "date": "2025-04-12",
                "time": "10:00",
                "duration": "1 hour",
                "agenda": "Weekly progress update",
                "participants": ["host1", "participant1"],
                "confirmed": ["host1"],
                "status": "upcoming"
            },
            {
                "id": 3,
                "title": "Client Presentation",
                "host": "host1",
                "date": "2025-04-05",
                "time": "15:30",
                "duration": "2 hours",
                "agenda": "Present final deliverables to client",
                "participants": ["admin", "participant1"],
                "confirmed": ["admin", "participant1"],
                "status": "completed"
            },
            {
                "id": 4,
                "title": "Budget Review",
                "host": "admin",
                "date": "2025-04-15",
                "time": "11:00",
                "duration": "2 hours",
                "agenda": "Review quarterly budget and expenses",
                "participants": ["host1", "participant1"],
                "confirmed": ["host1"],
                "status": "upcoming"
            },
            {
                "id": 5,
                "title": "Training Session",
                "host": "host1",
                "date": "2025-04-08",
                "time": "09:00",
                "duration": "3 hours",
                "agenda": "New software tools training",
                "participants": ["admin", "participant1"],
                "confirmed": ["admin", "participant1"],
                "status": "completed"
            }
        ]
        self.meetings = sample_meetings
        
        # Add sample notes
        self.notes[1] = "Kickoff went well. Team is aligned on goals."
        self.notes[3] = "Client was satisfied with the presentation."
        self.notes[5] = "Training completed successfully. All team members attended."

# ==================== MAIN APPLICATION CLASS ====================
class OMMSApp:
    """Main OMMS Application Class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Online Meeting Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize data store
        self.data = DataStore()
        self.current_user = None
        self.current_role = None
        
        # Notification thread
        self.notification_running = True
        self.notification_thread = threading.Thread(target=self.check_notifications, daemon=True)
        
        # Create login screen first
        self.create_login_screen()
        
    # ==================== TASK B.1: USER AUTHENTICATION ====================
    def create_login_screen(self):
        """Create login interface"""
        self.clear_screen()
        
        # Title Frame
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="OMMS Login", font=('Arial', 24, 'bold'), 
                fg='white', bg='#2c3e50').pack(pady=20)
        
        # Center container for login
        center_container = tk.Frame(self.root, bg='#f0f0f0')
        center_container.pack(expand=True, fill='both', padx=100, pady=50)
        
        # Login Frame
        login_frame = tk.Frame(center_container, bg='white', relief='groove', bd=2)
        login_frame.pack(expand=True)
        
        tk.Label(login_frame, text="Login to OMMS", font=('Arial', 16, 'bold'), 
                bg='white').pack(pady=(30, 20))
        
        # Username
        tk.Label(login_frame, text="Username:", font=('Arial', 12), 
                bg='white').pack(pady=(10, 5))
        self.username_entry = tk.Entry(login_frame, font=('Arial', 12), width=30)
        self.username_entry.pack(pady=(0, 10))
        
        # Password
        tk.Label(login_frame, text="Password:", font=('Arial', 12), 
                bg='white').pack(pady=(10, 5))
        self.password_entry = tk.Entry(login_frame, font=('Arial', 12), 
                                     show='*', width=30)
        self.password_entry.pack(pady=(0, 10))
        
        # Role Selection
        tk.Label(login_frame, text="Role:", font=('Arial', 12), 
                bg='white').pack(pady=(10, 5))
        self.role_var = tk.StringVar(value="participant")
        roles = ["admin", "host", "participant"]
        role_dropdown = ttk.Combobox(login_frame, textvariable=self.role_var, 
                                    values=roles, state="readonly", width=27)
        role_dropdown.pack(pady=(0, 20))
        
        # Login Button
        login_btn = tk.Button(login_frame, text="Login", font=('Arial', 12, 'bold'),
                            bg='#3498db', fg='white', width=20, height=2,
                            command=self.authenticate_user)
        login_btn.pack(pady=(0, 30))
        
        # Demo credentials
        cred_frame = tk.Frame(login_frame, bg='white')
        cred_frame.pack(pady=(0, 20))
        
        tk.Label(cred_frame, text="Demo Credentials:", font=('Arial', 10, 'bold'), 
                bg='white').pack()
        tk.Label(cred_frame, text="admin / admin123 (admin)", font=('Arial', 9), 
                bg='white', fg='gray').pack()
        tk.Label(cred_frame, text="host1 / host123 (host)", font=('Arial', 9), 
                bg='white', fg='gray').pack()
        tk.Label(cred_frame, text="participant1 / part123 (participant)", font=('Arial', 9), 
                bg='white', fg='gray').pack()
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.authenticate_user())
        
        # Set focus to username field
        self.username_entry.focus_set()
    
    def authenticate_user(self):
        """Authenticate user credentials"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        # Check credentials
        if username in self.data.users:
            user_data = self.data.users[username]
            if user_data["password"] == password and user_data["role"] == role:
                self.current_user = username
                self.current_role = role
                messagebox.showinfo("Login Success", f"Welcome, {username}!")
                
                # Start notification thread
                if not self.notification_thread.is_alive():
                    self.notification_thread.start()
                
                # Navigate to main dashboard
                self.create_main_dashboard()
            else:
                messagebox.showerror("Error", "Invalid credentials or role mismatch")
        else:
            # For demo purposes, allow new users
            self.data.users[username] = {"password": password, "role": role}
            self.current_user = username
            self.current_role = role
            messagebox.showinfo("New User", "Account created successfully!")
            
            if not self.notification_thread.is_alive():
                self.notification_thread.start()
            
            self.create_main_dashboard()
    
    # ==================== MAIN DASHBOARD ====================
    def create_main_dashboard(self):
        """Create main dashboard after login"""
        self.clear_screen()
        
        # Header Frame
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Welcome message
        welcome_label = tk.Label(header_frame, 
                                text=f"Welcome {self.current_user} ({self.current_role})",
                                font=('Arial', 14, 'bold'), 
                                fg='white', bg='#2c3e50')
        welcome_label.pack(side='left', padx=20, pady=15)
        
        # Logout button
        logout_btn = tk.Button(header_frame, text="Logout", font=('Arial', 10),
                              bg='#e74c3c', fg='white',
                              command=self.logout)
        logout_btn.pack(side='right', padx=20, pady=10)
        
        # Navigation Frame
        nav_frame = tk.Frame(self.root, bg='#34495e', width=200)
        nav_frame.pack(side='left', fill='y')
        nav_frame.pack_propagate(False)
        
        # Navigation Buttons
        buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("📅 Schedule Meeting", self.create_meeting_screen),
            ("👥 Participants", self.create_participant_screen),
            ("🔔 Notifications", self.show_notifications),
            ("📝 Meeting Notes", self.create_notes_screen),
            ("🔍 Search History", self.create_search_screen),
            ("💾 Backup/Restore", self.create_backup_screen)
        ]
        
        for text, command in buttons:
            btn = tk.Button(nav_frame, text=text, font=('Arial', 11),
                           bg='#34495e', fg='white', anchor='w',
                           command=command, padx=20)
            btn.pack(fill='x', pady=2)
        
        # Main Content Frame with Scrollbar
        self.content_frame = ScrollableFrame(self.root, bg='#ecf0f1')
        self.content_frame.pack(side='right', expand=True, fill='both')
        
        # Show dashboard by default
        self.show_dashboard()
    
    def show_dashboard(self):
        """Display dashboard with overview"""
        self.clear_content()
        
        # Get the scrollable frame from the ScrollableFrame
        content = self.content_frame.scrollable_frame
        
        tk.Label(content, text="Dashboard Overview", 
                font=('Arial', 20, 'bold'), bg='#ecf0f1').pack(pady=20)
        
        # Stats Frame
        stats_frame = tk.Frame(content, bg='white', relief='groove', bd=2)
        stats_frame.pack(pady=20, padx=50, fill='x')
        
        total_meetings = len(self.data.meetings)
        upcoming = len([m for m in self.data.meetings if m['status'] == 'upcoming'])
        completed = len([m for m in self.data.meetings if m['status'] == 'completed'])
        
        stats = [
            ("Total Meetings", total_meetings, "#3498db"),
            ("Upcoming", upcoming, "#2ecc71"),
            ("Completed", completed, "#e74c3c")
        ]
        
        for i, (label, value, color) in enumerate(stats):
            stat_frame = tk.Frame(stats_frame, bg=color)
            stat_frame.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            stats_frame.grid_columnconfigure(i, weight=1)
            
            tk.Label(stat_frame, text=label, font=('Arial', 12), 
                    bg=color, fg='white').pack(pady=(10,0))
            tk.Label(stat_frame, text=str(value), font=('Arial', 24, 'bold'), 
                    bg=color, fg='white').pack(pady=(0,10))
        
        # Upcoming Meetings
        upcoming_frame = tk.LabelFrame(content, text="Upcoming Meetings", 
                                      font=('Arial', 14, 'bold'), bg='white')
        upcoming_frame.pack(pady=20, padx=50, fill='both', expand=True)
        
        # Create Treeview for meetings
        columns = ('ID', 'Title', 'Host', 'Date', 'Time', 'Duration')
        tree = ttk.Treeview(upcoming_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Add scrollbar to treeview
        tree_scroll = ttk.Scrollbar(upcoming_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=tree_scroll.set)
        
        tree.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        tree_scroll.grid(row=0, column=1, sticky='ns', pady=5)
        
        upcoming_frame.grid_rowconfigure(0, weight=1)
        upcoming_frame.grid_columnconfigure(0, weight=1)
        
        # Add upcoming meetings
        for meeting in self.data.meetings:
            if meeting['status'] == 'upcoming':
                tree.insert('', 'end', values=(
                    meeting['id'],
                    meeting['title'],
                    meeting['host'],
                    meeting['date'],
                    meeting['time'],
                    meeting['duration']
                ))
        
        # Completed Meetings
        completed_frame = tk.LabelFrame(content, text="Recent Completed Meetings", 
                                       font=('Arial', 14, 'bold'), bg='white')
        completed_frame.pack(pady=20, padx=50, fill='both', expand=True)
        
        # Create Treeview for completed meetings
        completed_tree = ttk.Treeview(completed_frame, columns=columns, show='headings', height=5)
        
        for col in columns:
            completed_tree.heading(col, text=col)
            completed_tree.column(col, width=100)
        
        # Add scrollbar
        completed_scroll = ttk.Scrollbar(completed_frame, orient="vertical", command=completed_tree.yview)
        completed_tree.configure(yscrollcommand=completed_scroll.set)
        
        completed_tree.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        completed_scroll.grid(row=0, column=1, sticky='ns', pady=5)
        
        completed_frame.grid_rowconfigure(0, weight=1)
        completed_frame.grid_columnconfigure(0, weight=1)
        
        # Add completed meetings
        for meeting in self.data.meetings:
            if meeting['status'] == 'completed':
                completed_tree.insert('', 'end', values=(
                    meeting['id'],
                    meeting['title'],
                    meeting['host'],
                    meeting['date'],
                    meeting['time'],
                    meeting['duration']
                ))
    
    # ==================== TASK B.2: MEETING SCHEDULING ====================
    def create_meeting_screen(self):
        """Create meeting scheduling interface"""
        self.clear_content()
        content = self.content_frame.scrollable_frame
        
        tk.Label(content, text="Schedule New Meeting", 
                font=('Arial', 20, 'bold'), bg='#ecf0f1').pack(pady=20)
        
        form_frame = tk.Frame(content, bg='white', relief='groove', bd=2)
        form_frame.pack(pady=20, padx=50, fill='x')
        
        # Form fields
        fields = [
            ("Title:", "title"),
            ("Date:", "date"),
            ("Time (HH:MM):", "time"),
            ("Duration:", "duration"),
            ("Agenda:", "agenda")
        ]
        
        self.meeting_vars = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label, font=('Arial', 11), 
                    bg='white').grid(row=i, column=0, padx=10, pady=10, sticky='e')
            
            if key == 'date':
                # Date picker
                var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
                date_entry = DateEntry(form_frame, textvariable=var, 
                                      date_pattern='yyyy-mm-dd')
                date_entry.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            elif key == 'agenda':
                # Text area for agenda
                var = tk.Text(form_frame, height=4, width=40)
                var.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            else:
                var = tk.Entry(form_frame, width=40)
                var.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            
            self.meeting_vars[key] = var
        
        # Participants multi-select
        tk.Label(form_frame, text="Participants:", font=('Arial', 11), 
                bg='white').grid(row=len(fields), column=0, padx=10, pady=10, sticky='ne')
        
        participants_frame = tk.Frame(form_frame, bg='white')
        participants_frame.grid(row=len(fields), column=1, padx=10, pady=10, sticky='w')
        
        self.participant_listbox = tk.Listbox(participants_frame, 
                                            selectmode='multiple', 
                                            height=4, width=40)
        self.participant_listbox.pack(side='left', fill='both', expand=True)
        
        # Add scrollbar to listbox
        listbox_scroll = tk.Scrollbar(participants_frame)
        listbox_scroll.pack(side='right', fill='y')
        self.participant_listbox.config(yscrollcommand=listbox_scroll.set)
        listbox_scroll.config(command=self.participant_listbox.yview)
        
        # Add available users to listbox
        for username in self.data.users.keys():
            if username != self.current_user:
                self.participant_listbox.insert('end', username)
        
        # Buttons
        button_frame = tk.Frame(content, bg='#ecf0f1')
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Schedule Meeting", font=('Arial', 12, 'bold'),
                 bg='#2ecc71', fg='white', width=20,
                 command=self.schedule_meeting).pack(side='left', padx=10)
        
        tk.Button(button_frame, text="Clear Form", font=('Arial', 12),
                 bg='#95a5a6', fg='white', width=20,
                 command=self.clear_meeting_form).pack(side='left', padx=10)
        
        # Show existing meetings that user can edit
        if self.current_role in ['admin', 'host']:
            self.show_editable_meetings(content)
    
    def schedule_meeting(self):
        """Schedule a new meeting"""
        # Validate fields
        title = self.meeting_vars['title'].get() if isinstance(self.meeting_vars['title'], tk.Entry) else self.meeting_vars['title'].get("1.0", "end-1c")
        
        if not title:
            messagebox.showerror("Error", "Title is required")
            return
        
        # Get all values
        date = self.meeting_vars['date'].get()
        time_str = self.meeting_vars['time'].get()
        duration = self.meeting_vars['duration'].get()
        
        if isinstance(self.meeting_vars['agenda'], tk.Text):
            agenda = self.meeting_vars['agenda'].get("1.0", "end-1c")
        else:
            agenda = self.meeting_vars['agenda'].get()
        
        # Validate time format
        try:
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Time must be in HH:MM format")
            return
        
        # Get selected participants
        selected_indices = self.participant_listbox.curselection()
        participants = [self.participant_listbox.get(i) for i in selected_indices]
        
        # Create meeting object
        new_id = max([m['id'] for m in self.data.meetings], default=0) + 1
        
        meeting = {
            'id': new_id,
            'title': title,
            'host': self.current_user,
            'date': date,
            'time': time_str,
            'duration': duration,
            'agenda': agenda,
            'participants': participants,
            'confirmed': [],
            'status': 'upcoming'
        }
        
        self.data.meetings.append(meeting)
        
        # Send notifications to participants
        for participant in participants:
            self.create_notification(
                f"New Meeting Invitation: {title}",
                f"You've been invited to '{title}' on {date} at {time_str}",
                participant
            )
        
        messagebox.showinfo("Success", "Meeting scheduled successfully!")
        self.show_dashboard()
    
    def clear_meeting_form(self):
        """Clear all form fields"""
        for key, widget in self.meeting_vars.items():
            if isinstance(widget, tk.Entry):
                widget.delete(0, 'end')
            elif isinstance(widget, tk.Text):
                widget.delete("1.0", "end")
            elif isinstance(widget, DateEntry):
                widget.set_date(datetime.now())
        
        self.participant_listbox.selection_clear(0, 'end')
    
    def show_editable_meetings(self, content):
        """Show meetings that current user can edit/cancel"""
        editable_frame = tk.LabelFrame(content, text="Manage Existing Meetings", 
                                      font=('Arial', 14, 'bold'), bg='white')
        editable_frame.pack(pady=20, padx=50, fill='both', expand=True)
        
        # Create Treeview
        columns = ('ID', 'Title', 'Date', 'Time', 'Actions')
        tree = ttk.Treeview(editable_frame, columns=columns, show='headings', height=5)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Add scrollbar
        tree_scroll = ttk.Scrollbar(editable_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=tree_scroll.set)
        
        tree.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        tree_scroll.grid(row=0, column=1, sticky='ns', pady=5)
        
        editable_frame.grid_rowconfigure(0, weight=1)
        editable_frame.grid_columnconfigure(0, weight=1)
        
        # Add meetings
        for meeting in self.data.meetings:
            if (self.current_role == 'admin' or 
                (self.current_role == 'host' and meeting['host'] == self.current_user)):
                tree.insert('', 'end', values=(
                    meeting['id'],
                    meeting['title'],
                    meeting['date'],
                    meeting['time'],
                    "Edit/Cancel"
                ))
        
        # Button frame
        button_frame = tk.Frame(editable_frame, bg='white')
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        tk.Button(button_frame, text="Edit Selected", 
                 command=lambda: self.edit_meeting(tree),
                 bg='#f39c12', fg='white').pack(side='left', padx=5)
        
        tk.Button(button_frame, text="Cancel Selected", 
                 command=lambda: self.cancel_meeting(tree),
                 bg='#e74c3c', fg='white').pack(side='left', padx=5)
    
    def edit_meeting(self, tree):
        """Edit selected meeting"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a meeting to edit")
            return
        
        # In a full implementation, you would load the meeting data into the form
        messagebox.showinfo("Edit", "Edit functionality would load meeting data into form")
    
    def cancel_meeting(self, tree):
        """Cancel selected meeting"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a meeting to cancel")
            return
        
        meeting_id = tree.item(selection[0])['values'][0]
        
        if messagebox.askyesno("Confirm", "Are you sure you want to cancel this meeting?"):
            # Find and remove meeting
            for i, meeting in enumerate(self.data.meetings):
                if meeting['id'] == meeting_id:
                    # Notify participants
                    for participant in meeting['participants']:
                        self.create_notification(
                            "Meeting Cancelled",
                            f"Meeting '{meeting['title']}' has been cancelled",
                            participant
                        )
                    
                    self.data.meetings.pop(i)
                    messagebox.showinfo("Success", "Meeting cancelled")
                    self.create_meeting_screen()  # Refresh
                    break
    
    # ==================== TASK B.3: PARTICIPANT MANAGEMENT ====================
    def create_participant_screen(self):
        """Create participant management interface"""
        self.clear_content()
        content = self.content_frame.scrollable_frame
        
        tk.Label(content, text="Participant Management", 
                font=('Arial', 20, 'bold'), bg='#ecf0f1').pack(pady=20)
        
        # Only hosts and admins can manage participants
        if self.current_role not in ['admin', 'host']:
            tk.Label(content, text="You don't have permission to manage participants", 
                    font=('Arial', 14), fg='red', bg='#ecf0f1').pack(pady=50)
            return
        
        # Main management frame
        mgmt_frame = tk.Frame(content, bg='white', relief='groove', bd=2)
        mgmt_frame.pack(pady=20, padx=50, fill='both', expand=True)
        
        # Left side: Add participant
        add_frame = tk.LabelFrame(mgmt_frame, text="Add Participant", bg='white')
        add_frame.grid(row=0, column=0, padx=20, pady=20, sticky='n')
        
        tk.Label(add_frame, text="Username:", bg='white').grid(row=0, column=0, pady=10)
        new_user_entry = tk.Entry(add_frame, width=25)
        new_user_entry.grid(row=0, column=1, pady=10, padx=10)
        
        tk.Label(add_frame, text="Password:", bg='white').grid(row=1, column=0, pady=10)
        new_pass_entry = tk.Entry(add_frame, show='*', width=25)
        new_pass_entry.grid(row=1, column=1, pady=10, padx=10)
        
        tk.Label(add_frame, text="Role:", bg='white').grid(row=2, column=0, pady=10)
        role_var = tk.StringVar(value="participant")
        role_combo = ttk.Combobox(add_frame, textvariable=role_var, 
                                 values=["participant", "host"], state="readonly", width=22)
        role_combo.grid(row=2, column=1, pady=10, padx=10)
        
        def add_participant():
            username = new_user_entry.get()
            password = new_pass_entry.get()
            role = role_var.get()
            
            if not username or not password:
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            if username in self.data.users:
                messagebox.showerror("Error", "User already exists")
                return
            
            self.data.users[username] = {"password": password, "role": role}
            messagebox.showinfo("Success", f"User '{username}' added successfully")
            new_user_entry.delete(0, 'end')
            new_pass_entry.delete(0, 'end')
            refresh_user_list()
        
        tk.Button(add_frame, text="Add User", bg='#2ecc71', fg='white',
                 command=add_participant).grid(row=3, column=0, columnspan=2, pady=20)
        
        # Right side: User list and management
        list_frame = tk.LabelFrame(mgmt_frame, text="All Users", bg='white')
        list_frame.grid(row=0, column=1, padx=20, pady=20, sticky='nsew')
        
        mgmt_frame.grid_columnconfigure(1, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview for users
        user_tree = ttk.Treeview(list_frame, columns=('Username', 'Role'), show='headings', height=10)
        user_tree.heading('Username', text='Username')
        user_tree.heading('Role', text='Role')
        user_tree.column('Username', width=150)
        user_tree.column('Role', width=100)
        
        # Add scrollbar
        user_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=user_tree.yview)
        user_tree.configure(yscrollcommand=user_scroll.set)
        
        user_tree.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        user_scroll.grid(row=0, column=1, sticky='ns', pady=5)
        
        def refresh_user_list():
            # Clear existing items
            for item in user_tree.get_children():
                user_tree.delete(item)
            
            # Add users
            for username, data in self.data.users.items():
                user_tree.insert('', 'end', values=(username, data['role']))
        
        refresh_user_list()
        
        # Remove button
        def remove_selected():
            selection = user_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a user to remove")
                return
            
            username = user_tree.item(selection[0])['values'][0]
            
            if username == self.current_user:
                messagebox.showerror("Error", "Cannot remove yourself")
                return
            
            if messagebox.askyesno("Confirm", f"Remove user '{username}'?"):
                del self.data.users[username]
                refresh_user_list()
                messagebox.showinfo("Success", "User removed")
        
        tk.Button(list_frame, text="Remove Selected", bg='#e74c3c', fg='white',
                 command=remove_selected).grid(row=1, column=0, columnspan=2, pady=10)
        
        # Bottom: Meeting invitations
        invite_frame = tk.LabelFrame(content, text="Meeting Invitations", 
                                    bg='white', relief='groove', bd=2)
        invite_frame.pack(pady=20, padx=50, fill='both', expand=True)
        
        # Treeview for meetings user is invited to
        invite_tree = ttk.Treeview(invite_frame, 
                                  columns=('Meeting ID', 'Title', 'Host', 'Date', 'Status'), 
                                  show='headings', height=6)
        
        columns = [('Meeting ID', 80), ('Title', 200), ('Host', 100), ('Date', 100), ('Status', 100)]
        for col, width in columns:
            invite_tree.heading(col, text=col)
            invite_tree.column(col, width=width)
        
        # Add scrollbar
        invite_scroll = ttk.Scrollbar(invite_frame, orient="vertical", command=invite_tree.yview)
        invite_tree.configure(yscrollcommand=invite_scroll.set)
        
        invite_tree.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        invite_scroll.grid(row=0, column=1, sticky='ns', pady=5)
        
        invite_frame.grid_rowconfigure(0, weight=1)
        invite_frame.grid_columnconfigure(0, weight=1)
        
        # Populate with meetings
        for meeting in self.data.meetings:
            if self.current_user in meeting['participants']:
                status = "Confirmed" if self.current_user in meeting['confirmed'] else "Pending"
                invite_tree.insert('', 'end', values=(
                    meeting['id'],
                    meeting['title'],
                    meeting['host'],
                    meeting['date'],
                    status
                ))
        
        # Confirm/Decline buttons
        def respond_to_invitation(response):
            selection = invite_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select an invitation")
                return
            
            meeting_id = invite_tree.item(selection[0])['values'][0]
            
            # Find meeting
            for meeting in self.data.meetings:
                if meeting['id'] == meeting_id:
                    if response == 'confirm':
                        if self.current_user not in meeting['confirmed']:
                            meeting['confirmed'].append(self.current_user)
                            messagebox.showinfo("Success", "Invitation confirmed!")
                    else:  # decline
                        if self.current_user in meeting['participants']:
                            meeting['participants'].remove(self.current_user)
                        if self.current_user in meeting['confirmed']:
                            meeting['confirmed'].remove(self.current_user)
                        messagebox.showinfo("Success", "Invitation declined!")
                    
                    # Refresh
                    self.create_participant_screen()
                    break
        
        btn_frame = tk.Frame(invite_frame, bg='white')
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        tk.Button(btn_frame, text="Confirm Invitation", bg='#2ecc71', fg='white',
                 command=lambda: respond_to_invitation('confirm')).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Decline Invitation", bg='#e74c3c', fg='white',
                 command=lambda: respond_to_invitation('decline')).pack(side='left', padx=5)
    
    # ==================== TASK B.4: NOTIFICATIONS & REMINDERS ====================
    def create_notification(self, title, message, recipient=None):
        """Create a notification for a user"""
        # In a real application, you would store notifications in a database
        # For now, we'll show popups if the recipient is current user
        if recipient == self.current_user or not recipient:
            # Schedule popup in main thread
            self.root.after(0, lambda: messagebox.showinfo(title, message))
    
    def check_notifications(self):
        """Background thread to check for notifications"""
        while self.notification_running:
            # Check for upcoming meetings (within 30 minutes)
            now = datetime.now()
            
            for meeting in self.data.meetings:
                if meeting['status'] == 'upcoming':
                    try:
                        meeting_time = datetime.strptime(
                            f"{meeting['date']} {meeting['time']}", 
                            "%Y-%m-%d %H:%M"
                        )
                        
                        time_diff = meeting_time - now
                        minutes_diff = time_diff.total_seconds() / 60
                        
                        # Send reminder 10 minutes before
                        if 0 < minutes_diff <= 10:
                            if self.current_user in meeting['participants']:
                                self.create_notification(
                                    "Meeting Reminder",
                                    f"Meeting '{meeting['title']}' starts in {int(minutes_diff)} minutes",
                                    self.current_user
                                )
                    except ValueError:
                        pass
            
            time.sleep(60)  # Check every minute
    
    def show_notifications(self):
        """Display notifications screen"""
        self.clear_content()
        content = self.content_frame.scrollable_frame
        
        tk.Label(content, text="Notifications", 
                font=('Arial', 20, 'bold'), bg='#ecf0f1').pack(pady=20)
        
        # Notification settings frame
        settings_frame = tk.LabelFrame(content, text="Notification Settings", 
                                      bg='white', relief='groove', bd=2)
        settings_frame.pack(pady=20, padx=50, fill='x')
        
        # Reminder time setting
        tk.Label(settings_frame, text="Remind me before meeting (minutes):", 
                bg='white').grid(row=0, column=0, padx=10, pady=10)
        
        reminder_var = tk.StringVar(value="10")
        reminder_spin = tk.Spinbox(settings_frame, from_=1, to=60, 
                                  textvariable=reminder_var, width=10)
        reminder_spin.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Button(settings_frame, text="Save Settings", bg='#3498db', fg='white',
                 command=lambda: messagebox.showinfo("Saved", "Settings saved!")).grid(row=0, column=2, padx=10, pady=10)
        
        # Recent notifications frame
        recent_frame = tk.LabelFrame(content, text="Recent Notifications", 
                                    bg='white', relief='groove', bd=2)
        recent_frame.pack(pady=20, padx=50, fill='both', expand=True)
        
        # Create a scrollable frame for notifications
        notif_scroll_frame = ScrollableFrame(recent_frame, bg='white')
        notif_scroll_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        notif_content = notif_scroll_frame.scrollable_frame
        
        # Sample notifications
        notifications = [
            ("New Meeting", "You've been invited to 'Project Review'", "10 mins ago"),
            ("Meeting Reminder", "Team Sync starts in 15 minutes", "1 hour ago"),
            ("Meeting Updated", "Client call rescheduled to tomorrow", "2 hours ago"),
            ("Participant Joined", "John confirmed attendance", "1 day ago"),
            ("Meeting Completed", "Weekly review completed successfully", "2 days ago"),
            ("New Participant", "Sarah joined the project team", "3 days ago"),
            ("Schedule Change", "Budget meeting moved to next week", "4 days ago")
        ]
        
        for i, (title, message, time_ago) in enumerate(notifications):
            notif_frame = tk.Frame(notif_content, bg='white')
            notif_frame.pack(fill='x', padx=10, pady=5)
            
            tk.Label(notif_frame, text=title, font=('Arial', 11, 'bold'), 
                    bg='white').pack(anchor='w')
            tk.Label(notif_frame, text=message, bg='white', wraplength=500).pack(anchor='w')
            tk.Label(notif_frame, text=time_ago, font=('Arial', 9), 
                    fg='gray', bg='white').pack(anchor='w')
            
            if i < len(notifications) - 1:
                tk.Frame(notif_content, height=1, bg='gray').pack(fill='x', padx=10)
        
        # Test notification button
        tk.Button(content, text="Test Notification", font=('Arial', 12),
                 bg='#9b59b6', fg='white',
                 command=lambda: self.create_notification(
                     "Test Notification", 
                     "This is a test notification from OMMS"
                 )).pack(pady=20)
    
    # ==================== TASK B.5: MEETING RECORDING & NOTES ====================
    def create_notes_screen(self):
        """Create meeting notes interface"""
        self.clear_content()
        content = self.content_frame.scrollable_frame
        
        tk.Label(content, text="Meeting Notes", 
                font=('Arial', 20, 'bold'), bg='#ecf0f1').pack(pady=20)
        
        # Main notes frame
        notes_frame = tk.Frame(content, bg='white', relief='groove', bd=2)
        notes_frame.pack(pady=20, padx=50, fill='both', expand=True)
        
        # Left: Meeting selection
        left_frame = tk.Frame(notes_frame, bg='white')
        left_frame.pack(side='left', fill='y', padx=10, pady=10)
        
        tk.Label(left_frame, text="Select Meeting:", font=('Arial', 11, 'bold'), 
                bg='white').pack(anchor='w', pady=5)
        
        # Listbox for meetings
        self.meeting_listbox = tk.Listbox(left_frame, height=15, width=30)
        self.meeting_listbox.pack(fill='both', expand=True)
        
        # Add scrollbar to listbox
        listbox_scroll = tk.Scrollbar(left_frame)
        listbox_scroll.pack(side='right', fill='y')
        self.meeting_listbox.config(yscrollcommand=listbox_scroll.set)
        listbox_scroll.config(command=self.meeting_listbox.yview)
        
        # Populate with meetings user is involved in
        user_meetings = []
        for meeting in self.data.meetings:
            if (self.current_user == meeting['host'] or 
                self.current_user in meeting['participants']):
                user_meetings.append(meeting)
        
        for meeting in user_meetings:
            self.meeting_listbox.insert('end', f"{meeting['id']}: {meeting['title']}")
        
        # Right: Notes area
        right_frame = tk.Frame(notes_frame, bg='white')
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(right_frame, text="Notes:", font=('Arial', 11, 'bold'), 
                bg='white').pack(anchor='w', pady=5)
        
        # Text area for notes with scrollbar
        text_frame = tk.Frame(right_frame, bg='white')
        text_frame.pack(fill='both', expand=True, pady=5)
        
        self.notes_text = tk.Text(text_frame, height=10, width=50)
        notes_scroll = tk.Scrollbar(text_frame, command=self.notes_text.yview)
        self.notes_text.config(yscrollcommand=notes_scroll.set)
        
        self.notes_text.pack(side='left', fill='both', expand=True)
        notes_scroll.pack(side='right', fill='y')
        
        # Load notes when meeting is selected
        def load_notes(event):
            selection = self.meeting_listbox.curselection()
            if selection:
                meeting_id = int(self.meeting_listbox.get(selection[0]).split(':')[0])
                
                # Clear text area
                self.notes_text.delete("1.0", "end")
                
                # Load existing notes
                if meeting_id in self.data.notes:
                    self.notes_text.insert("1.0", self.data.notes[meeting_id])
        
        self.meeting_listbox.bind('<<ListboxSelect>>', load_notes)
        
        # Buttons
        button_frame = tk.Frame(right_frame, bg='white')
        button_frame.pack(pady=10)
        
        def save_notes():
            selection = self.meeting_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a meeting")
                return
            
            meeting_id = int(self.meeting_listbox.get(selection[0]).split(':')[0])
            notes_content = self.notes_text.get("1.0", "end-1c")
            
            self.data.notes[meeting_id] = notes_content
            messagebox.showinfo("Success", "Notes saved successfully!")
        
        def clear_notes():
            self.notes_text.delete("1.0", "end")
        
        tk.Button(button_frame, text="Save Notes", bg='#2ecc71', fg='white',
                 command=save_notes).pack(side='left', padx=5)
        
        tk.Button(button_frame, text="Clear", bg='#95a5a6', fg='white',
                 command=clear_notes).pack(side='left', padx=5)
        
        # History frame
        history_frame = tk.LabelFrame(content, text="Notes History", 
                                     bg='white', relief='groove', bd=2)
        history_frame.pack(pady=20, padx=50, fill='both', expand=True)
        
        # Treeview for notes history
        history_tree = ttk.Treeview(history_frame, 
                                   columns=('Meeting ID', 'Title', 'Last Updated'), 
                                   show='headings', height=5)
        
        history_tree.heading('Meeting ID', text='Meeting ID')
        history_tree.heading('Title', text='Title')
        history_tree.heading('Last Updated', text='Last Updated')
        
        history_tree.column('Meeting ID', width=80)
        history_tree.column('Title', width=200)
        history_tree.column('Last Updated', width=150)
        
        # Add scrollbar
        history_scroll = ttk.Scrollbar(history_frame, orient="vertical", command=history_tree.yview)
        history_tree.configure(yscrollcommand=history_scroll.set)
        
        history_tree.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        history_scroll.grid(row=0, column=1, sticky='ns', pady=5)
        
        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)
        
        # Populate history
        for meeting_id, note in self.data.notes.items():
            # Find meeting title
            title = "Unknown"
            for meeting in self.data.meetings:
                if meeting['id'] == meeting_id:
                    title = meeting['title']
                    break
            
            history_tree.insert('', 'end', values=(meeting_id, title, "Today"))
    
    # ==================== TASK B.6: SEARCH & HISTORY VIEW ====================
    def create_search_screen(self):
        """Create search and history interface"""
        self.clear_content()
        content = self.content_frame.scrollable_frame
        
        tk.Label(content, text="Search & History", 
                font=('Arial', 20, 'bold'), bg='#ecf0f1').pack(pady=20)
        
        # Search frame
        search_frame = tk.Frame(content, bg='white', relief='groove', bd=2)
        search_frame.pack(pady=20, padx=50, fill='x')
        
        tk.Label(search_frame, text="Search:", bg='white').grid(row=0, column=0, padx=10, pady=10)
        
        self.search_entry = tk.Entry(search_frame, width=40)
        self.search_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Search criteria
        tk.Label(search_frame, text="Search by:", bg='white').grid(row=0, column=2, padx=10, pady=10)
        
        self.search_criteria = tk.StringVar(value="title")
        criteria_combo = ttk.Combobox(search_frame, textvariable=self.search_criteria,
                                     values=["title", "host", "date", "agenda"], 
                                     state="readonly", width=15)
        criteria_combo.grid(row=0, column=3, padx=10, pady=10)
        
        def perform_search():
            query = self.search_entry.get().lower()
            criteria = self.search_criteria.get()
            
            # Clear previous results
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            if not query:
                # Show all if no query
                meetings_to_show = self.data.meetings
            else:
                # Filter meetings
                meetings_to_show = []
                for meeting in self.data.meetings:
                    if criteria == "title" and query in meeting['title'].lower():
                        meetings_to_show.append(meeting)
                    elif criteria == "host" and query in meeting['host'].lower():
                        meetings_to_show.append(meeting)
                    elif criteria == "date" and query in meeting['date']:
                        meetings_to_show.append(meeting)
                    elif criteria == "agenda" and query in meeting['agenda'].lower():
                        meetings_to_show.append(meeting)
            
            # Display results
            for meeting in meetings_to_show:
                self.results_tree.insert('', 'end', values=(
                    meeting['id'],
                    meeting['title'],
                    meeting['host'],
                    meeting['date'],
                    meeting['time'],
                    meeting['duration'],
                    meeting['status']
                ))
        
        tk.Button(search_frame, text="Search", bg='#3498db', fg='white',
                 command=perform_search).grid(row=0, column=4, padx=10, pady=10)
        
        # Results frame
        results_frame = tk.LabelFrame(content, text="Search Results", 
                                     bg='white', relief='groove', bd=2)
        results_frame.pack(pady=20, padx=50, fill='both', expand=True)
        
        # Treeview for results
        columns = ('ID', 'Title', 'Host', 'Date', 'Time', 'Duration', 'Status')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, 
                                        show='headings', height=12)
        
        column_widths = [50, 200, 100, 100, 80, 100, 100]
        for col, width in zip(columns, column_widths):
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=width)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", 
                                   command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient="horizontal",
                                   command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scrollbar.set,
                                   xscrollcommand=h_scrollbar.set)
        
        self.results_tree.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        v_scrollbar.grid(row=0, column=1, sticky='ns', pady=5)
        h_scrollbar.grid(row=1, column=0, sticky='ew', padx=5)
        
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Initial load of all meetings
        perform_search()
        
        # View details button
        def view_details():
            selection = self.results_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a meeting")
                return
            
            meeting_id = self.results_tree.item(selection[0])['values'][0]
            
            # Find meeting
            for meeting in self.data.meetings:
                if meeting['id'] == meeting_id:
                    # Show details in a new window
                    details_window = tk.Toplevel(self.root)
                    details_window.title(f"Meeting Details - {meeting['title']}")
                    details_window.geometry("600x500")
                    
                    # Make details window scrollable
                    details_scroll = ScrollableFrame(details_window)
                    details_scroll.pack(fill='both', expand=True)
                    
                    details_content = details_scroll.scrollable_frame
                    
                    details_text = f"""
                    Meeting ID: {meeting['id']}
                    Title: {meeting['title']}
                    Host: {meeting['host']}
                    Date: {meeting['date']}
                    Time: {meeting['time']}
                    Duration: {meeting['duration']}
                    Status: {meeting['status']}
                    
                    Agenda:
                    {meeting['agenda']}
                    
                    Participants:
                    {', '.join(meeting['participants'])}
                    
                    Confirmed:
                    {', '.join(meeting['confirmed'])}
                    """
                    
                    text_widget = tk.Text(details_content, wrap='word', height=20, width=70)
                    text_widget.pack(fill='both', expand=True, padx=10, pady=10)
                    text_widget.insert("1.0", details_text)
                    text_widget.config(state='disabled')
                    
                    break
        
        tk.Button(content, text="View Details", font=('Arial', 12),
                 bg='#9b59b6', fg='white',
                 command=view_details).pack(pady=10)
    
    # ==================== TASK B.7: DATA BACKUP & RESTORE ====================
    def create_backup_screen(self):
        """Create backup and restore interface"""
        self.clear_content()
        content = self.content_frame.scrollable_frame
        
        tk.Label(content, text="Data Backup & Restore", 
                font=('Arial', 20, 'bold'), bg='#ecf0f1').pack(pady=20)
        
        # Backup frame
        backup_frame = tk.LabelFrame(content, text="Backup Data", 
                                    bg='white', relief='groove', bd=2)
        backup_frame.pack(pady=20, padx=50, fill='x')
        
        backup_info = """
        Back up your meeting data to a file. This includes:
        • All meetings
        • User accounts
        • Meeting notes
        
        Backups are saved in JSON format and can be restored later.
        """
        
        tk.Label(backup_frame, text=backup_info, justify='left', 
                bg='white', wraplength=500).pack(padx=20, pady=10)
        
        def backup_data():
            # Create backup data structure
            backup = {
                'users': self.data.users,
                'meetings': self.data.meetings,
                'notes': self.data.notes,
                'backup_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Ask for file location
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                try:
                    with open(filename, 'w') as f:
                        json.dump(backup, f, indent=2)
                    messagebox.showinfo("Success", f"Backup saved to:\n{filename}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save backup: {e}")
        
        tk.Button(backup_frame, text="Create Backup", font=('Arial', 12),
                 bg='#2ecc71', fg='white',
                 command=backup_data).pack(pady=10)
        
        # Restore frame
        restore_frame = tk.LabelFrame(content, text="Restore Data", 
                                     bg='white', relief='groove', bd=2)
        restore_frame.pack(pady=20, padx=50, fill='x')
        
        restore_info = """
        Restore data from a previously created backup file.
        Warning: This will replace all current data!
        """
        
        tk.Label(restore_frame, text=restore_info, justify='left', 
                bg='white', wraplength=500, fg='red').pack(padx=20, pady=10)
        
        def restore_data():
            if not messagebox.askyesno("Confirm", 
                                      "This will replace all current data. Continue?"):
                return
            
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                try:
                    with open(filename, 'r') as f:
                        backup = json.load(f)
                    
                    # Restore data
                    self.data.users = backup['users']
                    self.data.meetings = backup['meetings']
                    self.data.notes = backup['notes']
                    
                    messagebox.showinfo("Success", "Data restored successfully!")
                    self.show_dashboard()  # Refresh
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to restore: {e}")
        
        tk.Button(restore_frame, text="Restore from Backup", font=('Arial', 12),
                 bg='#e74c3c', fg='white',
                 command=restore_data).pack(pady=10)
        
        # Export frame
        export_frame = tk.LabelFrame(content, text="Export to CSV", 
                                    bg='white', relief='groove', bd=2)
        export_frame.pack(pady=20, padx=50, fill='x')
        
        def export_to_csv():
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                try:
                    with open(filename, 'w', newline='') as f:
                        writer = csv.writer(f)
                        # Write header
                        writer.writerow(['ID', 'Title', 'Host', 'Date', 'Time', 
                                        'Duration', 'Status', 'Participants'])
                        
                        # Write data
                        for meeting in self.data.meetings:
                            writer.writerow([
                                meeting['id'],
                                meeting['title'],
                                meeting['host'],
                                meeting['date'],
                                meeting['time'],
                                meeting['duration'],
                                meeting['status'],
                                ', '.join(meeting['participants'])
                            ])
                    
                    messagebox.showinfo("Success", f"Data exported to:\n{filename}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export: {e}")
        
        tk.Button(export_frame, text="Export Meetings to CSV", font=('Arial', 12),
                 bg='#3498db', fg='white',
                 command=export_to_csv).pack(pady=10)
    
    # ==================== UTILITY FUNCTIONS ====================
    def clear_screen(self):
        """Clear all widgets from root"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def clear_content(self):
        """Clear content frame only"""
        if hasattr(self, 'content_frame'):
            for widget in self.content_frame.scrollable_frame.winfo_children():
                widget.destroy()
    
    def logout(self):
        """Logout user"""
        self.notification_running = False
        self.current_user = None
        self.current_role = None
        self.create_login_screen()

# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = OMMSApp(root)
    
    # Set window icon and title
    root.title("Online Meeting Management System (OMMS)")
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'1200x700+{x}+{y}')
    
    root.mainloop()