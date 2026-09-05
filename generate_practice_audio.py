#!/usr/bin/env python3
"""
Generate the practice track from TTS_PRACTICE.md using Sarvam bulbul:v3.

Sarvam has no SSML, so <break time="2.0s"/> markers are honoured by splicing
real silence between synthesised segments. That is exact, unlike SSML.

Usage:
    export SARVAM_API_KEY=...
    python3 generate_practice_audio.py --dry-run     # validate, no API calls
    python3 generate_practice_audio.py               # generate everything
    python3 generate_practice_audio.py --chunk 3     # regenerate one chunk

Output: audio/chunk_1.mp3 ... chunk_9.mp3 and audio/full_talk.mp3
Already-rendered segments are cached, so a failed run resumes for free.
"""

import argparse, base64, hashlib, json, os, re, subprocess, sys, time
from pathlib import Path

SRC        = Path("TTS_PRACTICE.md")
OUT        = Path("audio")
SEG        = OUT / "segments"
ENDPOINT   = "https://api.sarvam.ai/text-to-speech"
MODEL      = "bulbul:v3"
LANGUAGE   = "en-IN"
SPEAKER    = os.environ.get("SARVAM_SPEAKER", "aditya")   # male en-IN
PACE       = float(os.environ.get("SARVAM_PACE", "0.95")) # slightly under 1.0
SAMPLE_RATE = 24000
MAX_CHARS  = 2400          # under the 2500 cap, with headroom
BREAK_RE   = re.compile(r'<break\s+time="([\d.]+)s"\s*/>')


def parse_chunks(md: str):
    """-> [(chunk_no, title, [('text', str) | ('break', float), ...])]"""
    chunks = []
    for m in re.finditer(r'^## CHUNK (\d+)[^\n]*\n(.*?)(?=^## CHUNK |\Z|^# 3 )',
                         md, re.S | re.M):
        no, body = int(m.group(1)), m.group(2)
        body = re.sub(r'^---\s*$', '', body, flags=re.M).strip()
        items, pos = [], 0
        for b in BREAK_RE.finditer(body):
            txt = body[pos:b.start()].strip()
            if txt:
                items.append(("text", txt))
            items.append(("break", float(b.group(1))))
            pos = b.end()
        tail = body[pos:].strip()
        if tail:
            items.append(("text", tail))
        chunks.append((no, items))
    return chunks


def split_long(text: str, limit: int = MAX_CHARS):
    """Split oversized text on sentence boundaries."""
    if len(text) <= limit:
        return [text]
    sentences = re.split(r'(?<=[.?!])\s+', text)
    out, cur = [], ""
    for s in sentences:
        if len(cur) + len(s) + 1 > limit and cur:
            out.append(cur.strip()); cur = s
        else:
            cur = f"{cur} {s}".strip()
    if cur:
        out.append(cur.strip())
    return out


