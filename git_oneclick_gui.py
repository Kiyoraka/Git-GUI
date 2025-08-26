import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from threading import Thread
import json
import shutil
import platform


class GitOneClickGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Git-OneClick v2.0.0 💜 Alice Edition")
        self.root.resizable(True, True)
        
        # Glassmorphism setup
        self.setup_glassmorphism()
        
        # Set perfect fixed window size - no scrolling needed
        self.root.minsize(740, 700)
        self.root.maxsize(740, 700)  # Fixed size like your perfect adjustment
        
        # Load development types
        self.dev_types = {}
        self.load_development_types()
        
        # Variables
        self.folder_path = ""
        self.repo_url = tk.StringVar(value="")
        self.user_type = tk.StringVar(value="new_user")  # new_user or existing_user
        self.dev_type = tk.StringVar(value="basic")  # Will be populated from config
        self.git_name = tk.StringVar(value="")
        self.git_email = tk.StringVar(value="")
        self.git_installed = False
        
        # Store references to important UI elements
        self.dev_type_frame = None
        self.dev_scrollable_frame = None
        
        # Create GUI elements
        self.create_widgets()
        
        # Auto-resize window based on content
        self.auto_resize_window()
        
        # Check for Git installation
        self.git_installed = self.check_git()
    
    def setup_glassmorphism(self):
        """Setup glassmorphism effects and styling"""
        # Configure window transparency and blur effects
        if platform.system() == "Windows":
            # Windows-specific blur effects
            try:
                self.root.wm_attributes("-alpha", 0.95)  # Semi-transparent
                # Modern Windows blur effect
                self.root.configure(bg='#1a1625')  # Dark purple base
            except:
                self.root.configure(bg='#2D1B69')  # Fallback purple
        else:
            # Cross-platform transparency
            self.root.configure(bg='#2D1B69')
            try:
                self.root.wm_attributes("-alpha", 0.93)
            except:
                pass
        
        # Setup custom styling
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Create beautiful glassmorphism-inspired TTK styles"""
        style = ttk.Style()
        
        # Set theme base
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        
        # Alice's signature purple palette
        colors = {
            'bg_primary': '#2D1B69',      # Deep purple
            'bg_secondary': '#3D2B79',    # Medium purple
            'bg_glass': '#4A3B89',        # Glass effect purple
            'accent': '#9B59B6',          # Alice purple
            'accent_light': '#BB77D4',    # Light purple
            'text_primary': '#FFFFFF',    # White text
            'text_secondary': '#E6E6FA',  # Lavender text
            'border': '#6A5ACD'           # Slate blue border
        }
        
        # Configure main window styles
        style.configure('Glass.TFrame', 
                       background=colors['bg_glass'],
                       relief='flat',
                       borderwidth=1)
        
        style.configure('Transparent.TFrame',
                       background=colors['bg_primary'],
                       relief='flat')
        
        # Beautiful labels with purple glow effect
        style.configure('Title.TLabel',
                       background=colors['bg_primary'],
                       foreground=colors['accent_light'],
                       font=('Segoe UI', 20, 'bold'))
        
        style.configure('Subtitle.TLabel',
                       background=colors['bg_primary'],
                       foreground=colors['text_secondary'],
                       font=('Segoe UI', 10, 'italic'))
        
        style.configure('Glass.TLabel',
                       background=colors['bg_glass'],
                       foreground=colors['text_primary'],
                       font=('Segoe UI', 9))
        
        style.configure('Accent.TLabel',
                       background=colors['bg_primary'],
                       foreground=colors['accent'],
                       font=('Segoe UI', 9, 'bold'))
        
        # Glassmorphism LabelFrame
        style.configure('Glass.TLabelframe',
                       background=colors['bg_glass'],
                       bordercolor=colors['border'],
                       borderwidth=1,
                       relief='raised')
        
        style.configure('Glass.TLabelframe.Label',
                       background=colors['bg_glass'],
                       foreground=colors['accent_light'],
                       font=('Segoe UI', 10, 'bold'))
        
        # Beautiful buttons with hover effects
        style.configure('Glass.TButton',
                       background=colors['bg_secondary'],
                       foreground=colors['text_primary'],
                       bordercolor=colors['border'],
                       borderwidth=1,
                       font=('Segoe UI', 9),
                       padding=(12, 8))
        
        style.map('Glass.TButton',
                 background=[('active', colors['accent']),
                            ('pressed', colors['bg_primary'])])
        
        # Primary action button (Connect to GitHub)
        style.configure('Primary.TButton',
                       background=colors['accent'],
                       foreground='white',
                       bordercolor=colors['accent_light'],
                       borderwidth=2,
                       font=('Segoe UI', 12, 'bold'),
                       padding=(20, 12))
        
        style.map('Primary.TButton',
                 background=[('active', colors['accent_light']),
                            ('pressed', colors['bg_secondary'])])
        
        # Entry fields with glass effect
        style.configure('Glass.TEntry',
                       background=colors['bg_secondary'],
                       foreground=colors['text_primary'],
                       bordercolor=colors['border'],
                       insertcolor=colors['accent'],
                       font=('Segoe UI', 9))
        
        # Radio buttons
        style.configure('Glass.TRadiobutton',
                       background=colors['bg_glass'],
                       foreground=colors['text_primary'],
                       font=('Segoe UI', 9))
        
        style.map('Glass.TRadiobutton',
                 background=[('active', colors['bg_secondary'])])
        
        # Progress bar with Alice purple
        style.configure('Alice.Horizontal.TProgressbar',
                       background=colors['accent'],
                       troughcolor=colors['bg_secondary'],
                       borderwidth=1,
                       lightcolor=colors['accent_light'],
                       darkcolor=colors['bg_primary'])
        
        # Scrollbars
        style.configure('Glass.Vertical.TScrollbar',
                       background=colors['bg_secondary'],
                       troughcolor=colors['bg_primary'],
                       bordercolor=colors['border'])
        
        return colors  # Return colors for use in Text widgets
    
    def get_dev_type_emoji(self, dev_id):
        """Get appropriate emoji for development type"""
        emoji_map = {
            'web': '🌐',
            'python': '🐍', 
            'flutter': '📱',
            'unity': '🎮',
            'android': '🤖',
            'laravel': '🚀',
            'basic': '⚙️',
            'fastapi': '⚡',
            'nextjs': '⚛️',
            'alice-portfolio': '💜'
        }
        return emoji_map.get(dev_id, '📁')

    def load_development_types(self):
        """Load development types from the configuration file"""
        try:
            # Try to find the config file in the same directory as the script
            config_path = self.resource_path("development_types.json")
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.dev_types = json.load(f)
                print(f"Loaded {len(self.dev_types)} development types from {config_path}")
            else:
                # Use default development types if config file doesn't exist
                self.dev_types = {
                    "basic": {
                        "name": "Basic",
                        "description": "Basic project structure with minimal ignores",
                        "gitignore": [
                            "# List of ignore folder and files",
                            "/[Tt]emp/",
                            "# List of ignore files",
                            "*.exe",
                            "*.txt"
                        ],
                        "readme_template": "# PROJECT TITLE\n\nSoftware Version: [Version]\n\n## Description\nThis software is used for..."
                    },
                    "unity": {
                        "name": "Unity",
                        "description": "Unity game development project",
                        "gitignore": [
                            "# Unity generated folders and files",
                            "/[Ll]ibrary/",
                            "/[Tt]emp/",
                            "/[Ll]ogs/",
                            "/[Uu]serSettings/",
                            "/[Oo]bj/",
                            "/[Bb]uild/",
                            "/[Bb]uilds/"
                        ],
                        "readme_template": "# Unity Project\n\nUnity Version: [Your Unity Version]"
                    }
                }
                print("Using default development types")
        except Exception as e:
            print(f"Error loading development types: {e}")
            # Fallback to basic type if there's an error
            self.dev_types = {
                "basic": {
                    "name": "Basic",
                    "description": "Basic project structure",
                    "gitignore": ["# Basic gitignore", "/[Tt]emp/", "*.exe"],
                    "readme_template": "# Project\n\n## Description\nA basic project."
                }
            }

    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(os.path.dirname(sys.argv[0]))
        
        return os.path.join(base_path, relative_path)

    def auto_resize_window(self):
        """Set perfect fixed window size - no scrolling needed"""
        self.root.update_idletasks()
        
        # Perfect fixed dimensions for no-scroll experience
        window_width = 740
        window_height = 700
        
        # Center the window on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set fixed geometry - exactly like your perfect manual adjustment
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Prevent resizing to maintain perfect layout
        self.root.resizable(False, False)

    def create_widgets(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Get color scheme from styles
        colors = self.setup_custom_styles()
        
        # Main scrollable frame with glassmorphism
        main_canvas = tk.Canvas(self.root, bg=colors['bg_primary'], highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview, style="Glass.Vertical.TScrollbar")
        main_scrollable_frame = ttk.Frame(main_canvas, style="Transparent.TFrame")
        
        main_scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=main_scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        # Pack main canvas and scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")
        
        # Create content in the scrollable frame with glassmorphism padding
        content_frame = ttk.Frame(main_scrollable_frame, padding="20", style="Transparent.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Beautiful title with Alice purple glow
        title_label = ttk.Label(content_frame, text="✨ Git-OneClick v2.0.0 ✨", style="Title.TLabel")
        title_label.pack(pady=(10, 5))
        
        # Elegant subtitle with Alice signature
        subtitle_label = ttk.Label(content_frame, text="💜 Instant GitHub Repository Setup - Powered by Alice 💜", style="Subtitle.TLabel")
        subtitle_label.pack(pady=(0, 20))
        
        # User Type section with glassmorphism
        user_type_frame = ttk.LabelFrame(content_frame, text="👤 User Type", padding="15", style="Glass.TLabelframe")
        user_type_frame.pack(fill=tk.X, pady=(0, 12))
        
        ttk.Radiobutton(user_type_frame, text="🆕 First Time User (Setup Git configuration)", 
                      variable=self.user_type, value="new_user", 
                      command=self.toggle_user_fields, style="Glass.TRadiobutton").pack(anchor=tk.W, pady=4)
        ttk.Radiobutton(user_type_frame, text="✅ Existing User (Already have Git configured)", 
                      variable=self.user_type, value="existing_user", 
                      command=self.toggle_user_fields, style="Glass.TRadiobutton").pack(anchor=tk.W, pady=4)
        
        # User info section with glassmorphism (only shown for new users)
        self.user_info_frame = ttk.Frame(content_frame, style="Glass.TFrame")
        self.user_info_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Create user info fields with glassmorphism styling
        user_info_inner = ttk.Frame(self.user_info_frame, style="Glass.TFrame")
        user_info_inner.pack(fill=tk.X, padx=15, pady=10)
        
        # Git name and email in same row with beautiful styling
        user_row = ttk.Frame(user_info_inner, style="Glass.TFrame")
        user_row.pack(fill=tk.X, pady=8)
        
        # Git name (left half) with glass effect
        name_frame = ttk.Frame(user_row, style="Glass.TFrame")
        name_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        ttk.Label(name_frame, text="🔑 Git Username:", style="Accent.TLabel").pack(anchor=tk.W, pady=(0, 3))
        ttk.Entry(name_frame, textvariable=self.git_name, style="Glass.TEntry", font=('Segoe UI', 9)).pack(fill=tk.X)
        
        # Git email (right half) with glass effect
        email_frame = ttk.Frame(user_row, style="Glass.TFrame")
        email_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        ttk.Label(email_frame, text="📧 Git Email:", style="Accent.TLabel").pack(anchor=tk.W, pady=(0, 3))
        ttk.Entry(email_frame, textvariable=self.git_email, style="Glass.TEntry", font=('Segoe UI', 9)).pack(fill=tk.X)
        
        # Project Configuration section with beautiful glassmorphism
        project_frame = ttk.LabelFrame(content_frame, text="📁 Project Configuration", padding="15", style="Glass.TLabelframe")
        project_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Folder selection with glassmorphism
        folder_frame = ttk.Frame(project_frame, style="Glass.TFrame")
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(folder_frame, text="📂 Project Folder:", style="Accent.TLabel").pack(anchor=tk.W, pady=(0, 5))
        folder_row = ttk.Frame(folder_frame, style="Glass.TFrame")
        folder_row.pack(fill=tk.X, pady=(3, 0))
        
        self.folder_label = ttk.Label(folder_row, text="No folder selected", style="Glass.TLabel", relief=tk.SUNKEN, anchor=tk.W)
        self.folder_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        folder_btn = ttk.Button(folder_row, text="🔍 Browse", command=self.select_folder, style="Glass.TButton")
        folder_btn.pack(side=tk.RIGHT)
        
        # Repository URL input with glassmorphism
        repo_frame = ttk.Frame(project_frame, style="Glass.TFrame")
        repo_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(repo_frame, text="🌐 GitHub Repository URL:", style="Accent.TLabel").pack(anchor=tk.W, pady=(0, 5))
        ttk.Entry(repo_frame, textvariable=self.repo_url, style="Glass.TEntry", font=('Segoe UI', 9)).pack(fill=tk.X, pady=(3, 0))
        
        # Development Type section with glassmorphism
        self.dev_type_frame = ttk.LabelFrame(content_frame, text="⚙️ Development Type", padding="15", style="Glass.TLabelframe")
        self.dev_type_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.create_development_type_widgets()
        
        # Manage Types button with glassmorphism
        manage_btn_frame = ttk.Frame(self.dev_type_frame, style="Glass.TFrame")
        manage_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(manage_btn_frame, text="🔧 Manage Development Types", 
                  command=self.open_manage_types, style="Glass.TButton").pack()
        
        # Action buttons frame with glassmorphism
        action_frame = ttk.Frame(content_frame, style="Glass.TFrame")
        action_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Beautiful primary connect button
        connect_btn = ttk.Button(action_frame, text="🚀 Connect to GitHub 💫", 
                               command=self.start_connection, style="Primary.TButton")
        connect_btn.pack(pady=(5, 15))
        
        # Alice-themed progress bar
        self.progress_bar = ttk.Progressbar(action_frame, mode="determinate", style="Alice.Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X, pady=(0, 15))
        
        # Log area with beautiful glassmorphism
        log_frame = ttk.LabelFrame(content_frame, text="📝 Connection Log", padding="12", style="Glass.TLabelframe")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        # Create log text with glassmorphism styling
        log_container = ttk.Frame(log_frame, style="Glass.TFrame")
        log_container.pack(fill=tk.BOTH, expand=True)
        
        log_scrollbar = ttk.Scrollbar(log_container, style="Glass.Vertical.TScrollbar")
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Beautiful log text with Alice color scheme - perfect height for fixed window
        self.log_text = tk.Text(log_container, height=6, wrap=tk.WORD, 
                               yscrollcommand=log_scrollbar.set,
                               bg=colors['bg_secondary'], fg=colors['text_primary'],
                               insertbackground=colors['accent'], selectbackground=colors['accent'],
                               font=('Consolas', 9), relief=tk.FLAT, borderwidth=0)
        self.log_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        log_scrollbar.config(command=self.log_text.yview)
        
        # Beautiful status bar with Alice signature
        self.status_var = tk.StringVar(value="✨ Ready - Alice is here to help! ✨")
        status_bar = ttk.Label(content_frame, textvariable=self.status_var, 
                              style="Glass.TLabel", relief=tk.RAISED, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(8, 5))
        
        # Bind mouse wheel to main canvas
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Update scroll region after all widgets are created
        self.root.after(100, lambda: main_canvas.configure(scrollregion=main_canvas.bbox("all")))

    def create_development_type_widgets(self):
        """Create the development type selection widgets"""
        # Clear existing dev type widgets
        for widget in self.dev_type_frame.winfo_children():
            if not isinstance(widget, ttk.Button) and not isinstance(widget, ttk.Frame):
                widget.destroy()
        
        # Create beautiful development type layout with glassmorphism
        if len(self.dev_types) <= 6:
            # If 6 or fewer types, show them all without scrolling
            for dev_id, dev_info in self.dev_types.items():
                dev_row = ttk.Frame(self.dev_type_frame, style="Glass.TFrame")
                dev_row.pack(fill=tk.X, pady=3)
                
                # Add appropriate emoji for each dev type
                dev_emoji = self.get_dev_type_emoji(dev_id)
                rb = ttk.Radiobutton(dev_row, text=f"{dev_emoji} {dev_info['name']}", 
                                   variable=self.dev_type, value=dev_id, style="Glass.TRadiobutton")
                rb.pack(side=tk.LEFT)
                
                if "description" in dev_info:
                    desc_label = ttk.Label(dev_row, text=f"• {dev_info['description']}", 
                                         style="Glass.TLabel", font=("Segoe UI", 8))
                    desc_label.pack(side=tk.LEFT, padx=(10, 0))
        else:
            # If more than 6 types, use a beautiful scrollable frame with glassmorphism
            colors = self.setup_custom_styles()
            dev_canvas = tk.Canvas(self.dev_type_frame, highlightthickness=0, height=150, 
                                 bg=colors['bg_glass'])
            dev_canvas.pack(fill=tk.X, pady=(0, 8))
            
            dev_scrollbar = ttk.Scrollbar(self.dev_type_frame, orient="vertical", command=dev_canvas.yview, 
                                        style="Glass.Vertical.TScrollbar")
            dev_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, before=dev_canvas)
            
            dev_canvas.configure(yscrollcommand=dev_scrollbar.set)
            
            self.dev_scrollable_frame = ttk.Frame(dev_canvas, style="Glass.TFrame")
            canvas_window = dev_canvas.create_window((0, 0), window=self.dev_scrollable_frame, anchor="nw")
            
            # Create beautiful radio buttons with glassmorphism for each development type
            for dev_id, dev_info in self.dev_types.items():
                dev_row = ttk.Frame(self.dev_scrollable_frame, style="Glass.TFrame")
                dev_row.pack(fill=tk.X, pady=3)
                
                # Add appropriate emoji for each dev type
                dev_emoji = self.get_dev_type_emoji(dev_id)
                rb = ttk.Radiobutton(dev_row, text=f"{dev_emoji} {dev_info['name']}", 
                                   variable=self.dev_type, value=dev_id, style="Glass.TRadiobutton")
                rb.pack(side=tk.LEFT)
                
                if "description" in dev_info:
                    desc_label = ttk.Label(dev_row, text=f"• {dev_info['description']}", 
                                         style="Glass.TLabel", font=("Segoe UI", 8))
                    desc_label.pack(side=tk.LEFT, padx=(10, 0))
            
            # Configure scroll region
            def configure_dev_scroll(event=None):
                dev_canvas.configure(scrollregion=dev_canvas.bbox("all"))
                canvas_width = dev_canvas.winfo_width()
                if canvas_width > 1:
                    dev_canvas.itemconfig(canvas_window, width=canvas_width)
            
            self.dev_scrollable_frame.bind('<Configure>', configure_dev_scroll)
            dev_canvas.bind('<Configure>', configure_dev_scroll)
            self.root.after(100, configure_dev_scroll)
        
        # Set default development type
        if self.dev_types:
            if self.dev_type.get() not in self.dev_types:
                self.dev_type.set(next(iter(self.dev_types)))

    def refresh_development_types_ui(self):
        """Refresh the development types section in the main UI"""
        if self.dev_type_frame and self.dev_type_frame.winfo_exists():
            self.create_development_type_widgets()
            # Auto-resize window after refresh
            self.root.after(100, self.auto_resize_window)

    def open_manage_types(self):
        """Open dialog to manage development types with beautiful glassmorphism"""
        # Create a new top-level window with Alice styling
        manage_window = tk.Toplevel(self.root)
        manage_window.title("🔧 Manage Development Types - Alice Edition")
        manage_window.geometry("680x580")
        manage_window.resizable(True, True)
        manage_window.transient(self.root)
        manage_window.grab_set()
        
        # Apply Alice's glassmorphism to the manage window
        colors = self.setup_custom_styles()
        manage_window.configure(bg=colors['bg_primary'])
        if platform.system() == "Windows":
            try:
                manage_window.wm_attributes("-alpha", 0.95)
            except:
                pass
        
        # Center the dialog
        manage_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Create a list of current development types with glassmorphism
        types_frame = ttk.LabelFrame(manage_window, text="📋 Current Development Types", padding="15", style="Glass.TLabelframe")
        types_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create a listbox to display types with Alice styling
        listbox_frame = ttk.Frame(types_frame, style="Glass.TFrame")
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame, style="Glass.Vertical.TScrollbar")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, font=("Segoe UI", 10),
                           bg=colors['bg_secondary'], fg=colors['text_primary'],
                           selectbackground=colors['accent'], selectforeground='white',
                           borderwidth=0, relief=tk.FLAT)
        listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar.config(command=listbox.yview)
        
        # Populate listbox with types
        def refresh_listbox():
            listbox.delete(0, tk.END)
            for dev_id, dev_info in self.dev_types.items():
                listbox.insert(tk.END, f"{dev_info['name']} ({dev_id})")
        
        refresh_listbox()
        
        # Buttons for adding, editing, and removing types with glassmorphism
        btn_frame = ttk.Frame(types_frame, style="Glass.TFrame")
        btn_frame.pack(fill=tk.X, pady=12)
        
        ttk.Button(btn_frame, text="➕ Add New Type", 
                command=lambda: self.edit_type_dialog(manage_window, None, refresh_listbox), 
                style="Glass.TButton").pack(side=tk.LEFT, padx=6)
        
        def get_selected_type_id():
            selection = listbox.curselection()
            if selection:
                selected_text = listbox.get(selection[0])
                return selected_text.split(" (")[-1][:-1]
            return None
        
        ttk.Button(btn_frame, text="✏️ Edit Selected", 
                command=lambda: self.edit_type_dialog(manage_window, get_selected_type_id(), refresh_listbox), 
                style="Glass.TButton").pack(side=tk.LEFT, padx=6)
        
        ttk.Button(btn_frame, text="🗑️ Remove Selected", 
                command=lambda: self.remove_type(get_selected_type_id(), refresh_listbox), 
                style="Glass.TButton").pack(side=tk.LEFT, padx=6)
        
        # Import/Export buttons with glassmorphism
        io_frame = ttk.Frame(types_frame, style="Glass.TFrame")
        io_frame.pack(fill=tk.X, pady=8)
        
        ttk.Button(io_frame, text="📥 Import Types", 
                command=lambda: self.import_types(refresh_listbox), 
                style="Glass.TButton").pack(side=tk.LEFT, padx=6)
        
        ttk.Button(io_frame, text="📤 Export All Types", 
                command=self.export_types, 
                style="Glass.TButton").pack(side=tk.LEFT, padx=6)
        
        # Done button with Alice styling
        ttk.Button(manage_window, text="✅ Done", 
                command=manage_window.destroy, 
                style="Primary.TButton").pack(pady=15)

    def edit_type_dialog(self, parent, type_id=None, refresh_callback=None):
        """Open dialog to add or edit a development type with glassmorphism"""
        is_new = type_id is None
        
        dialog = tk.Toplevel(parent)
        dialog.title(f"{'➕ Add' if is_new else '✏️ Edit'} Development Type - Alice Edition")
        dialog.geometry("620x720")
        dialog.resizable(True, True)
        dialog.transient(parent)
        dialog.grab_set()
        
        # Apply Alice's glassmorphism to the dialog
        colors = self.setup_custom_styles()
        dialog.configure(bg=colors['bg_primary'])
        if platform.system() == "Windows":
            try:
                dialog.wm_attributes("-alpha", 0.95)
            except:
                pass
        
        # Variables
        type_id_var = tk.StringVar(value=type_id if not is_new else "")
        type_name_var = tk.StringVar(value=self.dev_types.get(type_id, {}).get("name", "") if not is_new else "")
        type_desc_var = tk.StringVar(value=self.dev_types.get(type_id, {}).get("description", "") if not is_new else "")
        
        # Main frame with glassmorphism
        main_frame = ttk.Frame(dialog, padding="15", style="Glass.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Type ID with glassmorphism
        id_frame = ttk.Frame(main_frame, style="Glass.TFrame")
        id_frame.pack(fill=tk.X, pady=8)
        
        ttk.Label(id_frame, text="🏷️ Type ID:", style="Accent.TLabel").pack(side=tk.LEFT)
        id_entry = ttk.Entry(id_frame, textvariable=type_id_var, style="Glass.TEntry")
        id_entry.pack(side=tk.LEFT, padx=8, fill=tk.X, expand=True)
        
        # Disable ID field if editing
        if not is_new:
            id_entry.config(state=tk.DISABLED)
        
        # Type Name with glassmorphism
        name_frame = ttk.Frame(main_frame, style="Glass.TFrame")
        name_frame.pack(fill=tk.X, pady=8)
        
        ttk.Label(name_frame, text="📝 Display Name:", style="Accent.TLabel").pack(side=tk.LEFT)
        ttk.Entry(name_frame, textvariable=type_name_var, style="Glass.TEntry").pack(side=tk.LEFT, padx=8, fill=tk.X, expand=True)
        
        # Type Description with glassmorphism
        desc_frame = ttk.Frame(main_frame, style="Glass.TFrame")
        desc_frame.pack(fill=tk.X, pady=8)
        
        ttk.Label(desc_frame, text="📄 Description:", style="Accent.TLabel").pack(side=tk.LEFT)
        ttk.Entry(desc_frame, textvariable=type_desc_var, style="Glass.TEntry").pack(side=tk.LEFT, padx=8, fill=tk.X, expand=True)
        
        # .gitignore content with glassmorphism
        gitignore_frame = ttk.LabelFrame(main_frame, text="📝 .gitignore Content", padding="10", style="Glass.TLabelframe")
        gitignore_frame.pack(fill=tk.BOTH, expand=True, pady=8)
        
        gitignore_scroll = ttk.Scrollbar(gitignore_frame, style="Glass.Vertical.TScrollbar")
        gitignore_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        gitignore_text = tk.Text(gitignore_frame, height=10, wrap=tk.WORD, yscrollcommand=gitignore_scroll.set,
                               bg=colors['bg_secondary'], fg=colors['text_primary'],
                               insertbackground=colors['accent'], selectbackground=colors['accent'],
                               font=('Consolas', 9), relief=tk.FLAT, borderwidth=0)
        gitignore_text.pack(fill=tk.BOTH, expand=True)
        gitignore_scroll.config(command=gitignore_text.yview)
        
        # README template with glassmorphism
        readme_frame = ttk.LabelFrame(main_frame, text="📄 README.md Template", padding="10", style="Glass.TLabelframe")
        readme_frame.pack(fill=tk.BOTH, expand=True, pady=8)
        
        readme_scroll = ttk.Scrollbar(readme_frame, style="Glass.Vertical.TScrollbar")
        readme_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        readme_text = tk.Text(readme_frame, height=10, wrap=tk.WORD, yscrollcommand=readme_scroll.set,
                             bg=colors['bg_secondary'], fg=colors['text_primary'],
                             insertbackground=colors['accent'], selectbackground=colors['accent'],
                             font=('Segoe UI', 9), relief=tk.FLAT, borderwidth=0)
        readme_text.pack(fill=tk.BOTH, expand=True)
        readme_scroll.config(command=readme_text.yview)
        
        # Fill the text areas if editing
        if not is_new:
            # Gitignore content
            gitignore_content = "\n".join(self.dev_types.get(type_id, {}).get("gitignore", []))
            gitignore_text.insert("1.0", gitignore_content)
            
            # README template
            readme_template = self.dev_types.get(type_id, {}).get("readme_template", "")
            readme_text.insert("1.0", readme_template)
        
        # Buttons with glassmorphism
        btn_frame = ttk.Frame(main_frame, style="Glass.TFrame")
        btn_frame.pack(fill=tk.X, pady=15)
        
        ttk.Button(btn_frame, text="❌ Cancel", 
                command=dialog.destroy, style="Glass.TButton").pack(side=tk.RIGHT, padx=8)
        
        ttk.Button(btn_frame, text="💾 Save", 
                command=lambda: self.save_type(
                    dialog, 
                    type_id_var.get(), 
                    type_name_var.get(), 
                    type_desc_var.get(), 
                    gitignore_text.get("1.0", tk.END), 
                    readme_text.get("1.0", tk.END),
                    refresh_callback
                ), style="Primary.TButton").pack(side=tk.RIGHT, padx=8)

    def save_type(self, dialog, type_id, name, description, gitignore, readme, refresh_callback=None):
        """Save a development type to the configuration"""
        if not type_id:
            messagebox.showwarning("Invalid Input", "Type ID is required.")
            return
        
        if not name:
            messagebox.showwarning("Invalid Input", "Display Name is required.")
            return
        
        # Process gitignore content
        gitignore_lines = [line for line in gitignore.splitlines() if line.strip()]
        
        # Save to configuration
        self.dev_types[type_id] = {
            "name": name,
            "description": description,
            "gitignore": gitignore_lines,
            "readme_template": readme.strip()
        }
        
        # Save to file
        self.save_development_types()
        
        # Close dialog
        dialog.destroy()
        
        # Refresh UI components
        if refresh_callback:
            refresh_callback()
        self.refresh_development_types_ui()

    def remove_type(self, type_id, refresh_callback=None):
        """Remove a development type from the configuration"""
        if not type_id:
            messagebox.showwarning("No Selection", "Please select a development type to remove.")
            return
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to remove the '{self.dev_types.get(type_id, {}).get('name', type_id)}' development type?"):
            # Remove from configuration
            if type_id in self.dev_types:
                del self.dev_types[type_id]
                
                # Save to file
                self.save_development_types()
                
                # Refresh UI components
                if refresh_callback:
                    refresh_callback()
                self.refresh_development_types_ui()

    def import_types(self, refresh_callback=None):
        """Import development types from a JSON file"""
        file_path = filedialog.askopenfilename(
            title="Import Development Types",
            filetypes=[("JSON files", "*.json"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_types = json.load(f)
                
                # Validate format
                if not isinstance(imported_types, dict):
                    messagebox.showerror("Invalid Format", "The selected file does not contain valid development types.")
                    return
                
                # Ask for import mode
                if messagebox.askyesno("Import Mode", "Do you want to merge with existing types? Click 'Yes' to merge, or 'No' to replace all existing types."):
                    # Merge with existing types
                    self.dev_types.update(imported_types)
                else:
                    # Replace all existing types
                    self.dev_types = imported_types
                
                # Save to file
                self.save_development_types()
                
                # Refresh UI components
                if refresh_callback:
                    refresh_callback()
                self.refresh_development_types_ui()
                
                messagebox.showinfo("Import Successful", f"Successfully imported {len(imported_types)} development types.")
            
            except Exception as e:
                messagebox.showerror("Import Error", f"An error occurred during import: {str(e)}")

    def export_types(self):
        """Export all development types to a JSON file"""
        file_path = filedialog.asksaveasfilename(
            title="Export Development Types",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.dev_types, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Export Successful", f"Successfully exported {len(self.dev_types)} development types to {file_path}.")
            
            except Exception as e:
                messagebox.showerror("Export Error", f"An error occurred during export: {str(e)}")

    def save_development_types(self):
        """Save development types to the configuration file"""
        try:
            config_path = self.resource_path("development_types.json")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.dev_types, f, indent=2, ensure_ascii=False)
            
            print(f"Saved {len(self.dev_types)} development types to {config_path}")
        
        except Exception as e:
            print(f"Error saving development types: {e}")
            messagebox.showwarning("Save Error", f"Could not save development types: {str(e)}")

    def toggle_user_fields(self):
        """Show or hide user info fields based on user type"""
        if self.user_type.get() == "new_user":
            self.user_info_frame.pack(fill=tk.X, pady=(0, 10), before=self.user_info_frame.master.winfo_children()[2])
        else:
            self.user_info_frame.pack_forget()

    def check_git(self):
        """Check if Git is installed"""
        try:
            result = subprocess.run(["git", "--version"], check=True, capture_output=True, text=True)
            version_output = result.stdout
            
            self.log(f"Git detected: {version_output.strip()}")
            return True
                
        except (subprocess.SubprocessError, FileNotFoundError):
            self.show_git_missing_dialog()
            return False

    def show_git_missing_dialog(self):
        """Show dialog when Git is not installed"""
        git_dialog = tk.Toplevel(self.root)
        git_dialog.title("Git Not Found")
        git_dialog.geometry("500x320")
        git_dialog.resizable(False, False)
        git_dialog.transient(self.root)
        git_dialog.grab_set()
        
        # Center the dialog
        git_dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + self.root.winfo_width()//2 - 250,
            self.root.winfo_rooty() + self.root.winfo_height()//2 - 160
        ))
        
        # Warning icon
        warning_frame = ttk.Frame(git_dialog)
        warning_frame.pack(pady=(20, 0))
        
        # Use Unicode warning symbol
        warning_label = ttk.Label(warning_frame, text="⚠️", font=("Helvetica", 48))
        warning_label.pack()
        
        # Message
        message_frame = ttk.Frame(git_dialog, padding=20)
        message_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(message_frame, text="Git is not installed or not found!", 
                 font=("Helvetica", 12, "bold")).pack(pady=(0, 10))
        
        message_text = "This application requires Git to setup your repository.\n\n" + \
                      "Please install Git from the official website."
        ttk.Label(message_frame, text=message_text, wraplength=400).pack()
        
        # Download link
        link_frame = ttk.Frame(message_frame)
        link_frame.pack(pady=10)
        
        ttk.Label(link_frame, text="Download from:").pack(side=tk.LEFT)
        
        # Create hyperlink style labels
        link_style = ttk.Style()
        link_style.configure("Link.TLabel", foreground="blue", font=("Helvetica", 10, "underline"))
        
        git_link = ttk.Label(link_frame, text="git-scm.com", style="Link.TLabel", cursor="hand2")
        git_link.pack(side=tk.LEFT, padx=5)
        git_link.bind("<Button-1>", lambda e: self.open_url("https://git-scm.com/downloads"))
        
        # Buttons
        button_frame = ttk.Frame(git_dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Check Again", command=lambda: self.recheck_git(git_dialog)).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Continue Anyway", command=git_dialog.destroy).pack(side=tk.LEFT, padx=10)
        
        self.log("ERROR: Git not found. Please install Git to continue.")
    
    def open_url(self, url):
        """Open URL in default browser"""
        import webbrowser
        webbrowser.open(url)
    
    def recheck_git(self, dialog):
        """Recheck if Git is installed after user potentially installed it"""
        if self.check_git():
            dialog.destroy()
            messagebox.showinfo("Git Detected", "Git has been successfully detected on your system.")
        # If Git is still not found, the check_git method will show the dialog again

    def select_folder(self):
        """Select folder for Git repository"""
        directory = filedialog.askdirectory(title="Select Project Folder")
        if directory:
            self.folder_path = directory
            self.folder_label.config(text=directory)
            self.log(f"Project folder set to: {directory}")

    def log(self, message):
        """Add message to log area"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        print(message)  # Also print to console for debugging

    def update_status(self, message):
        """Update status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()

    def validate_inputs(self):
        """Validate user inputs before connecting"""
        if not self.folder_path:
            messagebox.showwarning("No Folder", "Please select a project folder.")
            return False
        
        if not self.repo_url.get():
            messagebox.showwarning("No Repository URL", "Please enter a GitHub repository URL.")
            return False
        
        if self.user_type.get() == "new_user":
            if not self.git_name.get():
                messagebox.showwarning("Missing Information", "Please enter your Git username.")
                return False
            if not self.git_email.get():
                messagebox.showwarning("Missing Information", "Please enter your Git email.")
                return False
        
        if not self.git_installed:
            result = messagebox.askokcancel(
                "Git Not Detected", 
                "Git is required for this process. The operation will likely fail without Git installed. Continue anyway?"
            )
            if not result:
                return False
        
        return True

    def start_connection(self):
        """Start the GitHub connection process"""
        if not self.validate_inputs():
            return
        
        # Disable UI elements during process
        self.root.config(cursor="wait")
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.config(state=tk.DISABLED)
        
        # Reset progress bar
        self.progress_bar["value"] = 0
        
        # Start process in a separate thread to keep UI responsive
        connection_thread = Thread(target=self.perform_connection)
        connection_thread.daemon = True
        connection_thread.start()

    def perform_connection(self):
        """Perform the GitHub connection process"""
        try:
            self.log("Starting GitHub connection process...")
            self.update_status("Connecting...")
            
            # Step 1: Create appropriate .gitignore and README based on development type
            self.progress_bar["value"] = 10
            self.create_git_files()
            
            # Step 2: Initialize Git repository
            self.progress_bar["value"] = 30
            self.initialize_git()
            
            # Step 3: Configure Git (for new users)
            self.progress_bar["value"] = 50
            if self.user_type.get() == "new_user":
                self.configure_git()
            
            # Step 4: Add and commit files
            self.progress_bar["value"] = 70
            self.commit_files()
            
            # Step 5: Connect to GitHub and push
            self.progress_bar["value"] = 90
            self.push_to_github()
            
            # Complete
            self.progress_bar["value"] = 100
            self.update_status("Connection completed successfully.")
            messagebox.showinfo("Success", "GitHub repository setup completed successfully!")
            
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during the connection process: {str(e)}")
            self.update_status("Connection failed.")
        
        finally:
            # Re-enable UI elements
            self.root.config(cursor="")
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Button):
                    widget.config(state=tk.NORMAL)

    def create_git_files(self):
        """Create .gitignore and README.md based on selected development type"""
        self.log(f"Creating Git files for {self.dev_type.get()} development type...")
        
        # Change to the project directory
        os.chdir(self.folder_path)
        
        # Get selected development type
        dev_type_id = self.dev_type.get()
        dev_type = self.dev_types.get(dev_type_id, {})
        
        if not dev_type:
            raise Exception(f"Development type '{dev_type_id}' not found in configuration.")
        
        # Create .gitignore based on development type
        gitignore_content = "\n".join(dev_type.get("gitignore", []))
        with open(".gitignore", "w") as f:
            f.write(gitignore_content)
        
        # Create README.md based on development type
        readme_content = dev_type.get("readme_template", "# Project\n\n## Description\nProject description.")
        with open("README.md", "w") as f:
            f.write(readme_content)
        
        self.log(f"Created .gitignore and README.md files for {dev_type.get('name', dev_type_id)} development")

    def initialize_git(self):
        """Initialize Git repository"""
        self.log("Initializing Git repository...")
        
        # Initialize git repository
        subprocess.run(["git", "init"], check=True, capture_output=True, text=True)
        self.log("Git repository initialized")

    def configure_git(self):
        """Configure Git for new users"""
        self.log("Configuring Git user settings...")
        
        # Set user name
        subprocess.run(["git", "config", "--global", "user.name", self.git_name.get()], 
                       check=True, capture_output=True, text=True)
        
        # Set user email
        subprocess.run(["git", "config", "--global", "user.email", self.git_email.get()], 
                       check=True, capture_output=True, text=True)
        
        self.log(f"Git configured with username: {self.git_name.get()} and email: {self.git_email.get()}")

    def commit_files(self):
        """Add and commit files to the repository"""
        self.log("Adding files to repository...")
        
        # Remove cached files to respect new .gitignore
        try:
            subprocess.run(["git", "rm", "-r", "--cached", "."], 
                        check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError:
            # This might fail if no files were previously tracked, which is fine
            pass
        
        # Add all files respecting .gitignore
        subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
        
        # Initial commit
        subprocess.run(["git", "commit", "-m", "Initial commit"], 
                     check=True, capture_output=True, text=True)
        
        # Create main branch
        subprocess.run(["git", "branch", "-M", "main"], 
                     check=True, capture_output=True, text=True)
        
        self.log("Files committed to repository")

    def push_to_github(self):
        """Connect to GitHub repository and push"""
        self.log("Connecting to GitHub repository...")
        
        # Add remote origin
        subprocess.run(["git", "remote", "add", "origin", self.repo_url.get()], 
                     check=True, capture_output=True, text=True)
        
        try:
            # Push to GitHub
            self.log("Pushing to GitHub (this may take a moment)...")
            result = subprocess.run(["git", "push", "-u", "origin", "main"], 
                                 check=True, capture_output=True, text=True)
            
            self.log("Successfully pushed to GitHub repository")
            self.log(f"Output: {result.stdout}")
            
        except subprocess.CalledProcessError as e:
            error_output = e.stderr if e.stderr else "No detailed error information available"
            self.log(f"Error during push: {error_output}")
            
            # Check for common errors
            if "Authentication failed" in error_output:
                self.log("HINT: Authentication failed. Make sure you have the correct permissions and credentials.")
                self.log("For first-time users, you might need to set up a Personal Access Token (PAT) in GitHub.")
                
                raise Exception("GitHub authentication failed. Check credentials and permissions.")
            else:
                raise Exception(f"Failed to push to GitHub: {error_output}")


if __name__ == "__main__":
    root = tk.Tk()
    app = GitOneClickGUI(root)
    root.mainloop()