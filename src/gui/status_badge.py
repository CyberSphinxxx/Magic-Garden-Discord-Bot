import customtkinter as ctk

class StatusBadge(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=20, fg_color="#D97706", **kwargs)  # Default IDLE (Amber)
        
        self.colors = {
            "IDLE": "#D97706",    # Amber-600
            "RUNNING": "#2EA043", # Green
            "STOPPED": "#ED4245", # Red
        }
        
        self.current_status = "IDLE"
        self._animating = False
        
        # Inner layout
        self.inner_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.inner_frame.pack(padx=12, pady=6)
        
        # Pulse Circle Canvas
        self.canvas = ctk.CTkCanvas(
            self.inner_frame,
            width=10,
            height=10,
            bg=self.colors["IDLE"],
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(side="left", padx=(0, 8))
        
        # Draw initial circle
        self.dot = self.canvas.create_oval(1, 1, 9, 9, fill="white", outline="")
        
        # Text Label
        self.label = ctk.CTkLabel(
            self.inner_frame,
            text="IDLE",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="white"
        )
        self.label.pack(side="left")
        
    def set_status(self, status):
        """Update the badge status and color."""
        status = status.upper()
        if status not in self.colors:
            return
            
        self.current_status = status
        color = self.colors[status]
        
        # Update Colors
        self.configure(fg_color=color)
        self.canvas.configure(bg=color)
        self.label.configure(text=status)
        
        # Handle Animation
        if status == "RUNNING":
            if not self._animating:
                self._animating = True
                self._animate_pulse()
        else:
            self._animating = False
            self.canvas.itemconfig(self.dot, fill="white") # Reset dot
            
    def _animate_pulse(self):
        """Simple pulsing effect for the dot."""
        if not self._animating:
            return
            
        # Toggle dot color between white and transparent/dim
        current_fill = self.canvas.itemcget(self.dot, "fill")
        new_fill = "" if current_fill == "white" else "white"
        
        # Actually, let's just toggle opacity or similar.
        # Tkinter canvas colors can be tricky. Let's toggle between white and a slightly transparent white (greyish)
        # or just blink it.
        
        if current_fill == "white":
             new_fill = "#dddddd" # slightly dimmer
        else:
             new_fill = "white"
             
        self.canvas.itemconfig(self.dot, fill=new_fill)
        
        # Recurse
        self.after(500, self._animate_pulse)
