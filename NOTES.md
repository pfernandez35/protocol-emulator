# Protocol Emulator — carnet de bord

Concours ASIC Jane Street. Deadline : **18 janvier 2027**.
Source : https://blog.janestreet.com/protocol-emulator-asic-competition/

## Contraintes fermes

| | |
|---|---|
| Process | IHP 130nm CMOS5L (`ihp-sg13cmos5l`) via Tiny Tapeout |
| Aire | 6x4 tiles ≈ 0,7 mm². Budget ≈ **1K cellules logiques / tile** → ~24K cellules |
| Template | `TinyTapeout/ttihp-verilog-template` branche `cmos5l` |
| Licence | Open source obligatoire |
| Jugement | Fonctionnalité originale + méthodologie de design/vérification originale |
| Prix | Tape-out payé (navette mars 2027) + puce physique sur dev board |

## Questions ouvertes

- [ ] **6x4 est-il réellement accepté ?** Le commentaire de `info.yaml` en amont ne liste
      que `1x1, 1x2, 2x2, 3x2, 4x2, 6x2, 8x2`. Le blog dit explicitement 6x4. On a mis
      6x4 ; **la CI est l'arbitre** — le job `precheck` le dira. Si ça casse, écrire à
      asic-competition@janestreet.com.
- [ ] **8x4 (+30% d'aire)** est « à l'étude ». Ils préviendront par mail les inscrits.
      → raison concrète de remplir le formulaire d'inscription.
- [ ] **Fréquence d'horloge max** sur ce nœud/cette carte. On a supposé 50 MHz dans
      `info.yaml`. À confirmer : c'est ce qui fixe la résolution temporelle du chip,
      donc le débit max des protocoles. Détermine si USB low-speed (1,5 Mbit/s) et
      Ethernet 10M sont atteignables.
- [ ] **Inscription** au formulaire Google (à faire par Paul — données perso).

## Décisions prises

- **Verilog**, pas Hardcaml. Hardcaml aurait flatté les juges (c'est leur outil) mais
  ajoute une couche d'apprentissage OCaml sur un projet déjà dense.
- **Top module** : `tt_um_pfernandez35_protoemu`.
- **Milestone 1 = UART TX en dur.** Ce n'est *pas* l'architecture finale : c'est un
  étalon d'aire et une preuve que la chaîne RTL → GDS tourne. Le bloc doit disparaître,
  remplacé par du firmware sur le core.

## Direction architecturale proposée (à valider)

Les juges veulent de la **nouveauté**, pas un clone de PIO en plus petit. Deux axes :

1. **Écouter, pas seulement parler.** Jane Street dit que leur usage est « le debug
   hardware et le reverse engineering ». Un core qui sait *sniffer et auto-identifier*
   un protocole inconnu (capture d'edges horodatée, auto-baud, classification
   UART/SPI/I2C à la volée) répond à leur besoin déclaré et n'existe ni dans le PIO
   du RP2040 ni dans les PRU de TI.
2. **La vérification comme produit.** ISS cycle-accurate + fuzzer différentiel
   RTL ↔ ISS + propriétés formelles SymbiYosys sur les instructions de timing. Ils
   citent nommément « formal methods, random constrained tests, AI-assisted
   verification » comme critère de jugement.

## Mesures

### Milestone 1 — UART TX en dur (16 sept 2026)

Synthèse générique yosys (`synth -flatten`, sans PDK) :

| | |
|---|---|
| Cellules | **104** |
| Flip-flops | **23** (cnt 9b + bit_idx 4b + frame 8b utiles + tx + active) |
| Budget total | ~24 000 cellules (24 tiles × ~1K) |
| **Occupation** | **~0,4 %** |

Lecture : un UART figé ne coûte rien. Tout le budget part dans le core programmable —
instruction memory, décodeur, ALU, compteurs de timing. C'est là que se joue le projet.
Chiffre à re-mesurer contre le vrai PDK via la CI (les cellules génériques ≠ cellules
standard IHP), mais l'ordre de grandeur est bon.

## Pièges rencontrés

- Ajouter un fichier source demande **deux** éditions : `info.yaml:source_files` **et**
  `test/Makefile:PROJECT_SOURCES`. Oublier la seconde donne une erreur d'élaboration
  obscure.
- cocotb 2.x utilise `unit=` (singulier), plus `units=`.
- Écrire un testbench UART avec `0xAA` est un piège : le bit de start (0) et `data[0]`
  (0) fusionnent en un seul palier, ce qui fausse toute mesure de largeur de bit.
  Utiliser `0x55`, qui alterne sur chaque slot.

## Commandes

```bash
# Simulation RTL
cd test && PATH=../.venv/bin:$PATH make -B

# Voir les ondes
gtkwave test/tb.fst    # ou: surfer test/tb.fst

# Estimation d'aire (synthèse générique, sans PDK)
yosys -p "read_verilog src/*.v; synth -top tt_um_pfernandez35_protoemu; stat"
```
