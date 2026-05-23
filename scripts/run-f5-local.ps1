param(
    [int]$Port = 7860
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (-not (Test-Path ".\.venv-f5\Scripts\python.exe")) {
    throw "Missing .venv-f5. Run: powershell -ExecutionPolicy Bypass -File .\scripts\setup-local.ps1"
}

.\.venv-f5\Scripts\python.exe .\scripts\patch_f5_local.py

$FfmpegExe = & ".\.venv-f5\Scripts\python.exe" -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"
$env:PATH = "$(Split-Path -Parent $FfmpegExe);$env:PATH"

& ".\.venv-f5\Scripts\f5-tts_infer-gradio.exe" --port $Port
