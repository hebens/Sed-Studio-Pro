import customtkinter as ctk
import re
import pyperclip
import os
from datetime import datetime
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SedGui(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Pro Sed Script Architect")
        self.geometry("1400x950")

        self.grid_columnconfigure(0, weight=0) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_columnconfigure(2, weight=1) 

        self.command_chain = [] 

        # --- SIDEBAR: Presets ---
        self.sidebar = ctk.CTkScrollableFrame(self, width=200, label_text="Presets")
        self.sidebar.grid(row=0, column=0, rowspan=2, padx=10, pady=20, sticky="nsew")

        presets = [
            ("Remove Numbers", r"\d+", ""),
            ("Remove Whitespace", r"\s+", ""),
            ("IP to [MASK]", r"([0-9]{1,3}\.){3}[0-9]{1,3}", "[MASK]"),
            ("Delete Empty Lines", r"^$", "DELETE"),
            ("Comment Line", r"^(.*)$", r"# \1"),
            ("Strip HTML", r"<[^>]*>", "")
        ]

        for label, s, r in presets:
            btn = ctk.CTkButton(self.sidebar, text=label, command=lambda s=s, r=r: self.apply_preset(s, r))
            btn.pack(pady=5, fill="x")

        # --- MIDDLE PANEL: Editor ---
        self.middle_frame = ctk.CTkFrame(self)
        self.middle_frame.grid(row=0, column=1, padx=10, pady=20, sticky="nsew")

        ctk.CTkLabel(self.middle_frame, text="Step Editor", font=("Roboto", 22, "bold")).pack(pady=10)
        self.search_entry = ctk.CTkEntry(self.middle_frame, placeholder_text="Search Pattern", width=350)
        self.search_entry.pack(pady=10)
        self.replace_entry = ctk.CTkEntry(self.middle_frame, placeholder_text="Replace with", width=350)
        self.replace_entry.pack(pady=10)
        
        self.step_switches = ctk.CTkFrame(self.middle_frame, fg_color="transparent")
        self.step_switches.pack(pady=5)
        self.global_switch = ctk.CTkSwitch(self.step_switches, text="Global (g)")
        self.global_switch.grid(row=0, column=0, padx=10)
        self.global_switch.select()

        self.add_chain_btn = ctk.CTkButton(self.middle_frame, text="Add Step to Chain +", command=self.add_to_chain, fg_color="#2ecc71")
        self.add_chain_btn.pack(pady=15)

        self.pop_btn = ctk.CTkButton(self.middle_frame, text="Remove Last Step", command=self.remove_last, fg_color="#e67e22")
        self.pop_btn.pack(pady=5)

        self.clear_chain_btn = ctk.CTkButton(self.middle_frame, text="Clear All Steps", command=self.clear_chain, fg_color="#e74c3c")
        self.clear_chain_btn.pack(pady=5)

        ctk.CTkLabel(self.middle_frame, text="Execution Flags:").pack(pady=(20, 0))
        self.inplace_switch = ctk.CTkSwitch(self.middle_frame, text="In-place Edit (-i)", command=self.update_all)
        self.inplace_switch.pack(pady=5)

        ctk.CTkLabel(self.middle_frame, text="Final Generated Command:").pack(pady=(10, 0))
        self.cmd_output = ctk.CTkTextbox(self.middle_frame, height=120, width=350, font=("Courier New", 13))
        self.cmd_output.pack(pady=10)

        self.copy_btn = ctk.CTkButton(self.middle_frame, text="Copy Command", command=self.copy_to_clipboard, fg_color="#3498db")
        self.copy_btn.pack(pady=5)

        self.export_btn = ctk.CTkButton(self.middle_frame, text="Export as .sh Script", command=self.export_bash_script, fg_color="#9b59b6")
        self.export_btn.pack(pady=5)

        # --- RIGHT PANEL: Preview ---
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=2, padx=10, pady=20, sticky="nsew")

        ctk.CTkLabel(self.right_frame, text="Current Chain", font=("Roboto", 18)).pack(pady=5)
        self.chain_list_box = ctk.CTkTextbox(self.right_frame, height=150, width=400, fg_color="#2c3e50")
        self.chain_list_box.pack(pady=5)

        ctk.CTkLabel(self.right_frame, text="Live Script Preview").pack(pady=5)
        self.input_text = ctk.CTkTextbox(self.right_frame, height=200, width=400)
        self.input_text.pack(pady=5)
        self.input_text.insert("0.0", "Config_File_v1\nServer: 127.0.0.1\nAdmin: user1\nStatus: active")

        self.preview_output = ctk.CTkTextbox(self.right_frame, height=200, width=400, fg_color="#1e1e1e", text_color="#2ecc71")
        self.preview_output.pack(pady=5)

    def apply_preset(self, s, r):
        self.search_entry.delete(0, "end"); self.search_entry.insert(0, s)
        self.replace_entry.delete(0, "end"); self.replace_entry.insert(0, r)

    def add_to_chain(self):
        s = self.search_entry.get(); r = self.replace_entry.get(); is_g = self.global_switch.get()
        if not s: return
        self.command_chain.append({'s': s, 'r': r, 'g': is_g})
        self.update_chain_display(); self.update_all()

    def remove_last(self):
        if self.command_chain:
            self.command_chain.pop()
            self.update_chain_display(); self.update_all()

    def clear_chain(self):
        self.command_chain = []; self.update_chain_display(); self.update_all()

    def update_chain_display(self):
        self.chain_list_box.delete("0.0", "end")
        for i, item in enumerate(self.command_chain):
            g_tag = "[g]" if item['g'] else "[1st]"
            display_r = "DELETE" if item['r'] == "DELETE" else f"-> {item['r']}"
            self.chain_list_box.insert("end", f"{i+1}. {g_tag} [{item['s']}] {display_r}\n")

    def update_all(self):
        inplace = "-i " if self.inplace_switch.get() else ""
        expressions = []
        for item in self.command_chain:
            s, r, g = item['s'], item['r'], "g" if item['g'] else ""
            if r == "DELETE": expressions.append(f"-e '/{s}/d'")
            else: expressions.append(f"-e 's|{s}|{r}|{g}'")
        
        final_cmd = f"sed {inplace}-E {' '.join(expressions)} target_file.txt"
        self.cmd_output.delete("0.0", "end")
        self.cmd_output.insert("0.0", final_cmd)

        try:
            content = self.input_text.get("0.0", "end-1c")
            processed = content
            for item in self.command_chain:
                s, r, g = item['s'], item['r'], item['g']
                lines = processed.splitlines()
                count = 0 if g else 1
                if r == "DELETE": new_lines = [l for l in lines if not re.search(s, l)]
                else: new_lines = [re.sub(s, r, l, count=count) for l in lines]
                processed = "\n".join(new_lines)
            self.preview_output.delete("0.0", "end"); self.preview_output.insert("0.0", processed)
        except Exception as e:
            self.preview_output.delete("0.0", "end"); self.preview_output.insert("0.0", f"Error: {e}")

    def export_bash_script(self):
        if not self.command_chain:
            messagebox.showwarning("Export Error", "Command chain is empty!")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".sh", filetypes=[("Shell Script", "*.sh")])
        if file_path:
            # Reconstruct the command for script format
            expressions = []
            for item in self.command_chain:
                s, r, g = item['s'], item['r'], "g" if item['g'] else ""
                if r == "DELETE": expressions.append(f"-e '/{s}/d'")
                else: expressions.append(f"-e 's|{s}|{r}|{g}'")
            
            inplace = "-i" if self.inplace_switch.get() else ""
            cmd_part = f"sed {inplace} -E {' '.join(expressions)}"
            
            script_content = f"""#!/bin/bash
# Generated by Pro Sed Architect on {datetime.now().strftime('%Y-%m-%d')}

# Usage: ./script.sh [file1 file2 ...]
if [ $# -eq 0 ]; then
    echo "Usage: $0 file1 [file2 ...]"
    exit 1
fi

for file in "$@"; do
    if [ -f "$file" ]; then
        echo "Processing $file..."
        {cmd_part} "$file"
    else
        echo "Skipping $file: Not a valid file"
    fi
done

echo "Done."
"""
            with open(file_path, "w") as f:
                f.write(script_content)
            messagebox.showinfo("Success", f"Script exported to {file_path}\nRemember to run 'chmod +x' on it!")

    def copy_to_clipboard(self):
        pyperclip.copy(self.cmd_output.get("0.0", "end-1c"))
        self.copy_btn.configure(text="Copied!")
        self.after(1500, lambda: self.copy_btn.configure(text="Copy Command"))

if __name__ == "__main__":
    app = SedGui(); app.mainloop()