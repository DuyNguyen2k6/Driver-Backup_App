Add-Type -AssemblyName System.Windows.Forms

function Show-Menu {
    Clear-Host
    Write-Host "============ DRIVER BACKUP TOOL ============" -ForegroundColor Cyan
    Write-Host "1. Backup drivers"
    Write-Host "2. Restore drivers"
    Write-Host "3. Check missing/faulty drivers"
    Write-Host "4. Exit"
}

function Pick-Folder {
    $fbd = New-Object System.Windows.Forms.FolderBrowserDialog
    $fbd.Description = "Select folder"
    $fbd.ShowNewFolderButton = $true
    if ($fbd.ShowDialog() -eq "OK") {
        return $fbd.SelectedPath
    } else {
        return $null
    }
}

function Backup-Drivers {
    $folder = Pick-Folder
    if (!$folder) { Write-Host "No folder selected!"; Pause; return }
    Write-Host "Backing up drivers to $folder ..." -ForegroundColor Yellow
    Start-Process -Verb RunAs -FilePath "dism.exe" -ArgumentList "/online /export-driver /destination:`"$folder`"" -Wait
    Write-Host "Backup completed." -ForegroundColor Green
    Pause
}

function Restore-Drivers {
    $folder = Pick-Folder
    if (!$folder) { Write-Host "No folder selected!"; Pause; return }
    Write-Host "Restoring drivers from $folder ..." -ForegroundColor Yellow
    Start-Process -Verb RunAs -FilePath "pnputil.exe" -ArgumentList "/add-driver `"$folder\*.inf`" /subdirs /install" -Wait
    Write-Host "Restore completed." -ForegroundColor Green
    Pause
}

function Check-Drivers {
    Write-Host "Checking for missing/faulty drivers..." -ForegroundColor Yellow
    $drivers = Get-WmiObject Win32_PnPEntity | Where-Object { $_.ConfigManagerErrorCode -ne 0 }
    if ($drivers) {
        Write-Host "List of missing/faulty drivers:" -ForegroundColor Red
        $drivers | ForEach-Object { Write-Host $_.Name }
    } else {
        Write-Host "No missing/faulty drivers detected." -ForegroundColor Green
    }
    Pause
}

do {
    Show-Menu
    $choice = Read-Host "Choose option [1-4]"
    switch ($choice) {
        "1" { Backup-Drivers }
        "2" { Restore-Drivers }
        "3" { Check-Drivers }
        "4" { Write-Host "Goodbye!"; break }
        default { Write-Host "Invalid option. Try again." -ForegroundColor Red; Pause }
    }
} while ($choice -ne "4")
