import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from threading import Thread
import json
import shutil


class GitOneClickGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Git-OneClick")
        self.root.geometry("700x580")
        self.root.resizable(True, True)
        
        # Set minimum window size
        self.root.minsize(600, 500)
        
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
        
        # Create GUI elements
        self.create_widgets()
        
        # Check for Git installation
        self.git_installed = self.check_git()

    def load_development_types(self):
        """Load development types from the configuration file"""
        try:
            # Try to find the config file in the same directory as the script
            config_path = self.resource_path("development_types.json")
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
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

    def create_widgets(self):
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Git-OneClick", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)
        
        # User Type section
        user_type_frame = ttk.LabelFrame(main_frame, text="User Type", padding="10")
        user_type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(user_type_frame, text="First Time User (Setup Git configuration)", 
                      variable=self.user_type, value="new_user", 
                      command=self.toggle_user_fields).pack(anchor=tk.W)
        ttk.Radiobutton(user_type_frame, text="Existing User (Already have Git configured)", 
                      variable=self.user_type, value="existing_user", 
                      command=self.toggle_user_fields).pack(anchor=tk.W)
        
        # User info section (only shown for new users)
        self.user_info_frame = ttk.Frame(main_frame)
        self.user_info_frame.pack(fill=tk.X, pady=5)
        
        # Git name
        name_frame = ttk.Frame(self.user_info_frame)
        name_frame.pack(fill=tk.X, pady=5)
        ttk.Label(name_frame, text="Git Username:").pack(side=tk.LEFT)
        ttk.Entry(name_frame, textvariable=self.git_name).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Git email
        email_frame = ttk.Frame(self.user_info_frame)
        email_frame.pack(fill=tk.X, pady=5)
        ttk.Label(email_frame, text="Git Email:").pack(side=tk.LEFT)
        ttk.Entry(email_frame, textvariable=self.git_email).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Project Configuration section
        project_frame = ttk.LabelFrame(main_frame, text="Project Configuration", padding="10")
        project_frame.pack(fill=tk.X, pady=5)
        
        # Folder selection
        folder_frame = ttk.Frame(project_frame)
        folder_frame.pack(fill=tk.X, pady=5)
        
        self.folder_label = ttk.Label(folder_frame, text="No folder selected")
        self.folder_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        folder_btn = ttk.Button(folder_frame, text="Select Folder", command=self.select_folder)
        folder_btn.pack(side=tk.RIGHT)
        
        # Repository URL input
        repo_frame = ttk.Frame(project_frame)
        repo_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(repo_frame, text="GitHub Repository URL:").pack(side=tk.LEFT)
        ttk.Entry(repo_frame, textvariable=self.repo_url).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Development Type section
        dev_type_frame = ttk.LabelFrame(main_frame, text="Development Type", padding="10")
        dev_type_frame.pack(fill=tk.X, pady=5)
        
        # Scrollable frame for development types (in case there are many)
        dev_canvas = tk.Canvas(dev_type_frame, highlightthickness=0)
        dev_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(dev_type_frame, orient="vertical", command=dev_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        dev_canvas.configure(yscrollcommand=scrollbar.set)
        dev_canvas.bind('<Configure>', lambda e: dev_canvas.configure(scrollregion=dev_canvas.bbox("all")))
        
        dev_scrollable_frame = ttk.Frame(dev_canvas)
        dev_canvas.create_window((0, 0), window=dev_scrollable_frame, anchor="nw", width=dev_canvas.winfo_reqwidth())
        
        # Create radio buttons for each development type
        for dev_id, dev_info in self.dev_types.items():
            dev_container = ttk.Frame(dev_scrollable_frame)
            dev_container.pack(fill=tk.X, pady=2)
            
            rb = ttk.Radiobutton(dev_container, text=dev_info["name"], variable=self.dev_type, value=dev_id)
            rb.pack(side=tk.LEFT)
            
            # Description tooltip
            if "description" in dev_info:
                desc_label = ttk.Label(dev_container, text=f"- {dev_info['description']}", font=("Helvetica", 9), foreground="gray")
                desc_label.pack(side=tk.LEFT, padx=10)
        
        # Set default development type
        if self.dev_types:
            self.dev_type.set(next(iter(self.dev_types)))
        
        # Custom Development Type button
        custom_btn = ttk.Button(dev_type_frame, text="Manage Types", command=self.open_manage_types)
        custom_btn.pack(pady=5)
        
        # Connect button
        connect_btn = ttk.Button(main_frame, text="Connect to GitHub", 
                               command=self.start_connection, style="Accent.TButton")
        connect_btn.pack(pady=10)
        
        # Create custom style for the connect button
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Helvetica", 12, "bold"))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Connection Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbar for log
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Log text widget
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(5, 0))

    def open_manage_types(self):
        """Open dialog to manage development types"""
        # Create a new top-level window
        manage_window = tk.Toplevel(self.root)
        manage_window.title("Manage Development Types")
        manage_window.geometry("600x500")
        manage_window.resizable(True, True)
        manage_window.transient(self.root)
        manage_window.grab_set()
        
        # Create a list of current development types
        types_frame = ttk.LabelFrame(manage_window, text="Current Development Types", padding="10")
        types_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a listbox to display types
        listbox_frame = ttk.Frame(types_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, font=("Helvetica", 10))
        listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar.config(command=listbox.yview)
        
        # Populate listbox with types
        for dev_id, dev_info in self.dev_types.items():
            listbox.insert(tk.END, f"{dev_info['name']} ({dev_id})")
        
        # Buttons for adding, editing, and removing types
        btn_frame = ttk.Frame(types_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Add New Type", 
                command=lambda: self.edit_type_dialog(manage_window)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Edit Selected", 
                command=lambda: self.edit_type_dialog(manage_window, listbox.get(tk.ACTIVE).split(" (")[-1][:-1] if listbox.curselection() else None)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Remove Selected", 
                command=lambda: self.remove_type(listbox.get(tk.ACTIVE).split(" (")[-1][:-1] if listbox.curselection() else None, listbox)).pack(side=tk.LEFT, padx=5)
        
        # Import/Export buttons
        io_frame = ttk.Frame(types_frame)
        io_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(io_frame, text="Import Types", 
                command=lambda: self.import_types(listbox)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(io_frame, text="Export All Types", 
                command=self.export_types).pack(side=tk.LEFT, padx=5)
        
        # Done button
        ttk.Button(manage_window, text="Done", 
                command=manage_window.destroy).pack(pady=10)

    def edit_type_dialog(self, parent, type_id=None):
        """Open dialog to add or edit a development type"""
        is_new = type_id is None
        
        dialog = tk.Toplevel(parent)
        dialog.title("Add Development Type" if is_new else "Edit Development Type")
        dialog.geometry("600x700")
        dialog.resizable(True, True)
        dialog.transient(parent)
        dialog.grab_set()
        
        # Variables
        type_id_var = tk.StringVar(value=type_id if not is_new else "")
        type_name_var = tk.StringVar(value=self.dev_types.get(type_id, {}).get("name", "") if not is_new else "")
        type_desc_var = tk.StringVar(value=self.dev_types.get(type_id, {}).get("description", "") if not is_new else "")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Type ID
        id_frame = ttk.Frame(main_frame)
        id_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(id_frame, text="Type ID:").pack(side=tk.LEFT)
        id_entry = ttk.Entry(id_frame, textvariable=type_id_var)
        id_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Disable ID field if editing
        if not is_new:
            id_entry.config(state=tk.DISABLED)
        
        # Type Name
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(name_frame, text="Display Name:").pack(side=tk.LEFT)
        ttk.Entry(name_frame, textvariable=type_name_var).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Type Description
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(desc_frame, text="Description:").pack(side=tk.LEFT)
        ttk.Entry(desc_frame, textvariable=type_desc_var).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # .gitignore content
        gitignore_frame = ttk.LabelFrame(main_frame, text=".gitignore Content", padding="5")
        gitignore_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        gitignore_scroll = ttk.Scrollbar(gitignore_frame)
        gitignore_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        gitignore_text = tk.Text(gitignore_frame, height=10, wrap=tk.WORD, yscrollcommand=gitignore_scroll.set)
        gitignore_text.pack(fill=tk.BOTH, expand=True)
        gitignore_scroll.config(command=gitignore_text.yview)
        
        # README template
        readme_frame = ttk.LabelFrame(main_frame, text="README.md Template", padding="5")
        readme_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        readme_scroll = ttk.Scrollbar(readme_frame)
        readme_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        readme_text = tk.Text(readme_frame, height=10, wrap=tk.WORD, yscrollcommand=readme_scroll.set)
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
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Cancel", 
                command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(btn_frame, text="Save", 
                command=lambda: self.save_type(
                    dialog, 
                    type_id_var.get(), 
                    type_name_var.get(), 
                    type_desc_var.get(), 
                    gitignore_text.get("1.0", tk.END), 
                    readme_text.get("1.0", tk.END)
                )).pack(side=tk.RIGHT, padx=5)

    def save_type(self, dialog, type_id, name, description, gitignore, readme):
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
        
        # Refresh the GUI
        self.create_widgets()

    def remove_type(self, type_id, listbox):
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
                
                # Refresh listbox
                listbox.delete(0, tk.END)
                for dev_id, dev_info in self.dev_types.items():
                    listbox.insert(tk.END, f"{dev_info['name']} ({dev_id})")

    def import_types(self, listbox):
        """Import development types from a JSON file"""
        file_path = filedialog.askopenfilename(
            title="Import Development Types",
            filetypes=[("JSON files", "*.json"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
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
                
                # Refresh listbox
                listbox.delete(0, tk.END)
                for dev_id, dev_info in self.dev_types.items():
                    listbox.insert(tk.END, f"{dev_info['name']} ({dev_id})")
                
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
                with open(file_path, 'w') as f:
                    json.dump(self.dev_types, f, indent=2)
                
                messagebox.showinfo("Export Successful", f"Successfully exported {len(self.dev_types)} development types to {file_path}.")
            
            except Exception as e:
                messagebox.showerror("Export Error", f"An error occurred during export: {str(e)}")

    def save_development_types(self):
        """Save development types to the configuration file"""
        try:
            config_path = self.resource_path("development_types.json")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(self.dev_types, f, indent=2)
            
            print(f"Saved {len(self.dev_types)} development types to {config_path}")
        
        except Exception as e:
            print(f"Error saving development types: {e}")
            messagebox.showwarning("Save Error", f"Could not save development types: {str(e)}")

    def toggle_user_fields(self):
        """Show or hide user info fields based on user type"""
        if self.user_type.get() == "new_user":
            self.user_info_frame.pack(fill=tk.X, pady=5, after=self.root.nametowidget(".!frame.!labelframe"))
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