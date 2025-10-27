# PowerShell script to safely run magic_gpu.py overnight with logging and resume support
# Usage: Right-click and 'Run with PowerShell' or run in a PowerShell terminal

# --- CONFIGURABLE PARAMETERS ---
$pythonExe = "python"
$script = "magic_gpu.py"
$batchMode = "--batch_mode"
$batchSize = "--batch_size 50"  # Lowered further for safety
$mode = "--mode tier1"

while ($true) {
    # --- SAFETY CHECKS ---
    $ram = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB
    if ($ram -lt 8) {
        Write-Host "[ERROR] Less than 8GB free RAM ($([math]::Round($ram,2)) GB). Aborting for safety." -ForegroundColor Red
        break
    }
    $drive = (Get-Item .).PSDrive
    $freeGB = $drive.Free/1GB
    if ($freeGB -lt 10) {
        Write-Host "[ERROR] Less than 10GB free disk space ($([math]::Round($freeGB,2)) GB). Aborting for safety." -ForegroundColor Red
        break
    }
    if ($ram -lt 16) {
        Write-Host "[WARNING] Free RAM is below 16GB ($([math]::Round($ram,2)) GB). Consider closing other programs." -ForegroundColor Yellow
    }
    if ($freeGB -lt 20) {
        Write-Host "[WARNING] Free disk space is below 20GB ($([math]::Round($freeGB,2)) GB). Monitor output size." -ForegroundColor Yellow
    }
    # --- TIMESTAMPED FILENAMES FOR THIS BATCH ---
    $ts = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
    $logFile = "overnight_run_$ts.log"
    $defaultOutput = "near_magic_candidates_base36.txt"
    $timestampedOutput = "overnight_candidates_$ts.txt"
    # --- RUN THE GENERATOR WITH LOGGING ---
    Write-Host "[INFO] Starting candidate batch at $(Get-Date)"
    $cmd = "$pythonExe $script $batchMode $batchSize $mode 2>&1 | Tee-Object -FilePath $logFile"
    Write-Host "[INFO] Command: $cmd"
    Invoke-Expression $cmd
    Write-Host "[INFO] Finished batch at $(Get-Date)"
    # --- RENAME OUTPUT FILE FOR UNIQUENESS ---
    if (Test-Path $defaultOutput) {
        Rename-Item -Path $defaultOutput -NewName $timestampedOutput -Force
        Write-Host "[INFO] Renamed $defaultOutput to $timestampedOutput"
    } else {
        Write-Host "[WARNING] Default output file $defaultOutput not found. No file renamed."
    }
    Start-Sleep -Seconds 2  # Short pause between batches
}
Write-Host "[INFO] Loop ended. To resume, simply re-run this script."
