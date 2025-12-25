import customtkinter as ctk

class CollapsibleFrame(ctk.CTkFrame):
    def __init__(self, master, title="Configuration", **kwargs):
        super().__init__(master, **kwargs)
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0) # Header
        self.rowconfigure(1, weight=1) # Content (when expanded)
        
        self.expanded = False
        
        # --- Header (Clickable) ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        
        self.header_frame.bind("<Button-1>", self.toggle)
        self.header_frame.bind("<Enter>", lambda e: self.header_frame.configure(fg_color="#3b3d42"))
        self.header_frame.bind("<Leave>", lambda e: self.header_frame.configure(fg_color="transparent"))
        
        # Icon (ToggleButton)
        self.toggle_btn = ctk.CTkLabel(
            self.header_frame,
            text="▼",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#949BA4"
        )
        self.toggle_btn.pack(side="right", padx=10)
        self.toggle_btn.bind("<Button-1>", self.toggle)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#949BA4"
        )
        self.title_label.pack(side="left", padx=10, pady=8)
        self.title_label.bind("<Button-1>", self.toggle)
        
        # --- Content Frame ---
        self.content_frame = ctk.CTkFrame(
            self, 
            fg_color="transparent",
            corner_radius=0
        )
        # We don't grid it initially (Collapsed)
        
    def toggle(self, event=None):
        if self.expanded:
            self.expanded = False
            self.content_frame.grid_forget()
            self.toggle_btn.configure(text="▼")
        else:
            self.expanded = True
            self.content_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
            self.toggle_btn.configure(text="▲")
