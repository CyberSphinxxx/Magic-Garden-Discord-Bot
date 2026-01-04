import customtkinter as ctk

class ToolTip:
    """
    Lightweight tooltip that appears on hover.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        
        self.widget.bind("<Enter>", self._show_tip)
        self.widget.bind("<Leave>", self._hide_tip)
    
    def _show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        
        # Get position below the widget
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tip_window = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)  # Remove window decorations
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)
        
        label = ctk.CTkLabel(
            tw,
            text=self.text,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            fg_color="#202020",
            text_color="#FFFFFF",
            corner_radius=4,
            padx=8,
            pady=4
        )
        label.pack()
    
    def _hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None
