import os
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox
from PIL import Image, ImageTk


class UserProfilePopup:
    def __init__(self):
        # Hard-coded data
        name = "Username Goez Here"
        header = "The Colony Scholar 🐧"
        description = "Just like emperor penguins huddling together in the Antarctic cold, the Colony Scholar thrives when surrounded by their study group. They organize collaborative sessions, rotate teaching roles like penguins shifting in the huddle, and constantly share resources through group chats. Solo studying feels isolating and drains their motivation—they need the energy and accountability of the colony to stay focused and process information through discussion."
        tags = ["Robarts Commons", "Gerstein Library", "Hart House"]
        
        # Construct absolute path to image
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        photo_path = os.path.join(project_root, "assets", "Pengu.jpg")
        
        extra_details = {
            'Start Sessions': 4,
            'End Sessions': 4,
            'Look Aways': 3,
            'Switch Tabs': 7
        }
        
        # Create a brand new root window with its own mainloop
        self.root = tk.Tk()
        self.root.title("User Profile")
        self.root.geometry("700x400")
        self.root.resizable(False, False)
        
        # Exit Python when window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Colors
        self.bg_color = "#ffffff"
        self.accent_color = "#4a90e2"
        self.text_color = "#333333"
        self.light_gray = "#f5f5f5"
        
        self.root.configure(bg=self.bg_color)
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # LEFT SIDE - Photo
        photo_frame = tk.Frame(main_frame, bg=self.accent_color, width=250)
        photo_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        photo_frame.pack_propagate(False)
        
        # Large photo
        try:
            # Load and resize image to fit the frame
            img = Image.open(photo_path)
            img = img.resize((250, 400), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            photo_label = tk.Label(photo_frame, image=photo, bg=self.accent_color)
            photo_label.image = photo  # Keep a reference
            photo_label.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            print(f"⚠️  Could not load image from {photo_path}: {e}")
            # Fallback to initial if image fails to load
            self._create_initial_placeholder(photo_frame, name)
        
        # RIGHT SIDE - Details
        details_frame = tk.Frame(main_frame, bg=self.bg_color)
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Name
        name_label = tk.Label(details_frame, text=name, 
                            font=("Arial", 26, "bold"),
                            bg=self.bg_color, fg=self.text_color)
        name_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Description box
        desc_frame = tk.Frame(details_frame, bg=self.light_gray, relief=tk.FLAT)
        desc_frame.pack(fill=tk.BOTH, pady=(0, 15))
        
        # Header inside box
        header_label = tk.Label(desc_frame, text=header,
                              font=("Arial", 12, "bold"),
                              bg=self.light_gray, fg=self.accent_color)
        header_label.pack(padx=15, pady=(15, 5), anchor=tk.W)
        
        desc_label = tk.Label(desc_frame, text=description,
                            font=("Arial", 11),
                            bg=self.light_gray, fg=self.text_color,
                            wraplength=320, justify=tk.LEFT)
        desc_label.pack(padx=15, pady=(5, 15), anchor=tk.W)
        
        # Tags section
        tags_container = tk.Frame(details_frame, bg=self.bg_color)
        tags_container.pack(fill=tk.X, pady=(0, 15))
        
        tags_label = tk.Label(tags_container, text="FAVORITE SPOTS",
                            font=("Arial", 9, "bold"),
                            bg=self.bg_color, fg=self.text_color)
        tags_label.pack(anchor=tk.W, pady=(0, 8))
        
        tags_frame = tk.Frame(tags_container, bg=self.bg_color)
        tags_frame.pack(fill=tk.X)
        
        # Create tag buttons
        for tag in tags:
            tag_btn = tk.Label(tags_frame, text=tag,
                             font=("Arial", 9),
                             bg=self.accent_color, fg="white",
                             padx=10, pady=5, relief=tk.FLAT)
            tag_btn.pack(side=tk.LEFT, padx=(0, 5), pady=2)
        
        # Extra details
        if extra_details:
            extra_frame = tk.Frame(details_frame, bg=self.bg_color)
            extra_frame.pack(fill=tk.X, pady=(10, 0))
            
            for key, value in extra_details.items():
                detail_row = tk.Frame(extra_frame, bg=self.bg_color)
                detail_row.pack(fill=tk.X, pady=3)
                
                tk.Label(detail_row, text=f"{key}:", 
                        font=("Arial", 10, "bold"),
                        bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT)
                
                tk.Label(detail_row, text=value,
                        font=("Arial", 10),
                        bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT, padx=(5, 0))
    
    def _create_initial_placeholder(self, frame, name):
        """Create initial letter placeholder when no photo is provided"""
        photo_canvas = tk.Canvas(frame, bg=self.accent_color, highlightthickness=0)
        photo_canvas.pack(fill=tk.BOTH, expand=True)
        initial = name[0].upper() if name else "?"
        photo_canvas.create_text(125, 200, text=initial, 
                                font=("Arial", 120, "bold"), fill="white")
    
    def on_close(self):
        """Handle window close event - exit all Python processes"""
        print("👋 Profile closed - shutting down all processes...")
        self.root.destroy()
        import sys
        import os
        import signal
        
        # Kill all processes in the same process group
        os.killpg(os.getpgrp(), signal.SIGTERM)
        
        # Fallback in case killpg doesn't work
        sys.exit(0)
        
    def show(self):
        # Run its own mainloop
        self.root.mainloop()


# Example usage - for standalone testing
if __name__ == "__main__":
    profile = UserProfilePopup()
    profile.show()