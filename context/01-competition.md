# Le concours

Source : https://blog.janestreet.com/protocol-emulator-asic-competition/ (10 sept. 2026)
Contact : `asic-competition@janestreet.com`

## Ce qui est demandé

Concevoir un **émulateur de protocoles généraliste et open source** : un micro-CPU dont
le jeu d'instructions est taillé pour lire des pins, écrire des pins, compter des cycles
et tenir un timing au cycle près — de sorte qu'un protocole s'implémente **en firmware**,
pas en logique figée.

> « The goal isn't to put a UART block, an SPI block, and an I2C block on one die and
> call it done. »

La puce doit rester **reprogrammable après fabrication**, dans ses limites de timing et
d'I/O. Références citées : les state machines PIO du RP2040, les cores PRU des TI Sitara
— « et ce que vous feriez différemment ».

- **Minimum** : UART, SPI, I2C
- **Stretch** : USB low-speed, Ethernet 10 Mbit
- **Bonus évoqués** : JTAG, SWD, PS/2, CAN

## Contraintes dures

| | |
|---|---|
| Process | IHP 130nm CMOS5L (`ihp-sg13cmos5l`) via [Tiny Tapeout](https://www.tinytapeout.com/) |
| Template | [`TinyTapeout/ttihp-verilog-template`](https://github.com/TinyTapeout/ttihp-verilog-template/tree/cmos5l) branche `cmos5l` |
| Aire | **6x4 tiles** ≈ 0,7 mm² ; budget ≈ **1K cellules logiques / tile** → ~24 000 cellules |
| Licence | Open source obligatoire. Développement public encouragé (pas de secret à tenir) |
| Équipes | Fortement recommandées |
| Deadline | **18 janvier 2027** |
| Outils | Tous gratuits et open source |

Aucune règle n'interdit l'usage de l'IA. Au contraire — voir critères ci-dessous.

## Critères de jugement

Textuellement, ils cherchent :

1. Une **fonctionnalité originale** (« unique functionality »)
2. Des **approches originales de design et de vérification** — ils citent nommément
   « formal methods, random constrained tests, **AI-assisted verification** »

> « As AI-assisted chip design becomes more common, we believe verification will be an
> extremely important aspect of the ASIC design flow going forwards. »

**Conséquence directe sur la stratégie** : la vérification n'est pas une corvée de fin de
projet, c'est un **livrable jugé**. Un design plus modeste avec une méthodologie de vérif
remarquable bat un design ambitieux mal vérifié. Voir ADR-007.

## Prix

Jane Street paie le tape-out des designs les plus originaux sur une navette Tiny Tapeout,
cible **mars 2027** (sous réserve du planning de la fonderie). Les gagnants reçoivent la
puce fabriquée, montée sur une dev board.

## Questions en suspens

- [ ] **6x4 est-il réellement accepté par les outils ?** Le commentaire de `info.yaml` en
      amont ne liste que `1x1, 1x2, 2x2, 3x2, 4x2, 6x2, 8x2`. Le blog impose 6x4. On a mis
      6x4 (ADR-002). **La CI est l'arbitre** — le job `precheck` tranchera. Si ça casse :
      mail à `asic-competition@janestreet.com`.
- [ ] **8x4 (+30 % d'aire)** est « à l'étude ». Ils préviendront par mail **les inscrits**.
      → raison concrète de remplir le formulaire d'inscription, au-delà de la formalité.
- [ ] **Fréquence d'horloge max** sur ce nœud. On a supposé 50 MHz (ADR-008). C'est ce qui
      fixe la résolution temporelle, donc le débit max atteignable, donc si USB low-speed
      (1,5 Mbit/s) et Ethernet 10M sont réalistes. **À confirmer avant de figer l'ISA.**
- [ ] **Formulaire d'inscription** : pas encore rempli. À faire par Paul (données perso).
      https://docs.google.com/forms/d/e/1FAIpQLSeF7fq756MegxZRQxotBwUJYZx-cL9MrGjxV0z4uD_J0sADxQ/viewform
- [ ] Le lien de **soumission finale** sera ajouté sur la page du blog plus tard.

## Ressources

- Documentation Tiny Tapeout : https://www.tinytapeout.com/
- Exemple de SRAM sur ce nœud : https://www.tinytapeout.com/chips/ttihp0p2/tt_um_urish_sram_test
- Hardcaml (leur outil maison, non obligatoire) : https://hardcaml.org/
