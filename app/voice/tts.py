import os
import requests
from pathlib import Path


def synthesize_elevenlabs(text: str, voice_id: str, out_dir: Path) -> str:
    api_key = os.getenv("ELEVENLABS_API_KEY", "")
    if not api_key:
        return ""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": api_key, "accept": "audio/mpeg", "content-type": "application/json"}
    payload = {"text": text}
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "output.mp3"
    out_path.write_bytes(r.content)
    return str(out_path)
