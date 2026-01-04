import customtkinter as ctk

class MiniMapWidget(ctk.CTkFrame):
    def __init__(self, master, rows=10, cols=10, **kwargs):
        super().__init__(master, **kwargs)
        
        self.rows = rows
        self.cols = cols
        
        # Colors
        self.color_default = "#2b2d31"  # Dark Grey
        self.color_grid = "#40444b"     # Subtle Grey
        self.color_active = "#2EA043"   # Green (Github/Discord style)
        
        # Create Canvas (fill container dynamically)
        self.canvas = ctk.CTkCanvas(
            self,
            bg=self.color_default,
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        self.tiles = {}  # Store (row, col) -> item_id
        self.current_pos = (0, 0)
        
        # Bind resize event to canvas
        self.canvas.bind("<Configure>", self._draw_grid)

    def _draw_grid(self, event=None):
        """Draws a centered square grid based on available canvas size."""
        self.canvas.delete("all")
        self.tiles.clear()
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Avoid issues before fully rendered
        if w <= 1 or h <= 1:
            return
        
        # Calculate the largest square that fits
        margin = 10  # Small padding from edges
        available_w = w - margin * 2
        available_h = h - margin * 2
        
        grid_size = min(available_w, available_h)
        if grid_size <= 0:
            return
        
        # Center the grid
        offset_x = (w - grid_size) / 2
        offset_y = (h - grid_size) / 2
        
        cell_size = grid_size / max(self.rows, self.cols)
        
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = offset_x + c * cell_size
                y1 = offset_y + r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                # Create rectangle for the tile
                item_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=self.color_default,
                    outline=self.color_grid,
                    width=1
                )
                self.tiles[(r, c)] = item_id
        
        # Redraw active position
        self._highlight_tile(self.current_pos[0], self.current_pos[1])

    def update_position(self, row, col):
        """Updates the active tile position."""
        # bounds check
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return

        # Restore previous tile color
        prev_r, prev_c = self.current_pos
        if (prev_r, prev_c) in self.tiles:
            self.canvas.itemconfig(self.tiles[(prev_r, prev_c)], fill=self.color_default)
            
        # Highlight new tile
        self.current_pos = (row, col)
        self._highlight_tile(row, col)

    def _highlight_tile(self, row, col):
        if (row, col) in self.tiles:
            self.canvas.itemconfig(self.tiles[(row, col)], fill=self.color_active)
