import tkinter as tk
from tkinter import messagebox
import platform

class LoginDialog:
    """Styled Login Dialog matching the FlowState theme."""
    def __init__(self, parent, api_client):
        self.api_client = api_client
        self.success = False
        
        # Determine valid parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("FlowState Login")
        self.dialog.geometry("600x600")
        
        # Colors
        self.bg_color = "#1e293b"
        self.text_bg = "#334155"
        self.accent_color = "#38bdf8"
        self.text_color = "white"
        
        self.dialog.config(bg=self.bg_color)
        self.dialog.transient(parent)
        
        # Define Fonts
        try:
            is_mac = platform.system() == "Darwin"
            font_main = "Alice" if not is_mac else "Optima"
            font_input = ("Arial", 12)
        except:
            font_main = "Arial"
            font_input = ("Arial", 12)
        
        # Header
        tk.Label(self.dialog, text="Welcome Back", 
                 font=(font_main, 20, "bold"), bg=self.bg_color, 
                 fg=self.accent_color, pady=20).pack()
        
        # Input Frame
        frame = tk.Frame(self.dialog, bg=self.bg_color)
        frame.pack(fill=tk.BOTH, expand=True, padx=40)
        
        # Username
        tk.Label(frame, text="Username", bg=self.bg_color, fg="#94a3b8", 
                 font=("Arial", 10), anchor="w").pack(fill=tk.X, pady=(10, 2))
        self.username_entry = tk.Entry(frame, bg=self.text_bg, fg=self.text_color, 
                                     font=font_input, relief="flat", insertbackground="white")
        self.username_entry.pack(fill=tk.X, ipady=5)
        
        # Password
        tk.Label(frame, text="Password", bg=self.bg_color, fg="#94a3b8", 
                 font=("Arial", 10), anchor="w").pack(fill=tk.X, pady=(15, 2))
        self.password_entry = tk.Entry(frame, bg=self.text_bg, fg=self.text_color, 
                                     font=font_input, relief="flat", insertbackground="white", show="•")
        self.password_entry.pack(fill=tk.X, ipady=5)
        
        # Login Button
        tk.Button(frame, text="Log In", command=self.login, bg=self.accent_color,
                 fg="#0f172a", font=(font_main, 12, "bold"), pady=5, relief="flat",
                 activebackground="#7dd3fc").pack(fill=tk.X, pady=30)
                 
        # Status Label
        self.status_label = tk.Label(frame, text="", bg=self.bg_color, fg="#ff4444", font=("Arial", 9))
        self.status_label.pack()

        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.login())
        
        # Center the window
        self.center_window()
        
        self.dialog.grab_set()
        self.username_entry.focus_set()

    def center_window(self):
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.status_label.config(text="Please enter both username and password")
            return
            
        self.status_label.config(text="Logging in...", fg=self.accent_color)
        self.dialog.update()
        
        success, message = self.api_client.login(username, password)
        
        if success:
            self.success = True
            self.dialog.destroy()
            self.dialog.master.quit()
        else:
            self.status_label.config(text=message, fg="#ef4444")
            self.password_entry.delete(0, tk.END)

    def is_authenticated(self):
        return self.success
