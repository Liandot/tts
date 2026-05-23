from __future__ import annotations

import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / ".venv-f5" / "Lib" / "site-packages"
GRADIO = SITE / "f5_tts" / "infer" / "infer_gradio.py"
UTILS = SITE / "f5_tts" / "infer" / "utils_infer.py"
CLI = SITE / "f5_tts" / "infer" / "infer_cli.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"Could not patch {label}; expected text not found.")
    return text.replace(old, new, 1)


def patch_gradio() -> None:
    original = GRADIO.read_text(encoding="utf-8")
    text = original

    text = replace_once(
        text,
        "import tempfile\n",
        "import tempfile\nfrom datetime import datetime\n",
        "infer_gradio datetime import",
    )

    text = replace_once(
        text,
        'DEFAULT_TTS_MODEL = "F5-TTS_v1"\ntts_model_choice = DEFAULT_TTS_MODEL\n\nDEFAULT_TTS_MODEL_CFG = [\n'
        '    "hf://SWivid/F5-TTS/F5TTS_v1_Base/model_1250000.safetensors",\n'
        '    "hf://SWivid/F5-TTS/F5TTS_v1_Base/vocab.txt",\n',
        'DEFAULT_TTS_MODEL = "F5-TTS_v1"\ntts_model_choice = DEFAULT_TTS_MODEL\n'
        'LOCAL_MODELS_DIR = os.path.abspath("models")\n'
        'LOCAL_OUTPUTS_DIR = os.path.abspath("outputs")\n\nDEFAULT_TTS_MODEL_CFG = [\n'
        '    os.path.join(LOCAL_MODELS_DIR, "F5TTS_v1_Base", "model_1250000.safetensors"),\n'
        '    os.path.join(LOCAL_MODELS_DIR, "F5TTS_v1_Base", "vocab.txt"),\n',
        "infer_gradio local model config",
    )

    text = replace_once(
        text,
        "vocoder = load_vocoder()\n",
        'vocoder = load_vocoder(is_local=True, local_path=os.path.join(LOCAL_MODELS_DIR, "vocos-mel-24khz"))\n',
        "infer_gradio local vocoder",
    )

    text = replace_once(
        text,
        'def load_f5tts():\n    ckpt_path = str(cached_path(DEFAULT_TTS_MODEL_CFG[0]))\n'
        "    F5TTS_model_cfg = json.loads(DEFAULT_TTS_MODEL_CFG[2])\n"
        "    return load_model(DiT, F5TTS_model_cfg, ckpt_path)\n",
        "def load_f5tts():\n    ckpt_path = DEFAULT_TTS_MODEL_CFG[0]\n"
        "    F5TTS_model_cfg = json.loads(DEFAULT_TTS_MODEL_CFG[2])\n"
        "    return load_model(DiT, F5TTS_model_cfg, ckpt_path, vocab_file=DEFAULT_TTS_MODEL_CFG[1])\n",
        "infer_gradio load_f5tts",
    )

    save_func = '''\n\ndef save_generated_audio(gen_text, sample_rate, wave):\n    os.makedirs(LOCAL_OUTPUTS_DIR, exist_ok=True)\n    filename_text = re.sub(r"\\s+", " ", gen_text).strip()[:48]\n    filename_text = re.sub(r'[<>:"/\\\\|?*\\x00-\\x1f]', "_", filename_text).strip(" ._")\n    if not filename_text:\n        filename_text = "tts"\n\n    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")\n    output_path = os.path.join(LOCAL_OUTPUTS_DIR, f"{filename_text}_{timestamp}.wav")\n    sf.write(output_path, wave, sample_rate)\n    print(f"Saved generated audio: {output_path}")\n    return output_path\n'''
    if "def save_generated_audio(" not in text:
        text = text.replace("chat_model_state = None\nchat_tokenizer_state = None\n", "chat_model_state = None\nchat_tokenizer_state = None\n" + save_func, 1)

    text = replace_once(
        text,
        "    save_spectrogram(combined_spectrogram, spectrogram_path)\n\n    return (final_sample_rate, final_wave), spectrogram_path, ref_text, used_seed\n",
        "    save_spectrogram(combined_spectrogram, spectrogram_path)\n\n"
        "    output_path = save_generated_audio(gen_text, final_sample_rate, final_wave)\n"
        '    show_info(f"Saved generated audio to {output_path}")\n\n'
        "    return (final_sample_rate, final_wave), spectrogram_path, ref_text, used_seed\n",
        "infer_gradio autosave",
    )

    text = text.replace("            final_wave, _ = torchaudio.load(f.name)\n", '            final_wave, _ = sf.read(f.name, dtype="float32")\n')
    text = text.replace("        final_wave = final_wave.squeeze().cpu().numpy()\n", "        final_wave = np.squeeze(final_wave)\n")
    text = text.replace("            value=32,\n", "            value=16,\n", 1)
    text = text.replace("            value=8,\n", "            value=16,\n", 1)
    text = text.replace("            value=0.15,\n", "            value=0.0,\n", 1)

    if text != original:
        GRADIO.write_text(text, encoding="utf-8")


