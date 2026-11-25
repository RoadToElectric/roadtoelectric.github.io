"""Make one short mp3 per word with ElevenLabs Eleven v4 Turbo, in Frank's cloned voice (same setup as make_voice.py).

Usage: python scripts/voice/make_words.py <words.txt> <out_dir>
words.txt = one item per line, "id|text" (id = file name without .mp3) or just "text" (file name = text).
Existing files are skipped, so a run can be repeated safely. One WebSocket session per word (v4 Turbo only works over the dialogue socket).
"""
import asyncio, base64, json, os, re, sys, unicodedata
from pathlib import Path
import websockets
from dotenv import load_dotenv

REPO = Path(__file__).resolve().parents[2]
load_dotenv(REPO / ".env.local")
VOICE = os.getenv("WORDS_VOICE", "mGetNfupYuyABoOVawCR")   # set WORDS_VOICE=<voice id> to use another voice (e.g. a Quebec French library voice)
URL = "wss://api.elevenlabs.io/v1/text-to-dialogue/stream-input?model_id=eleven_v4_turbo&output_format=mp3_44100_64"

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_") or "x"

async def one(text, out):
    buf = b""
    async with websockets.connect(URL, max_size=None, open_timeout=30) as ws:
        await ws.send(json.dumps({"voices": [VOICE], "xi_api_key": os.environ["ELEVENLABS_API_KEY"], "settings": {"stability": 0.6, "similarity_boost": 0.75}}))
        await ws.send(json.dumps({"inputs": [{"text": text + " ", "voice_id": VOICE, "new_turn": False}]}))
        await ws.send(json.dumps({"close_socket": True}))
        while True:
            try:
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=60))
            except websockets.ConnectionClosedOK:
                break
            if msg.get("error"): raise RuntimeError(msg)
            if msg.get("audio"): buf += base64.b64decode(msg["audio"])
            if msg.get("is_final"): break
    if not buf: raise RuntimeError("no audio")
    out.write_bytes(buf)

async def main(src, outdir, workers=4):
    outdir.mkdir(parents=True, exist_ok=True)
    jobs = []
    for line in Path(src).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line: continue
        fid, _, text = line.partition("|") if "|" in line else (None, "", line)
        text = text.strip() if fid else line
        out = outdir / ((slug(fid) if fid else slug(text)) + ".mp3")
        if not out.exists(): jobs.append((text, out))
    q = asyncio.Queue()
    for j in jobs: q.put_nowait(j)
    done = [0, 0, 0]
    async def worker():
        while True:
            try: text, out = q.get_nowait()
            except asyncio.QueueEmpty: return
            for attempt in range(4):
                try:
                    await one(text, out); done[0] += 1; done[1] += len(text); break
                except Exception as e:
                    await asyncio.sleep(2 + attempt * 3)
            else:
                done[2] += 1; print("FAILED", out.name, text, flush=True)
            if (done[0] + done[2]) % 100 == 0: print(f"{done[0]}/{len(jobs)} files, {done[1]} characters", flush=True)
    await asyncio.gather(*[worker() for _ in range(workers)])
    print(f"done: {done[0]} files, {done[1]} characters, {done[2]} failed of {len(jobs)}")

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], Path(sys.argv[2])))
