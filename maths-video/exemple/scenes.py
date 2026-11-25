"""EXEMPLE COMPLET : Exo type, système 3 équations / 4 inconnues (système 3 équations / 4 inconnues).
Copier ce fichier dans <dossier>/_video_<nom>/scenes.py et l'adapter.
Rendu : python3 ~/.claude/skills/maths-video/engine/render.py <dossier>/_video_<nom> still
"""
from engine import *

OUTPUT = "../Exo 3 - systeme_video"
CHAPTERS = ["Intro", "Énoncé", "Q1 · matrice", "Q2 · infinité", "Q3 · x_4 = −1", "Q4 · x_4 = 1", "À retenir"]

# Pense-bête réutilisé à droite des scènes de calcul (le système reste sous les yeux)
def memo_sys(extra=()):
    return memo("Le système", [[("x_1 − x_2 = 1", {})], [("x_2 − x_3 = 1", {})], [("x_3 + 3x_4 = 3", {})], *extra], size=40)

# ============================================================ 00 intro
s = S("00_intro", chap=0)
t1 = T([("Corrigé : Question 3", {"k": "cav", "c": ROUGE})], X0 + 120, 250, size=150, kind="cav", dur=1.2)
u1 = Stroke([[(t1.x + 10, t1.bottom - 25), (t1.right - 10, t1.bottom - 32)]], ROUGE, 6, 0.6)
sub = T("Un système de 3 équations à 4 inconnues, expliqué pas à pas", X0 + 130, 480, size=52, color=NOIR)
tag = T([("Algèbre linéaire  ·  systèmes", {"c": VERT})], X0 + 130, 560, size=42)
chips = []
cx = X0 + 130
for i, l in enumerate(["1) forme matricielle", "2) infinité de solutions", "3) x_4 = −1", "4) x_4 = 1"]):
    c = T([(l, {"c": BLEU})], cx, 740, size=44, anim="pop", dur=0.4)
    chips.append([c, frame_box(c, BLEU, pad=6, seed=10 + i, dur=0.4, width=3)]); cx = c.right + 60
s.beat("Salut ! Dans cette vidéo, on corrige ensemble un exercice sur les systèmes d'équations.", t1, (0.5, u1), (0.6, sub))
s.beat("C'est un système de trois équations à quatre inconnues. On y va étape par étape, tranquillement.", tag)
s.beat("Il y a quatre questions : @a la forme matricielle, @b l'infinité de solutions, puis @c deux solutions @d précises.",
       ("@a", chips[0]), ("@b", chips[1]), ("@c", chips[2]), ("@d", chips[3]))

# ============================================================ 01 énoncé
s = S("01_enonce", chap=1)
ti = title("L'énoncé")
sysl = system(["x_1 − x_2 = 1", "x_2 − x_3 = 1", "x_3 + 3x_4 = 3"], X0 + 60, 250, size=60, color=NOIR)
q = [T([("1) ", {"c": ROUGE}), ("Écrire le système sous forme matricielle.", {})], X0, 560, size=46, color=NOIR),
     T([("2) ", {"c": ROUGE}), ("Montrer qu'il a une infinité de solutions.", {})], X0, 640, size=46, color=NOIR),
     T([("3) ", {"c": ROUGE}), ("Donner la solution unique quand x_4 = −1.", {})], X0, 720, size=46, color=NOIR),
     T([("4) ", {"c": ROUGE}), ("Donner la solution unique quand x_4 = 1.", {})], X0, 800, size=46, color=NOIR)]
s.beat("Voici l'énoncé.", ti)
s.beat("On a trois équations. @a x 1 moins x 2 égale 1. @b x 2 moins x 3 égale 1. @c Et x 3 plus 3 x 4 égale 3.",
       ("@a", sysl[0:2]), ("@b", sysl[2]), ("@c", sysl[3]))
s.beat("On nous demande quatre choses. @a Un : écrire ce système sous forme matricielle. @b Deux : montrer qu'il a une infinité de solutions.",
       ("@a", q[0]), ("@b", q[1]))
s.beat("@a Trois : donner la solution quand x 4 vaut moins 1. @b Et quatre : quand x 4 vaut 1.", ("@a", q[2]), ("@b", q[3]))

