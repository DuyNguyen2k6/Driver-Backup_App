# Driver Backup & Restore

A modern, user-friendly utility for Windows that lets you **back up and restore all system drivers** with a single click.  
Ideal for reinstalling Windows, migrating systems, or simply keeping your drivers safe.  
Features a Windows 11-inspired interface, real-time log display, and simple step-by-step actions.

---

## Features

- **One-click backup** of all Windows drivers to a selected folder.
- **One-click restore**: Reinstall all drivers from your backup folder.
- **Modern Win 11 style UI** using CustomTkinter.
- **Real-time log window**: See progress, command output, and errors live.
- **Admin rights check**: Automatically requests admin privileges.
- **Safe & reliable**: Uses official Windows tools (DISM and pnputil).
- **Easy to use**: No command line knowledge required.

---



## How to use

1. **Install requirements:**

    ```bash
    pip install customtkinter
    # If you want to show PNG logo: pip install pillow
    ```

2. **Run the app:**

    ```bash
    python Driver Backup.py
    ```

3. **Backup your drivers:**
    - Click **“Chọn thư mục”** to choose a backup location.
    - Click **“Backup Driver”**.  
      The log panel will show progress and results.

4. **Restore drivers:**
    - Choose the folder with your backup.
    - Click **“Khôi phục Driver”**.  
      The app will automatically reinstall missing/outdated drivers.

---

## Requirements

- Windows 10/11
- Python 3.8+
- `customtkinter`
- (Optional for logo) `pillow`

---
