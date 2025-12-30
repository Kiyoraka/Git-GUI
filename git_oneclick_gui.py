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
        self.root.title("Git-OneClick v2.0.0")
        self.root.resizable(True, True)

        # Glassmorphism setup
        self.setup_glassmorphism()

        # Set window size for wizard layout
        self.root.minsize(700, 550)
        self.root.maxsize(700, 550)

        # Load development types
        self.dev_types = {}
        self.load_development_types()

        # Variables
        self.folder_path = ""
        self.repo_url = tk.StringVar(value="")
        self.user_type = tk.StringVar(value="new_user")
        self.dev_type = tk.StringVar(value="basic")
        self.git_name = tk.StringVar(value="")
        self.git_email = tk.StringVar(value="")
        self.git_installed = False

        # Wizard step management
        self.current_step = 1
        self.total_steps = 4
        self.step_frames = {}

        # Store references
        self.dev_type_frame = None

        # Create GUI elements
        self.create_widgets()

        # Auto-resize window
        self.auto_resize_window()

        # Check for Git installation
        self.git_installed = self.check_git()

    def setup_glassmorphism(self):
        """Setup glassmorphism effects and styling"""
        if platform.system() == "Windows":
            try:
                self.root.wm_attributes("-alpha", 0.95)
                self.root.configure(bg='#0A1929')  # Deep Navy base
            except:
                self.root.configure(bg='#0A1929')
        else:
            self.root.configure(bg='#0A1929')
            try:
                self.root.wm_attributes("-alpha", 0.93)
            except:
                pass

        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Create Cyan Dark glassmorphism TTK styles"""
        style = ttk.Style()

        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')

        # Cyan Dark palette
        colors = {
            'bg_primary': '#0A1929',      # Deep Navy
            'bg_secondary': '#132F4C',    # Dark Blue
            'bg_glass': '#1E4976',        # Glass Blue
            'accent': '#00D9FF',          # Cyan
            'accent_hover': '#00B8D9',    # Darker Cyan
            'text_primary': '#FFFFFF',    # White
            'text_secondary': '#B2BAC2',  # Gray
            'border': '#2196F3',          # Blue border
            'success': '#4CAF50',         # Green (completed)
            'inactive': '#546E7A'         # Gray (inactive steps)
        }

        # Configure styles
        style.configure('Glass.TFrame',
                       background=colors['bg_glass'],
                       relief='flat',
                       borderwidth=1)

        style.configure('Transparent.TFrame',
                       background=colors['bg_primary'],
                       relief='flat')

        style.configure('Title.TLabel',
                       background=colors['bg_primary'],
                       foreground=colors['accent'],
                       font=('Segoe UI', 20, 'bold'))

        style.configure('Subtitle.TLabel',
                       background=colors['bg_primary'],
                       foreground=colors['text_secondary'],
                       font=('Segoe UI', 10))

        style.configure('Glass.TLabel',
                       background=colors['bg_glass'],
                       foreground=colors['text_primary'],
                       font=('Segoe UI', 9))

        style.configure('Accent.TLabel',
                       background=colors['bg_primary'],
                       foreground=colors['accent'],
                       font=('Segoe UI', 9, 'bold'))

        style.configure('Step.TLabel',
                       background=colors['bg_primary'],
                       foreground=colors['text_secondary'],
                       font=('Segoe UI', 9))

        style.configure('StepActive.TLabel',
                       background=colors['bg_primary'],
                       foreground=colors['accent'],
                       font=('Segoe UI', 9, 'bold'))

        style.configure('Glass.TLabelframe',
                       background=colors['bg_glass'],
                       bordercolor=colors['border'],
                       borderwidth=1,
                       relief='raised')

        style.configure('Glass.TLabelframe.Label',
                       background=colors['bg_glass'],
                       foreground=colors['accent'],
                       font=('Segoe UI', 10, 'bold'))

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

        style.configure('Primary.TButton',
                       background=colors['accent'],
                       foreground='white',
                       bordercolor=colors['accent_hover'],
                       borderwidth=2,
                       font=('Segoe UI', 11, 'bold'),
                       padding=(20, 10))

        style.map('Primary.TButton',
                 background=[('active', colors['accent_hover']),
                            ('pressed', colors['bg_secondary'])])

        style.configure('Nav.TButton',
                       background=colors['bg_secondary'],
                       foreground=colors['text_primary'],
                       bordercolor=colors['border'],
                       borderwidth=1,
                       font=('Segoe UI', 10),
                       padding=(15, 8))

        style.map('Nav.TButton',
                 background=[('active', colors['accent']),
                            ('pressed', colors['bg_primary'])])

        style.configure('Glass.TRadiobutton',
                       background=colors['bg_glass'],
                       foreground=colors['text_primary'],
                       font=('Segoe UI', 9))

        style.map('Glass.TRadiobutton',
                 background=[('active', colors['bg_secondary'])])

        style.configure('Cyan.Horizontal.TProgressbar',
                       background=colors['accent'],
                       troughcolor=colors['bg_secondary'],
                       borderwidth=1,
                       lightcolor=colors['accent_hover'],
                       darkcolor=colors['bg_primary'])

        style.configure('Glass.Vertical.TScrollbar',
                       background=colors['bg_secondary'],
                       troughcolor=colors['bg_primary'],
                       bordercolor=colors['border'])

        return colors

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
        }
        return emoji_map.get(dev_id, '📁')

    def load_development_types(self):
        """Load development types from configuration file"""
        try:
            config_path = self.resource_path("development_types.json")

            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.dev_types = json.load(f)
            else:
                self.dev_types = {
                    "basic": {
                        "name": "Basic",
                        "description": "Basic project structure",
                        "gitignore": ["# Basic gitignore", "/[Tt]emp/", "*.exe"],
                        "readme_template": "# Project\n\n## Description\nA basic project."
                    }
                }
        except Exception as e:
            print(f"Error loading development types: {e}")
            self.dev_types = {
                "basic": {
                    "name": "Basic",
                    "description": "Basic project structure",
                    "gitignore": ["# Basic gitignore", "/[Tt]emp/", "*.exe"],
                    "readme_template": "# Project\n\n## Description\nA basic project."
                }
            }

    def resource_path(self, relative_path):
        """Get absolute path to resource"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(os.path.dirname(sys.argv[0]))

        return os.path.join(base_path, relative_path)

    def auto_resize_window(self):
        """Set fixed window size and center"""
        self.root.update_idletasks()

        window_width = 700
        window_height = 550

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)

    def create_widgets(self):
        """Create wizard stepper UI"""
        for widget in self.root.winfo_children():
            widget.destroy()

        colors = self.setup_custom_styles()
        self.colors = colors

        # Main container
        main_frame = ttk.Frame(self.root, padding="15", style="Transparent.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="⚡ Git-OneClick v2.0.0", style="Title.TLabel")
        title_label.pack(pady=(5, 3))

        subtitle_label = ttk.Label(main_frame, text="Quick Repository Setup", style="Subtitle.TLabel")
        subtitle_label.pack(pady=(0, 15))

        # ===== STEPPER NAVIGATION =====
        stepper_frame = ttk.Frame(main_frame, style="Transparent.TFrame")
        stepper_frame.pack(fill=tk.X, pady=(0, 15))

        self.step_indicators = []
        self.step_labels = []
        step_names = ['Setup', 'Project', 'Dev Type', 'Connect']

        # Create stepper with circles and lines
        stepper_inner = ttk.Frame(stepper_frame, style="Transparent.TFrame")
        stepper_inner.pack()

        for i, name in enumerate(step_names):
            step_container = ttk.Frame(stepper_inner, style="Transparent.TFrame")
            step_container.pack(side=tk.LEFT)

            # Circle indicator
            canvas = tk.Canvas(step_container, width=30, height=30,
                             bg=colors['bg_primary'], highlightthickness=0)
            canvas.pack()

            # Draw circle
            if i + 1 == self.current_step:
                circle = canvas.create_oval(3, 3, 27, 27, fill=colors['accent'], outline=colors['accent'])
                canvas.create_text(15, 15, text=str(i+1), fill='white', font=('Segoe UI', 10, 'bold'))
            else:
                circle = canvas.create_oval(3, 3, 27, 27, fill=colors['bg_secondary'], outline=colors['inactive'])
                canvas.create_text(15, 15, text=str(i+1), fill=colors['inactive'], font=('Segoe UI', 10))

            self.step_indicators.append(canvas)

            # Step label
            label_style = "StepActive.TLabel" if i + 1 == self.current_step else "Step.TLabel"
            label = ttk.Label(step_container, text=name, style=label_style)
            label.pack(pady=(3, 0))
            self.step_labels.append(label)

            # Add connecting line (except for last step)
            if i < len(step_names) - 1:
                line_canvas = tk.Canvas(stepper_inner, width=60, height=30,
                                       bg=colors['bg_primary'], highlightthickness=0)
                line_canvas.pack(side=tk.LEFT)
                line_canvas.create_line(0, 15, 60, 15, fill=colors['inactive'], width=2)

        # ===== STEP CONTENT AREA =====
        self.content_frame = ttk.Frame(main_frame, style="Glass.TFrame")
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create all step frames
        self.create_step_frames()

        # ===== NAVIGATION BUTTONS =====
        nav_frame = ttk.Frame(main_frame, style="Transparent.TFrame")
        nav_frame.pack(fill=tk.X, pady=(10, 5))

        self.back_btn = ttk.Button(nav_frame, text="← Back", command=self.prev_step, style="Nav.TButton")
        self.back_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = ttk.Button(nav_frame, text="Next →", command=self.next_step, style="Nav.TButton")
        self.next_btn.pack(side=tk.RIGHT, padx=5)

        # ===== PROGRESS BAR =====
        progress_frame = ttk.Frame(main_frame, style="Transparent.TFrame")
        progress_frame.pack(fill=tk.X, pady=(5, 0))

        self.progress_bar = ttk.Progressbar(progress_frame, mode="determinate", style="Cyan.Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        self.progress_bar["value"] = 25  # Step 1 of 4

        # Status bar
        self.status_var = tk.StringVar(value="Step 1 of 4 - Configure your settings")
        status_bar = ttk.Label(progress_frame, textvariable=self.status_var, style="Glass.TLabel")
        status_bar.pack(fill=tk.X)

        # Show first step
        self.show_step(1)

    def create_step_frames(self):
        """Create all step content frames"""
        colors = self.colors

        # ===== STEP 1: Setup =====
        step1 = ttk.Frame(self.content_frame, padding="15", style="Glass.TFrame")
        self.step_frames[1] = step1

        user_type_frame = ttk.LabelFrame(step1, text="User Type", padding="15", style="Glass.TLabelframe")
        user_type_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Radiobutton(user_type_frame, text="🆕 First Time User (Setup Git configuration)",
                      variable=self.user_type, value="new_user",
                      command=self.toggle_user_fields, style="Glass.TRadiobutton").pack(anchor=tk.W, pady=4)
        ttk.Radiobutton(user_type_frame, text="✅ Existing User (Already have Git configured)",
                      variable=self.user_type, value="existing_user",
                      command=self.toggle_user_fields, style="Glass.TRadiobutton").pack(anchor=tk.W, pady=4)

        self.user_info_frame = ttk.LabelFrame(step1, text="Git Credentials", padding="15", style="Glass.TLabelframe")
        self.user_info_frame.pack(fill=tk.X, pady=(0, 10))

        user_row = ttk.Frame(self.user_info_frame, style="Glass.TFrame")
        user_row.pack(fill=tk.X, pady=5)

        name_frame = ttk.Frame(user_row, style="Glass.TFrame")
        name_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        ttk.Label(name_frame, text="🔑 Git Username:", style="Accent.TLabel").pack(anchor=tk.W, pady=(0, 3))
        tk.Entry(name_frame, textvariable=self.git_name,
                bg=colors['bg_secondary'], fg=colors['text_primary'],
                insertbackground=colors['accent'], selectbackground=colors['accent'],
                font=('Segoe UI', 9), relief=tk.FLAT, borderwidth=1,
                highlightthickness=1, highlightcolor=colors['border'], highlightbackground=colors['bg_secondary']).pack(fill=tk.X)

        email_frame = ttk.Frame(user_row, style="Glass.TFrame")
        email_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        ttk.Label(email_frame, text="📧 Git Email:", style="Accent.TLabel").pack(anchor=tk.W, pady=(0, 3))
        tk.Entry(email_frame, textvariable=self.git_email,
                bg=colors['bg_secondary'], fg=colors['text_primary'],
                insertbackground=colors['accent'], selectbackground=colors['accent'],
                font=('Segoe UI', 9), relief=tk.FLAT, borderwidth=1,
                highlightthickness=1, highlightcolor=colors['border'], highlightbackground=colors['bg_secondary']).pack(fill=tk.X)

        # ===== STEP 2: Project =====
        step2 = ttk.Frame(self.content_frame, padding="15", style="Glass.TFrame")
        self.step_frames[2] = step2

        project_frame = ttk.LabelFrame(step2, text="Project Configuration", padding="15", style="Glass.TLabelframe")
        project_frame.pack(fill=tk.X, pady=(0, 15))

        folder_frame = ttk.Frame(project_frame, style="Glass.TFrame")
        folder_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(folder_frame, text="📂 Project Folder:", style="Accent.TLabel").pack(anchor=tk.W, pady=(0, 5))
        folder_row = ttk.Frame(folder_frame, style="Glass.TFrame")
        folder_row.pack(fill=tk.X, pady=(3, 0))

        self.folder_label = tk.Label(folder_row, text="No folder selected",
                                     bg=colors['bg_secondary'], fg=colors['text_primary'],
                                     font=('Segoe UI', 9), anchor=tk.W, padx=5, pady=4,
                                     relief=tk.FLAT, borderwidth=1,
                                     highlightthickness=1, highlightcolor=colors['border'], highlightbackground=colors['bg_secondary'])
        self.folder_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        folder_btn = ttk.Button(folder_row, text="🔍 Browse", command=self.select_folder, style="Glass.TButton")
        folder_btn.pack(side=tk.RIGHT)

        repo_frame = ttk.Frame(project_frame, style="Glass.TFrame")
        repo_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(repo_frame, text="🌐 GitHub Repository URL:", style="Accent.TLabel").pack(anchor=tk.W, pady=(0, 5))
        tk.Entry(repo_frame, textvariable=self.repo_url,
                bg=colors['bg_secondary'], fg=colors['text_primary'],
                insertbackground=colors['accent'], selectbackground=colors['accent'],
                font=('Segoe UI', 9), relief=tk.FLAT, borderwidth=1,
                highlightthickness=1, highlightcolor=colors['border'], highlightbackground=colors['bg_secondary']).pack(fill=tk.X, pady=(3, 0))

        # ===== STEP 3: Dev Type =====
        step3 = ttk.Frame(self.content_frame, padding="15", style="Glass.TFrame")
        self.step_frames[3] = step3

        self.dev_type_frame = ttk.LabelFrame(step3, text="Select Development Type", padding="15", style="Glass.TLabelframe")
        self.dev_type_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.create_development_type_widgets()

        manage_btn_frame = ttk.Frame(step3, style="Glass.TFrame")
        manage_btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(manage_btn_frame, text="🔧 Manage Development Types",
                  command=self.open_manage_types, style="Glass.TButton").pack()

        # ===== STEP 4: Connect =====
        step4 = ttk.Frame(self.content_frame, padding="15", style="Glass.TFrame")
        self.step_frames[4] = step4

        connect_btn = ttk.Button(step4, text="🚀 Connect to GitHub",
                               command=self.start_connection, style="Primary.TButton")
        connect_btn.pack(pady=(10, 15))

        self.connect_progress = ttk.Progressbar(step4, mode="determinate", style="Cyan.Horizontal.TProgressbar")
        self.connect_progress.pack(fill=tk.X, pady=(0, 15))

        log_frame = ttk.LabelFrame(step4, text="📝 Connection Log", padding="12", style="Glass.TLabelframe")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        log_container = ttk.Frame(log_frame, style="Glass.TFrame")
        log_container.pack(fill=tk.BOTH, expand=True)

        log_scrollbar = ttk.Scrollbar(log_container, style="Glass.Vertical.TScrollbar")
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(log_container, height=8, wrap=tk.WORD,
                               yscrollcommand=log_scrollbar.set,
                               bg=colors['bg_secondary'], fg=colors['text_primary'],
                               insertbackground=colors['accent'], selectbackground=colors['accent'],
                               font=('Consolas', 9), relief=tk.FLAT, borderwidth=0)
        self.log_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        log_scrollbar.config(command=self.log_text.yview)

    def show_step(self, step_num):
        """Show specified step and update UI"""
        # Hide all steps
        for frame in self.step_frames.values():
            frame.pack_forget()

        # Show current step
        self.step_frames[step_num].pack(fill=tk.BOTH, expand=True)
        self.current_step = step_num

        # Update stepper indicators
        colors = self.colors
        step_names = ['Setup', 'Project', 'Dev Type', 'Connect']

        for i, (canvas, label) in enumerate(zip(self.step_indicators, self.step_labels)):
            canvas.delete("all")
            if i + 1 < step_num:
                # Completed step - green
                canvas.create_oval(3, 3, 27, 27, fill=colors['success'], outline=colors['success'])
                canvas.create_text(15, 15, text="✓", fill='white', font=('Segoe UI', 12, 'bold'))
                label.configure(style="Step.TLabel")
            elif i + 1 == step_num:
                # Current step - cyan
                canvas.create_oval(3, 3, 27, 27, fill=colors['accent'], outline=colors['accent'])
                canvas.create_text(15, 15, text=str(i+1), fill='white', font=('Segoe UI', 10, 'bold'))
                label.configure(style="StepActive.TLabel")
            else:
                # Future step - gray
                canvas.create_oval(3, 3, 27, 27, fill=colors['bg_secondary'], outline=colors['inactive'])
                canvas.create_text(15, 15, text=str(i+1), fill=colors['inactive'], font=('Segoe UI', 10))
                label.configure(style="Step.TLabel")

        # Update navigation buttons
        self.back_btn.config(state=tk.NORMAL if step_num > 1 else tk.DISABLED)

        if step_num == self.total_steps:
            self.next_btn.config(text="Finish", state=tk.DISABLED)
        else:
            self.next_btn.config(text="Next →", state=tk.NORMAL)

        # Update progress bar and status
        progress_value = (step_num / self.total_steps) * 100
        self.progress_bar["value"] = progress_value

        status_messages = {
            1: "Step 1 of 4 - Configure your settings",
            2: "Step 2 of 4 - Select your project",
            3: "Step 3 of 4 - Choose development type",
            4: "Step 4 of 4 - Connect to GitHub"
        }
        self.status_var.set(status_messages.get(step_num, ""))

    def next_step(self):
        """Move to next step with validation"""
        # Validate current step
        if self.current_step == 1:
            if self.user_type.get() == "new_user":
                if not self.git_name.get():
                    messagebox.showwarning("Missing Information", "Please enter your Git username.")
                    return
                if not self.git_email.get():
                    messagebox.showwarning("Missing Information", "Please enter your Git email.")
                    return
        elif self.current_step == 2:
            if not self.folder_path:
                messagebox.showwarning("No Folder", "Please select a project folder.")
                return
            if not self.repo_url.get():
                messagebox.showwarning("No Repository URL", "Please enter a GitHub repository URL.")
                return

        if self.current_step < self.total_steps:
            self.show_step(self.current_step + 1)

    def prev_step(self):
        """Move to previous step"""
        if self.current_step > 1:
            self.show_step(self.current_step - 1)

    def create_development_type_widgets(self):
        """Create development type selection in two-column layout"""
        for widget in self.dev_type_frame.winfo_children():
            widget.destroy()

        columns_frame = ttk.Frame(self.dev_type_frame, style="Glass.TFrame")
        columns_frame.pack(fill=tk.BOTH, expand=True)

        left_col = ttk.Frame(columns_frame, style="Glass.TFrame")
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_col = ttk.Frame(columns_frame, style="Glass.TFrame")
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        dev_items = list(self.dev_types.items())
        mid_point = (len(dev_items) + 1) // 2

        for idx, (dev_id, dev_info) in enumerate(dev_items):
            parent_col = left_col if idx < mid_point else right_col

            dev_row = ttk.Frame(parent_col, style="Glass.TFrame")
            dev_row.pack(fill=tk.X, pady=4, anchor=tk.W)

            dev_emoji = self.get_dev_type_emoji(dev_id)
            rb = ttk.Radiobutton(dev_row, text=f"{dev_emoji} {dev_info['name']}",
                               variable=self.dev_type, value=dev_id, style="Glass.TRadiobutton")
            rb.pack(anchor=tk.W)

        if self.dev_types:
            if self.dev_type.get() not in self.dev_types:
                self.dev_type.set(next(iter(self.dev_types)))

    def refresh_development_types_ui(self):
        """Refresh development types section"""
        if self.dev_type_frame and self.dev_type_frame.winfo_exists():
            self.create_development_type_widgets()

    def toggle_user_fields(self):
        """Show or hide user info fields"""
        if self.user_type.get() == "new_user":
            self.user_info_frame.pack(fill=tk.X, pady=(0, 10))
        else:
            self.user_info_frame.pack_forget()

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
        print(message)

    def update_status(self, message):
        """Update status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()

    def check_git(self):
        """Check if Git is installed"""
        try:
            result = subprocess.run(["git", "--version"], check=True, capture_output=True, text=True)
            self.log(f"Git detected: {result.stdout.strip()}")
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            self.show_git_missing_dialog()
            return False

    def show_git_missing_dialog(self):
        """Show dialog when Git is not installed"""
        colors = self.colors

        git_dialog = tk.Toplevel(self.root)
        git_dialog.title("Git Not Found")
        git_dialog.geometry("500x320")
        git_dialog.resizable(False, False)
        git_dialog.transient(self.root)
        git_dialog.grab_set()
        git_dialog.configure(bg=colors['bg_primary'])

        git_dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + self.root.winfo_width()//2 - 250,
            self.root.winfo_rooty() + self.root.winfo_height()//2 - 160
        ))

        warning_frame = ttk.Frame(git_dialog, style="Transparent.TFrame")
        warning_frame.pack(pady=(20, 0))

        warning_label = ttk.Label(warning_frame, text="⚠️", font=("Helvetica", 48), style="Title.TLabel")
        warning_label.pack()

        message_frame = ttk.Frame(git_dialog, padding=20, style="Transparent.TFrame")
        message_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(message_frame, text="Git is not installed!",
                 font=("Helvetica", 12, "bold"), style="Accent.TLabel").pack(pady=(0, 10))

        message_text = "This application requires Git.\nPlease install Git from the official website."
        ttk.Label(message_frame, text=message_text, wraplength=400, style="Subtitle.TLabel").pack()

        link_frame = ttk.Frame(message_frame, style="Transparent.TFrame")
        link_frame.pack(pady=10)

        ttk.Label(link_frame, text="Download from: git-scm.com", style="Subtitle.TLabel").pack()

        button_frame = ttk.Frame(git_dialog, style="Transparent.TFrame")
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="Check Again", command=lambda: self.recheck_git(git_dialog), style="Glass.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Continue Anyway", command=git_dialog.destroy, style="Glass.TButton").pack(side=tk.LEFT, padx=10)

        self.log("ERROR: Git not found. Please install Git to continue.")

    def open_url(self, url):
        """Open URL in default browser"""
        import webbrowser
        webbrowser.open(url)

    def recheck_git(self, dialog):
        """Recheck if Git is installed"""
        if self.check_git():
            dialog.destroy()
            messagebox.showinfo("Git Detected", "Git has been successfully detected.")

    def validate_inputs(self):
        """Validate all inputs before connecting"""
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
                "Git is required. The operation will likely fail. Continue anyway?"
            )
            if not result:
                return False

        return True

    def start_connection(self):
        """Start the GitHub connection process"""
        if not self.validate_inputs():
            return

        self.root.config(cursor="wait")
        self.connect_progress["value"] = 0

        connection_thread = Thread(target=self.perform_connection)
        connection_thread.daemon = True
        connection_thread.start()

    def perform_connection(self):
        """Perform the GitHub connection process"""
        try:
            self.log("Starting GitHub connection process...")
            self.update_status("Connecting...")

            self.connect_progress["value"] = 10
            self.create_git_files()

            self.connect_progress["value"] = 30
            self.initialize_git()

            self.connect_progress["value"] = 50
            if self.user_type.get() == "new_user":
                self.configure_git()

            self.connect_progress["value"] = 70
            self.commit_files()

            self.connect_progress["value"] = 90
            self.push_to_github()

            self.connect_progress["value"] = 100
            self.update_status("Connection completed successfully!")
            messagebox.showinfo("Success", "GitHub repository setup completed!")

        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.update_status("Connection failed.")

        finally:
            self.root.config(cursor="")

    def create_git_files(self):
        """Create .gitignore and README.md"""
        self.log(f"Creating Git files for {self.dev_type.get()} development type...")

        os.chdir(self.folder_path)

        dev_type_id = self.dev_type.get()
        dev_type = self.dev_types.get(dev_type_id, {})

        if not dev_type:
            raise Exception(f"Development type '{dev_type_id}' not found.")

        gitignore_content = "\n".join(dev_type.get("gitignore", []))
        with open(".gitignore", "w") as f:
            f.write(gitignore_content)

        readme_content = dev_type.get("readme_template", "# Project\n\n## Description\nProject description.")
        with open("README.md", "w") as f:
            f.write(readme_content)

        self.log(f"Created .gitignore and README.md")

    def initialize_git(self):
        """Initialize Git repository"""
        self.log("Initializing Git repository...")
        subprocess.run(["git", "init"], check=True, capture_output=True, text=True)
        self.log("Git repository initialized")

    def configure_git(self):
        """Configure Git for new users"""
        self.log("Configuring Git user settings...")
        subprocess.run(["git", "config", "--global", "user.name", self.git_name.get()],
                       check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "--global", "user.email", self.git_email.get()],
                       check=True, capture_output=True, text=True)
        self.log(f"Git configured: {self.git_name.get()} <{self.git_email.get()}>")

    def commit_files(self):
        """Add and commit files"""
        self.log("Adding files to repository...")

        try:
            subprocess.run(["git", "rm", "-r", "--cached", "."],
                        check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError:
            pass

        subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"],
                     check=True, capture_output=True, text=True)
        subprocess.run(["git", "branch", "-M", "main"],
                     check=True, capture_output=True, text=True)

        self.log("Files committed to repository")

    def push_to_github(self):
        """Connect to GitHub and push"""
        self.log("Connecting to GitHub repository...")

        subprocess.run(["git", "remote", "add", "origin", self.repo_url.get()],
                     check=True, capture_output=True, text=True)

        try:
            self.log("Pushing to GitHub...")
            result = subprocess.run(["git", "push", "-u", "origin", "main"],
                                 check=True, capture_output=True, text=True)
            self.log("Successfully pushed to GitHub!")

        except subprocess.CalledProcessError as e:
            error_output = e.stderr if e.stderr else "No detailed error"
            self.log(f"Error during push: {error_output}")

            if "Authentication failed" in error_output:
                raise Exception("GitHub authentication failed. Check credentials.")
            else:
                raise Exception(f"Failed to push: {error_output}")

    def open_manage_types(self):
        """Open dialog to manage development types"""
        colors = self.colors

        manage_window = tk.Toplevel(self.root)
        manage_window.title("🔧 Manage Development Types")
        manage_window.geometry("680x580")
        manage_window.resizable(True, True)
        manage_window.transient(self.root)
        manage_window.grab_set()
        manage_window.configure(bg=colors['bg_primary'])

        if platform.system() == "Windows":
            try:
                manage_window.wm_attributes("-alpha", 0.95)
            except:
                pass

        manage_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))

        types_frame = ttk.LabelFrame(manage_window, text="📋 Current Development Types", padding="15", style="Glass.TLabelframe")
        types_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

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

        def refresh_listbox():
            listbox.delete(0, tk.END)
            for dev_id, dev_info in self.dev_types.items():
                listbox.insert(tk.END, f"{dev_info['name']} ({dev_id})")

        refresh_listbox()

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

        io_frame = ttk.Frame(types_frame, style="Glass.TFrame")
        io_frame.pack(fill=tk.X, pady=8)

        ttk.Button(io_frame, text="📥 Import Types",
                command=lambda: self.import_types(refresh_listbox),
                style="Glass.TButton").pack(side=tk.LEFT, padx=6)

        ttk.Button(io_frame, text="📤 Export All Types",
                command=self.export_types,
                style="Glass.TButton").pack(side=tk.LEFT, padx=6)

        ttk.Button(manage_window, text="✅ Done",
                command=manage_window.destroy,
                style="Primary.TButton").pack(pady=15)

    def edit_type_dialog(self, parent, type_id=None, refresh_callback=None):
        """Open dialog to add or edit a development type"""
        is_new = type_id is None
        colors = self.colors

        dialog = tk.Toplevel(parent)
        dialog.title(f"{'➕ Add' if is_new else '✏️ Edit'} Development Type")
        dialog.geometry("620x720")
        dialog.resizable(True, True)
        dialog.transient(parent)
        dialog.grab_set()
        dialog.configure(bg=colors['bg_primary'])

        if platform.system() == "Windows":
            try:
                dialog.wm_attributes("-alpha", 0.95)
            except:
                pass

        type_id_var = tk.StringVar(value=type_id if not is_new else "")
        type_name_var = tk.StringVar(value=self.dev_types.get(type_id, {}).get("name", "") if not is_new else "")
        type_desc_var = tk.StringVar(value=self.dev_types.get(type_id, {}).get("description", "") if not is_new else "")

        main_frame = ttk.Frame(dialog, padding="15", style="Glass.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        id_frame = ttk.Frame(main_frame, style="Glass.TFrame")
        id_frame.pack(fill=tk.X, pady=8)

        ttk.Label(id_frame, text="🏷️ Type ID:", style="Accent.TLabel").pack(side=tk.LEFT)
        id_entry = ttk.Entry(id_frame, textvariable=type_id_var, style="Glass.TEntry")
        id_entry.pack(side=tk.LEFT, padx=8, fill=tk.X, expand=True)

        if not is_new:
            id_entry.config(state=tk.DISABLED)

        name_frame = ttk.Frame(main_frame, style="Glass.TFrame")
        name_frame.pack(fill=tk.X, pady=8)

        ttk.Label(name_frame, text="📝 Display Name:", style="Accent.TLabel").pack(side=tk.LEFT)
        ttk.Entry(name_frame, textvariable=type_name_var, style="Glass.TEntry").pack(side=tk.LEFT, padx=8, fill=tk.X, expand=True)

        desc_frame = ttk.Frame(main_frame, style="Glass.TFrame")
        desc_frame.pack(fill=tk.X, pady=8)

        ttk.Label(desc_frame, text="📄 Description:", style="Accent.TLabel").pack(side=tk.LEFT)
        ttk.Entry(desc_frame, textvariable=type_desc_var, style="Glass.TEntry").pack(side=tk.LEFT, padx=8, fill=tk.X, expand=True)

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

        if not is_new:
            gitignore_content = "\n".join(self.dev_types.get(type_id, {}).get("gitignore", []))
            gitignore_text.insert("1.0", gitignore_content)
            readme_template = self.dev_types.get(type_id, {}).get("readme_template", "")
            readme_text.insert("1.0", readme_template)

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
        """Save a development type"""
        if not type_id:
            messagebox.showwarning("Invalid Input", "Type ID is required.")
            return

        if not name:
            messagebox.showwarning("Invalid Input", "Display Name is required.")
            return

        gitignore_lines = [line for line in gitignore.splitlines() if line.strip()]

        self.dev_types[type_id] = {
            "name": name,
            "description": description,
            "gitignore": gitignore_lines,
            "readme_template": readme.strip()
        }

        self.save_development_types()
        dialog.destroy()

        if refresh_callback:
            refresh_callback()
        self.refresh_development_types_ui()

    def remove_type(self, type_id, refresh_callback=None):
        """Remove a development type"""
        if not type_id:
            messagebox.showwarning("No Selection", "Please select a development type to remove.")
            return

        if messagebox.askyesno("Confirm Deletion", f"Remove '{self.dev_types.get(type_id, {}).get('name', type_id)}'?"):
            if type_id in self.dev_types:
                del self.dev_types[type_id]
                self.save_development_types()

                if refresh_callback:
                    refresh_callback()
                self.refresh_development_types_ui()

    def import_types(self, refresh_callback=None):
        """Import development types from JSON"""
        file_path = filedialog.askopenfilename(
            title="Import Development Types",
            filetypes=[("JSON files", "*.json"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_types = json.load(f)

                if not isinstance(imported_types, dict):
                    messagebox.showerror("Invalid Format", "Invalid development types format.")
                    return

                if messagebox.askyesno("Import Mode", "Merge with existing? (No = Replace all)"):
                    self.dev_types.update(imported_types)
                else:
                    self.dev_types = imported_types

                self.save_development_types()

                if refresh_callback:
                    refresh_callback()
                self.refresh_development_types_ui()

                messagebox.showinfo("Import Successful", f"Imported {len(imported_types)} types.")

            except Exception as e:
                messagebox.showerror("Import Error", f"Error: {str(e)}")

    def export_types(self):
        """Export development types to JSON"""
        file_path = filedialog.asksaveasfilename(
            title="Export Development Types",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.dev_types, f, indent=2, ensure_ascii=False)

                messagebox.showinfo("Export Successful", f"Exported {len(self.dev_types)} types.")

            except Exception as e:
                messagebox.showerror("Export Error", f"Error: {str(e)}")

    def save_development_types(self):
        """Save development types to config file"""
        try:
            config_path = self.resource_path("development_types.json")
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.dev_types, f, indent=2, ensure_ascii=False)

            print(f"Saved {len(self.dev_types)} development types")

        except Exception as e:
            print(f"Error saving development types: {e}")
            messagebox.showwarning("Save Error", f"Could not save: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = GitOneClickGUI(root)
    root.mainloop()
