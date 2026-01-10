"""
Magic Garden Bot - Auto-Update Module.

Handles checking for updates from GitHub Releases and downloading new versions.
"""

import os
import sys
import subprocess
import tempfile
import threading
from typing import Optional, Callable, Dict, Any

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# =============================================================================
# CONSTANTS
# =============================================================================

CURRENT_VERSION = "3.1.2"
GITHUB_REPO = "CyberSphinxxx/Magic-Garden-Automation-Bot"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_RELEASES_URL = f"https://github.com/{GITHUB_REPO}/releases/latest"

# =============================================================================
# VERSION UTILITIES
# =============================================================================

def parse_version(version_str: str) -> tuple:
    """
    Parse a version string like 'v3.1.2' or '3.1.2' into a tuple of integers.
    Returns (0, 0, 0) if parsing fails.
    """
    try:
        # Remove 'v' prefix if present
        clean = version_str.strip().lstrip('v')
        parts = clean.split('.')
        return tuple(int(p) for p in parts[:3])
    except (ValueError, AttributeError):
        return (0, 0, 0)


def compare_versions(current: str, latest: str) -> int:
    """
    Compare two version strings.
    Returns:
        1 if latest > current (update available)
        0 if latest == current (up to date)
        -1 if latest < current (running newer version)
    """
    current_tuple = parse_version(current)
    latest_tuple = parse_version(latest)
    
    if latest_tuple > current_tuple:
        return 1
    elif latest_tuple == current_tuple:
        return 0
    else:
        return -1


# =============================================================================
# UPDATE CHECK
# =============================================================================

def check_for_updates() -> Dict[str, Any]:
    """
    Check GitHub Releases API for the latest version.
    
    Returns a dictionary with:
        - 'available': bool - True if update available
        - 'current_version': str - Current app version
        - 'latest_version': str - Latest release version (or None)
        - 'download_url': str - URL to download the exe (or None)
        - 'release_notes': str - Release body/notes (or None)
        - 'release_url': str - URL to the release page
        - 'error': str - Error message if check failed (or None)
    """
    result = {
        'available': False,
        'current_version': CURRENT_VERSION,
        'latest_version': None,
        'download_url': None,
        'release_notes': None,
        'release_url': GITHUB_RELEASES_URL,
        'error': None
    }
    
    if not REQUESTS_AVAILABLE:
        result['error'] = "requests library not available"
        return result
    
    try:
        response = requests.get(
            GITHUB_API_URL,
            timeout=10,
            headers={'Accept': 'application/vnd.github.v3+json'}
        )
        response.raise_for_status()
        
        data = response.json()
        
        latest_version = data.get('tag_name', '')
        result['latest_version'] = latest_version
        result['release_notes'] = data.get('body', '')
        result['release_url'] = data.get('html_url', GITHUB_RELEASES_URL)
        
        # Find the .exe asset
        assets = data.get('assets', [])
        for asset in assets:
            if asset.get('name', '').endswith('.exe'):
                result['download_url'] = asset.get('browser_download_url')
                break
        
        # Check if update is available
        if compare_versions(CURRENT_VERSION, latest_version) > 0:
            result['available'] = True
        
    except requests.exceptions.Timeout:
        result['error'] = "Connection timed out"
    except requests.exceptions.ConnectionError:
        result['error'] = "No internet connection"
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            result['error'] = "No releases found"
        elif e.response.status_code == 403:
            result['error'] = "API rate limit exceeded"
        else:
            result['error'] = f"HTTP error: {e.response.status_code}"
    except Exception as e:
        result['error'] = f"Check failed: {str(e)}"
    
    return result


def check_for_updates_async(callback: Callable[[Dict[str, Any]], None]) -> threading.Thread:
    """
    Check for updates in a background thread.
    Calls the callback with the result when done.
    
    Args:
        callback: Function to call with the update check result
        
    Returns:
        The started thread (for optional joining)
    """
    def _check():
        result = check_for_updates()
        callback(result)
    
    thread = threading.Thread(target=_check, daemon=True)
    thread.start()
    return thread


# =============================================================================
# DOWNLOAD UPDATE
# =============================================================================

def download_update(
    url: str,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> Optional[str]:
    """
    Download the update file to a temporary location.
    
    Args:
        url: Download URL for the new exe
        progress_callback: Optional callback(downloaded_bytes, total_bytes)
        
    Returns:
        Path to the downloaded file, or None on failure
    """
    if not REQUESTS_AVAILABLE:
        return None
    
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        # Get total file size
        total_size = int(response.headers.get('content-length', 0))
        
        # Create temp file with .exe extension
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, 'MagicGardenBot_update.exe')
        
        downloaded = 0
        chunk_size = 8192
        
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total_size)
        
        return temp_path
        
    except Exception as e:
        print(f"Download failed: {e}")
        return None


def download_update_async(
    url: str,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    completion_callback: Optional[Callable[[Optional[str]], None]] = None
) -> threading.Thread:
    """
    Download update in a background thread.
    
    Args:
        url: Download URL
        progress_callback: Called with (downloaded, total) during download
        completion_callback: Called with the file path (or None) when done
        
    Returns:
        The started thread
    """
    def _download():
        result = download_update(url, progress_callback)
        if completion_callback:
            completion_callback(result)
    
    thread = threading.Thread(target=_download, daemon=True)
    thread.start()
    return thread


# =============================================================================
# APPLY UPDATE
# =============================================================================

def get_current_exe_path() -> str:
    """Get the path to the currently running executable."""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return sys.executable
    else:
        # Running as script - return script path for testing
        return os.path.abspath(sys.argv[0])


def create_update_script(new_exe_path: str, current_exe_path: str) -> str:
    """
    Create a batch script that will replace the current exe with the new one.
    
    The script:
    1. Waits for the current app to close
    2. Copies the new exe over the old one
    3. Deletes the temp file
    4. Restarts the application
    
    Returns the path to the created script.
    """
    script_content = f'''@echo off
echo Updating Magic Garden Bot...
echo.
echo Waiting for application to close...

:waitloop
tasklist /FI "IMAGENAME eq {os.path.basename(current_exe_path)}" 2>NUL | find /I /N "{os.path.basename(current_exe_path)}">NUL
if "%ERRORLEVEL%"=="0" (
    timeout /t 1 /nobreak >NUL
    goto waitloop
)

echo Application closed. Applying update...
timeout /t 1 /nobreak >NUL

copy /Y "{new_exe_path}" "{current_exe_path}"
if errorlevel 1 (
    echo Update failed! Could not copy new file.
    pause
    exit /b 1
)

echo Update complete! Restarting...
del "{new_exe_path}" 2>NUL
start "" "{current_exe_path}"

del "%~f0"
'''
    
    script_path = os.path.join(tempfile.gettempdir(), 'magic_garden_update.bat')
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    return script_path


def apply_update(new_exe_path: str) -> bool:
    """
    Apply the downloaded update.
    
    This creates and launches the update script, then signals the app to close.
    
    Args:
        new_exe_path: Path to the downloaded new exe
        
    Returns:
        True if the update script was launched successfully
    """
    try:
        current_exe = get_current_exe_path()
        
        # Don't try to replace if running as script (development mode)
        if not getattr(sys, 'frozen', False):
            print("Running in development mode - update not applied")
            return False
        
        # Create the update script
        script_path = create_update_script(new_exe_path, current_exe)
        
        # Launch the update script (it will wait for us to close)
        subprocess.Popen(
            ['cmd', '/c', script_path],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            close_fds=True
        )
        
        return True
        
    except Exception as e:
        print(f"Failed to apply update: {e}")
        return False
