"""Rendu d'une vidéo de maths.

  PY=python3   # Pillow, fonttools, imageio-ffmpeg, edge-tts, sympy
  $PY render.py <dossier_projet> still  [scènes…]   # voix + une image de fin par scène + planche.png + contrôles
  $PY render.py <dossier_projet> beats  <scène>     # une image à la fin de CHAQUE phrase de la scène (contrôle fin)
  $PY render.py <dossier_projet> video  [scènes…]   # rendu complet -> OUTPUT.mp4 + .srt + chapitres
  $PY render.py <dossier_projet> chapitres          # refait juste les chapitres d'une vidéo déjà rendue

<dossier_projet>/scenes.py définit SCENES (via S(...)), et :
  OUTPUT   = "../Nom du fichier final"   (sans extension, relatif au dossier projet)
  CHAPTERS = ["Énoncé", "Q1", "Q2", ...]  (optionnel : barre de chapitres + chapitres dans le .mp4)
  VOICE    = "fr-FR-RemyMultilingualNeural"  (optionnel)
"""
import os, re, sys, glob, subprocess, importlib
from multiprocessing import Pool

ENGINE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
MODE = sys.argv[2] if len(sys.argv) > 2 else "still"
sys.path.insert(0, ENGINE); sys.path.insert(0, PROJ)
import engine as E
import voice as V
scenes = importlib.import_module("scenes")
SCENES = E.SCENES
CHAPTERS = getattr(scenes, "CHAPTERS", None)
VOICE = getattr(scenes, "VOICE", None)
RATE = getattr(scenes, "RATE", None)
OUT = os.path.join(PROJ, "build"); os.makedirs(OUT, exist_ok=True)
LEAD, GAP, TAIL = 0.6, 0.45, 0.9


