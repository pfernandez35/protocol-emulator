# Protocol Emulator — instructions projet

## À lire AVANT toute intervention sur ce dépôt

**Lis `context/README.md`, puis les fichiers qu'il indique.** Ce n'est pas optionnel :
ce projet a des contraintes non devinables depuis le code seul — un budget d'aire dur,
une deadline de concours, des critères de jugement qui orientent l'architecture, et des
décisions déjà prises dont le *pourquoi* n'est écrit nulle part ailleurs.

| Fichier | Contenu |
|---|---|
| `context/README.md` | Carte du projet, état actuel, prochaines actions |
| `context/01-competition.md` | Le brief, les contraintes dures, les critères de jugement |
| `context/02-decisions.md` | Journal des décisions techniques et architecturales (ADR) |
| `context/03-workflow.md` | Commandes, layout, pièges déjà rencontrés |

## Le contexte en une phrase

Concevoir un ASIC open source : un micro-CPU programmable qui bit-bang des protocoles
matériels (UART/SPI/I2C) en firmware plutôt qu'en logique figée, dans **~24 000 cellules**,
pour le concours Jane Street, **deadline 18 janvier 2027**. Jugé sur la **nouveauté
fonctionnelle** et sur la **méthodologie de vérification**.

## Règles de travail

1. **Consigner les décisions.** Une décision structurante prise = une entrée dans
   `context/02-decisions.md`, au format des existantes (Contexte / Décision / Pourquoi /
   Conséquence). Sans le pourquoi, la décision sera re-débattue dans trois semaines.
2. **Ne pas contredire un ADR sans le dire.** S'il faut revenir sur une décision, changer
   son statut en `Remplacée` et en écrire une nouvelle. Ne jamais réécrire l'historique.
3. **Tester par les pins, jamais par l'état interne** (ADR-004). La suite de tests doit
   rester rejouable telle quelle contre le netlist post-synthèse.
4. **Les assertions de timing sont exactes, jamais tolérantes** (ADR-005). La précision
   temporelle est la raison d'être de la puce.
5. **Surveiller le budget d'aire à chaque ajout notable.**
   `yosys -p "read_verilog src/*.v; synth -top tt_um_pfernandez35_protoemu -flatten; stat"`
   Repère : l'UART TX figé = 104 cellules, soit 0,4 % du budget.
6. **Ajouter un fichier source demande deux éditions** : `info.yaml:source_files` **et**
   `test/Makefile:PROJECT_SOURCES`. Oublier la seconde donne une erreur incompréhensible.
7. **`docs/` appartient à Tiny Tapeout** (datasheet publiée, en anglais). La doc interne
   va dans `context/`, en français. Ne pas mélanger.

## Ce qui relève de Paul, pas de l'assistant

- Créer le dépôt public et pousser (le dépôt doit être open source, mais c'est sa décision).
- Remplir le formulaire d'inscription Jane Street (données personnelles).
- Trancher les ADR marqués **Proposé** — notamment 007 (stratégie de vérification) et
  009 (axe de nouveauté), qui engagent le design de l'ISA.
