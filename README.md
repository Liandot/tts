# AI TTS Playground

Tiny Windows playground for local F5-TTS voice cloning experiments.

## Setup

Install Python 3.11, Git, and `uv`, then run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup-local.ps1
```

Start the WebUI:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-f5-local.ps1
```

Open:

```text
http://127.0.0.1:7860
```

## Use

1. Put your own short reference audio in `samples/`.
2. Upload it as `Reference Audio`.
3. Fill `Reference Text` manually with the exact words in that audio.
4. Enter a short `Text to Generate`.
5. Click `Synthesize`.

Generated files are saved in `outputs/`.

## Smoke Test

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke-test.ps1 -RefAudio samples\your_voice.wav -RefText "exact transcript here"
```

## Project Structure

```text
scripts/   setup, run, patch, and smoke-test helpers
samples/   your private reference audio files
models/    downloaded model files
outputs/   generated audio
```

`samples/`, `models/`, `outputs/`, and `.venv-f5/` are ignored by Git.
