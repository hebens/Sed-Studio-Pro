import customtkinter as ctk
import re

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SedGui(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Pro Sed Builder & Simulator")
        self.geometry("1000x750")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- LEFT PANEL: Settings ---
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(self.left_frame, text="Command Settings", font=("Roboto", 22, "bold")).pack(pady=10)

        self.search_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Search Pattern (e.g. ([0-9]+))", width=380)
        self.search_entry.pack(pady=10)

        self.replace_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Replace with (e.g. ID-\\1)", width=380)
        self.replace_entry.pack(pady=10)

        self.file_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Filename (e.g. data.txt)", width=380)
        self.file_entry.pack(pady=10)

        self.range_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Line Range (Optional, e.g. 1,5)", width=380)
        self.range_entry.pack(pady=10)

        # Switches Container
        self.switch_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.switch_frame.pack(pady=10)

        self.global_switch = ctk.CTkSwitch(self.switch_frame, text="Global (g)")
        self.global_switch.grid(row=0, column=0, padx=10, pady=5)
        self.global_switch.select()

        self.extended_switch = ctk.CTkSwitch(self.switch_frame, text="Extended Regex (-E)")
        self.extended_switch.grid(row=0, column=1, padx=10, pady=5)
        self.extended_switch.select() # Enabled by default for ease of use

        self.inplace_switch = ctk.CTkSwitch(self.switch_frame, text="In-place (-i)")
        self.inplace_switch.grid(row=1, column=0, columnspan=2, pady=10)

        self.gen_button = ctk.CTkButton(self.left_frame, text="Update Command & Preview", 
                                        command=self.update_all, fg_color="#3498db", hover_color="#2980b9", height=40)
        self.gen_button.pack(pady=15)

        self.cmd_output = ctk.CTkTextbox(self.left_frame, height=80, width=380, font=("Courier New", 14), fg_color="#1e1e1e")
        self.cmd_output.pack(pady=10)

        # --- RIGHT PANEL: Preview ---
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(self.right_frame, text="Live Preview Sandbox", font=("Roboto", 22, "bold")).pack(pady=10)

        ctk.CTkLabel(self.right_frame, text="Input Text:").pack()
        self.input_text = ctk.CTkTextbox(self.right_frame, height=220, width=450)
        self.input_text.pack(pady=5)
        self.input_text.insert("0.0", "Order_ID: 5521\nOrder_ID: 9928\nStatus: Pending")

        ctk.CTkLabel(self.right_frame, text="Result After Sed:").pack()
        self.preview_output = ctk.CTkTextbox(self.right_frame, height=220, width=450, fg_color="#1e1e1e", text_color="#2ecc71")
        self.preview_output.pack(pady=5)

    def update_all(self):
        search = self.search_entry.get()
        replace = self.replace_entry.get()
        filename = self.file_entry.get() or "file.txt"
        line_range = self.range_entry.get()
        
        # Flag logic
        inplace = "-i " if self.inplace_switch.get() else ""
        extended = "-E " if self.extended_switch.get() else ""
        g_flag = "g" if self.global_switch.get() else ""
        
        # 1. Generate Command String
        final_cmd = f"sed {inplace}{extended}'{line_range}s|{search}|{replace}|{g_flag}' {filename}"
        self.cmd_output.delete("0.0", "end")
        self.cmd_output.insert("0.0", final_cmd)

        # 2. Simulate Preview
        if search:
            try:
                original_content = self.input_text.get("0.0", "end-1c")
                lines = original_content.splitlines()
                
                # Python re.sub handles \1, \2 etc for backreferences, just like sed
                # However, sed uses \1 and Python re uses \1 as well, so they match!
                count = 0 if self.global_switch.get() else 1
                processed_lines = [re.sub(search, replace, line, count=count) for line in lines]
                
                self.preview_output.delete("0.0", "end")
                self.preview_output.insert("0.0", "\n".join(processed_lines))
            except Exception as e:
                self.preview_output.delete("0.0", "end")
                self.preview_output.insert("0.0", f"Regex Error: {e}")

if __name__ == "__main__":
    app = SedGui()
    app.mainloop()