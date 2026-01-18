import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os
import subprocess
import sys
import time


class FeedbackForm:
    def __init__(self, root):
        self.root = root
        self.root.title("FlowState Session Feedback")
        self.root.geometry("550x700")
        self.root.configure(bg="#ffecc4")

        # Create main frame
        main_frame = tk.Frame(root, bg="#ffecc4", padx=40, pady=35)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = tk.Label(
            main_frame,
            text="✨ Session Feedback",
            font=("SF Pro Display", 28, "bold"),
            bg="#ffecc4",
            fg="#1a1a1a"
        )
        title.pack(pady=(0, 25))

        # Focus Rating Section
        focus_frame = tk.Frame(main_frame, bg="#ffecc4")
        focus_frame.pack(fill=tk.X, pady=15)

        focus_label = tk.Label(
            focus_frame,
            text="How focused were you?",
            font=("SF Pro Display", 14, "bold"),
            bg="#ffecc4",
            fg="#1a1a1a"
        )
        focus_label.pack(anchor=tk.W)

        # Focus scale
        scale_frame = tk.Frame(main_frame, bg="#ffecc4")
        scale_frame.pack(fill=tk.X, pady=15)

        self.focus_var = tk.IntVar(value=5)
        self.focus_value_label = tk.Label(
            scale_frame,
            text="5",
            font=("SF Pro Display", 48, "bold"),
            bg="#ffecc4",
            fg="#db2323"
        )
        self.focus_value_label.pack()

        self.focus_scale = tk.Scale(
            scale_frame,
            from_=1,
            to=10,
            orient=tk.HORIZONTAL,
            variable=self.focus_var,
            command=self.update_focus_label,
            length=450,
            bg="#db2323",
            highlightthickness=0,
            troughcolor="#e8e8ed",
            activebackground="#0500ff",
            showvalue=0,
            bd=0,
            sliderrelief=tk.FLAT
        )
        self.focus_scale.pack(pady=10)

        # Scale labels
        labels_frame = tk.Frame(scale_frame, bg="#ffecc4")
        labels_frame.pack()
        tk.Label(labels_frame, text="Not Focused", bg="#ffecc4", fg="#8e8e93", font=("SF Pro Display", 12)).pack(side=tk.LEFT, padx=(0, 280))
        tk.Label(labels_frame, text="Very Focused", bg="#ffecc4", fg="#8e8e93", font=("SF Pro Display", 12)).pack(side=tk.RIGHT)

        # Work Environment Section
        env_frame = tk.Frame(main_frame, bg="#ffecc4")
        env_frame.pack(fill=tk.X, pady=(25, 10))

        env_label = tk.Label(
            env_frame,
            text="Work Environment",
            font=("SF Pro Display", 14, "bold"),
            bg="#ffecc4",
            fg="#1a1a1a"
        )
        env_label.pack(anchor=tk.W)

        # Environment text box
        self.env_text = tk.Text(
            main_frame,
            height=5,
            width=50,
            font=("SF Pro Display",12),
            wrap=tk.WORD,
            relief=tk.SOLID,
            borderwidth=2,
            bd=2,
            highlightthickness=0,
            highlightcolor="#db2323",
            highlightbackground="#e8e8ed",
            fg="#000000"
        )       
        self.env_text.pack(pady=10)
        self.env_text.insert("1.0", "e.g., Quiet home office, coffee shop, library...")
        self.env_text.bind("<FocusIn>", self.clear_placeholder)
        self.env_text.config(fg="#8e8e93")  # This makes the placeholder gray

        # Optional: Additional notes
        notes_frame = tk.Frame(main_frame, bg="#ffecc4")
        notes_frame.pack(fill=tk.X, pady=(15, 10))

        notes_label = tk.Label(
            notes_frame,
            text="Additional Notes (optional)",
            font=("SF Pro Display", 14, "bold"),
            bg="#ffecc4",
            fg="#000000"
        )
        notes_label.pack(anchor=tk.W)

        self.notes_text = tk.Text(
            main_frame,
            height=3,
            width=50,
            font=("SF Pro Display", 12),
            wrap=tk.WORD,
            relief=tk.SOLID,
            borderwidth=2,
            bd=2,
            highlightthickness=0,
            highlightcolor="#db2323",
            highlightbackground="#db2323",
            fg="#ffecc4"
        )
        self.notes_text.pack(pady=10)

        # Submit button
        submit_btn = tk.Button(
            main_frame,
            text="Submit Feedback",
            command=self.submit_feedback,
            font=("SF Pro Display", 14, "bold"),
            bg="#db2323",
            fg="#db2323",
            padx=40,
            pady=12,
            relief=tk.FLAT,
            cursor="hand2",
            bd=0,
            activebackground="#db2323",
            activeforeground="#db2323"
        )
        submit_btn.pack(pady=25)

    def update_focus_label(self, value):
        self.focus_value_label.config(text=value)

    def clear_placeholder(self, event):
        if self.env_text.get("1.0", tk.END).strip() == "e.g., Quiet home office, coffee shop, library...":
            self.env_text.delete("1.0", tk.END)
            self.env_text.config(fg="#ffffff")  # Keep original black text for visibility

    def submit_feedback(self):
        # Get values
        focus_rating = self.focus_var.get()
        environment = self.env_text.get("1.0", tk.END).strip()
        notes = self.notes_text.get("1.0", tk.END).strip()

        # Validate
        if environment == "e.g., Quiet home office, coffee shop, library..." or not environment:
            messagebox.showwarning("Missing Information", "Please describe your work environment.")
            return

        # Create feedback data
        feedback = {
            "timestamp": datetime.now().isoformat(),
            "focus_rating": focus_rating,
            "work_environment": environment,
            "additional_notes": notes if notes else None
        }

        self.save_feedback(feedback)
    
        # Launch profile.py as separate process
        script_dir = os.path.dirname(os.path.abspath(__file__))
        profile_path = os.path.join(script_dir, '..', 'frontend', 'profile.py')
        subprocess.Popen([sys.executable, profile_path])
        
        # Close feedback form
        self.root.destroy()
        
        # Trigger amplitude
        self.trigger_amplitude_analysis(focus_rating)

    def save_feedback(self, feedback):
        # Create feedback directory if it doesn't exist
        os.makedirs("feedback_data", exist_ok=True)

        # Append to JSON file
        filename = "feedback_data/session_feedback.json"

        try:
            # Load existing data
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    data = json.load(f)
            else:
                data = []

            # Add new feedback
            data.append(feedback)

            # Save back to file
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"Feedback saved to {filename}")

        except Exception as e:
            print(f"Error saving feedback: {e}")
            messagebox.showerror("Error", "Failed to save feedback.")

    def trigger_amplitude_analysis(self, focus_rating):
        """Trigger amplitude_response.py with the human focus rating"""
        try:
            # feedback_form.py is in backend/, amplitude_response.py is in backend/amplitude_service/
            script_dir = os.path.dirname(os.path.abspath(__file__))
            amplitude_path = os.path.join(script_dir, 'amplitude_service', 'amplitude_response.py')
            
            # Pass focus_rating as a command line argument
            subprocess.Popen([sys.executable, amplitude_path, str(focus_rating)])

            print(f"Triggered amplitude analysis with focus_rating={focus_rating}")
            print(f"📂 Amplitude path: {amplitude_path}")
        except Exception as e:
            print(f"Error triggering amplitude analysis: {e}")


def main():
    
    root = tk.Tk()
    app = FeedbackForm(root)
    root.mainloop()


if __name__ == "__main__":
    main()