import customtkinter as ctk
import re
import pyperclip
from datetime import datetime
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SedGui(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Ultimate Sed Builder & Sandbox")
        self.geometry("1300x950")

        self.grid_columnconfigure(0, weight=0) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_columnconfigure(2, weight=1) 

        self.history = []

        # --- SIDEBAR: Quick Presets ---
        self.sidebar = ctk.CTkScrollableFrame(self, width=220, label_text="Regex Cheat Sheet")
        self.sidebar.grid(row=0, column=0, rowspan=2, padx=10, pady=20, sticky="nsew")

        presets = [
            ("Remove Numbers", r"\d+", ""),
            ("Remove Whitespace", r"\s+", ""),
            ("Find IP Addresses", r"([0-9]{1,3}\.){3}[0-9]{1,3}", "[IP]"),
            ("Delete Empty Lines", r"^$", "DELETE"),
            ("Comment Out Line", r"^(.*)$", r"# \1"),
            ("Extract Emails", r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "[EMAIL]"),
            ("Strip HTML Tags", r"<[^>]*>", ""),
            ("Match Dates", r"\d{4}-\d{2}-\d{2}", "DATE")
        ]

        for label, search, replace in presets:
            btn = ctk.CTkButton(self.sidebar, text=label, command=lambda s=search, r=replace: self.apply_preset(s, r))
            btn.pack(pady=5, fill="x")

        # --- MIDDLE PANEL: Settings ---
        self.middle_frame = ctk.CTkFrame(self)
        self.middle_frame.grid(row=0, column=1, padx=10, pady=20, sticky="nsew")

        ctk.CTkLabel(self.middle_frame, text="Command Settings", font=("Roboto", 22, "bold")).pack(pady=10)
        self.search_entry = ctk.CTkEntry(self.middle_frame, placeholder_text="Search Pattern", width=350)
        self.search_entry.pack(pady=10)
        self.replace_entry = ctk.CTkEntry(self.middle_frame, placeholder_text="Replace with", width=350)
        self.replace_entry.pack(pady=10)
        self.file_entry = ctk.CTkEntry(self.middle_frame, placeholder_text="Filename (data.txt)", width=350)
        self.file_entry.pack(pady=10)
        
        self.switch_frame = ctk.CTkFrame(self.middle_frame, fg_color="transparent")
        self.switch_frame.pack(pady=10)
        self.global_switch = ctk.CTkSwitch(self.switch_frame, text="Global (g)"); self.global_switch.grid(row=0, column=0, padx=5); self.global_switch.select()
        self.extended_switch = ctk.CTkSwitch(self.switch_frame, text="Extended (-E)"); self.extended_switch.grid(row=0, column=1, padx=5); self.extended_switch.select()
        self.inplace_switch = ctk.CTkSwitch(self.middle_frame, text="In-place (-i)"); self.inplace_switch.pack(pady=5)

        self.gen_button = ctk.CTkButton(self.middle_frame, text="Generate & Preview", command=self.update_all, fg_color="#3498db", height=40)
        self.gen_button.pack(pady=15)

        self.cmd_output = ctk.CTkTextbox(self.middle_frame, height=80, width=350, font=("Courier New", 14))
        self.cmd_output.pack(pady=10)
        self.copy_button = ctk.CTkButton(self.middle_frame, text="Copy to Clipboard", command=self.copy_to_clipboard, fg_color="#e67e22")
        self.copy_button.pack(pady=5)

        # --- RIGHT PANEL: Preview ---
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=2, padx=10, pady=20, sticky="nsew")

        ctk.CTkLabel(self.right_frame, text="Live Preview", font=("Roboto", 22, "bold")).pack(pady=10)
        self.input_text = ctk.CTkTextbox(self.right_frame, height=250, width=400)
        self.input_text.pack(pady=5)
        self.input_text.insert("0.0", "Sample Data:\nUser: admin\nPass: 12345\nIP: 127.0.0.1")
        self.preview_output = ctk.CTkTextbox(self.right_frame, height=250, width=400, fg_color="#1e1e1e", text_color="#2ecc71")
        self.preview_output.pack(pady=5)

        # --- BOTTOM PANEL: History ---
        self.history_frame = ctk.CTkFrame(self)
        self.history_frame.grid(row=1, column=1, columnspan=2, padx=10, pady=(0, 20), sticky="nsew")
        
        history_header = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        history_header.pack(fill="x")
        ctk.CTkLabel(history_header, text="Command History", font=("Roboto", 16, "bold")).pack(side="left", padx=20, pady=5)
        
        self.export_button = ctk.CTkButton(history_header, text="Export History (.txt)", command=self.export_history, fg_color="#9b59b6", width=150)
        self.export_button.pack(side="right", padx=20, pady=5)

        self.history_box = ctk.CTkTextbox(self.history_frame, height=150, width=800, font=("Courier New", 12))
        self.history_box.pack(padx=10, pady=10, fill="both")

    def apply_preset(self, search, replace):
        self.search_entry.delete(0, "end"); self.search_entry.insert(0, search)
        self.replace_entry.delete(0, "end"); self.replace_entry.insert(0, replace)
        self.update_all()

    def update_all(self):
        search = self.search_entry.get()
        replace = self.replace_entry.get()
        filename = self.file_entry.get() or "file.txt"
        
        inplace = "-i " if self.inplace_switch.get() else ""
        extended = "-E " if self.extended_switch.get() else ""
        g_flag = "g" if self.global_switch.get() else ""
        
        if replace == "DELETE":
            final_cmd = f"sed {inplace}{extended}'/{search}/d' {filename}"
        else:
            final_cmd = f"sed {inplace}{extended}'s|{search}|{replace}|{g_flag}' {filename}"
            
        self.cmd_output.delete("0.0", "end")
        self.cmd_output.insert("0.0", final_cmd)
        self.add_to_history(final_cmd)

        if search:
            try:
                content = self.input_text.get("0.0", "end-1c")
                lines = content.splitlines()
                count = 0 if self.global_switch.get() else 1
                if replace == "DELETE":
                    processed = [l for l in lines if not re.search(search, l)]
                else:
                    processed = [re.sub(search, replace, l, count=count) for l in lines]
                self.preview_output.delete("0.0", "end")
                self.preview_output.insert("0.0", "\n".join(processed))
            except Exception as e:
                self.preview_output.delete("0.0", "end")
                self.preview_output.insert("0.0", f"Regex Error: {e}")

    def add_to_history(self, cmd):
        if not self.history or self.history[-1] != cmd:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.history.append(f"[{timestamp}] {cmd}")
            self.history_box.insert("0.0", f"[{timestamp}] {cmd}\n")

    def export_history(self):
        if not self.history:
            messagebox.showwarning("Export", "History is currently empty.")
            return
            
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                                                title="Save Sed History")
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write("--- SED COMMAND HISTORY EXPORT ---\n")
                    f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    for entry in reversed(self.history): # Newest first
                        f.write(entry + "\n")
                messagebox.showinfo("Export Success", f"History saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Could not save file: {e}")

    def copy_to_clipboard(self):
        cmd = self.cmd_output.get("0.0", "end-1c")
        if cmd.strip():
            pyperclip.copy(cmd)
            self.copy_button.configure(text="Copied!", fg_color="#2ecc71")
            self.after(2000, lambda: self.copy_button.configure(text="Copy to Clipboard", fg_color="#e67e22"))

if __name__ == "__main__":
    app = SedGui()
    app.mainloop()