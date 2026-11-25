---
name: maths-video
description: Vidéo tuto animée d'un exo de maths, façon cahier quadrillé qui s'écrit tout seul, avec voix off naturelle (voix neuronale française) calée au mot près, chapitres, sous-titres. Longue si besoin, mais chaque étape détaillée pour qu'on comprenne comment faire l'exo. À utiliser quand l'utilisateur tape /maths-video suivi d'un exo collé, ou demande « une vidéo / une animation / un tuto » qui explique un exo de maths ou d'Optimization.
---

# /maths-video : la vidéo explicative d'un exo de maths

Résultat : un `.mp4` 1080p (+ `.srt`, + chapitres intégrés) où une page de cahier se remplit au rythme d'une voix calme qui explique tout, étape par étape. Exemple de référence : `exemple/scenes.py` (un système de 3 équations à 4 inconnues).

L'étudiant n'aime pas les maths. Il ne veut pas une vidéo courte : il veut une vidéo où **rien n'est sauté**, après laquelle il sait refaire l'exo.

## Outils
- Python : `PY=python3` (ou le Python d'un venv) (Pillow, fonttools, imageio-ffmpeg, edge-tts, sympy).
- Moteur : `~/.claude/skills/maths-video/engine/` (`engine.py` composants, `voice.py` voix, `render.py` rendu). Ne pas copier le moteur dans le projet : on l'appelle là où il est.
- Voix : `fr-FR-RemyMultilingualNeural` (homme, naturel) par défaut ; `fr-FR-VivienneMultilingualNeural` (femme) en alternative. Choix dans scenes.py : `VOICE = "…"`, débit `RATE = "-6%"`. Sans connexion, repli sur la voix Mac (robotique) : le signaler si ça arrive.

## Méthode
1. **Le corrigé d'abord.** Suivre le skill `math-corrige` (résoudre, vérifier avec sympy, faire la fiche HTML/PDF), sauf si un corrigé vérifié existe déjà à côté de l'exo. La vidéo suit ce corrigé : mêmes étapes, mêmes nombres. Si l'utilisateur ne voulait que la vidéo, le PDF est quand même utile (on le cite à la fin de la vidéo).
2. **Projet** : créer `<dossier de l'exo>/_video_<nom court>/scenes.py` en partant de `exemple/scenes.py` (garder la structure, réécrire le contenu). `OUTPUT = "../<Nom de l'exo>_video"`.
3. **Story-board dans scenes.py** (voir « Plan type » et « Écrire une scène »).
4. **Contrôle visuel** : `$PY ~/.claude/skills/maths-video/engine/render.py <projet> still` → génère la voix, une image de fin par scène, `build/planche.png`, et liste les CONTRÔLES (texte hors cadre, chevauchements, ancre introuvable). Regarder la planche, puis les scènes denses en plein format (`build/still_<scène>.png`). Pour vérifier la synchro d'une scène : `render.py <projet> beats <scène>` (une image à la fin de chaque phrase). Tout corriger jusqu'à « rien à signaler ».
5. **Autocritique** avec la grille ci-dessous, corriger, relancer `still`.
6. **Rendu** : `$PY …/render.py <projet> video` (en arrière-plan, quelques minutes ; les voix sont en cache, seules les phrases modifiées sont régénérées). Produit `<Nom>_video.mp4` + `.srt`.
   - **Un seul rendu à la fois sur le Mac.** Un rendu prend déjà 8 cœurs et ~14 Go de mémoire ; un jour, 7 sous-agents ont lancé 7 rendus en même temps et le Mac était inutilisable. render.py a maintenant une file d'attente (verrou) : si un autre rendu tourne, il affiche « en attente de mon tour » et démarre quand l'autre a fini. C'est normal, ne pas le tuer ni le relancer.
   - Plusieurs exos à faire : les sous-agents peuvent écrire les `scenes.py` et faire les `still` en parallèle (léger), mais les rendus `video` passent l'un après l'autre. Prévenir que ça prendra « quelques minutes × nombre d'exos ».
7. **Livrer** : `open` la vidéo, donner le chemin, la durée, les chapitres, et 2-3 points sur ce qui pourrait encore être mieux. Pas de citation `>`.

## Plan type (≈ 1 min par étape importante ; 8-15 min pour un exo à 4 questions, c'est normal)
1. Intro (titre, de quoi on parle, les questions en pastilles).
2. L'énoncé lu calmement, puis « L'idée en une phrase » : ce qu'on cherche vraiment, en français simple, **avant** tout calcul.
3. Pour chaque question : rappel du cours (carte verte) → méthode en étapes numérotées → calcul ligne par ligne → résultat encadré → vérification → pièges (carte rouge).
4. À retenir : 3 réflexes max + « pour t'entraîner » (refaire au stylo, revenir au chapitre qui coince, le corrigé PDF).

Une scène = une page = une idée. Si une page déborde, couper en deux scènes plutôt que rétrécir le texte (taille mini 40 pour du texte, 46+ pour les calculs).

## Écrire une scène
```python
from engine import *
OUTPUT = "../Exo 5 - Lagrange_video"
CHAPTERS = ["Intro", "Énoncé", "Q1 · gradient", "Q2 · Hessienne", "À retenir"]

s = S("05_q1_calcul", chap=2)                 # nom = ordre du film ; chap = index dans CHAPTERS
ti = title("1) Le gradient")
mm = memo("L'énoncé", ["f(x, y) = x^2 + 3xy", "point A = (1, 2)"])   # pense-bête qui reste à droite (x ≥ 1400)
a = row([T("∂f/∂x =", 0, 0, size=48), T("2x + 3y", 0, 0, size=48), T("→", 0, 0, size=48),
         T([("= 8", {"b": True})], 0, 0, size=48)], X0 + 60, 320)          # un calcul en morceaux
s.beat("Première étape : on dérive par rapport à x.", ti, (0.5, mm))
s.beat("On dérive x au carré, @a ça donne 2 x, et 3 x y donne 3 y. @b En A, ça fait 8.",
       ("@a", a[0:2]), ("@b", [a[2], a[3], highlight(a[3])]), gap=1.0)
```
- `@nom` dans la phrase = l'endroit exact où l'élément apparaît (synchro au mot près). C'est la règle : un calcul apparaît **quand la voix le dit**, pas avant. Éviter les fractions `(0.6, el)`, imprécises.
- `gap=1.0` après un résultat important (laisse le temps de lire). `s.pause(1.5)` pour un vrai silence.
- Texte : `T(segs, x, y, size, color)`, segs = `"texte"` ou `[(texte, {"c": ROUGE, "b": True, "k": "cav"})]`. Indices `x_1`, `x_{12}` ; exposants `x^2`, `e^{-t}`. `e.boxes[i]` = boîte du segment i.
- Composants : `title`, `step(n, segs, x, y)` (pastille + texte, texte = `[1]`), `side` (remarque verte « ← … »), `card(x, y, w, h, "note"|"piege"|"oral", titre)`, `memo`, `system`, `matrix(rows, …, bar=4)` (`.cells[(i, j)]`), `table` (une ligne par élément, `.cells[j]`), `frac(num, den)`, `row`, `num`.
- Annotations : `highlight(box, JAUNE|VERTF|ROSE)`, `circle(box)`, `underline(box, wavy=True)`, `strike(box)` (termes qui s'annulent), `arrow((x0, y0), (x1, y1))`, `frame_box(el)` (résultat final).
- Mise en page : grille de 40 px, texte à partir de `X0` (190), bord droit `X_MAX` (1860), bas `Y_MAX` (1000, en dessous = barre des chapitres). Avec un `memo` à droite, rester à x < 1360. Titres en y=40, contenu à partir de y≈200, lignes de calcul espacées de 90-120 px.

## La voix off (le texte dit)
- Écrire **comme on parle** à un pote qui galère : phrases courtes, « on », « tu », « regarde », « et là ». Une idée par phrase.
- Écrire les maths comme elles se prononcent : « x 3 plus 3 fois x 4 égale 3 », « moins 1 », « x au carré », « dérivée partielle de f par rapport à x », « 3 sur 4 ». Jamais de symboles (`−`, `×`, `²`, `∂`, `x_3`) dans la voix.
- Dire le **pourquoi** avant le **comment** ; annoncer l'étape (« Étape 2 : on remonte l'escalier »).
- Répéter le résultat après l'avoir trouvé (« x 3 égale 6. Six. ») seulement pour les résultats clés.
- Ce qui est à l'écran et ce qui est dit doivent correspondre mot pour mot pour les calculs.
- Pas de « Salut les amis », pas de blabla de youtubeur, pas d'injonction à faire l'exo seul avant de regarder.

## Grille d'autocritique (à passer avant le rendu)
- [ ] Chaque nombre à l'écran a été vérifié (sympy) et correspond au corrigé.
- [ ] Aucune étape sautée : chaque ligne de calcul = une seule opération, expliquée à voix haute.
- [ ] Synchro : chaque élément important a une ancre `@` ; rien n'apparaît avant d'être dit.
- [ ] L'œil sait où regarder : surligneur / cercle / flèche sur ce dont on parle, et l'énoncé ou les données restent visibles (`memo`) quand on calcule.
- [ ] Pages pas vides à moitié, pas surchargées, rien sous la barre des chapitres ; CONTRÔLES = rien à signaler.
- [ ] Pauses après les résultats ; rythme pas monotone (alterner phrases courtes et explications).
- [ ] Rappels de cours avant usage, pièges réels, vérification finale, récap 3 réflexes.
- [ ] Voix neuronale bien utilisée (pas de repli sur la voix Mac).

## Pièges techniques
- Glyphes : Patrick Hand n'a pas →, ←, ⟹, ✓, ∂, ∇, ₁ : ils passent en police STIX automatiquement (ok). Écrire les indices avec `x_1`, pas `x₁`.
- Les ancres doivent précéder un vrai mot prononcé (`@a 6`, pas `@a,`). Si une ancre n'est pas trouvée, render.py le signale.
- Le cache voix est dans `build/` (`*.wav.json`) : si on change de voix, tout est régénéré automatiquement.
- Garder `build/` tant que l'utilisateur peut demander des retouches ; le supprimer (et `_video_*`) seulement s'il le demande.
- Un « _ » dans du texte normal devient un indice (« Exo1_corrige » s'affiche mal) : écrire « le corrigé de l'exo 1 (PDF) ».
- Dans Patrick Hand, la matrice identité « I » ressemble à « l » ou « 1 » (« 2I » se lit « 21 ») : l'écrire avec un I à empattements (police de secours) ou en gras, et la nommer à l'oral.
- Chapitres : render.py coupe tout seul un chapitre de plus de 5 min en « (suite 2) » (au-delà de ~6 min 20, ffmpeg écrit des chapitres faux). Pour refaire les chapitres d'une vidéo déjà rendue : `render.py <projet> chapitres`.
