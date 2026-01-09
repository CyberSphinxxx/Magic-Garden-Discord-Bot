"""
Magic Garden Bot - User Guide Window.

Standalone Help & Guide window with Discord-style sidebar navigation.
Refactored for reduced code duplication and better maintainability.
"""

import customtkinter as ctk
import webbrowser

# Font constants
FONT_FAMILY = "Segoe UI"


class GuideWindow(ctk.CTkToplevel):
    """Standalone Help & Guide window with Discord-style sidebar navigation."""
    
    def __init__(self, master, colors=None):
        super().__init__(master)
        
        self.title("Magic Garden Bot - User Guide")
        self.geometry("700x520")
        self.resizable(False, False)
        
        # Color palette
        self.colors = colors or {
            'window_bg': "#2b2d31",
            'sidebar_bg': "#202225",
            'card_bg': "#2f3136",
            'text_primary': "#FFFFFF",
            'text_secondary': "#B5BAC1",
            'text_muted': "#949BA4",
            'blurple': "#5865F2",
            'red': "#ED4245",
        }
        
        self.configure(fg_color=self.colors['window_bg'])
        
        # Modal behavior
        self.grab_set()
        self.focus_force()
        
        # Track nav buttons and pages
        self.nav_buttons = {}
        self.pages = {}
        self.current_page = None
        
        # Build UI
        self._build_ui()
        
        # Default to About page
        self.select_frame("about")
    
    # =========================================================================
    # UI HELPERS
    # =========================================================================
    
    def _create_scrollable_page(self, parent):
        """Create a scrollable frame for page content."""
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        return scroll
    
    def _create_page_title(self, parent, title):
        """Create a page title label."""
        ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold"),
            text_color=self.colors['text_primary']
        ).pack(anchor="w", pady=(0, 15))
    
    def _create_section_header(self, parent, title):
        """Create a section header label."""
        ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=self.colors['text_primary']
        ).pack(anchor="w", pady=(10, 5))
    
    def _create_step_card(self, parent, number, text, badge_size=28):
        """Create a styled step card with number badge."""
        card = ctk.CTkFrame(parent, fg_color=self.colors['window_bg'], corner_radius=6)
        card.pack(fill="x", pady=4)
        
        badge = ctk.CTkLabel(
            card,
            text=number,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12 if badge_size < 28 else 14, weight="bold"),
            text_color=self.colors['window_bg'],
            fg_color=self.colors['blurple'],
            width=badge_size,
            height=badge_size,
            corner_radius=badge_size // 2
        )
        badge.pack(side="left", padx=8 if badge_size < 28 else 10, pady=8 if badge_size < 28 else 10)
        
        ctk.CTkLabel(
            card,
            text=text,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11 if badge_size < 28 else 12),
            text_color=self.colors['text_primary'],
            anchor="w",
            wraplength=350,
            justify="left"
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))
    
    def _create_bullet_list(self, parent, items):
        """Create a bullet point list."""
        for item in items:
            ctk.CTkLabel(
                parent,
                text=item,
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                text_color=self.colors['text_secondary'],
                anchor="w"
            ).pack(anchor="w", pady=2)
    
    def _create_definition_row(self, parent, term, description):
        """Create a term/definition row."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            row,
            text=f"{term}:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=self.colors['text_primary'],
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            row,
            text=description,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=self.colors['text_secondary'],
            anchor="w",
            wraplength=400
        ).pack(anchor="w", padx=(10, 0))
    
    def _create_qa_pair(self, parent, question, answer):
        """Create a question/answer pair."""
        ctk.CTkLabel(
            parent,
            text=f"Q: {question}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=self.colors['text_primary'],
            anchor="w"
        ).pack(anchor="w", pady=(10, 2))
        
        ctk.CTkLabel(
            parent,
            text=f"A: {answer}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=self.colors['text_secondary'],
            anchor="w",
            wraplength=400
        ).pack(anchor="w", padx=(15, 0))
    
    # =========================================================================
    # MAIN UI BUILDING
    # =========================================================================
    
    def _build_ui(self):
        """Build the sidebar navigation layout."""
        # Configure grid: 2 columns
        self.grid_columnconfigure(0, weight=0, minsize=180)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # === SIDEBAR (Navigation) ===
        self.navigation_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors['sidebar_bg'],
            corner_radius=0
        )
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        
        # Sidebar Header
        ctk.CTkLabel(
            self.navigation_frame,
            text="USER GUIDE",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
            text_color=self.colors['text_muted']
        ).pack(anchor="w", padx=15, pady=(20, 10))
        
        nav_items = [
            ("about", "About"),
            ("quick_start", "Quick Start"),
            ("auto_shop", "Auto Shop"),
            ("settings", "Settings"),
            ("safety", "Safety"),
            ("faq", "FAQ"),
        ]
        
        for key, label in nav_items:
            btn = ctk.CTkButton(
                self.navigation_frame,
                text=label,
                anchor="w",
                fg_color="transparent",
                hover_color="#36393f",
                text_color=self.colors['text_secondary'],
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                height=40,
                corner_radius=6,
                command=lambda k=key: self.select_frame(k)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[key] = btn
        
        # === CONTENT AREA ===
        self.content_area = ctk.CTkFrame(
            self,
            fg_color=self.colors['card_bg'],
            corner_radius=0
        )
        self.content_area.grid(row=0, column=1, sticky="nsew")
        
        # Create page frames
        self._create_pages()
    
    def _create_pages(self):
        """Create all page frames (hidden initially)."""
        page_builders = {
            "about": self._populate_about,
            "quick_start": self._populate_quick_start,
            "settings": self._populate_settings,
            "safety": self._populate_safety,
            "faq": self._populate_faq,
            "auto_shop": self._populate_auto_shop,
        }
        
        for key, builder in page_builders.items():
            self.pages[key] = ctk.CTkFrame(self.content_area, fg_color="transparent")
            builder(self.pages[key])
    
    def select_frame(self, name):
        """Switch to the selected page and highlight the nav button."""
        # Hide all pages
        for page in self.pages.values():
            page.pack_forget()
        
        # Reset all button colors
        for btn in self.nav_buttons.values():
            btn.configure(fg_color="transparent", text_color=self.colors['text_secondary'])
        
        # Show selected page
        if name in self.pages:
            self.pages[name].pack(fill="both", expand=True, padx=15, pady=15)
            self.current_page = name
        
        # Highlight selected button
        if name in self.nav_buttons:
            self.nav_buttons[name].configure(
                fg_color=self.colors['blurple'],
                text_color=self.colors['text_primary']
            )
    
    # =========================================================================
    # PAGE CONTENT
    # =========================================================================
    
    def _populate_quick_start(self, parent):
        """Content for Quick Start page."""
        scroll = self._create_scrollable_page(parent)
        self._create_page_title(scroll, "Quick Start Guide")
        
        steps = [
            ("1", "Launch the bot application."),
            ("2", "In-game: Move character to Top-Left corner (Tile 0,0)."),
            ("3", "Ensure game window is fully visible (do not minimize)."),
            ("4", "Click '▶ START' on the bot dashboard."),
            ("5", "IMMEDIATELY click back on the game window to focus it."),
            ("6", "Monitor the bot. Click '⏹ STOP' to pause."),
            ("7", "Click '↺ RESET' before starting a fresh session."),
        ]
        
        for num, text in steps:
            self._create_step_card(scroll, num, text)
    
    def _populate_settings(self, parent):
        """Content for Settings page."""
        scroll = self._create_scrollable_page(parent)
        self._create_page_title(scroll, "Settings Reference")
        
        definitions = [
            ("Columns", "Number of columns in your garden grid."),
            ("Harvest Count", "How many times to click each crop tile."),
            ("Move Delay", "Time in seconds between arrow key presses. Recommended: 0.12s."),
            ("Harvest Delay", "Pause time after each harvest click."),
            ("Loop Cooldown", "Wait time between full garden cycles."),
        ]
        
        for term, desc in definitions:
            self._create_definition_row(scroll, term, desc)
    
    def _populate_safety(self, parent):
        """Content for Safety page."""
        scroll = self._create_scrollable_page(parent)
        self._create_page_title(scroll, "Safety Guidelines")
        
        # Warning Box
        warning_frame = ctk.CTkFrame(
            scroll,
            fg_color="#3d2020",
            border_color=self.colors['red'],
            border_width=2,
            corner_radius=8
        )
        warning_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            warning_frame,
            text="⚠️ WARNING",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=self.colors['red']
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            warning_frame,
            text="To avoid detection, do not set delays to 0.0s.\nKeep 'Move Delay' above 0.12s for safe operation.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=self.colors['text_secondary'],
            wraplength=380,
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 10))
        
        notes = [
            "• This bot is for personal, educational use only.",
            "• Use at your own risk. Automation may violate game ToS.",
            "• Do not leave unattended for extended periods.",
            "• We are not responsible for any consequences.",
        ]
        self._create_bullet_list(scroll, notes)
    
    def _populate_faq(self, parent):
        """Content for FAQ page."""
        scroll = self._create_scrollable_page(parent)
        self._create_page_title(scroll, "Frequently Asked Questions")
        
        faqs = [
            ("Map is blank?", "Resize the window to refresh the grid."),
            ("Bot not moving?", "Check if the game window is blocked or minimized."),
            ("Clicks not registering?", "Increase 'Harvest Delay' in Settings."),
            ("Bot moves too fast/slow?", "Adjust 'Move Delay' in Settings."),
            ("How do I change grid size?", "Modify 'Columns' in Settings."),
        ]
        
        for q, a in faqs:
            self._create_qa_pair(scroll, q, a)
    
    def _populate_auto_shop(self, parent):
        """Content for Auto Shop page."""
        scroll = self._create_scrollable_page(parent)
        self._create_page_title(scroll, "Auto Shop Guide")
        
        # Description
        ctk.CTkLabel(
            scroll,
            text="The Auto Shop feature automatically purchases seeds from the in-game shop at regular intervals.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=self.colors['text_secondary'],
            wraplength=400,
            justify="left"
        ).pack(anchor="w", pady=(0, 15))
        
        # How to Use section
        self._create_section_header(scroll, "How to Use")
        
        steps = [
            ("1", "Go to the 'Shop' tab in the sidebar."),
            ("2", "Select the seeds you want to buy from the inventory grid."),
            ("3", "Configure 'Seeds Per Trip' (how many of each seed to buy)."),
            ("4", "Set the 'Shop Interval' (time between shop visits)."),
            ("5", "Click 'START SHOPPING' to begin auto-buying."),
            ("6", "Watch the timer countdown to the next purchase."),
        ]
        
        for num, text in steps:
            self._create_step_card(scroll, num, text, badge_size=24)
        
        # Tips section
        self._create_section_header(scroll, "Tips")
        
        tips = [
            "• Enable Shopping from Farm tab to auto-buy while harvesting.",
            "• The first purchase happens 5 seconds after starting.",
            "• Out-of-stock items are automatically skipped.",
            "• The timer shows when the next shop visit will occur.",
        ]
        self._create_bullet_list(scroll, tips)
    
    def _populate_about(self, parent):
        """Content for About page."""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        # Header - Title
        ctk.CTkLabel(
            container,
            text="Magic Garden Bot",
            font=ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold"),
            text_color=self.colors['text_primary']
        ).pack(anchor="center", pady=(40, 5))
        
        # Description
        ctk.CTkLabel(
            container,
            text="An open-source automation tool for the\nMagic Garden Discord game.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=self.colors['text_secondary'],
            justify="center"
        ).pack(anchor="center", pady=(20, 30))
        
        # Link Buttons
        links_frame = ctk.CTkFrame(container, fg_color="transparent")
        links_frame.pack(anchor="center")
        
        link_buttons = [
            ("GitHub Repository", "https://github.com/CyberSphinxxx/Magic-Garden-Discord-Bot"),
            ("Latest Releases", "https://github.com/CyberSphinxxx/Magic-Garden-Discord-Bot/releases"),
            ("Report an Issue", "https://github.com/CyberSphinxxx/Magic-Garden-Discord-Bot/issues"),
        ]
        
        for text, url in link_buttons:
            btn = ctk.CTkButton(
                links_frame,
                text=text,
                command=lambda u=url: webbrowser.open(u),
                fg_color="#4a4a4a",
                hover_color="#5a5a5a",
                text_color=self.colors['text_primary'],
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                height=36,
                width=220,
                corner_radius=8
            )
            btn.pack(pady=5)
        
        # Footer
        ctk.CTkLabel(
            container,
            text="Created by John Lemar Gonzales aka CyberSphinxxx",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=self.colors['text_secondary']
        ).pack(side="bottom", pady=(30, 20))
