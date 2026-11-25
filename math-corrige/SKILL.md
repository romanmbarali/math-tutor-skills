---
name: math-corrige
description: Corrigé papier d'un exo de maths pour un étudiant qui galère, style cahier quadrillé (Patrick Hand + Caveat, étapes numérotées, rappels de cours verts, calculs bleus surlignés, résultats encadrés rouges, pièges, « à l'oral », mémo). Sortie HTML + PDF A4. À utiliser quand l'utilisateur tape /math-corrige (ou /math-corrigé) suivi d'un exo collé, ou demande « le corrigé » / « corrige-moi cet exo » / « fais la fiche » pour un exo de maths ou d'Optimization. C'est aussi la première étape de /maths-video.
---

# /math-corrige : corrigé papier d'un exo de maths

L'étudiant n'aime pas les maths : il veut comprendre **chaque** étape, sans rien sauter, en français très simple. Le format est celui d'une fiche « cahier » ; le modèle de référence est `modele.html` (un système de 3 équations à 4 inconnues).

## Fichiers du skill
- `modele.html` : corrigé modèle complet. **Copier son `<style>` tel quel** et reprendre ses blocs (énoncé, tableau « ce que l'énoncé veut dire », note, step, math, box, piège, oral, mémo). Ne pas réinventer le CSS.
- `build.sh corrige.html [sortie.pdf]` : PDF A4 via Chrome headless + `_apercu.png` (planche des pages) + vérif de la police.

## Méthode
1. **Lire l'exo** (texte collé, PDF ou image). Si l'énoncé est en anglais, le recopier tel quel dans l'encadré « L'énoncé » et tout expliquer en français. S'il manque un morceau (question coupée, figure absente), le dire au lieu d'inventer.
   Chercher le cours si un dossier de cours existe pour reprendre les mêmes notations et citer le chapitre (« Cours chap. 1 »). Ne citer que ce qu'on a vraiment lu.
2. **Résoudre au brouillon, puis vérifier par le calcul** avec Python/sympy (`$PY`, avec sympy installé) : chaque résultat, chaque valeur intermédiaire, chaque exemple chiffré du corrigé. Aucun nombre dans le corrigé qui n'ait pas été recalculé. Si sympy et la main ne sont pas d'accord, trouver pourquoi avant d'écrire.
3. **Plan de la fiche** (une `<section class="sheet">` par page, le modèle fait 6 pages pour 4 questions) :
   - Page 1 : titre, encadré « L'énoncé », tableau « Ce que l'énoncé veut dire, en français simple » (question / en vrai on te demande / outil), note « L'idée en une phrase », vocabulaire à connaître (cartes vertes).
   - Par question : `h2` « n) … », note verte « 📗 Rappel du cours », étapes numérotées (`.step` + `.n`), calculs ligne par ligne (`.math`, résultats intermédiaires surlignés `.hl`), résultat dans `.box`, **vérification** (on remet dans l'énoncé), notes `.side` (« ← 3 × (−1) = −3 »), encadré `.piege` « ⚠ Les pièges ».
   - Dernière page : « À retenir » avec encadré `.oral` « 🎤 À l'oral, dis : » (la réponse rédigée comme on la dirait au prof) puis la fiche mémo (cartes vertes).
4. **Écrire** directement le fichier `.html` final (voir « Où ranger »). Jamais de fichier temporaire au nom générique (`body.html`…) : plusieurs corrigés peuvent tourner en parallèle et s'écraser. Si un brouillon est nécessaire, le nommer d'après l'exo (`exo3_brouillon.html`), puis `zsh ~/.claude/skills/math-corrige/build.sh <fichier.html>`.
5. **Regarder l'aperçu** (`_apercu.png`, puis zoom `pdftoppm -r 90 -f N -l N` sur les pages denses) : rien de coupé entre deux pages, pas de page à moitié vide sans raison, matrices lisibles. Corriger, relancer. Supprimer `_apercu.png` à la fin.
6. `open` le PDF et livrer : chemin du PDF + 2-3 lignes sur les résultats (pas de citation `>`).

## Règles d'écriture (le plus important)
- **Aucun saut d'étape.** Si on passe de `x₃ + 3t = 3` à `x₃ = 3 − 3t`, écrire pourquoi (« on passe 3t de l'autre côté, il change de signe »). Une ligne de calcul = une seule opération.
- Chaque mot technique expliqué la première fois en quelques mots (pivot, rang, gradient, Hessienne, multiplicateur de Lagrange…). Les formules du cours sont rappelées avant d'être utilisées.
- Toujours dire **pourquoi on fait** l'étape avant de la faire (« on commence par le bas parce que c'est la seule équation avec une seule inconnue »).
- Toujours une **vérification** concrète (remettre dans l'énoncé de départ, pas dans une version transformée) et, quand c'est utile, un exemple chiffré.
- Pièges : les vraies erreurs probables (signe devant une parenthèse, 0 oubliés, ordre des colonnes, condition oubliée…), pas des généralités.
- Couleurs : bleu = calcul, rouge = titres/résultats/pièges, vert = rappels et remarques, noir = énoncé. Surligneur jaune = résultat d'une étape, vert = ce qui confirme, rose = ce qui cloche.
- Pas de tiret long « — ». Notations mathématiques en Unicode (x₁, −, ×, ≤, ⟹, √, ², ∂) ; fractions avec `.fr`, matrices avec `.m`, déterminants avec `.d`, systèmes avec `.sys`.

## Où ranger
- Exo venant d'un fichier ou d'un dossier de cours : à côté de l'exo, nommé `<Nom de l'exo>_corrige.html` / `.pdf` (ex. `Exo 3 - systeme_corrige.pdf`).
- Exo collé sans contexte : dans un dossier `Corrigés maths/<AAAA-MM-JJ> - <titre court>/`.

## Si une vidéo suit (/maths-video)
Ce corrigé est la source de vérité de la vidéo : mêmes étapes, mêmes notations, mêmes nombres. Garder le HTML à jour si la vidéo révèle une explication à améliorer.
