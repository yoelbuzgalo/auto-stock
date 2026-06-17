# ==============================================================================
# Script Name: install.ps1
# Description: High-throughput localized deployment of Ollama (DeepSeek-R1)
#              and isolated Hugging Face FinBERT environments.
# Author:      DE4Fxx
# Context:     Dual-Privilege (Self-Elevating Core, User-Space Execution)
# ==============================================================================

Clear-Host
Write-Host ":: Spam return or enter" -ForegroundColor Yellow

# Capture current workspace matrix for restitution
$OriginalDir = Get-Location

# --- Global Configurations (Picks up from Env, falls back to defaults) --------
$Config = @{
    TargetDir   = if ($env:AI_TARGET_DIR)  { $env:AI_TARGET_DIR }  else { "$home\ai_models" }
    EnvName     = if ($env:AI_ENV_NAME)    { $env:AI_ENV_NAME }    else { "finbert_env" }
    OllamaHost  = if ($env:OLLAMA_HOST)    { $env:OLLAMA_HOST }    else { "0.0.0.0:11434" }
    ModelLocal  = if ($env:AI_MODEL_NAME)  { $env:AI_MODEL_NAME }  else { "deepseek-r1:8b" }
    PyTorchWhl  = if ($env:AI_PYTORCH_WHL) { $env:AI_PYTORCH_WHL } else { "https://download.pytorch.org/whl/cu121" }
}

# --- Initialization & Elevation ----------------------------------------------
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    $AdminPayload = {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        if (-not (Test-Path "$env:ProgramData\Chocolatey")) {
            [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
            Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        }
        choco install ollama -y --no-progress
        [Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0:11434", "Machine")
        Remove-NetFirewallRule -DisplayName "Ollama Inbound LAN" -ErrorAction SilentlyContinue
        New-NetFirewallRule -DisplayName "Ollama Inbound LAN" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 11434 -Profile Private
    }
    
    $EncodedPayload = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($AdminPayload.ToString()))
    Start-Process powershell -ArgumentList "-NoProfile", "-EncodedCommand", $EncodedPayload -Verb RunAs -Wait -WindowStyle Hidden
}

# --- High-Throughput Execution Core -------------------------------------------
Set-ExecutionPolicy Bypass -Scope Process -Force

Write-Host ":: Starting AI Infrastructure Deployment..." -ForegroundColor Cyan

# Environment path refresh
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
$env:OLLAMA_HOST = $Config.OllamaHost

# Core Daemon Spin-up
$OllamaExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
if (-not (Test-Path $OllamaExe)) { $OllamaExe = "C:\Program Files\Ollama\ollama.exe" }
Start-Process -FilePath $OllamaExe -ArgumentList "serve" -WindowStyle Hidden

# Health-checking loop
$ServerOnline = $false
for ($i = 0; $i -lt 15; $i++) {
    try {
        $Response = Invoke-WebRequest -Uri "http://127.0.0.1:11434" -Method Get -ErrorAction Stop
        if ($Response.StatusCode -eq 200) { $ServerOnline = $true; break }
    } catch {
        Start-Sleep -Seconds 1
    }
}
if (-not $ServerOnline) { throw "Fatal: Local Ollama daemon failed to bind within timeout limits." }

# Pipeline Stream 1: Ollama Model Weights with bypass execution
"" | ollama pull $Config.ModelLocal

# Directory workspace structuring
if (-not (Test-Path $Config.TargetDir)) { New-Item -ItemType Directory -Path $Config.TargetDir | Out-Null }
Set-Location -Path $Config.TargetDir

# Python Runtime Binding
$PythonRuntime = "python.exe"
if (-not (Get-Command $PythonRuntime -ErrorAction SilentlyContinue)) {
    if (Test-Path "C:\Python311\python.exe") { $PythonRuntime = "C:\Python311\python.exe" }
    elseif (Test-Path "C:\Python312\python.exe") { $PythonRuntime = "C:\Python312\python.exe" }
    else { throw "Fatal: System Python runtime could not be resolved from environment pathing." }
}

# Virtual Environment Assembly
if (-not (Test-Path ".\$($Config.EnvName)")) {
    Write-Host ":: Allocating local Python virtual environment workspace..." -ForegroundColor Gray
    & $PythonRuntime -m venv $Config.EnvName
}
& ".\$($Config.EnvName)\Scripts\python.exe" -m pip install --upgrade pip --quiet

# Pipeline Stream 2: PyTorch GPU dependencies
Write-Host ":: Resolving framework matrices (PyTorch CUDA + Transformers)..." -ForegroundColor Yellow
& ".\$($Config.EnvName)\Scripts\pip.exe" install torch transformers --index-url $Config.PyTorchWhl --no-cache-dir --quiet

# Pipeline Stream 3: FinBERT local cache validation
Write-Host ":: Validating cache layers for FinBERT..." -ForegroundColor Yellow
$PyCacheScript = "from transformers import AutoModelForSequenceClassification, AutoTokenizer; name = 'ProsusAI/finbert'; AutoTokenizer.from_pretrained(name); AutoModelForSequenceClassification.from_pretrained(name)"
& ".\$($Config.EnvName)\Scripts\python.exe" -c "$PyCacheScript"

# Restitute structural execution context pathing
Set-Location -Path $OriginalDir

Write-Host "`n>> Infrastructure deployment complete. Systems online." -ForegroundColor Green
Start-Sleep -Seconds 3