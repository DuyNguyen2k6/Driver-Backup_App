import customtkinter as ctk
import ctypes
import subprocess
import sys
import threading
from tkinter import filedialog, messagebox, END

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join([f'"{arg}"' for arg in sys.argv]), None, 1)
    sys.exit()

selected_folder = ""

def add_log(msg):
    log_box.configure(state="normal")
    log_box.insert(END, msg + "\n")
    log_box.see(END)
    log_box.configure(state="disabled")

def choose_folder():
    global selected_folder
    folder = filedialog.askdirectory(title="Chọn thư mục Driver Backup/Restore")
    if folder:
        selected_folder = folder
        folder_var.set(selected_folder)
        add_log(f"[INFO] Đã chọn thư mục: {folder}")

def run_command(cmd, desc=""):
    add_log(f"[RUN] {cmd}")
    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                add_log(line.strip())
        ret = process.wait()
        if ret == 0:
            add_log(f"[SUCCESS] {desc} thành công.")
        else:
            add_log(f"[FAIL] {desc} thất bại.")
        return ret
    except Exception as e:
        add_log(f"[ERROR] {str(e)}")
        return -1

def backup_driver():
    if not selected_folder:
        messagebox.showwarning("Chưa chọn thư mục", "Vui lòng chọn thư mục lưu driver trước!")
        return

    def backup_thread():
        cmd = f'dism /online /export-driver /destination:"{selected_folder}"'
        add_log("[TASK] Bắt đầu backup driver…")
        ret = run_command(cmd, "Backup driver")
        if ret == 0:
            messagebox.showinfo("Thành công", f"Backup driver thành công!\nLưu tại: {selected_folder}")
        else:
            messagebox.showerror("Lỗi", "Backup driver thất bại. Hãy kiểm tra quyền Admin hoặc đường dẫn.")
    threading.Thread(target=backup_thread).start()

def restore_driver():
    if not selected_folder:
        messagebox.showwarning("Chưa chọn thư mục", "Vui lòng chọn thư mục chứa driver backup!")
        return

    confirm = messagebox.askyesno("Khôi phục driver", "Khôi phục driver sẽ cài lại các driver đã backup vào máy tính. Tiếp tục?")
    if not confirm:
        return

    def restore_thread():
        cmd = f'pnputil /add-driver "{selected_folder}\\*.inf" /subdirs /install'
        add_log("[TASK] Bắt đầu khôi phục (restore) driver…")
        ret = run_command(cmd, "Khôi phục driver")
        if ret == 0:
            messagebox.showinfo("Thành công", "Cài đặt driver thành công!")
        else:
            messagebox.showerror("Lỗi", "Cài đặt driver thất bại. Có thể một số driver đã cài, hoặc xảy ra lỗi.")
    threading.Thread(target=restore_thread).start()

def check_missing_drivers():
    add_log("[TASK] Đang kiểm tra thiết bị thiếu driver...")
    cmd = 'powershell "Get-WmiObject Win32_PnPEntity | Where-Object { $_.ConfigManagerErrorCode -ne 0 } | Select-Object Name, DeviceID, ConfigManagerErrorCode"'
    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        found = False
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line and line.strip():
                add_log(line.strip())
                found = True
        if not found:
            add_log("[INFO] Không phát hiện thiết bị nào thiếu driver hoặc lỗi driver.")
    except Exception as e:
        add_log(f"[ERROR] {str(e)}")

# Tùy chỉnh màu viền cho từng nút (dùng fg_color là trắng, border_color riêng)
def ctk_white_button(master, text, command, border_color, hover_color, text_color, width, height):
    return ctk.CTkButton(
        master, text=text, command=command,
        width=width, height=height,
        font=("Segoe UI", 15, "bold"),
        fg_color="#ffffff",  # nền trắng
        border_width=2, border_color=border_color,
        text_color=text_color,
        hover_color=hover_color,
        corner_radius=24
    )

# UI setup
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Driver Backup & Restore - Win11 Style")
root.geometry("760x550")
root.resizable(False, False)

title_label = ctk.CTkLabel(root, text="Driver Backup & Restore", font=("Segoe UI", 26, "bold"))
title_label.pack(pady=(16, 4))

# Folder Entry + Button (in a frame)
folder_var = ctk.StringVar(value="Chưa chọn thư mục")

folder_frame = ctk.CTkFrame(root, fg_color="transparent")
folder_frame.pack(pady=(10, 8))

entry_folder = ctk.CTkEntry(
    folder_frame, textvariable=folder_var, width=500, height=38,
    font=("Segoe UI", 15), state="readonly", corner_radius=16
)
entry_folder.pack(side="left", padx=(0, 6))

# Nút chọn thư mục: trắng, viền xanh ngọc, hover xanh nhạt
choose_btn = ctk_white_button(
    folder_frame, text="Chọn thư mục", command=choose_folder,
    border_color="#00b2d9", hover_color="#e6f8fd", text_color="#049dc7",
    width=130, height=38
)
choose_btn.pack(side="left")

# Button row: Backup - Restore - Check
button_frame = ctk.CTkFrame(root, fg_color="transparent")
button_frame.pack(pady=16)

btn_width = 210
btn_height = 50
btn_spacing = 22

backup_btn = ctk_white_button(
    button_frame, text="Backup Driver", command=backup_driver,
    border_color="#27b353", hover_color="#e7f9ed", text_color="#219150",
    width=btn_width, height=btn_height
)
backup_btn.grid(row=0, column=0, padx=(0, btn_spacing))

restore_btn = ctk_white_button(
    button_frame, text="Khôi phục Driver", command=restore_driver,
    border_color="#2563eb", hover_color="#e6eaff", text_color="#2563eb",
    width=btn_width, height=btn_height
)
restore_btn.grid(row=0, column=1, padx=(0, btn_spacing))

check_driver_btn = ctk_white_button(
    button_frame, text="Kiểm tra driver thiếu", command=lambda: threading.Thread(target=check_missing_drivers).start(),
    border_color="#fdba08", hover_color="#fff9e6", text_color="#c98e13",
    width=btn_width, height=btn_height
)
check_driver_btn.grid(row=0, column=2, padx=(0, 0))

# Log box
log_box = ctk.CTkTextbox(root, width=720, height=265, font=("Consolas", 12), corner_radius=14, wrap="word", state="disabled")
log_box.pack(pady=(18, 8))

credit = ctk.CTkLabel(
    root, text="© 2024 Duy Nguyen - Backup & Restore Driver | Kiểm tra driver thiếu",
    font=("Segoe UI", 10, "italic"), text_color="#888"
)
credit.pack(pady=(2, 0))

root.mainloop()
