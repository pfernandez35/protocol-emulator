# Workflow

## Layout

```
src/
  project.v          Top level. Doit s'appeler tt_um_pfernandez35_protoemu.
  uart_tx.v          UART 8N1 figé — jetable par construction (ADR-003).
test/
  Makefile           PROJECT_SOURCES doit lister chaque fichier de src/.
  tb.v               Wrapper Verilog instanciant le top. Dump les ondes en FST.
  test.py            Tests cocotb.
info.yaml            Métadonnées Tiny Tapeout : tiles, pinout, source_files.
docs/info.md         Datasheet PUBLIÉE par Tiny Tapeout. En anglais. Ne pas confondre
                     avec context/, qui est interne.
context/             Ce dossier. Interne, français.
.github/workflows/   gds · test · docs · fpga (le vrai flow ASIC est ici)
```

## Commandes

```bash
# Simulation RTL — le boulot quotidien
cd test && PATH=../.venv/bin:$PATH make -B

# Voir les ondes
gtkwave test/tb.fst        # ou: surfer test/tb.fst

# Estimation d'aire, sans PDK (rapide, ordre de grandeur)
yosys -p "read_verilog src/*.v; synth -top tt_um_pfernandez35_protoemu -flatten; stat"

# Aire PDK réelle, precheck 6x4, test gate-level → uniquement en CI, sur push
```

Environnement local : `.venv/` (cocotb 2.0.1, pytest), `iverilog` et `yosys` via Homebrew.
Tout le reste du flow ASIC tourne dans les GitHub Actions — rien à installer.

## Le flow CI

Un `git push` déclenche `.github/workflows/gds.yaml` :

| Job | Ce qu'il donne |
|---|---|
| `gds` | Synthèse + place & route → GDS. **L'aire PDK réelle.** |
| `precheck` | Vérifs de conformité Tiny Tapeout. **C'est lui qui tranchera le 6x4** (ADR-002). |
| `gl_test` | Rejoue les tests cocotb contre le netlist post-synthèse. Passe tel quel grâce à ADR-004. |
| `viewer` | Publie une vue du layout sur GitHub Pages. |

`fpga.yaml` produit un bitstream ICE40UP5K mais ne tourne pas sur push (`branches: none`).
À activer si une carte compatible est disponible — le blog recommande de tester sur FPGA
avant le flow ASIC.

## Pièges rencontrés

**Ajouter un fichier source demande deux éditions.** `info.yaml:source_files` **et**
`test/Makefile:PROJECT_SOURCES`. Oublier la seconde donne une erreur d'élaboration
obscure, sans rapport apparent avec la cause.

**cocotb 2.x utilise `unit=`, pas `units=`.** Le pluriel est l'API 1.x. Les exemples
qui traînent en ligne sont majoritairement en 1.x.

**Tester un UART avec `0xAA` est un piège.** Trame émise LSB first :
`{stop, data, start}`. Avec `0xAA`, le bit de start (0) et `data[0]` (0) sont au même
niveau et **fusionnent en un seul palier** de deux temps-bit — toute mesure de largeur de
bit est alors fausse. Utiliser **`0x55`**, dont la trame alterne sur chaque slot
(`0,1,0,1,0,1,0,1,0,1`), ce qui rend chaque bit mesurable isolément.

**Il faut attendre `busy == 0` entre deux octets.** Pas de registre shadow (ADR-006).
Strobé pendant `busy`, `load` est ignoré silencieusement — le test échoue plus loin, sur
une absence de start bit, à un endroit qui ne désigne pas la cause. Helper `wait_idle()`
dans `test.py`.

**Le dépôt a été cloné depuis le template.** Le remote `origin` a été renommé `upstream`
pour éviter un push accidentel vers TinyTapeout. Un `origin` reste à créer.

## Conventions

- Un fichier `src/*.v` = un module, même nom.
- Tout test observe les pins, jamais l'état interne (ADR-004).
- Toute assertion de timing est exacte, jamais tolérante (ADR-005).
- Une décision structurante prise = une entrée dans `02-decisions.md`, avec son pourquoi.
