import customtkinter as ctk

# Animation constants
PULSE_INTERVAL_MS = 500
PULSE_COLOR_DIM = "#dddddd"
PULSE_COLOR_BRIGHT = "white"


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
        self.dot = self.canvas.create_oval(1, 1, 9, 9, fill=PULSE_COLOR_BRIGHT, outline="")
        
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
            self.canvas.itemconfig(self.dot, fill=PULSE_COLOR_BRIGHT)
            
    def _animate_pulse(self):
        """Simple pulsing effect for the dot."""
        # Early exit if animation was stopped
        if not self._animating:
            return
        
        # Toggle dot color between bright and dim
        current_fill = self.canvas.itemcget(self.dot, "fill")
        new_fill = PULSE_COLOR_DIM if current_fill == PULSE_COLOR_BRIGHT else PULSE_COLOR_BRIGHT
        self.canvas.itemconfig(self.dot, fill=new_fill)
        
        # Schedule next pulse
        self.after(PULSE_INTERVAL_MS, self._animate_pulse)
