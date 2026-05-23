param(
    [Parameter(Mandatory = $true)]
    [string]$RefAudio,

    [Parameter(Mandatory = $true)]
    [string]$RefText,

    [string]$GenText = "This is a short smoke test.",
    [string]$OutputFile = "smoke_test.wav",
    [int]$NfeStep = 8
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (-not (Test-Path ".\.venv-f5\Scripts\f5-tts_infer-cli.exe")) {
    throw "Missing .venv-f5. Run setup-local.ps1 first."
}

.\.venv-f5\Scripts\python.exe .\scripts\patch_f5_local.py

$FfmpegExe = & ".\.venv-f5\Scripts\python.exe" -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"
$env:PATH = "$(Split-Path -Parent $FfmpegExe);$env:PATH"

New-Item -ItemType Directory -Force outputs | Out-Null

& ".\.venv-f5\Scripts\f5-tts_infer-cli.exe" `
    --model F5TTS_v1_Base `
    --ckpt_file "models\F5TTS_v1_Base\model_1250000.safetensors" `
    --vocab_file "models\F5TTS_v1_Base\vocab.txt" `
    --ref_audio $RefAudio `
    --ref_text $RefText `
    --gen_text $GenText `
    --output_dir outputs `
    --output_file $OutputFile `
    --nfe_step $NfeStep `
    --cross_fade_duration 0 `
    --speed 1 `
    --device cpu `
    --load_vocoder_from_local
