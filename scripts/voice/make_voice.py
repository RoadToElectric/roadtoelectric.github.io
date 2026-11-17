"""Make a voiceover mp3 from a text file with ElevenLabs Eleven v4 Turbo.

The key is read from .env.local at the repo root (ELEVENLABS_API_KEY); it is
never stored in code. eleven_v4_turbo only works over the Text to Dialogue
WebSocket, so the text is streamed there paragraph by paragraph.

Usage:
  python scripts/voice/make_voice.py <voiceover.txt> [-o out.mp3] [--voice NAME_OR_ID]
  python scripts/voice/make_voice.py --list-voices

Default output: <name>_voiceover.txt -> <name>_voice.mp3 (else <name>.mp3),
next to the input file.
"""
import argparse
import asyncio
import base64
import json
import os
import sys
from pathlib import Path

import websockets
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

REPO = Path(__file__).resolve().parents[2]
load_dotenv(REPO / ".env.local")

DEFAULT_VOICE = "JBFqnCBsd6RMkjVDRZzb"  # George (pre-made, narrative)
MODEL = "eleven_v4_turbo"
WS_URL = "wss://api.elevenlabs.io/v1/text-to-dialogue/stream-input"


def client():
    if not os.getenv("ELEVENLABS_API_KEY"):
        sys.exit("ELEVENLABS_API_KEY not found: run `npx -y @elevenlabs/cli@latest onboard init` in the repo.")
    return ElevenLabs()


def list_voices():
    for v in client().voices.get_all().voices:
        print(f"{v.voice_id}  {v.category or '':10}  {v.name}")


def resolve_voice(arg):
    if not arg:
        return DEFAULT_VOICE
    for v in client().voices.get_all().voices:
        if arg in (v.voice_id, v.name) or v.name.lower().startswith(arg.lower()):
            return v.voice_id
    return arg  # assume it is an id the account can use


def paragraphs(text):
    parts = [p.strip().replace("\n", " ") for p in text.split("\n\n")]
    return [p for p in parts if p]


async def synth(paras, voice_id, out, stability, similarity, fmt):
    url = f"{WS_URL}?model_id={MODEL}&output_format={fmt}"
    tmp = out.with_suffix(out.suffix + ".part")
    n_bytes = 0
    async with websockets.connect(url, max_size=None, open_timeout=30) as ws:
        await ws.send(json.dumps({
            "voices": [voice_id],
            "xi_api_key": os.environ["ELEVENLABS_API_KEY"],
            "settings": {"stability": stability, "similarity_boost": similarity},
        }))
        for p in paras:
            await ws.send(json.dumps({"inputs": [{"text": p + " ", "voice_id": voice_id, "new_turn": False}]}))
        await ws.send(json.dumps({"close_socket": True}))
        with open(tmp, "wb") as f:
            while True:
                try:
                    msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=120))
                except websockets.ConnectionClosedOK:
                    break
                if msg.get("error"):
                    raise RuntimeError(msg)
                if msg.get("audio"):
                    chunk = base64.b64decode(msg["audio"])
                    f.write(chunk)
                    n_bytes += len(chunk)
                    print(f"\r  received {n_bytes / 1024:,.0f} KB", end="", flush=True)
                if msg.get("is_final"):
                    break
    print()
    if n_bytes == 0:
        tmp.unlink(missing_ok=True)
        raise RuntimeError("no audio received")
    tmp.replace(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text_file", nargs="?")
    ap.add_argument("-o", "--out")
    ap.add_argument("--voice", help="voice name or id (default George)")
    ap.add_argument("--stability", type=float, default=0.5)
    ap.add_argument("--similarity", type=float, default=0.75)
    ap.add_argument("--format", default="mp3_44100_128")
    ap.add_argument("--list-voices", action="store_true")
    a = ap.parse_args()

    if a.list_voices:
        return list_voices()
    if not a.text_file:
        ap.error("text_file is required")

    src = Path(a.text_file)
    text = src.read_text(encoding="utf-8")
    paras = paragraphs(text)
    chars = sum(len(p) for p in paras)
    if a.out:
        out = Path(a.out)
    elif src.stem.endswith("_voiceover"):
        out = src.with_name(src.stem[: -len("_voiceover")] + "_voice.mp3")
    else:
        out = src.with_suffix(".mp3")

    voice_id = resolve_voice(a.voice)
    print(f"{src.name}: {chars:,} characters in {len(paras)} paragraphs -> {out}")
    print(f"model {MODEL}, voice {voice_id}")
    asyncio.run(synth(paras, voice_id, out, a.stability, a.similarity, a.format))
    print(f"saved {out} ({out.stat().st_size / 1024:,.0f} KB)")


if __name__ == "__main__":
    main()
