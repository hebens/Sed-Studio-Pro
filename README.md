# 🛠️ Sed Creator: The Ultimate Sed IDE

Sed Studio is a modern, graphical architect for building, testing, and exporting `sed` (Stream Editor) scripts. Designed for Linux power users and beginners alike, it simplifies complex text transformations through a real-time sandbox and an intuitive multi-command chain logic.

## ✨ Features

- **Multi-Step Command Chaining**: Sequence multiple `sed` expressions (`-e`) into a single execution plan.
- **Live Preview Sandbox**: Test your logic against sample data instantly.
- **Auto-Escaper**: Automatically switches delimiters (e.g., `/` to `|`) when file paths or URLs are detected.
- **Extended Regex Support**: Enabled by default (`-E`) for modern, readable regex syntax.
- **Bash Script Exporter**: Turn your chain into a professional, portable `.sh` script with built-in file looping and safety checks.
- **Regex Cheat Sheet**: Sidebar presets for common tasks like IP masking, HTML stripping, and line commenting.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Linux, Windows, or macOS

### Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/sed-studio.git](https://github.com/yourusername/sed-studio.git)
   cd sed-studio
2. Install dependencies:
   ```bash
   pip install customtkinter pyperclip
4. Run the application:
   ```bash
   python sed-studio-pro.py
## 📖 Usage Tips
Chaining Commands
Enter your search/replace patterns in the Step Editor.

Click Add Step to Chain.

Your final command is automatically constructed using the -e flag for maximum efficiency.

Handling File Paths
Sed Studio monitors your input. If you type a path like /etc/passwd, the tool automatically uses | as a delimiter to avoid "Leaning Toothpick Syndrome."

## 🐧 Linux Integration
After exporting a script (.sh), ensure you give it execution permissions:
```bash
      chmod +x my_generated_script.sh
      ./my_generated_script.sh target_file.txt

