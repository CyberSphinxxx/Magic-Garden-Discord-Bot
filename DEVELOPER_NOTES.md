# Developer Notes

## Release Workflow

When ready to create a new release:

### 1. Update Version Numbers

Update the version in **two files**:

| File | What to change |
|------|----------------|
| `src/version.txt` | Update `filevers`, `prodvers`, `FileVersion`, `ProductVersion` |
| `src/core/updater.py` | Update `CURRENT_VERSION` constant (line 24) |

### 2. Commit and Push

```bash
git add src/version.txt src/core/updater.py
git commit -m "chore: bump version to vX.X.X"
git push
```

### 3. Create GitHub Release

1. Go to GitHub > Releases > Create new release
2. Create tag `vX.X.X` (must match version in code)
3. Add release notes
4. Publish - GitHub Actions will auto-build the exe

---

## Auto-Update System

The app checks for updates from GitHub Releases API.

- **Startup check**: Silent check 2 seconds after launch
- **Manual check**: Click version button in footer
- **Config file**: `~/magic_garden_bot_config.json`
  - `AUTO_UPDATE_CHECK`: Enable/disable startup check
  - `UPDATE_SKIPPED_VERSION`: Version user chose to skip

---

## PyInstaller Build

```bash
pyinstaller MagicGardenBot.spec
```

The `.spec` file bundles `src/images` as `images` in the exe. The `resource_path()` function in `config.py` handles path resolution for both script and exe modes.
