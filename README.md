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

### For WSL2

The Windows `.venv-f5` cannot be reused inside WSL2. Create a Linux virtual environment:

```bash
cd ai-tts-playground
uv venv .venv-f5-wsl --python 3.11
source .venv-f5-wsl/bin/activate
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
uv pip install -r requirements.txt
python scripts/patch_f5_local.py
```

Start the WebUI from WSL2:

```bash
cd ai-tts-playground
source .venv-f5-wsl/bin/activate
f5-tts_infer-gradio --port 7860 --host 0.0.0.0
```

Open in Windows:

```text
http://localhost:7860
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
