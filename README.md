# Git-OneClick GUI

**Version**: 2.0.0
**A powerful desktop application for instant GitHub repository setup**

## Description

Git-OneClick GUI is a comprehensive desktop application that automates the entire process of setting up Git repositories and connecting them to GitHub. Whether you're a beginner starting your first project or an experienced developer who wants to streamline repository creation, this tool eliminates the manual steps and gets you coding faster.

## Features

### Wizard-Based Setup
- **Step-by-step workflow**: 4-step wizard guides you through the setup process
- **Progress tracking**: Visual stepper shows your current progress
- **Back/Next navigation**: Easy navigation between steps

### One-Click Repository Setup
- **Instant Git Initialization**: Automatically initializes Git repository in your project folder
- **GitHub Connection**: Direct integration with your GitHub repositories
- **Smart File Generation**: Creates appropriate .gitignore and README.md files
- **Automated Commits**: Handles initial commit and push to GitHub

### Development Type Templates
Pre-configured templates for popular development frameworks:

| Template | Description |
|----------|-------------|
| **Basic** | General purpose projects |
| **Web Development** | Node.js, React, Vue projects |
| **Python** | Python applications & scripts |
| **Flutter** | Cross-platform mobile apps |
| **Unity** | Game development projects |
| **Android** | Native Android development |
| **Laravel** | PHP web applications |
| **FastAPI** | Modern Python API |
| **Next.js** | React framework |

### User-Friendly Design
- **Dark Glassmorphism UI**: Modern cyan-themed dark interface
- **New User Onboarding**: Automated Git configuration for first-time users
- **Existing User Support**: Quick setup for developers with existing Git config
- **Real-time Logging**: See exactly what's happening during setup
- **Error Handling**: Helpful error messages and recovery suggestions

### Advanced Features
- **Custom Template Management**: Create, edit, and manage your own development templates
- **Import/Export Templates**: Share template configurations across teams
- **Flexible .gitignore**: Comprehensive ignore patterns for each development type
- **README Templates**: Professional README.md generation with proper structure
- **Git Detection**: Automatic Git installation verification with download links

## System Requirements

- **Operating System**: Windows 10/11, macOS, Linux
- **Git**: Required for repository operations ([Download Git](https://git-scm.com/downloads))
- **GitHub Account**: Required for repository creation and pushing
- **Python** (for development): Python 3.8+ with tkinter support

## Quick Start

### Option 1: Download Executable (Recommended)
1. Download the latest `Git-OneClick.exe` from the releases
2. Run the executable - no installation required!
3. Follow the 4-step wizard to configure your repository

### Option 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/Kiyoraka/git-oneclick-gui.git
cd git-oneclick-gui

# Run the application
python git_oneclick_gui.py
```

## How to Use

### Step 1: Setup
- Choose user type (First Time User or Existing User)
- Enter Git username and email (for new users)

### Step 2: Project
- Select your project folder
- Enter your GitHub repository URL

### Step 3: Dev Type
- Choose the appropriate development template
- Manage custom templates if needed

### Step 4: Connect
- Click "Connect to GitHub"
- Watch the progress as files are created and pushed
- Your repository is ready!

## Building from Source

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable (Windows)
pyinstaller --onefile --windowed --icon=git-gui.ico --name="Git-OneClick" --add-data "development_types.json;." git_oneclick_gui.py

# The executable will be in dist/Git-OneClick.exe
```

Or use the included build script:
```bash
Create-Normal-EXE.bat
```

## Troubleshooting

### Git Not Found
1. Install Git from [git-scm.com](https://git-scm.com/downloads)
2. Restart the application
3. Use "Check Again" button to verify installation

### Authentication Failed
1. Ensure your repository URL is correct
2. Check your GitHub permissions
3. Consider using Personal Access Token (PAT) for authentication

### Template Issues
1. Check that `development_types.json` exists in the same directory
2. Verify the JSON format is valid
3. Use "Manage Development Types" to reset to defaults

## License

This project is open source and available under the MIT License.

---

**Ready to streamline your Git workflow? Download Git-OneClick GUI today!**