# ============================================================ 02 idée
s = S("02_idee", chap=1)
ti = title("L'idée en une phrase")
cd = card(X0, 230, 1560, 400, "note", "Avant de calculer")
l1 = T([("On a ", {}), ("4 inconnues", {"b": True}), (" mais seulement ", {}), ("3 équations", {"b": True}), (" (3 « règles »).", {})], X0 + 30, 320, size=48, color=VERT)
l2 = T("3 règles ne suffisent pas à bloquer 4 nombres : il en reste un qu'on choisit librement.", X0 + 30, 400, size=48, color=VERT)
l3 = T([("Une fois choisi, les 3 autres sont ", {}), ("forcés", {"b": True}), (".", {})], X0 + 30, 480, size=48, color=VERT)
ex = T([("Questions 3 et 4 = « je choisis x_4, je trouve les autres ».", {"c": BLEU})], X0, 700, size=52)
s.beat("Avant de calculer quoi que ce soit, voici l'idée générale.", ti, (0.4, cd))
s.beat("On a quatre inconnues, mais seulement trois équations. Donc trois règles.", l1)
s.beat("Et trois règles, ce n'est pas assez pour bloquer quatre nombres : il en reste un qu'on peut choisir librement.", l2)
s.beat("Une fois qu'on l'a choisi, les trois autres sont forcés.", l3, gap=0.9)
s.beat("Et les questions 3 et 4, c'est exactement ça : @a on choisit x 4, et on trouve les autres.", ex, ("@a", highlight(ex.boxes[0])))

# ============================================================ 03 Q1 rappel
s = S("03_q1_rappel", chap=2)
ti = title("1) La forme matricielle")
cd = card(X0, 220, 1560, 430, "note", "Rappel du cours : A · x = b")
r1 = T([("A", {"b": True}), (" = la matrice des coefficients : ", {}), ("une ligne par équation, une colonne par inconnue", {"b": True})], X0 + 30, 310, size=46, color=VERT)
r2 = T([("x", {"b": True}), (" = la colonne des inconnues", {})], X0 + 30, 390, size=46, color=VERT)
r3 = T([("b", {"b": True}), (" = la colonne de ce qu'il y a à droite du « = »", {})], X0 + 30, 470, size=46, color=VERT)
r4 = T([("Coefficient = le nombre devant une inconnue. Dans « 3x_4 », c'est 3. Absente → 0.", {"c": VERT})], X0 + 30, 560, size=40)
s.beat("Question 1 : la forme matricielle.", ti)
s.beat("Petit rappel du cours : tout système linéaire peut s'écrire A fois x égale b.", cd)
s.beat("A, c'est la matrice des coefficients : une ligne par équation, et une colonne par inconnue.", r1)
s.beat("x, c'est la colonne des inconnues. @a Et b, c'est la colonne de ce qu'il y a à droite du signe égal.", r2, ("@a", r3))
s.beat("Un coefficient, c'est simplement le nombre devant une inconnue. Dans 3 x 4, c'est 3. Et si l'inconnue n'apparaît pas, c'est zéro.", r4)

# ============================================================ 04 Q1 tableau
s = S("04_q1_tableau", chap=2)
ti = title("1) La forme matricielle")
st1 = step(1, [("On réécrit chaque équation avec ", {}), ("les 4 inconnues, dans l'ordre", {"b": True}), (" :", {})], X0, 200)
G = {"c": VERT, "b": True}
rows = [["Équation", "x_1", "x_2", "x_3", "x_4", "= b"],
        [[("x_1 − x_2 = 1", {"c": NOIR})], "1", "−1", [("0", G)], [("0", G)], "1"],
        [[("x_2 − x_3 = 1", {"c": NOIR})], [("0", G)], "1", "−1", [("0", G)], "1"],
        [[("x_3 + 3x_4 = 3", {"c": NOIR})], [("0", G)], [("0", G)], "1", "3", "3"]]
tb = table(rows, X0 + 40, 300, size=50, colw=[340, 130, 130, 130, 130, 140], rowh=86)
note = side("← les 0 en vert = les inconnues absentes : c'est eux qu'on oublie le plus souvent !", X0, 680)
s.beat("Premier réflexe : on réécrit chaque équation avec les quatre inconnues, dans l'ordre. @a x 1, x 2, x 3, x 4.", ti, (0.2, st1), ("@a", tb[0]))
s.beat("Première équation : @a x 1 moins x 2 égale 1. Devant x 1, il y a 1. Devant x 2, il y a moins 1. "
       "x 3 et x 4 n'apparaissent pas : @b on met zéro. Et à droite, 1.", ("@a", tb[1]), ("@b", circle(tb[1].cells[3], VERT, pad=4)))
s.beat("Deuxième équation : @a zéro, 1, moins 1, zéro. Et à droite, 1.", ("@a", tb[2]))
s.beat("Troisième équation : @a zéro, zéro, 1, 3. Et à droite, 3.", ("@a", tb[3]))
s.beat("Les zéros en vert, ce sont les inconnues absentes. C'est eux qu'on oublie le plus souvent, alors fais-y attention.", note)

