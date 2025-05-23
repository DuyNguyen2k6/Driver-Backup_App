Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Auto-elevate to Administrator
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    $script = $MyInvocation.MyCommand.Path
    Start-Process powershell -Verb runAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$script`""
    exit
}

# GUI SETUP
$formWidth = 600
$form = New-Object System.Windows.Forms.Form
$form.Text = "Driver Backup & Restore"
$form.Size = New-Object System.Drawing.Size($formWidth, 330)
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false
$form.StartPosition = "CenterScreen"
$form.BackColor = [System.Drawing.Color]::FromArgb(245,245,250)

# Title
$title = New-Object System.Windows.Forms.Label
$title.Text = "Driver Backup & Restore"
$title.Font = New-Object System.Drawing.Font("Segoe UI Semibold", 15, [System.Drawing.FontStyle]::Bold)
$title.ForeColor = [System.Drawing.Color]::FromArgb(60,60,70)
$title.AutoSize = $true
$title.Location = New-Object System.Drawing.Point([int](($formWidth - 270)/2),16)
$form.Controls.Add($title)

$font = New-Object System.Drawing.Font("Segoe UI", 10)

# Folder label
$label = New-Object System.Windows.Forms.Label
$label.Text = "Folder:"
$label.Location = New-Object System.Drawing.Point(38,63)
$label.Size = New-Object System.Drawing.Size(60,25)
$label.Font = $font
$label.ForeColor = [System.Drawing.Color]::FromArgb(80,90,120)
$form.Controls.Add($label)

$textBox = New-Object System.Windows.Forms.TextBox
$textBox.Location = New-Object System.Drawing.Point(100, 61)
$textBox.Size = New-Object System.Drawing.Size(320, 25)
$textBox.Font = $font
$textBox.BorderStyle = 'FixedSingle'
$form.Controls.Add($textBox)

$btnFolder = New-Object System.Windows.Forms.Button
$btnFolder.Text = "Browse..."
$btnFolder.Size = New-Object System.Drawing.Size(90, 28)
$btnFolder.Location = New-Object System.Drawing.Point(430, 59)
$btnFolder.Font = $font
$btnFolder.FlatStyle = 'Flat'
$btnFolder.BackColor = [System.Drawing.Color]::White
$btnFolder.ForeColor = [System.Drawing.Color]::FromArgb(31, 140, 202)
$btnFolder.FlatAppearance.BorderColor = [System.Drawing.Color]::FromArgb(31, 140, 202)
$btnFolder.FlatAppearance.BorderSize = 2
$btnFolder.Add_MouseEnter({ $this.BackColor = [System.Drawing.Color]::FromArgb(220,240,255) })
$btnFolder.Add_MouseLeave({ $this.BackColor = [System.Drawing.Color]::White })
$btnFolder.Add_Click({
    $fbd = New-Object System.Windows.Forms.FolderBrowserDialog
    if ($fbd.ShowDialog() -eq "OK") {
        $textBox.Text = $fbd.SelectedPath
    }
})
$form.Controls.Add($btnFolder)

# Button styling function
function Set-ButtonStyle($btn, $color) {
    $btn.FlatStyle = 'Flat'
    $btn.BackColor = [System.Drawing.Color]::White
    $btn.ForeColor = $color
    $btn.FlatAppearance.BorderColor = $color
    $btn.FlatAppearance.BorderSize = 2
    $btn.Font = $font
    $btn.Add_MouseEnter({ $this.BackColor = [System.Drawing.Color]::FromArgb(238, 248, 255) })
    $btn.Add_MouseLeave({ $this.BackColor = [System.Drawing.Color]::White })
}

# Nút: Kích thước và vị trí tính tự động theo form (đều, giữa)
$btnWidth = 120
$btnHeight = 36
$numBtn = 3
$btnSpacing = 40
$totalBtnWidth = $btnWidth * $numBtn + $btnSpacing * ($numBtn-1)
$btnY = 115
$startX = [int](($formWidth - $totalBtnWidth)/2)

# Backup
$btnBackup = New-Object System.Windows.Forms.Button
$btnBackup.Text = "Backup"
$btnBackup.Size = New-Object System.Drawing.Size($btnWidth, $btnHeight)
$btnBackup.Location = New-Object System.Drawing.Point($startX, $btnY)
Set-ButtonStyle $btnBackup ([System.Drawing.Color]::FromArgb(56,166,62))
$btnBackup.Add_Click({
    $folder = $textBox.Text
    if ($folder -eq "") { [System.Windows.Forms.MessageBox]::Show("Please select a backup folder first!") }
    else {
        $logBox.AppendText("Backing up drivers to $folder`r`n")
        Start-Process -NoNewWindow -FilePath dism -ArgumentList "/online /export-driver /destination:`"$folder`"" -Wait
        $logBox.AppendText("Driver backup completed.`r`n")
    }
})
$form.Controls.Add($btnBackup)

# Restore
$btnRestore = New-Object System.Windows.Forms.Button
$btnRestore.Text = "Restore"
$btnRestore.Size = New-Object System.Drawing.Size($btnWidth, $btnHeight)
$btnRestore.Location = New-Object System.Drawing.Point([int]($startX + $btnWidth + $btnSpacing), $btnY)
Set-ButtonStyle $btnRestore ([System.Drawing.Color]::FromArgb(31, 140, 202))
$btnRestore.Add_Click({
    $folder = $textBox.Text
    if ($folder -eq "") { [System.Windows.Forms.MessageBox]::Show("Please select your driver folder!") }
    else {
        $logBox.AppendText("Restoring drivers from $folder`r`n")
        Start-Process -NoNewWindow -FilePath pnputil -ArgumentList "/add-driver `"$folder\*.inf`" /subdirs /install" -Wait
        $logBox.AppendText("Driver restore completed.`r`n")
    }
})
$form.Controls.Add($btnRestore)

# Check
$btnCheck = New-Object System.Windows.Forms.Button
$btnCheck.Text = "Check Missing"
$btnCheck.Size = New-Object System.Drawing.Size($btnWidth, $btnHeight)
$btnCheck.Location = New-Object System.Drawing.Point([int]($startX + 2*($btnWidth + $btnSpacing)), $btnY)
Set-ButtonStyle $btnCheck ([System.Drawing.Color]::FromArgb(238, 169, 12))
$btnCheck.Add_Click({
    $logBox.AppendText("Checking for missing or faulty drivers:`r`n")
    $drivers = Get-WmiObject Win32_PnPEntity | Where-Object { $_.ConfigManagerErrorCode -ne 0 }
    foreach ($d in $drivers) {
        $logBox.AppendText("$($d.Name)`r`n")
    }
    if ($drivers.Count -eq 0) {
        $logBox.AppendText("No missing or faulty drivers detected.`r`n")
    }
})
$form.Controls.Add($btnCheck)

# Log Box nhỏ, luôn căn giữa, sát đáy
$logBoxWidth = 500
$logBoxHeight = 85
$logBoxX = [int](($formWidth - $logBoxWidth)/2)
$logBoxY = 175

$logBox = New-Object System.Windows.Forms.TextBox
$logBox.Location = New-Object System.Drawing.Point($logBoxX, $logBoxY)
$logBox.Size = New-Object System.Drawing.Size($logBoxWidth, $logBoxHeight)
$logBox.Multiline = $true
$logBox.ScrollBars = "Vertical"
$logBox.ReadOnly = $true
$logBox.Font = $font
$logBox.BackColor = [System.Drawing.Color]::White
$logBox.BorderStyle = 'FixedSingle'
$form.Controls.Add($logBox)

[void]$form.ShowDialog()
