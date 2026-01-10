"""
Magic Garden Bot - Update Dialog.

A modern dialog for displaying update availability and handling the update process.
"""

import customtkinter as ctk
import webbrowser
from typing import Callable, Optional, Dict, Any

from src.gui.constants import FONT_FAMILY, UI_COLORS


class UpdateDialog(ctk.CTkToplevel):
    """
    Modal dialog for showing update availability and handling downloads.
    
    Features:
    - Version comparison display
    - Release notes preview
    - Download progress bar
    - Options: Update Now, Remind Later, Skip This Version
    """
    
    def __init__(
        self,
        parent,
        update_info: Dict[str, Any],
        on_update: Optional[Callable[[], None]] = None,
        on_skip: Optional[Callable[[str], None]] = None,
        on_dismiss: Optional[Callable[[], None]] = None,
        colors: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the update dialog.
        
        Args:
            parent: Parent window
            update_info: Dictionary from updater.check_for_updates()
            on_update: Callback when user clicks Update Now
            on_skip: Callback when user clicks Skip This Version (receives version string)
            on_dismiss: Callback when user clicks Remind Me Later or closes dialog
            colors: Color palette (uses UI_COLORS if not provided)
        """
        super().__init__(parent)
        
        self.update_info = update_info
        self.on_update = on_update
        self.on_skip = on_skip
        self.on_dismiss = on_dismiss
        self.colors = colors or UI_COLORS
        
        # Window setup
        self.title("Update Available")
        self.geometry("500x450")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 450) // 2
        self.geometry(f"+{x}+{y}")
        
        # Configure appearance
        self.configure(fg_color=self.colors['window_bg'])
        
        # Track download state
        self.is_downloading = False
        self.download_cancelled = False
        
        # Build UI
        self._build_ui()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _build_ui(self):
        """Build the dialog UI."""
        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=20)
        
        # === HEADER ===
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        
        # Update icon and title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(fill="x")
        
        ctk.CTkLabel(
            title_frame,
            text="🚀",
            font=ctk.CTkFont(size=32)
        ).pack(side="left", padx=(0, 10))
        
        title_text = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_text.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            title_text,
            text="Update Available!",
            font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
            text_color=self.colors['text_primary']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_text,
            text="A new version of Magic Garden Bot is ready",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=self.colors['text_muted']
        ).pack(anchor="w")
        
        # === VERSION COMPARISON ===
        version_frame = ctk.CTkFrame(
            container, 
            fg_color=self.colors['card_bg'],
            corner_radius=10
        )
        version_frame.pack(fill="x", pady=(0, 15))
        
        version_inner = ctk.CTkFrame(version_frame, fg_color="transparent")
        version_inner.pack(fill="x", padx=20, pady=15)
        
        # Current version
        current_frame = ctk.CTkFrame(version_inner, fg_color="transparent")
        current_frame.pack(side="left", expand=True)
        
        ctk.CTkLabel(
            current_frame,
            text="Current",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=self.colors['text_muted']
        ).pack()
        
        ctk.CTkLabel(
            current_frame,
            text=f"v{self.update_info.get('current_version', '?')}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold"),
            text_color=self.colors['text_secondary']
        ).pack()
        
        # Arrow
        ctk.CTkLabel(
            version_inner,
            text="→",
            font=ctk.CTkFont(size=24),
            text_color=self.colors['blurple']
        ).pack(side="left", padx=20)
        
        # New version
        new_frame = ctk.CTkFrame(version_inner, fg_color="transparent")
        new_frame.pack(side="left", expand=True)
        
        ctk.CTkLabel(
            new_frame,
            text="New",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=self.colors['text_muted']
        ).pack()
        
        latest = self.update_info.get('latest_version', '?')
        if not latest.startswith('v'):
            latest = f"v{latest}"
        
        ctk.CTkLabel(
            new_frame,
            text=latest,
            font=ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold"),
            text_color=self.colors['green']
        ).pack()
        
        # === RELEASE NOTES ===
        notes_label = ctk.CTkLabel(
            container,
            text="What's New",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=self.colors['text_primary']
        )
        notes_label.pack(anchor="w", pady=(0, 5))
        
        notes_text = self.update_info.get('release_notes', 'No release notes available.')
        if len(notes_text) > 500:
            notes_text = notes_text[:500] + "..."
        
        self.notes_box = ctk.CTkTextbox(
            container,
            fg_color=self.colors['card_bg'],
            text_color=self.colors['text_secondary'],
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            corner_radius=8,
            height=100,
            wrap="word"
        )
        self.notes_box.pack(fill="x", pady=(0, 15))
        self.notes_box.insert("1.0", notes_text)
        self.notes_box.configure(state="disabled")
        
        # === PROGRESS BAR (hidden by default) ===
        self.progress_frame = ctk.CTkFrame(container, fg_color="transparent")
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Downloading update...",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=self.colors['text_secondary']
        )
        self.progress_label.pack(anchor="w")
        
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            fg_color=self.colors['card_bg'],
            progress_color=self.colors['blurple'],
            corner_radius=5,
            height=10
        )
        self.progress_bar.pack(fill="x", pady=(5, 0))
        self.progress_bar.set(0)
        
        self.progress_percent = ctk.CTkLabel(
            self.progress_frame,
            text="0%",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=self.colors['text_muted']
        )
        self.progress_percent.pack(anchor="e")
        
        # === BUTTONS ===
        self.buttons_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.buttons_frame.pack(fill="x", side="bottom")
        
        # Skip This Version (left)
        self.skip_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Skip This Version",
            command=self._on_skip,
            fg_color="transparent",
            hover_color=self.colors['card_bg'],
            text_color=self.colors['text_muted'],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            height=35,
            width=120
        )
        self.skip_btn.pack(side="left")
        
        # Update Now (right, primary)
        self.update_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Update Now",
            command=self._on_update,
            fg_color=self.colors['green'],
            hover_color="#238636",
            text_color="white",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            height=40,
            width=130
        )
        self.update_btn.pack(side="right")
        
        # Remind Me Later (right)
        self.later_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Later",
            command=self._on_later,
            fg_color=self.colors['card_bg'],
            hover_color=self.colors['sidebar_bg'],
            text_color=self.colors['text_secondary'],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            height=40,
            width=80
        )
        self.later_btn.pack(side="right", padx=(0, 10))
        
        # View on GitHub link
        link_frame = ctk.CTkFrame(container, fg_color="transparent")
        link_frame.pack(fill="x", pady=(10, 0))
        
        link_btn = ctk.CTkButton(
            link_frame,
            text="View on GitHub →",
            command=self._open_release_page,
            fg_color="transparent",
            hover_color="transparent",
            text_color=self.colors['blurple'],
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            height=20,
            cursor="hand2"
        )
        link_btn.pack(anchor="center")
    
    def _on_update(self):
        """Handle Update Now button click."""
        if self.on_update:
            self.show_download_progress()
            self.on_update()
    
    def _on_skip(self):
        """Handle Skip This Version button click."""
        version = self.update_info.get('latest_version', '')
        if self.on_skip and version:
            self.on_skip(version)
        self.destroy()
    
    def _on_later(self):
        """Handle Remind Me Later button click."""
        if self.on_dismiss:
            self.on_dismiss()
        self.destroy()
    
    def _on_close(self):
        """Handle window close."""
        if self.is_downloading:
            self.download_cancelled = True
        if self.on_dismiss:
            self.on_dismiss()
        self.destroy()
    
    def _open_release_page(self):
        """Open the GitHub release page in browser."""
        url = self.update_info.get('release_url', '')
        if url:
            webbrowser.open(url)
    
    def show_download_progress(self):
        """Switch to download progress view."""
        self.is_downloading = True
        
        # Hide notes box, show progress
        self.notes_box.pack_forget()
        self.progress_frame.pack(fill="x", pady=(0, 15))
        
        # Disable buttons except cancel
        self.skip_btn.configure(state="disabled")
        self.update_btn.configure(
            text="Downloading...",
            state="disabled",
            fg_color="gray"
        )
        self.later_btn.configure(text="Cancel", command=self._cancel_download)
    
    def _cancel_download(self):
        """Cancel the download."""
        self.download_cancelled = True
        self._on_close()
    
    def update_progress(self, downloaded: int, total: int):
        """
        Update the download progress bar.
        
        Args:
            downloaded: Bytes downloaded so far
            total: Total bytes to download
        """
        if total > 0:
            progress = downloaded / total
            self.progress_bar.set(progress)
            
            # Format sizes
            dl_mb = downloaded / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            
            self.progress_percent.configure(
                text=f"{dl_mb:.1f} MB / {total_mb:.1f} MB ({int(progress * 100)}%)"
            )
        else:
            # Unknown total size
            dl_mb = downloaded / (1024 * 1024)
            self.progress_percent.configure(text=f"{dl_mb:.1f} MB downloaded")
    
    def show_download_complete(self):
        """Show download complete state."""
        self.progress_label.configure(text="Download complete! Applying update...")
        self.progress_bar.set(1.0)
        self.later_btn.configure(state="disabled")
    
    def show_download_error(self, error: str):
        """Show download error state."""
        self.is_downloading = False
        self.progress_label.configure(
            text=f"Download failed: {error}",
            text_color=self.colors['red']
        )
        self.later_btn.configure(text="Close", command=self._on_close, state="normal")


class UpdateCheckingDialog(ctk.CTkToplevel):
    """Small dialog shown while checking for updates."""
    
    def __init__(self, parent, colors: Optional[Dict[str, str]] = None):
        super().__init__(parent)
        
        self.colors = colors or UI_COLORS
        self._destroyed = False
        
        self.title("Checking for Updates")
        self.geometry("300x120")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 300) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 120) // 2
        self.geometry(f"+{x}+{y}")
        
        self.configure(fg_color=self.colors['window_bg'])
        
        # Content
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            container,
            text="🔄 Checking for updates...",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14),
            text_color=self.colors['text_primary']
        ).pack(pady=(10, 15))
        
        self.progress = ctk.CTkProgressBar(
            container,
            fg_color=self.colors['card_bg'],
            progress_color=self.colors['blurple'],
            mode="indeterminate"
        )
        self.progress.pack(fill="x")
        self.progress.start()
    
    def safe_destroy(self):
        """Safely destroy the dialog, handling race conditions with CTk callbacks."""
        if self._destroyed:
            return
        self._destroyed = True
        try:
            self.progress.stop()
            # Use after to let pending callbacks complete
            self.after(50, self._do_destroy)
        except Exception:
            pass
    
    def _do_destroy(self):
        """Actually destroy the window."""
        try:
            if self.winfo_exists():
                self.destroy()
        except Exception:
            pass


class NoUpdateDialog(ctk.CTkToplevel):
    """Simple dialog shown when no updates are available."""
    
    def __init__(self, parent, current_version: str, colors: Optional[Dict[str, str]] = None):
        super().__init__(parent)
        
        self.colors = colors or UI_COLORS
        
        self.title("Up to Date")
        self.geometry("320x150")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 320) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 150) // 2
        self.geometry(f"+{x}+{y}")
        
        self.configure(fg_color=self.colors['window_bg'])
        
        # Content
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=20)
        
        ctk.CTkLabel(
            container,
            text="✅",
            font=ctk.CTkFont(size=28)
        ).pack(pady=(5, 10))
        
        ctk.CTkLabel(
            container,
            text="You're up to date!",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=self.colors['text_primary']
        ).pack()
        
        ctk.CTkLabel(
            container,
            text=f"Magic Garden Bot v{current_version}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=self.colors['text_muted']
        ).pack(pady=(2, 15))
        
        ctk.CTkButton(
            container,
            text="OK",
            command=self.destroy,
            fg_color=self.colors['blurple'],
            hover_color="#4752c4",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            height=32,
            width=80
        ).pack()
