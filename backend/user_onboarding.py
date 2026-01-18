import tkinter as tk
import platform

IS_MAC = platform.system() != "Windows"

class TaskInputDialog:
    """Styled dialog that works on both Windows and macOS."""
    def __init__(self, parent):
        self.result = []
        self.with_friends = False
        self.with_food = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("FlowState Tasks")
        self.dialog.geometry("450x450")
        
        # Colors & Fonts
        self.bg_color = "#ffecc4"
        self.text_bg = "#6a4800"
        self.accent_color = "#db2323"
        self.font_main = "Alice" if not IS_MAC else "Optima"

        self.dialog.config(bg=self.bg_color)
        self.dialog.transient(parent)

        # UI Elements
        tk.Label(self.dialog, text="What are you working on?", 
                 font=(self.font_main, 16, "bold"), bg=self.bg_color, 
                 fg=self.accent_color, pady=15).pack()

        text_frame = tk.Frame(self.dialog, bg=self.bg_color)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        self.text_area = tk.Text(text_frame, font=("Arial", 12), bg=self.text_bg, 
                                 fg="white", insertbackground="white", padx=10, pady=10, bd=0,
                                 height=8)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Checkboxes
        checkbox_frame = tk.Frame(self.dialog, bg=self.bg_color)
        checkbox_frame.pack(pady=15)
        
        self.friends_var = tk.BooleanVar()
        self.food_var = tk.BooleanVar()
        
        tk.Checkbutton(checkbox_frame, text="Studying with friends", 
                      variable=self.friends_var, bg=self.bg_color, fg="black",
                      selectcolor=self.accent_color, activebackground=self.bg_color,
                      activeforeground="white", font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=3)
        
        tk.Checkbutton(checkbox_frame, text="Studying with food/drinks", 
                      variable=self.food_var, bg=self.bg_color, fg="black",
                      selectcolor=self.accent_color, activebackground=self.bg_color,
                      activeforeground="white", font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=3)
        
        # Bindings
        self.text_area.bind("<FocusIn>", self.clear_placeholder)
        shortcut = "<Meta-Return>" if IS_MAC else "<Control-Return>"
        self.dialog.bind(shortcut, lambda e: self.submit())

        # Buttons
        btn_frame = tk.Frame(self.dialog, bg=self.bg_color)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="Add Tasks", command=self.submit, bg=self.accent_color,
                  fg="#0f172a", font=(self.accent_color, 11, "bold"), padx=20).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="Cancel", command=self.cancel, bg=self.accent_color,
                  fg="#0f172a", font=(self.accent_color, 11, "bold"), padx=20).pack(side=tk.LEFT, padx=10)

        # Helper label for shortcut
        hint = "⌘ + Enter" if IS_MAC else "Ctrl + Enter"
        tk.Label(self.dialog, text=f"Shortcut: {hint}", bg=self.bg_color, fg="#64748b", font=("Arial", 8)).pack()

        # Setup focus after everything is rendered
        self.dialog.update_idletasks()
        self.dialog.grab_set()
        self.text_area.focus_set()

    def clear_placeholder(self, event):
        if "e.g.," in self.text_area.get("1.0", tk.END):
            self.text_area.delete("1.0", tk.END)
            self.text_area.config(fg="white")

    def submit(self):
        content = self.text_area.get("1.0", tk.END).strip()
        if content:
            self.result = [l.strip() for l in content.split("\n") if l.strip()]
        self.with_friends = self.friends_var.get()
        self.with_food = self.food_var.get()
        self.dialog.destroy()
        self.dialog.master.quit()

    def cancel(self):
        self.result = []
        self.with_friends = False
        self.with_food = False
        self.dialog.destroy()
        self.dialog.master.quit()
        import sys
        sys.exit(0)  # Kill the entire program