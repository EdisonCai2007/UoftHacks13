import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os


class FeedbackForm:
    def __init__(self, root):
        self.root = root
        self.root.title("FlowState Session Feedback")
        self.root.geometry("500x600")
        self.root.configure(bg="#f0f0f0")

        # Create main frame
        main_frame = tk.Frame(root, bg="#f0f0f0", padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = tk.Label(
            main_frame,
            text="Session Feedback",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="#333"
        )
        title.pack(pady=(0, 20))

        # Focus Rating Section
        focus_frame = tk.Frame(main_frame, bg="#f0f0f0")
        focus_frame.pack(fill=tk.X, pady=10)

        focus_label = tk.Label(
            focus_frame,
            text="How focused were you during this session?",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#333"
        )
        focus_label.pack(anchor=tk.W)

        # Focus scale
        scale_frame = tk.Frame(main_frame, bg="#f0f0f0")
        scale_frame.pack(fill=tk.X, pady=10)

        self.focus_var = tk.IntVar(value=5)
        self.focus_value_label = tk.Label(
            scale_frame,
            text="5",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
            fg="#0066cc"
        )
        self.focus_value_label.pack()

        self.focus_scale = tk.Scale(
            scale_frame,
            from_=1,
            to=10,
            orient=tk.HORIZONTAL,
            variable=self.focus_var,
            command=self.update_focus_label,
            length=400,
            bg="#f0f0f0",
            highlightthickness=0,
            troughcolor="#ddd"
        )
        self.focus_scale.pack(pady=5)

        # Scale labels
        labels_frame = tk.Frame(scale_frame, bg="#f0f0f0")
        labels_frame.pack()
        tk.Label(labels_frame, text="Not Focused", bg="#f0f0f0", fg="#666").pack(side=tk.LEFT, padx=(0, 245))
        tk.Label(labels_frame, text="Very Focused", bg="#f0f0f0", fg="#666").pack(side=tk.RIGHT)

        # Work Environment Section
        env_frame = tk.Frame(main_frame, bg="#f0f0f0")
        env_frame.pack(fill=tk.X, pady=(30, 10))

        env_label = tk.Label(
            env_frame,
            text="Describe your work environment:",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#333"
        )
        env_label.pack(anchor=tk.W)

        # Environment text box
        self.env_text = tk.Text(
            main_frame,
            height=8,
            width=50,
            font=("Arial", 11),
            wrap=tk.WORD,
            relief=tk.SOLID,
            borderwidth=1
        )
        self.env_text.pack(pady=10)
        self.env_text.insert("1.0", "e.g., Quiet home office, coffee shop, library...")
        self.env_text.bind("<FocusIn>", self.clear_placeholder)
        self.env_text.config(fg="#999")

        # Optional: Additional notes
        notes_frame = tk.Frame(main_frame, bg="#f0f0f0")
        notes_frame.pack(fill=tk.X, pady=(20, 10))

        notes_label = tk.Label(
            notes_frame,
            text="Additional notes (optional):",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#333"
        )
        notes_label.pack(anchor=tk.W)

        self.notes_text = tk.Text(
            main_frame,
            height=4,
            width=50,
            font=("Arial", 11),
            wrap=tk.WORD,
            relief=tk.SOLID,
            borderwidth=1
        )
        self.notes_text.pack(pady=10)

        # Submit button
        submit_btn = tk.Button(
            main_frame,
            text="Submit Feedback",
            command=self.submit_feedback,
            font=("Arial", 12, "bold"),
            bg="#0066cc",
            fg="white",
            padx=30,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        submit_btn.pack(pady=20)

    def update_focus_label(self, value):
        self.focus_value_label.config(text=value)

    def clear_placeholder(self, event):
        if self.env_text.get("1.0", tk.END).strip() == "e.g., Quiet home office, coffee shop, library...":
            self.env_text.delete("1.0", tk.END)
            self.env_text.config(fg="#000")

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

        # Save to file
        self.save_feedback(feedback)

        # Show confirmation
        messagebox.showinfo(
            "Feedback Submitted",
            f"Thank you for your feedback!\n\nFocus Rating: {focus_rating}/10"
        )

        # Close window
        self.root.destroy()

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


def main():
    root = tk.Tk()
    app = FeedbackForm(root)
    root.mainloop()


if __name__ == "__main__":
    main()