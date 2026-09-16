# Journal des décisions

Format : une décision structurante = une entrée. On garde les décisions **abandonnées**
aussi (statut `Remplacée`), parce que savoir ce qu'on a écarté et pourquoi évite de le
re-proposer dans deux mois.

| # | Décision | Statut |
|---|---|---|
| [001](#adr-001--verilog-plutôt-que-hardcaml) | Verilog plutôt que Hardcaml | Accepté |
| [002](#adr-002--tiles--6x4-malgré-le-template) | `tiles: 6x4` malgré le template | Accepté, à valider en CI |
| [003](#adr-003--le-milestone-1-est-jetable-par-construction) | Milestone 1 jetable par construction | Accepté |
| [004](#adr-004--les-tests-décodent-la-pin-jamais-létat-interne) | Tests via les pins, jamais l'état interne | Accepté |
| [005](#adr-005--le-timing-est-asserté-dès-le-premier-jour) | Timing asserté dès le jour 1 | Accepté |
| [006](#adr-006--pas-de-registre-shadow-sur-luart-tx) | Pas de registre shadow sur l'UART TX | Accepté, portée locale |
| [007](#adr-007--la-vérification-est-un-livrable-pas-une-corvée) | La vérification est un livrable | **Proposé** |
| [008](#adr-008--horloge-supposée-à-50-mhz) | Horloge à 50 MHz | **Provisoire** |
| [009](#adr-009--axe-de-nouveauté--écouter-pas-seulement-parler) | Axe de nouveauté : écouter, pas seulement parler | **Proposé** |
| [010](#adr-010--docs-internes-en-français-code-et-docs-publiques-en-anglais) | Docs internes en FR, code et public en EN | Accepté, révocable |

---

## ADR-001 — Verilog plutôt que Hardcaml

**Statut :** Accepté · 16 sept. 2026

**Contexte.** Jane Street utilise Hardcaml (DSL de génération de RTL en OCaml) pour ses
propres designs et l'annonce dans le post. L'utiliser aurait une valeur de signal auprès
des juges. Le template officiel du concours est en Verilog.

**Décision.** Verilog.

**Pourquoi.** Paul a pratiqué le FPGA et le VHDL mais il y a plusieurs années. Hardcaml
empilerait l'apprentissage d'OCaml *et* d'un DSL de génération de matériel par-dessus une
remise à niveau HDL, sur un projet déjà dense et une deadline de 18 semaines. Le chemin
Verilog est celui du template, de la documentation Tiny Tapeout et de la quasi-totalité
des exemples disponibles — donc moins de friction à chaque blocage.

**Conséquence.** On perd un point de séduction facile. On le compense sur l'axe
vérification (ADR-007), qui pèse plus lourd dans les critères annoncés. À reconsidérer
seulement si le projet prend beaucoup d'avance, ce qui est improbable.

---

## ADR-002 — `tiles: 6x4` malgré le template

**Statut :** Accepté, à valider en CI · 16 sept. 2026

**Contexte.** Le blog impose explicitement `tiles: "6x4"` dans `info.yaml`. Le commentaire
du template en amont ne liste comme valeurs valides que `1x1, 1x2, 2x2, 3x2, 4x2, 6x2,
8x2` — 6x4 n'y figure pas.

**Décision.** Mettre `6x4` comme le blog l'exige, et laisser la CI trancher.

**Pourquoi.** Deux hypothèses : soit les outils du concours ont été mis à jour sans que le
commentaire suive, soit le blog est en avance sur le template. On ne peut pas départager
par la lecture, seulement par l'exécution. Le job `precheck` donne la réponse en une
exécution et pour zéro effort — beaucoup moins cher que de deviner.

**Conséquence.** Si `precheck` refuse 6x4, c'est un mail à `asic-competition@janestreet.com`
et non un problème de design. Le budget d'aire (~24K cellules) ne bouge pas tant que la
question n'est pas tranchée. Ne pas dimensionner l'architecture sur l'hypothèse 8x4.

---

## ADR-003 — Le milestone 1 est jetable par construction

**Statut :** Accepté · 16 sept. 2026

**Contexte.** Le blog conseille : « Start by getting a UART transmitter out of a pin. Then
make it programmable. » Un UART figé est l'inverse exact de ce que le concours demande.

**Décision.** Écrire un UART TX 8N1 en dur (`src/uart_tx.v`), et le documenter comme
destiné à disparaître.

**Pourquoi.** Trois usages, tous transitoires : valider la chaîne RTL → GDS de bout en
bout, obtenir un **premier chiffre d'aire réel** qui calibre tout le reste, et servir de
**modèle de référence** pour tester plus tard le firmware UART tournant sur le core.

**Conséquence.** Le risque est de s'y attacher. Le commentaire en tête de `uart_tx.v` dit
explicitement que le bloc doit disparaître. Si à la semaine 10 un UART figé est encore
dans le design, c'est que le projet a échoué à son objectif principal.

---

## ADR-004 — Les tests décodent la pin, jamais l'état interne

**Statut :** Accepté · 16 sept. 2026

**Contexte.** Un testbench peut soit observer les signaux internes du DUT, soit
n'observer que ses pins.

**Décision.** Les tests cocotb échantillonnent `uo_out` au milieu de chaque temps-bit,
comme le ferait un vrai récepteur. Aucun accès à l'état interne.

**Pourquoi.** Après synthèse, la simulation gate-level ne voit qu'un netlist : les noms
de signaux internes ont disparu. Un test écrit sur l'état interne doit être réécrit à ce
moment-là — exactement quand on a le moins de temps et le plus besoin de confiance. Un
test écrit sur les pins passe tel quel du RTL au netlist.

**Conséquence.** Les tests sont un peu plus longs à écrire. En échange, la suite entière
est réutilisable en gate-level (job `gl_test` de la CI) sans modification. Cette règle
vaut pour tout le projet, pas seulement le milestone 1.

---

## ADR-005 — Le timing est asserté dès le premier jour

**Statut :** Accepté · 16 sept. 2026

**Contexte.** Sur ce projet, la précision temporelle n'est pas une qualité parmi d'autres :
c'est *la* raison d'être de la puce. Un émulateur de protocoles qui dérive d'un cycle ne
parle aucun protocole.

**Décision.** `test_bit_timing` vérifie que chaque slot de bit dure **exactement**
`CLK_DIV` cycles d'horloge, et non « à peu près ».

**Pourquoi.** Une dérive de timing ne se voit pas dans un test fonctionnel — l'octet
arrive quand même. Elle se voit en silicium, face à un vrai périphérique, quand il est
trop tard. Le coût d'écrire l'assertion maintenant est de dix lignes.

**Conséquence.** Toute future instruction de timing du core doit recevoir le même
traitement : une assertion exacte, pas une tolérance. C'est aussi la fondation de
l'argumentaire de vérification (ADR-007).

---

## ADR-006 — Pas de registre shadow sur l'UART TX

**Statut :** Accepté, portée locale · 16 sept. 2026

**Contexte.** L'UART TX ignore `load` tant qu'il est occupé. Un UART de production
double-bufferise pour permettre l'émission dos à dos sans trou.

**Décision.** Pas de double buffer. `load` pendant `busy` est ignoré silencieusement.

**Pourquoi.** Un registre shadow coûte 8 flip-flops et de la logique de contrôle pour un
bloc qui doit disparaître (ADR-003). Sur le chip final, l'enchaînement des trames sera
géré **en firmware** — c'est précisément le genre de politique qu'on veut sortir du
matériel.

**Conséquence.** Les tests doivent attendre `busy == 0` entre deux octets (helper
`wait_idle`). C'est un piège qui a coûté un échec de test lors de la première exécution —
documenté dans `03-workflow.md`.

---

## ADR-007 — La vérification est un livrable, pas une corvée

**Statut :** **Proposé** — à valider avec Paul · 16 sept. 2026

**Contexte.** Les critères de jugement citent nommément « formal methods, random
constrained tests, AI-assisted verification » et affirment que la vérification sera
« extremely important » dans le flow ASIC à venir.

**Décision proposée.** Construire la vérification comme un produit à part entière :

1. Un **simulateur de jeu d'instructions (ISS)** cycle-accurate en Python, écrit *avant*
   le RTL et servant de spécification exécutable.
2. Un **fuzzer différentiel** : génération de programmes aléatoires contraints, exécutés
   en parallèle sur l'ISS et sur le RTL, comparaison cycle par cycle.
3. Des **propriétés formelles** (SymbiYosys) sur les instructions de timing — par exemple
   « `WAIT n` relâche toujours exactement n cycles plus tard, quel que soit l'état ».

**Pourquoi.** C'est là que le rapport valeur/effort est le meilleur pour ce projet précis.
C'est du logiciel, donc le terrain où Paul est fort et où l'assistance IA est la plus
efficace — alors que la fermeture de timing physique est le terrain où les deux sont les
plus faibles. Et c'est explicitement noté par le jury.

**Conséquence.** L'ISS devient un chemin critique : le RTL ne peut pas démarrer avant.
Cela justifie de consacrer les semaines 2–3 à la spec et à l'ISS sans écrire une ligne de
Verilog, ce qui peut sembler lent. Ça ne l'est pas.

---

## ADR-008 — Horloge supposée à 50 MHz

**Statut :** **Provisoire** — à confirmer avant de figer l'ISA · 16 sept. 2026

**Contexte.** `info.yaml` demande une fréquence. La fréquence max réellement tenable sur
CMOS5L via Tiny Tapeout n'est pas connue à ce stade.

**Décision.** 50 MHz, avec `CLK_DIV = 434` pour 115200 bauds.

**Pourquoi.** Ordre de grandeur plausible pour une carte Tiny Tapeout, et il fallait un
chiffre pour avancer. Aucune information ne l'infirme pour l'instant.

**Conséquence — importante.** C'est l'hypothèse la plus lourde du projet. La fréquence
fixe la résolution temporelle, donc le débit max, donc **la faisabilité des stretch goals**
(USB low-speed à 1,5 Mbit/s, Ethernet 10M). Elle conditionne aussi le nombre de cycles
disponibles par bit pour exécuter du firmware — c'est-à-dire la complexité que l'ISA peut
se permettre. **À confirmer avant de figer l'ISA**, pas après.

---

## ADR-009 — Axe de nouveauté : écouter, pas seulement parler

**Statut :** **Proposé** — à valider avec Paul · 16 sept. 2026

**Contexte.** Le critère n°1 est la fonctionnalité originale. Les références explicites
(PIO du RP2040, PRU des Sitara) définissent l'état de l'art : refaire un PIO en plus petit
est le chemin par défaut, et donc le moins remarquable.

**Décision proposée.** Ne pas seulement **émettre** les protocoles, mais savoir les
**sniffer et les auto-identifier** : capture d'edges horodatée, détection automatique de
baud, classification UART/SPI/I2C à la volée.

**Pourquoi.** Jane Street dit que son usage est « hardware debugging and reverse
engineering ». Un chip qui identifie un protocole inconnu sur un bus répond à ce besoin
déclaré, et ni le PIO ni les PRU ne le font. C'est aussi une fonction qui exploite
exactement les primitives déjà nécessaires à l'émulation (lire des pins, compter des
cycles) — donc un coût d'aire marginal, pas un second sous-système.

**Conséquence.** À trancher **pendant** le design de l'ISA, pas après : si le sniffing est
retenu, l'ISA a besoin d'une primitive de capture temporelle (timestamp d'edge) qu'on ne
peut pas greffer ensuite sans tout reprendre.

---

## ADR-010 — Docs internes en français, code et docs publiques en anglais

**Statut :** Accepté, révocable · 16 sept. 2026

**Contexte.** Paul travaille en français. Le dépôt est public et sera lu par des juges
anglophones, et un second contributeur pourrait rejoindre le projet.

**Décision.** `context/` en français. Code, commentaires, messages de commit,
`docs/info.md` (la datasheet publiée) et le write-up final en anglais.

**Pourquoi.** `context/` sert au pilotage du projet et son lecteur principal est Paul.
Tout ce qui est jugé ou lu par des tiers est en anglais.

**Conséquence.** Si un contributeur non francophone rejoint le projet, basculer
`context/` en anglais — c'est une traduction, pas une réécriture. Décision à revoir à ce
moment-là.