def clean(text: str) -> str:
    """Strip markdown that would otherwise be spoken aloud."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'^[#>\-\s]+', '', text, flags=re.M)
    return re.sub(r'\n{2,}', '\n', text).strip()


def synth(text: str, key: str, path: Path, tries: int = 4):
    if path.exists():
        return path
    import requests
    payload = {
        "text": text, "language_code": LANGUAGE, "speaker": SPEAKER,
        "model": MODEL, "pace": PACE, "speech_sample_rate": SAMPLE_RATE,
        "output_audio_codec": "wav", "enable_preprocessing": True,
    }
    for attempt in range(1, tries + 1):
        r = requests.post(ENDPOINT, json=payload,
                          headers={"api-subscription-key": key,
                                   "Content-Type": "application/json"},
                          timeout=120)
        if r.status_code == 200:
            audio = r.json()["audios"][0]
            path.write_bytes(base64.b64decode(audio))
            return path
        if r.status_code in (429, 500, 502, 503, 504) and attempt < tries:
            wait = 2 ** attempt
            print(f"    {r.status_code}, retry in {wait}s", flush=True)
            time.sleep(wait); continue
        sys.exit(f"Sarvam API {r.status_code}: {r.text[:400]}")


def silence(seconds: float, path: Path):
    if path.exists():
        return path
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i",
         f"anullsrc=r={SAMPLE_RATE}:cl=mono", "-t", f"{seconds}",
         "-c:a", "pcm_s16le", str(path)],
        check=True, capture_output=True)
    return path


def concat(parts, out_path: Path):
    listing = out_path.with_suffix(".txt")
    listing.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
         "-ar", str(SAMPLE_RATE), "-b:a", "128k", str(out_path)],
        check=True, capture_output=True)
    listing.unlink()
    return out_path


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="validate chunking and char counts, no API calls")
    ap.add_argument("--chunk", type=int, help="generate only this chunk")
    args = ap.parse_args()

    chunks = parse_chunks(SRC.read_text())
    if args.chunk:
        chunks = [c for c in chunks if c[0] == args.chunk]

    if args.dry_run:
        total_chars = total_break = calls = 0
        for no, items in chunks:
            ch_chars = sum(len(clean(t)) for k, t in items if k == "text")
            ch_break = sum(t for k, t in items if k == "break")
            segs = sum(len(split_long(clean(t)))
                       for k, t in items if k == "text")
            over = [len(clean(t)) for k, t in items
                    if k == "text" and len(clean(t)) > MAX_CHARS]
            print(f"  chunk {no}: {ch_chars:>5} chars · {segs:>2} API calls · "
                  f"{ch_break:>4.1f}s silence · ~{ch_chars/900:.1f} min speech"
                  + ("  [SPLIT NEEDED]" if over else ""))
            total_chars += ch_chars; total_break += ch_break; calls += segs
        print(f"\n  TOTAL: {total_chars} chars · {calls} API calls · "
              f"{total_break:.0f}s ({total_break/60:.1f} min) of silence")
        print(f"  Estimated runtime: "
              f"~{total_chars/900 + total_break/60:.1f} min "
              f"({total_chars/900:.1f} speech + {total_break/60:.1f} silence)")
        print("\n  No API calls made. Drop --dry-run to generate.")
        return

    key = os.environ.get("SARVAM_API_KEY")
    if not key:
        sys.exit("SARVAM_API_KEY not set.")

    OUT.mkdir(exist_ok=True); SEG.mkdir(exist_ok=True)
    chunk_files = []

    for no, items in chunks:
        print(f"chunk {no}:", flush=True)
        parts = []
        for idx, (kind, val) in enumerate(items):
            if kind == "break":
                parts.append(silence(val, SEG / f"sil_{val}.wav"))
                continue
            for j, piece in enumerate(split_long(clean(val))):
                h = hashlib.sha1(
                    f"{piece}{SPEAKER}{PACE}{MODEL}".encode()).hexdigest()[:12]
                p = SEG / f"c{no}_{idx:02d}_{j}_{h}.wav"
                if not p.exists():
                    print(f"  synth {len(piece):>4} chars", flush=True)
                    synth(piece, key, p)
                    time.sleep(0.35)          # be polite to the API
                parts.append(p)
        cf = concat(parts, OUT / f"chunk_{no}.mp3")
        chunk_files.append(cf)
        print(f"  -> {cf.name}  {duration(cf)/60:.2f} min\n", flush=True)

    if len(chunk_files) > 1:
        full = concat(chunk_files, OUT / "full_talk.mp3")
        total = duration(full)
        print(f"FULL TALK: {full}  {total/60:.1f} min")
        if total < 22 * 60:
            print("  Under 22 min — check that silences spliced correctly.")
        elif total > 26 * 60:
            print("  Over 26 min — trim before Sunday.")
        else:
            print("  In range.")


if __name__ == "__main__":
    main()