def prepare(sc):
    """Voix de chaque phrase -> wav de la scène ; calcule t0 de chaque élément."""
    import array, wave
    data = array.array("h"); sr = 44100
    def sil(s): data.extend([0] * int(s * sr))
    t = LEAD; sil(LEAD)
    els, subs, warns = [], [], []
    for i, (say, items, gap) in enumerate(sc.beats):
        if say is None:                      # pause
            sil(gap or 1.0); t += gap or 1.0
            continue
        clean, pos = V.split_anchors(say)
        wav = os.path.join(OUT, f"{sc.name}_{i:02d}.wav")
        dur, words = V.synth(clean, wav, VOICE, RATE)
        at = V.anchor_times(clean, pos, words, dur)
        for fr, k, el in items:
            if isinstance(fr, str):
                name = fr.lstrip("@")
                if name not in at:
                    warns.append(f"{sc.name}: ancre @{name} absente de la phrase « {say[:50]}… »"); off = 0
                else: off = at[name]
            else:
                off = fr * dur
            el.t0 = t + off + k + getattr(el, "t_off", 0)
            els.append(el)
        subs.append((clean, t, dur))
        with wave.open(wav) as w: data.frombytes(w.readframes(w.getnframes()))
        g = GAP if gap is None else gap
        t += dur; sil(g); t += g
    sil(TAIL); t += TAIL
    with wave.open(os.path.join(OUT, f"{sc.name}.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(data.tobytes())
    return els, len(data) / sr, subs, warns


def job(name):
    sc = next(s for s in SCENES if s.name == name)
    els, total, subs, warns = prepare(sc)
    warns += E.check_layout(sc.name, els)
    bg = E.paper(CHAPTERS, sc.chap)
    if MODE == "still":
        E.still(els, total, os.path.join(OUT, f"still_{sc.name}.png"), bg)
    elif MODE == "beats":
        for k, (_, st, d) in enumerate(subs):
            E.still(els, st + d + 0.4, os.path.join(OUT, f"beat_{sc.name}_{k:02d}.png"), bg)
    else:
        E.render_scene(els, total, os.path.join(OUT, f"{sc.name}.wav"), os.path.join(OUT, f"{sc.name}.mp4"), bg)
    return name, total, subs, warns, sc.chap


def planche(names, path):
    from PIL import Image
    ims = [Image.open(os.path.join(OUT, f"still_{n}.png")).resize((640, 360)) for n in names]
    c = 3; r = (len(ims) + c - 1) // c
    S = Image.new("RGB", (c * 650, r * 370), (120, 120, 120))
    for i, im in enumerate(ims): S.paste(im, ((i % c) * 650 + 5, (i // c) * 370 + 5))
    S.save(path)


def ts(x):
    h, m = divmod(int(x), 3600); m, s = divmod(m, 60); return f"{h:02d}:{m:02d}:{s:02d},{int((x % 1) * 1000):03d}"


MAX_CHAP = 300   # ffmpeg (mp4) déborde au-delà d'environ 380 s par chapitre : chapitres faux.
                 # On coupe donc les chapitres longs en « (suite) », à une frontière de scène.


def _lab(c):
    return re.sub(r"_(\w)", lambda m: m.group(1).translate(str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")), c)


def write_chapters(items, final):
    """items : [(nom_scène, durée, chap)] dans l'ordre. Écrit build/chapters.txt, retourne son chemin."""
    starts = []; off = 0; cur = None; cur_start = 0; part = 1
    for n, t, chap in items:
        if CHAPTERS and chap is not None:
            if chap != cur:
                starts.append((off, _lab(CHAPTERS[chap]))); cur = chap; cur_start = off; part = 1
            elif off - cur_start + t > MAX_CHAP and off > cur_start:
                part += 1; starts.append((off, _lab(CHAPTERS[chap]) + f" (suite {part})")); cur_start = off
        off += t
    meta = [";FFMETADATA1", "title=" + os.path.basename(final)]
    for k, (st, lab) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else off
        meta += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={int(st * 1000)}", f"END={int(end * 1000)}", f"title={lab}"]
    mf = os.path.join(OUT, "chapters.txt"); open(mf, "w").write("\n".join(meta) + "\n")
    return mf


def rechapter():
    """Mode 'chapitres' : recalcule les chapitres d'une vidéo déjà rendue (sans re-rendu)."""
    import wave
    final = os.path.normpath(os.path.join(PROJ, getattr(scenes, "OUTPUT", "../video")))
    items = []
    for sc in SCENES:
        with wave.open(os.path.join(OUT, f"{sc.name}.wav")) as w: items.append((sc.name, w.getnframes() / w.getframerate(), sc.chap))
    mf = write_chapters(items, final)
    tmp = final + ".tmp.mp4"
    subprocess.run([E.FFMPEG, "-y", "-loglevel", "error", "-i", final + ".mp4", "-i", mf, "-map", "0", "-map_metadata", "1",
                    "-map_chapters", "1", "-c", "copy", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, final + ".mp4"); print("chapitres refaits :", final + ".mp4")


if __name__ == "__main__":
    if MODE == "chapitres":
        rechapter(); sys.exit()
    names = sys.argv[3:] or [s.name for s in SCENES]
    for f in glob.glob(os.path.join(OUT, "still_*.png")) if MODE == "still" and not sys.argv[3:] else []:
        os.remove(f)
    if MODE == "beats":
        for f in glob.glob(os.path.join(OUT, "beat_*.png")): os.remove(f)
    # Un seul rendu à la fois sur le Mac : chaque rendu lance 8 ffmpeg (~1,7 Go chacun),
    # plusieurs rendus en parallèle saturent la mémoire et tout devient plus lent.
    # Les rendus suivants attendent leur tour ici (file d'attente automatique).
    import fcntl, time
    lockf = open(os.path.join(ENGINE, ".render.lock"), "w")
    try:
        if MODE == "video": fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("Un autre rendu tourne déjà : en attente de mon tour…", flush=True)
        t0 = time.time(); fcntl.flock(lockf, fcntl.LOCK_EX)
        print(f"À moi ({(time.time() - t0) / 60:.1f} min d'attente).", flush=True)
    with Pool(min(8, len(names))) as p:
        res = p.map(job, names)
    allw = [w for r in res for w in r[3]]
    for n, t, *_ in res: print(f"{n:28s} {t:6.1f} s")
    tot = sum(r[1] for r in res)
    print(f"TOTAL {tot:.0f} s  ({tot / 60:.1f} min)")
    print("\n".join(["CONTRÔLES :"] + allw) if allw else "CONTRÔLES : rien à signaler")
    if MODE == "still":
        planche(names, os.path.join(OUT, "planche.png")); print("planche :", os.path.join(OUT, "planche.png"))
    if MODE == "beats":
        print("images :", os.path.join(OUT, "beat_*.png"))
    if MODE == "video" and len(names) == len(SCENES):
        final = os.path.normpath(os.path.join(PROJ, getattr(scenes, "OUTPUT", "../video")))
        lst = os.path.join(OUT, "list.txt")
        open(lst, "w").write("".join(f"file '{n}.mp4'\n" for n, *_ in res))
        mf = write_chapters([(n, t, chap) for n, t, subs, w, chap in res], final)
        subprocess.run([E.FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", mf,
                        "-map_metadata", "1", "-map_chapters", "1", "-c", "copy", "-movflags", "+faststart", final + ".mp4"], check=True)
        off = 0; k = 1; srt = []
        for n, t, subs, *_ in res:
            for say, st, d in subs:
                srt.append(f"{k}\n{ts(off + st)} --> {ts(off + st + d)}\n{say}\n"); k += 1
            off += t
        open(final + ".srt", "w").write("\n".join(srt))
        print("OK", final + ".mp4")
