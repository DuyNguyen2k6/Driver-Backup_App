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

# UI Win 11 style
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Driver Backup & Restore - Win11 Style + Log")
root.geometry("650x480")
root.resizable(False, False)

title_label = ctk.CTkLabel(root, text="Driver Backup & Restore", font=("Segoe UI", 26, "bold"))
title_label.pack(pady=(18, 8))

folder_var = ctk.StringVar(value="Chưa chọn thư mục")

entry_folder = ctk.CTkEntry(
    root, textvariable=folder_var, width=450, height=38, font=("Segoe UI", 15), state="readonly", corner_radius=18
)
entry_folder.pack(pady=8)

button_frame = ctk.CTkFrame(root, fg_color="transparent")
button_frame.pack(pady=18)

btn_width = 185
btn_height = 46

choose_btn = ctk.CTkButton(
    button_frame, text="Chọn thư mục", command=choose_folder,
    width=btn_width, height=btn_height,
    font=("Segoe UI", 15, "bold"),
    corner_radius=24,
    hover_color="#0078D4"
)
choose_btn.grid(row=0, column=0, padx=12)

backup_btn = ctk.CTkButton(
    button_frame, text="Backup Driver", command=backup_driver,
    width=btn_width, height=btn_height,
    font=("Segoe UI", 15, "bold"),
    fg_color="#28a745", hover_color="#218838",
    corner_radius=24
)
backup_btn.grid(row=0, column=1, padx=12)

restore_btn = ctk.CTkButton(
    button_frame, text="Khôi phục Driver", command=restore_driver,
    width=btn_width, height=btn_height,
    font=("Segoe UI", 15, "bold"),
    fg_color="#2563eb", hover_color="#174ea6",
    corner_radius=24
)
restore_btn.grid(row=0, column=2, padx=12)

# Log Box
log_box = ctk.CTkTextbox(root, width=600, height=220, font=("Consolas", 12), corner_radius=14, wrap="word", state="disabled")
log_box.pack(pady=(18, 8))

credit = ctk.CTkLabel(
    root, text="© 2024 Nhat - Hiển thị log trực tiếp như Console",
    font=("Segoe UI", 10, "italic"), text_color="#888"
)
credit.pack(pady=(2, 0))

root.mainloop()
