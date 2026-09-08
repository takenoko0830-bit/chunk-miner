#!/usr/bin/env python3
"""chunks.json の例文から音声ファイルを生成する。

iOS は画面がロックされると speechSynthesis を止めるが、メディア再生は止めない。
そこで例文を事前に音声ファイルにしておき、アプリ側は <audio> で再生する。

ファイル名は本文の SHA-256 の先頭16桁。内容が同じなら同じファイルになるので、
再実行しても既存ファイルは書き換わらず、git の履歴が膨らまない。
本文を編集した例文だけが新しいファイルになる（古いほうは --prune で掃除できる）。

使い方:
    python3 tools/build-audio.py            # 未生成のものだけ作る
    python3 tools/build-audio.py --top 10   # seen 上位10チャンクぶんだけ作る
    python3 tools/build-audio.py --prune    # どの例文からも参照されないファイルを消す
"""
import argparse, hashlib, json, subprocess, sys, wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIO = ROOT / "audio"
VOICE = {"en": "Samantha", "ja": "Kyoko"}

# 間を埋めるための無音。再生を途切れさせないために使う（下の理由を参照）
SILENCE_MS = 500


def key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def synth(text: str, voice: str, out: Path) -> None:
    subprocess.run(
        ["say", "-v", voice, "--data-format=aac", "-o", str(out), text],
        check=True, capture_output=True,
    )


def write_silence(out: Path, ms: int) -> None:
    """無音の WAV。say では作れないので直接書く。外部依存を増やさないため。"""
    rate = 8000
    with wave.open(str(out), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00\x00" * (rate * ms // 1000))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=0,
                    help="seen 上位N件のチャンクだけを対象にする（0 は全部）")
    ap.add_argument("--prune", action="store_true",
                    help="どの例文からも参照されないファイルを消す")
    args = ap.parse_args()

    chunks = json.loads((ROOT / "chunks.json").read_text(encoding="utf-8"))["chunks"]
    if args.top:
        chunks = sorted(chunks, key=lambda c: -c["seen"])[: args.top]

    wanted = {"en": {}, "ja": {}}
    for c in chunks:
        for e in c["examples"]:
            if e.get("en"):
                wanted["en"][key(e["en"])] = e["en"]
            if e.get("ja"):
                wanted["ja"][key(e["ja"])] = e["ja"]

    made = skipped = 0
    for lang, items in wanted.items():
        d = AUDIO / lang
        d.mkdir(parents=True, exist_ok=True)
        for h, text in sorted(items.items()):
            out = d / f"{h}.m4a"
            if out.exists():
                skipped += 1
                continue
            synth(text, VOICE[lang], out)
            made += 1
            print(f"  + {lang}/{h}.m4a  {text[:52]}")

    silence = AUDIO / "silence.wav"
    if not silence.exists():
        write_silence(silence, SILENCE_MS)
        print(f"  + silence.wav ({SILENCE_MS}ms)")

    removed = 0
    if args.prune:
        for lang in ("en", "ja"):
            for f in (AUDIO / lang).glob("*.m4a"):
                if f.stem not in wanted[lang]:
                    f.unlink()
                    removed += 1
                    print(f"  - {lang}/{f.name}")

    manifest = {
        "v": 1,
        "voice": VOICE,
        "silenceMs": SILENCE_MS,
        "en": sorted(wanted["en"]),
        "ja": sorted(wanted["ja"]),
    }
    (AUDIO / "index.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    total = sum(f.stat().st_size for f in AUDIO.rglob("*") if f.is_file())
    print(f"\n生成 {made} / 既存 {skipped}" + (f" / 削除 {removed}" if args.prune else ""))
    print(f"英語 {len(wanted['en'])} 件・日本語 {len(wanted['ja'])} 件 / 合計 {total/1024/1024:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