# ============================================================ 05 Q1 matrice
s = S("05_q1_matrice", chap=2)
ti = title("1) La forme matricielle")
st2 = step(2, "On recopie le tableau : les 4 colonnes « x » donnent A, la dernière donne b.", X0, 200)
A = matrix([["1", "−1", "0", "0"], ["0", "1", "−1", "0"], ["0", "0", "1", "3"]], X0 + 260, 360, size=58, colw=50)
dot = T("·", A.right + 10, 400, size=70)
Xv = matrix([["x_1"], ["x_2"], ["x_3"], ["x_4"]], A.right + 60, 330, size=50, rowh=58)
eq = T("=", Xv.right + 18, 395, size=64)
Bv = matrix([["1"], ["1"], ["3"]], Xv.right + 80, 360, size=58)
fb = frame_box((A.x, Xv.y, Bv.right, Xv.bottom), pad=22, seed=5)
lab = [T([("A", {"c": ROUGE, "b": True})], A.x + A.w // 2 - 20, 620, size=50),
       T([("x", {"c": ROUGE, "b": True})], Xv.x + Xv.w // 2 - 14, 620, size=50),
       T([("b", {"c": ROUGE, "b": True})], Bv.x + Bv.w // 2 - 14, 620, size=50)]
sz = T([("A : 3 × 4 (3 lignes, 4 colonnes)     x : 4 × 1     b : 3 × 1", {"c": NOIR})], X0 + 120, 700, size=46)
v1 = T([("Vérif ligne 1 : ", {"c": VERT, "b": True}), ("1·x_1 + (−1)·x_2 + 0·x_3 + 0·x_4 = x_1 − x_2", {}), ("  → équation 1 ✓", {"c": VERT})], X0, 800, size=44)
v2 = T([("Pareil pour les lignes 2 et 3 : on retombe sur le système de départ ✓", {"c": VERT})], X0, 880, size=44)
s.beat("Maintenant, il suffit de recopier ce tableau.", ti, (0.3, st2))
s.beat("Les quatre colonnes des x donnent la matrice A. @a On la multiplie par la colonne des inconnues, x 1, x 2, x 3, x 4.", A, ("@a", [dot, Xv]))
s.beat("Et ça doit être égal à @a la colonne b : 1, 1, 3.", ("@a", [eq, Bv]), (0.8, fb))
s.beat("A a trois lignes et quatre colonnes : c'est une matrice 3 par 4. @a x a quatre lignes, et b en a trois.", lab, (0.3, sz))
s.beat("Petite vérification : si on multiplie la première ligne de A par x, on obtient x 1 moins x 2. C'est bien la première équation.", v1)
s.beat("Et pareil pour les deux autres lignes. Donc notre forme matricielle est juste.", v2)

# ============================================================ 06 Q1 pièges
s = S("06_q1_pieges", chap=2)
ti = title("1) Les pièges")
cd = card(X0, 230, 1560, 470, "piege", "⚠ Attention")
p1 = T([("· Oublier les 0 : ", {"b": True}), ("chaque ligne de A doit avoir 4 cases.", {})], X0 + 30, 320, size=48, color=ROUGE)
p2 = T([("· Le signe : ", {"b": True}), ("« x_1 − x_2 » c'est 1 et ", {}), ("−1", {"b": True}), (", pas 1 et 1.", {})], X0 + 30, 410, size=48, color=ROUGE)
p3 = T([("· L'ordre : ", {"b": True}), ("la colonne 4 de A, c'est toujours x_4.", {})], X0 + 30, 500, size=48, color=ROUGE)
p4 = T([("· Les tailles : ", {"b": True}), ("(3 × 4) · (4 × 1) = (3 × 1) = la taille de b ✓", {})], X0 + 30, 590, size=48, color=ROUGE)
s.beat("Attention aux pièges de cette question.", ti, (0.3, cd))
s.beat("Un : n'oublie pas les zéros. Chaque ligne de A doit avoir quatre cases, même si l'équation n'a que deux inconnues.", p1)
s.beat("Deux : le signe. x 1 moins x 2, c'est 1 et moins 1. Pas 1 et 1.", p2)
s.beat("Trois : l'ordre. La quatrième colonne, c'est toujours x 4, à chaque ligne.", p3)
s.beat("Et quatre : les tailles. 3 par 4, fois 4 par 1, ça donne 3 par 1. C'est bien la taille de b.", p4)

# ============================================================ 07 Q2 rappel
s = S("07_q2_rappel", chap=3)
ti = title("2) Une infinité de solutions ?")
cd = card(X0, 220, 1560, 560, "note", "Rappel du cours : combien de solutions ?")
c0 = T([("Un système a toujours ", {}), ("0, 1 ou une infinité", {"b": True}), (" de solutions. Jamais 2 ou 3 !", {})], X0 + 30, 310, size=48, color=VERT)
c1 = T("On le met en escalier (pivot de Gauss), puis :", X0 + 30, 390, size=48, color=VERT)
c2 = T([("· une ligne « 0 = un nombre non nul »  → ", {}), ("aucune", {"b": True}), (" solution", {})], X0 + 60, 470, size=48, color=VERT)
c3 = T([("· sinon, autant de pivots que d'inconnues  → ", {}), ("une seule", {"b": True})], X0 + 60, 550, size=48, color=VERT)
c4 = T([("· sinon, moins de pivots que d'inconnues  → ", {}), ("une infinité", {"b": True})], X0 + 60, 630, size=48, color=VERT)
s.beat("Question 2 : montrer que le système a une infinité de solutions.", ti)
s.beat("D'abord, un rappel du cours très important.", cd)
s.beat("Un système linéaire a toujours soit zéro, soit une, soit une infinité de solutions. Jamais deux, jamais trois.", c0)
s.beat("Pour savoir lequel, on met le système en escalier, avec le pivot de Gauss. Ensuite :", c1)
s.beat("S'il y a une ligne qui dit zéro égale un nombre non nul, c'est impossible : aucune solution.", c2)
s.beat("Sinon, s'il y a autant de pivots que d'inconnues : une seule solution.", c3)
s.beat("Et s'il y a moins de pivots que d'inconnues : @a une infinité de solutions.", c4, ("@a", highlight(c4.boxes[1], VERTF)), gap=1.0)

# ============================================================ 08 Q2 escalier
s = S("08_q2_escalier", chap=3)
ti = title("2) La matrice augmentée")
st1 = step(1, [("On écrit [A | b] : c'est A, avec la colonne b collée derrière une barre.", {})], X0, 200)
M = matrix([["1", "−1", "0", "0", "1"], ["0", "1", "−1", "0", "1"], ["0", "0", "1", "3", "3"]], X0 + 400, 310, size=62, colw=56, bar=4, rowh=88)
st2 = step(2, "Où commence chaque ligne ?", X0, 640)
lines = [T([("ligne 1 → colonne 1", {})], X0 + 60, 720, size=46),
         T([("ligne 2 → colonne 2", {}), ("   ← une marche plus à droite", {"k": "cav", "c": VERT})], X0 + 60, 790, size=46),
         T([("ligne 3 → colonne 3", {}), ("   ← encore une marche : c'est un escalier !", {"k": "cav", "c": VERT})], X0 + 60, 860, size=46)]
piv = [highlight(M.cells[(i, i)], JAUNE) for i in range(3)]
zer = [highlight(M.cells[c], VERTF) for c in [(1, 0), (2, 0), (2, 1)]]
stair = Stroke([[(M.cells[(0, 0)][0] - 4, M.cells[(0, 0)][3] + 2), (M.cells[(1, 1)][0] - 4, M.cells[(0, 0)][3] + 2),
                 (M.cells[(1, 1)][0] - 4, M.cells[(1, 1)][3] + 2), (M.cells[(2, 2)][0] - 4, M.cells[(1, 1)][3] + 2),
                 (M.cells[(2, 2)][0] - 4, M.cells[(2, 2)][3] + 4)]], ROUGE, 5, 1.2)
pv = side("← les 3 pivots", M.right + 30, 400, size=58, color=ROUGE)
s.beat("Pour répondre, on écrit la matrice augmentée : c'est la matrice A, avec la colonne b collée à droite, derrière une barre.", ti, (0.2, st1), (0.5, M))
s.beat("Maintenant, regarde où commence chaque ligne.", st2)
s.beat("La ligne 1 commence en @a colonne 1.", lines[0], ("@a", piv[0]))
s.beat("La ligne 2 commence en @a colonne 2 : une marche plus à droite.", lines[1], ("@a", piv[1]))
s.beat("Et la ligne 3 commence en @a colonne 3 : encore une marche. @b C'est un escalier !", lines[2], ("@a", piv[2]), ("@b", stair))
s.beat("Les zéros en bas à gauche sont déjà là. Donc ici, il n'y a aucun calcul de pivot de Gauss à faire.", zer)
s.beat("Les pivots, ce sont les premiers nombres non nuls de chaque ligne : ces trois 1 surlignés en jaune.", pv, gap=1.0)

# ============================================================ 09 Q2 deux tests
s = S("09_q2_tests", chap=3)
ti = title("2) Les deux tests")
M2 = matrix([["1", "−1", "0", "0", "1"], ["0", "1", "−1", "0", "1"], ["0", "0", "1", "3", "3"]], 1320, 210, size=48, colw=44, bar=4, rowh=66)
pv2 = [highlight(M2.cells[(i, i)], JAUNE) for i in range(3)]
t1a = step(1, [("Test 1 : une ligne « 0 0 0 0 | c » avec c ", {"b": True}), ("≠", {}), (" 0 ?", {"b": True})], X0, 220, size=42)
t1b = T([("Non : chaque ligne a un pivot. ", {}), ("✓ Au moins une solution.", {"c": VERT, "b": True})], X0 + 60, 290, size=42)
t2a = step(2, [("Test 2 : une inconnue libre (sans pivot) ?", {"b": True})], X0, 400, size=42)
tb2 = table([["Colonne", "x_1", "x_2", "x_3", "x_4"],
             ["pivot ?", [("oui", {"c": VERT})], [("oui", {"c": VERT})], [("oui", {"c": VERT})], [("non", {"c": ROUGE, "b": True})]]],
            X0 + 60, 470, size=44, colw=[200, 120, 120, 120, 120], rowh=70)
t2b = T([("3 pivots, 4 inconnues → ", {}), ("4 − 3 = 1 inconnue libre : x_4", {"b": True, "c": ROUGE})], X0 + 60, 630, size=44)
cc = card(X0, 730, 1560, 260, "note", "Conclusion")
cc1 = T([("Pas de contradiction ", {}), ("+", {"b": True}), (" une inconnue libre ⟹ ", {}), ("une infinité de solutions", {"b": True})], X0 + 30, 815, size=46, color=VERT)
cc2 = T("Version « prof » : rang(A) = rang([A | b]) = 3 < 4 inconnues", X0 + 30, 895, size=42, color=VERT)
s.beat("On fait maintenant deux tests.", ti, (0.4, M2), (0.8, pv2))
s.beat("Test numéro 1 : est-ce qu'il y a une contradiction ? C'est-à-dire une ligne avec que des zéros à gauche, et un nombre non nul à droite.", t1a)
s.beat("Non : chaque ligne a un pivot non nul à gauche de la barre. @a Donc le système a au moins une solution.", ("@a", t1b))
s.beat("Test numéro 2 : est-ce qu'il y a une inconnue libre, c'est-à-dire sans pivot ?", t2a)
s.beat("@a x 1 a un pivot. x 2 aussi. x 3 aussi. Mais @b x 4, non.", ("@a", tb2[0:2]), ("@b", circle(tb2[1].cells[4], ROUGE, pad=2)))
s.beat("Trois pivots pour quatre inconnues : il reste quatre moins trois, égale une inconnue libre. C'est x 4.", t2b)
s.beat("Conclusion : pas de contradiction, plus une inconnue libre, ça donne une infinité de solutions.", cc, (0.2, cc1), gap=0.9)
s.beat("En langage de prof, on dit : le rang de A égale le rang de la matrice augmentée, égale 3, et 3 est plus petit que 4, le nombre d'inconnues.", cc2)

# ============================================================ 10 Q2 toutes les solutions (avec pense-bête à droite)
s = S("10_q2_solutions", chap=3)
ti = title("2) Toutes les solutions")
mm = memo_sys()
a1 = step(1, [("On pose ", {}), ("x_4 = t", {"b": True}), (" (t = n'importe quel réel)", {})], X0, 200)
a1n = side("← un curseur", a1[1].right + 12, 196)
a2 = step(2, [("On remonte l'escalier, ", {}), ("en partant du bas", {"b": True}), (" :", {})], X0, 280)
# Équation 3, révélée morceau par morceau
e3 = row([T([("Éq. 3 : ", {"c": VERT})], 0, 0, size=48), T("x_3 + 3t = 3", 0, 0, size=48), T("→", 0, 0, size=48),
          T([("x_3 = 3 − 3t", {"b": True})], 0, 0, size=48)], X0 + 60, 400, gap=14)
e3n = T([("(3t passe de l'autre côté : il change de signe)", {"c": VERT})], X0 + 120, 445, size=36)
e2 = row([T([("Éq. 2 : ", {"c": VERT})], 0, 0, size=48), T("x_2 = 1 + x_3 = 1 + (3 − 3t)", 0, 0, size=48), T("→", 0, 0, size=48),
          T([("x_2 = 4 − 3t", {"b": True})], 0, 0, size=48)], X0 + 60, 560, gap=14)
e1 = row([T([("Éq. 1 : ", {"c": VERT})], 0, 0, size=48), T("x_1 = 1 + x_2 = 1 + (4 − 3t)", 0, 0, size=48), T("→", 0, 0, size=48),
          T([("x_1 = 5 − 3t", {"b": True})], 0, 0, size=48)], X0 + 60, 680, gap=14)
res = T([("(x_1, x_2, x_3, x_4) = (5 − 3t, 4 − 3t, 3 − 3t, t)", {})], X0 + 60, 790, size=56)
res2 = T([("pour tout réel t", {"c": NOIR})], X0 + 420, 870, size=44)
fbr = frame_box((res.x, res.y, res.right, res2.bottom), pad=16, seed=8, dur=0.9)
s.beat("Pour le prouver concrètement, on va écrire toutes les solutions. Garde le système sous les yeux, à droite.", ti, (0.6, mm))
s.beat("On pose @a x 4 égale t, où t est n'importe quel nombre réel. @b Imagine un curseur que tu peux bouger comme tu veux.", ("@a", a1), ("@b", a1n))
s.beat("Ensuite, on remonte l'escalier, en partant du bas. C'est là qu'il n'y a qu'une seule inconnue en plus de t.", a2, (0.5, circle(mm[3], ROUGE, pad=2)))
s.beat("Équation 3 : @a x 3 plus 3 t égale 3. @b On passe 3 t de l'autre côté, il change de signe : @c x 3 égale 3 moins 3 t.",
       ("@a", e3[0:2]), ("@b", e3n), ("@c", [e3[2], e3[3], highlight(e3[3])]))
s.beat("Équation 2 : @a x 2 égale 1 plus x 3. On remplace x 3 : 1 plus 3 moins 3 t. @b Donc x 2 égale 4 moins 3 t.",
       ("@a", e2[0:2]), ("@b", [e2[2], e2[3], highlight(e2[3])]))
s.beat("Équation 1 : @a x 1 égale 1 plus x 2. On remplace : 1 plus 4 moins 3 t. @b Donc x 1 égale 5 moins 3 t.",
       ("@a", e1[0:2]), ("@b", [e1[2], e1[3], highlight(e1[3])]))
s.beat("On rassemble tout. @a Les solutions s'écrivent : 5 moins 3 t, 4 moins 3 t, 3 moins 3 t, et t. @b Pour tout réel t.",
       ("@a", res), ("@b", [res2, fbr]), gap=1.2)

# ============================================================ 11 Q2 vérif + exemples
s = S("11_q2_verif", chap=3)
ti = title("2) On vérifie")
v1 = T([("x_1 − x_2 = (5 − 3t) − (4 − 3t) = 5 ", {}), ("− 3t", {}), (" − 4 ", {}), ("+ 3t", {}), (" = ", {}), ("1", {"b": True}), (" ✓", {"c": VERT})], X0, 210, size=46)
v1n = side("← les t s'annulent !", v1.right + 10, 205, size=52)
v2 = T([("x_2 − x_3 = (4 − 3t) − (3 − 3t) = ", {}), ("1", {"b": True}), (" ✓", {"c": VERT})], X0, 285, size=46)
v3 = T([("x_3 + 3x_4 = (3 − 3t) + 3t = ", {}), ("3", {"b": True}), (" ✓", {"c": VERT})], X0, 360, size=46)
tb = table([["t", "(x_1, x_2, x_3, x_4)", "x_1 − x_2", "x_2 − x_3", "x_3 + 3x_4"],
            ["0", "(5, 4, 3, 0)", "1 ✓", "1 ✓", "3 ✓"],
            ["2", "(−1, −2, −3, 2)", "1 ✓", "1 ✓", "−3 + 6 = 3 ✓"]], X0, 470, size=42, rowh=72)
cl = T([("Chaque t donne une solution différente, et il y a une infinité de t ⟹ ", {}), ("infinité de solutions ✓", {"b": True, "c": VERT})], X0, 720, size=44)
pg = card(X0, 810, 1560, 180, "piege", "⚠ Piège")
pg1 = T("« 3 équations, 4 inconnues » ne suffit pas ! Il faut aussi : pas de contradiction.", X0 + 30, 890, size=44, color=ROUGE)
s.beat("On vérifie cette formule dans les trois équations, avec t quelconque.", ti)
s.beat("x 1 moins x 2 : 5 moins 3 t, moins 4, plus 3 t. Attention, le moins devant la parenthèse change les signes. "
       "@a Moins 3 t et plus 3 t s'annulent, @b il reste 1. Parfait.",
       v1, ("@a", [strike(v1.boxes[1]), strike(v1.boxes[3]), v1n]), ("@b", highlight(v1.boxes[5])))
s.beat("x 2 moins x 3 : même chose, il reste 1.", v2)
s.beat("Et x 3 plus 3 x 4 : 3 moins 3 t, plus 3 t, ça fait 3. Les trois équations marchent, quel que soit t.", v3, gap=0.9)
s.beat("Quelques exemples. @a Avec t égale zéro, on obtient 5, 4, 3, zéro.", tb[0], ("@a", tb[1]))
s.beat("Avec t égale 2 : moins 1, moins 2, moins 3, et 2. Ça marche aussi.", tb[2])
s.beat("Chaque valeur de t donne une solution différente, et il y a une infinité de valeurs possibles pour t. Donc il y a une infinité de solutions.", cl)
s.beat("Et attention au piège : dire seulement trois équations, quatre inconnues, donc infinité, ça ne suffit pas. Il faut aussi montrer qu'il n'y a pas de contradiction.", pg, (0.2, pg1))

# ============================================================ 12 Q3 (calcul pas à pas + pense-bête)
s = S("12_q3", chap=4)
ti = title("3) La solution pour x_4 = −1")
mm = memo_sys([[("x_4 = −1", {"c": ROUGE, "b": True})]])
i0 = T([("On remonte l'escalier, du bas vers le haut :", {"c": VERT})], X0, 200, size=44)
n1 = num(1, X0, 296); a = row([T("Éq. 3 :", 0, 0, size=46, color=VERT), T("x_3 + 3 × (−1) = 3", 0, 0, size=46), T("→", 0, 0, size=46),
                              T("x_3 − 3 = 3", 0, 0, size=46), T("→", 0, 0, size=46), T([("x_3 = 6", {"b": True})], 0, 0, size=46)], X0 + 60, 320, gap=12)
a_n = side("3 × (−1) = −3", a[1].x + 60, a[1].bottom - 8, size=40)
n2 = num(2, X0, 446); b = row([T("Éq. 2 :", 0, 0, size=46, color=VERT), T("x_2 = 1 + x_3 = 1 + 6", 0, 0, size=46), T("→", 0, 0, size=46),
                              T([("x_2 = 7", {"b": True})], 0, 0, size=46)], X0 + 60, 470, gap=12)
n3 = num(3, X0, 556); c = row([T("Éq. 1 :", 0, 0, size=46, color=VERT), T("x_1 = 1 + x_2 = 1 + 7", 0, 0, size=46), T("→", 0, 0, size=46),
                              T([("x_1 = 8", {"b": True})], 0, 0, size=46)], X0 + 60, 580, gap=12)
r = T("(x_1, x_2, x_3, x_4) = (8, 7, 6, −1)", X0 + 140, 670, size=60)
rb = frame_box(r, pad=16, seed=12)
vv = T([("Vérif : ", {"b": True}), ("8 − 7 = 1 ✓    7 − 6 = 1 ✓    6 + 3 × (−1) = 3 ✓", {})], X0, 800, size=44)
un = T([("« Unique » : une fois x_4 fixé, plus d'inconnue libre, tout le reste est forcé.", {"c": VERT})], X0, 880, size=40)
s.beat("Question 3 : on impose x 4 égale moins 1.", ti, (0.5, mm))
s.beat("On remonte l'escalier, du bas vers le haut.", i0)
s.beat("Équation 3 : @a x 3 plus 3 fois moins 1 égale 3. @b Trois fois moins 1, ça fait moins 3. @c Donc x 3 moins 3 égale 3, @d et x 3 égale 6.",
       ("@a", [n1, a[0], a[1]]), ("@b", a_n), ("@c", [a[2], a[3]]), ("@d", [a[4], a[5], highlight(a[5])]))
s.beat("Équation 2 : @a x 2 égale 1 plus x 3, donc 1 plus 6 : @b x 2 égale 7.", ("@a", [n2, b[0], b[1]]), ("@b", [b[2], b[3], highlight(b[3])]))
s.beat("Équation 1 : @a x 1 égale 1 plus x 2, donc 1 plus 7 : @b x 1 égale 8.", ("@a", [n3, c[0], c[1]]), ("@b", [c[2], c[3], highlight(c[3])]))
s.beat("La solution, c'est donc @a 8, 7, 6, moins 1.", ("@a", [r, rb]), gap=1.2)
s.beat("On vérifie dans l'énoncé : 8 moins 7, 1. 7 moins 6, 1. 6 moins 3, 3. Tout est bon.", vv)
s.beat("Et pourquoi l'énoncé dit unique ? Parce qu'une fois x 4 fixé, il n'y a plus aucune inconnue libre. Tout le reste est forcé : une seule possibilité.", un)

# ============================================================ 13 Q4
s = S("13_q4", chap=5)
ti = title("4) La solution pour x_4 = 1")
mm = memo_sys([[("x_4 = 1", {"c": ROUGE, "b": True})]])
n1 = num(1, X0, 216); a = row([T("Éq. 3 :", 0, 0, size=46, color=VERT), T("x_3 + 3 × 1 = 3", 0, 0, size=46), T("→", 0, 0, size=46),
                              T([("x_3 = 0", {"b": True})], 0, 0, size=46)], X0 + 60, 240, gap=12)
a_n = side("← 0, c'est normal !", a[3].right + 14, 212)
n2 = num(2, X0, 336); b = row([T("Éq. 2 :", 0, 0, size=46, color=VERT), T("x_2 = 1 + x_3 = 1 + 0", 0, 0, size=46), T("→", 0, 0, size=46),
                              T([("x_2 = 1", {"b": True})], 0, 0, size=46)], X0 + 60, 360, gap=12)
n3 = num(3, X0, 456); c = row([T("Éq. 1 :", 0, 0, size=46, color=VERT), T("x_1 = 1 + x_2 = 1 + 1", 0, 0, size=46), T("→", 0, 0, size=46),
                              T([("x_1 = 2", {"b": True})], 0, 0, size=46)], X0 + 60, 480, gap=12)
r = T("(x_1, x_2, x_3, x_4) = (2, 1, 0, 1)", X0 + 160, 580, size=60)
rb = frame_box(r, pad=16, seed=14)
vv = T([("Vérif : ", {"b": True}), ("2 − 1 = 1 ✓    1 − 0 = 1 ✓    0 + 3 × 1 = 3 ✓", {})], X0, 720, size=44)
ff = T([("Formule, t = 1 : ", {"c": VERT}), ("(5 − 3, 4 − 3, 3 − 3, 1) = (2, 1, 0, 1)", {}), ("  pareil ✓", {"k": "cav", "c": VERT})], X0, 810, size=42)
s.beat("Question 4 : cette fois, x 4 égale 1. Même méthode.", ti, (0.5, mm))
s.beat("Équation 3 : @a x 3 plus 3 égale 3, @b donc x 3 égale zéro. @c Et oui, zéro, c'est un résultat tout à fait normal, ce n'est pas une erreur.",
       ("@a", [n1, a[0], a[1]]), ("@b", [a[2], a[3], highlight(a[3])]), ("@c", a_n))
s.beat("Équation 2 : @a x 2 égale 1 plus zéro, @b donc 1.", ("@a", [n2, b[0], b[1]]), ("@b", [b[2], b[3], highlight(b[3])]))
s.beat("Équation 1 : @a x 1 égale 1 plus 1, @b donc 2.", ("@a", [n3, c[0], c[1]]), ("@b", [c[2], c[3], highlight(c[3])]))
s.beat("La solution est @a 2, 1, zéro, 1.", ("@a", [r, rb]), gap=1.2)
s.beat("Vérification : 2 moins 1, 1. 1 moins zéro, 1. Zéro plus 3, 3. Parfait.", vv)
s.beat("Et si on utilise la formule de la question 2 avec t égale 1, on retrouve exactement la même chose.", ff)

# ============================================================ 14 récap
s = S("14_recap", chap=6)
ti = title("À retenir : 3 réflexes")
k1 = step(1, [("Mettre des ", {}), ("0", {"b": True}), (" pour les inconnues absentes", {}), ("   (question 1)", {"c": VERT})], X0, 230, size=52)
k2 = step(2, [("Compter ", {}), ("pivots", {"b": True}), (" et ", {}), ("inconnues", {"b": True}), (" : moins de pivots → infinité", {}), ("   (question 2)", {"c": VERT})], X0, 340, size=52)
k3 = step(3, [("Remonter l'escalier ", {}), ("depuis le bas", {"b": True}), ("   (questions 3 et 4)", {"c": VERT})], X0, 450, size=52)
orc = card(X0, 600, 1560, 330, "oral", "Pour t'entraîner")
o1 = T("1. Prends une feuille et refais l'exo au stylo.", X0 + 30, 690, size=46, color=NOIR)
o2 = T("2. Bloqué ? Reviens juste au chapitre qui coince (barre en bas).", X0 + 30, 760, size=46, color=NOIR)
o3 = T("3. Le corrigé papier reprend tout, étape par étape.", X0 + 30, 830, size=46, color=NOIR)
s.beat("Pour finir, retiens trois réflexes.", ti)
s.beat("Un : mettre des zéros pour les inconnues absentes. C'est la question 1.", k1)
s.beat("Deux : compter les pivots et les inconnues. S'il y a moins de pivots que d'inconnues, et pas de contradiction, il y a une infinité de solutions.", k2)
s.beat("Trois : remonter l'escalier en partant du bas.", k3, gap=1.0)
s.beat("Pour t'entraîner, @a prends une feuille et refais l'exercice au stylo.", orc, ("@a", o1))
s.beat("Si tu bloques, reviens juste au chapitre qui coince. @a Et le corrigé papier reprend tout, étape par étape. Bon courage !", o2, ("@a", o3))
