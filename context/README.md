# Contexte projet — à lire avant toute session de travail

Émulateur de protocoles sur ASIC. Entrée au concours Jane Street.
**Deadline : 18 janvier 2027.**

## Lire dans cet ordre

| Fichier | Contenu | Quand le lire |
|---|---|---|
| **[01-competition.md](01-competition.md)** | Le brief, les contraintes dures, les critères de jugement, les questions en suspens | Une fois, en entier |
| **[02-decisions.md](02-decisions.md)** | Journal des décisions techniques et architecturales, avec leur *pourquoi* | Avant de remettre en cause quoi que ce soit |
| **[03-workflow.md](03-workflow.md)** | Commandes, layout des fichiers, pièges rencontrés | Au moment de coder |

Règle : **une décision structurante prise = une entrée dans `02-decisions.md`.**
Sans ça, la raison se perd et on la re-débat dans trois semaines.

## État au 16 septembre 2026

Milestone 1 **terminé** : un octet écrit sur `ui_in`, strobé par `uio_in[0]`, sort
de `uo_out[0]` en trame UART 8N1. 4 tests cocotb verts. La chaîne RTL → simulation
fonctionne en local.

| Mesure | Valeur |
|---|---|
| Aire UART TX (yosys générique, `-flatten`) | **104 cellules**, 23 flip-flops |
| Budget total | ~24 000 cellules (24 tiles × ~1K) |
| Occupation | **~0,4 %** |

Lecture : un UART figé ne coûte rien. Le budget partira intégralement dans le core
programmable — mémoire d'instructions, décodeur, compteurs de timing. C'est là que le
projet se gagne.

## Bloqué sur / prochaines actions

1. **Pousser sur GitHub** — le flow RTL → GDS → precheck → test gate-level ne tourne
   que dans les GitHub Actions. C'est le seul moyen d'obtenir une aire PDK réelle et
   de valider que 6x4 est accepté. Décision de Paul (dépôt public).
2. **Remplir le formulaire d'inscription** Jane Street — à faire par Paul. Ce n'est pas
   une formalité : c'est ce qui déclenche le mail si le 8x4 (+30 % d'aire) est débloqué,
   ce qui changerait l'architecture.
3. **Design de l'ISA** (semaines 2–3) — la décision structurante du projet. Rien de
   sérieux ne peut commencer avant.

## Planning

| Semaines | Objectif |
|---|---|
| 1 ✅ | Environnement + UART TX + première mesure d'aire |
| 2–3 | Design de l'ISA : spec + assembleur + simulateur (ISS) |
| 4–6 | Cœur RTL, co-simulé contre l'ISS |
| 7–9 | Firmware UART/SPI/I2C prouvé contre des modèles de référence |
| 10–12 | Tenir dans le budget : SRAM, synthèse, timing |
| 13–15 | Stretch (USB low-speed / mode sniffer) + preuves formelles |
| 16–17 | Write-up, démos, propreté du dépôt — la moitié de la note |
| 18 | Marge + soumission |