def patch_utils() -> None:
    original = UTILS.read_text(encoding="utf-8")
    text = original
    text = replace_once(text, "import re\n", "import re\nimport subprocess\n", "utils subprocess import")
    text = replace_once(text, "import numpy as np\n", "import numpy as np\nimport soundfile as sf\n", "utils soundfile import")
    text = replace_once(
        text,
        "cross_fade_duration = 0.15\n",
        "cross_fade_duration = 0.15\ngenerated_leading_trim_ms = 180\n",
        "utils generated leading trim setting",
    )

    conversion_block = '''\n    source_audio = ref_audio_orig\n    try:\n        import imageio_ffmpeg\n\n        with tempfile.NamedTemporaryFile(suffix=".wav", **tempfile_kwargs) as f:\n            converted_source = f.name\n        subprocess.run(\n            [\n                imageio_ffmpeg.get_ffmpeg_exe(),\n                "-y",\n                "-i",\n                ref_audio_orig,\n                "-ar",\n                str(target_sample_rate),\n                "-ac",\n                "1",\n                converted_source,\n            ],\n            check=True,\n            stdout=subprocess.DEVNULL,\n            stderr=subprocess.DEVNULL,\n        )\n        source_audio = converted_source\n    except Exception:\n        source_audio = ref_audio_orig\n'''
    if "source_audio = ref_audio_orig" not in text:
        text = text.replace("        audio_hash = hashlib.md5(audio_data).hexdigest()\n", "        audio_hash = hashlib.md5(audio_data).hexdigest()\n" + conversion_block, 1)

    text = text.replace("        aseg = AudioSegment.from_file(ref_audio_orig)\n", "        aseg = AudioSegment.from_wav(source_audio)\n")
    text = text.replace(
        "    audio, sr = torchaudio.load(ref_audio)\n",
        '    audio_np, sr = sf.read(ref_audio, dtype="float32", always_2d=True)\n    audio = torch.from_numpy(audio_np.T)\n',
    )
    text = text.replace("        text_list = [ref_text + gen_text]\n", '        text_list = [ref_text.rstrip() + " " + gen_text.lstrip()]\n')
    text = text.replace(
        "            generated_wave = generated_wave.squeeze().cpu().numpy()\n\n        return generated_wave, generated\n",
        "            generated_wave = generated_wave.squeeze().cpu().numpy()\n"
        "            leading_trim_samples = int(generated_leading_trim_ms * target_sample_rate / 1000)\n"
        "            if 0 < leading_trim_samples < len(generated_wave):\n"
        "                generated_wave = generated_wave[leading_trim_samples:]\n\n"
        "        return generated_wave, generated\n",
    )

    if text != original:
        UTILS.write_text(text, encoding="utf-8")


def patch_cli() -> None:
    original = CLI.read_text(encoding="utf-8")
    text = original
    text = text.replace('    vocoder_local_path = "../checkpoints/vocos-mel-24khz"\n', '    vocoder_local_path = os.path.abspath("models/vocos-mel-24khz")\n')
    text = text.replace('    vocoder_local_path = "../checkpoints/bigvgan_v2_24khz_100band_256x"\n', '    vocoder_local_path = os.path.abspath("models/bigvgan_v2_24khz_100band_256x")\n')
    if text != original:
        CLI.write_text(text, encoding="utf-8")


def main() -> None:
    for path in (GRADIO, UTILS, CLI):
        if not path.exists():
            raise FileNotFoundError(path)
    patch_gradio()
    patch_utils()
    patch_cli()
    print("Patched F5-TTS for local models, m4a reference audio, and output autosave.")


if __name__ == "__main__":
    main()
