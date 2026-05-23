param(
    [string]$Python = "3.11",
    [string]$ModelBaseUrl = "https://hf-mirror.com"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

function Download-IfMissing {
    param(
        [string]$Url,
        [string]$OutFile
    )

    if (Test-Path $OutFile) {
        Write-Host "Already exists: $OutFile"
        return
    }

    New-Item -ItemType Directory -Force (Split-Path -Parent $OutFile) | Out-Null
    Write-Host "Downloading $Url"
    curl.exe --ssl-no-revoke -L $Url -o $OutFile
}

if (-not (Test-Path ".\.venv-f5\Scripts\python.exe")) {
    uv venv .venv-f5 --python $Python
    .\.venv-f5\Scripts\python.exe -m ensurepip --upgrade
}

.\.venv-f5\Scripts\python.exe -m pip install --upgrade pip
.\.venv-f5\Scripts\python.exe -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
uv pip install --python .\.venv-f5\Scripts\python.exe -r requirements.txt

Download-IfMissing "$ModelBaseUrl/charactr/vocos-mel-24khz/resolve/main/config.yaml" "models\vocos-mel-24khz\config.yaml"
Download-IfMissing "$ModelBaseUrl/charactr/vocos-mel-24khz/resolve/main/pytorch_model.bin" "models\vocos-mel-24khz\pytorch_model.bin"
Download-IfMissing "$ModelBaseUrl/SWivid/F5-TTS/resolve/main/F5TTS_v1_Base/vocab.txt" "models\F5TTS_v1_Base\vocab.txt"
Download-IfMissing "$ModelBaseUrl/SWivid/F5-TTS/resolve/main/F5TTS_v1_Base/model_1250000.safetensors" "models\F5TTS_v1_Base\model_1250000.safetensors"

.\.venv-f5\Scripts\python.exe .\scripts\patch_f5_local.py

Write-Host ""
Write-Host "Setup complete. Start the WebUI with:"
Write-Host "powershell -ExecutionPolicy Bypass -File .\scripts\run-f5-local.ps1"
