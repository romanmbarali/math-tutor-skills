"""Voix off : voix neuronale Microsoft (edge-tts, gratuite, sans clé), avec le minutage de chaque mot.
Repli automatique sur la voix Mac (say) si pas de connexion.

Voix (variable d'env MV_VOICE ou VOICE dans scenes.py) :
  fr-FR-RemyMultilingualNeural      homme, naturel, posé   (défaut)
  fr-FR-VivienneMultilingualNeural  femme, naturelle
  fr-FR-HenriNeural / fr-FR-DeniseNeural / fr-FR-EloiseNeural  plus « annonce »
"""
import os, re, json, asyncio, hashlib, subprocess, wave
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
VOICE = os.environ.get("MV_VOICE", "fr-FR-RemyMultilingualNeural")
RATE = os.environ.get("MV_RATE", "-6%")      # un poil plus lent que la normale : on explique
ANCHOR = re.compile(r"@(\w+)\s?")


def split_anchors(say):
    """'On prend @a x 4' -> ('On prend x 4', {'a': 8})  (position en caractères dans le texte propre)."""
    clean, pos, last = "", {}, 0
    for m in ANCHOR.finditer(say):
        clean += say[last:m.start()]
        pos[m.group(1)] = len(clean)
        last = m.end()
    clean += say[last:]
    return clean, pos


def _dur(wav):
    with wave.open(wav) as w:
        return w.getnframes() / w.getframerate()


async def _edge(text, mp3, voice, rate):
    import edge_tts
    words = []
    c = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    with open(mp3, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary": words.append((ch["offset"] / 1e7, ch["text"]))
    return words


def synth(text, wav, voice=None, rate=None):
    """Écrit wav (44,1 kHz mono). Retourne (durée, [(t, mot), ...]). Cache : ne régénère que si le texte change."""
    voice = voice or VOICE; rate = rate or RATE
    key = hashlib.sha1(f"{voice}|{rate}|{text}".encode()).hexdigest()
    meta = wav + ".json"
    if os.path.exists(wav) and os.path.exists(meta):
        m = json.load(open(meta))
        if m.get("key") == key and not m.get("fallback"):
            return m["dur"], [tuple(w) for w in m["words"]]
    words = []; fallback = False
    try:
        mp3 = wav[:-4] + ".mp3"
        import time, random
        for attempt in range(6):
            try:
                words = asyncio.run(_edge(text, mp3, voice, rate))
                if not os.path.getsize(mp3): raise RuntimeError("audio vide")
                break
            except Exception:
                if attempt == 5: raise
                time.sleep(2 ** attempt + random.random() * 2)
        src = mp3
    except Exception as ex:
        print(f"  [voix] edge-tts indisponible ({ex.__class__.__name__}) -> voix Mac", flush=True)
        src = wav[:-4] + ".aiff"
        subprocess.run(["say", "-v", "Thomas", "-r", "165", "-o", src, text], check=True)
        words = []; fallback = True
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", src, "-ar", "44100", "-ac", "1", wav], check=True)
    os.remove(src)
    d = _dur(wav)
    json.dump({"key": key, "dur": d, "words": words, "text": text, "fallback": fallback}, open(meta, "w"), ensure_ascii=False)
    return d, words


def anchor_times(clean, pos, words, dur):
    """Temps (s, dans la phrase) de chaque ancre = début du premier mot prononcé à partir de l'ancre."""
    norm = clean.lower()
    wpos = []; cur = 0
    for t, w in words:
        i = norm.find(w.lower(), cur)
        if i < 0: continue
        wpos.append((i, t)); cur = i + len(w)
    out = {}
    for name, c in pos.items():
        t = next((t for i, t in wpos if i >= c), None)
        if t is None:
            t = dur * c / max(1, len(clean)) if not wpos else (wpos[-1][1] if c > wpos[-1][0] else dur * c / max(1, len(clean)))
        out[name] = t
    return out


def silence(wav, sec):
    import array
    sr = 44100
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(array.array("h", [0] * int(sec * sr)).tobytes())
    return sec
