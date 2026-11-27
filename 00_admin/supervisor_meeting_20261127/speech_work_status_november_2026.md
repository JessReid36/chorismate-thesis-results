# Speech: work status, November 2026

To go with the deck chorismate_work_status_november_2026.pptx (the same text is in its speaker notes). About 1400 words: roughly 11 minutes at an easy pace, leaving time for questions. Every number is the document's.
Total at 130 words a minute: about 10 min 49 s.

## Slide 1. Can designed point charges lower the chorismate barrier? (about 36 s)

Good morning. This is where the charge-design work stands at the end of November. The question is simple to state: can a handful of point charges, placed around chorismate with no protein, lower the barrier of its rearrangement to prephenate, and can an optimiser find where to put them? I will go through how the problem is set up, what the search found, how its candidates fared under harder tests, and what we can and cannot claim yet.

## Slide 2. The answer so far (about 49 s)

The short answer first. An exact search placed charges of a quarter of an electron's charge around the frozen substrate. Of 27 designs, 18 pass every reliability test in two basis sets, and they lower the frozen barrier by between 4.30 and 13.02 kilocalories per mole, where the barrier without charges is 26.82. Under a harder test, with basis functions placed at the positive charges, five of the ten largest designs keep their electrons at two functionals; the five with the very largest lowering are not settled. And nothing here is a catalytic result yet: it is one frame, frozen, in vacuum, and nothing has been relaxed.

## Slide 3. The inputs: one enzyme frame, taken out and frozen (about 50 s)

Where the inputs come from. In Phase 1 we simulated the reaction inside the enzyme by QM/MM. From a band of 30 reaction-path frames, one, frame 42436, went through the production protocol: its transition state was optimised and the path followed down to its reactant. Those two substrate geometries, the chorismate dianion, 24 atoms and 118 electrons, are taken out of the enzyme and held frozen. Every calculation reports ddE, the change in barrier; negative means the charges lower it. We use this frame because its two geometries are true stationary points. The frame used earlier was not: re-optimising its reactant lowered its energy by 4.58 kilocalories per mole.

## Slide 4. CAM-B3LYP is the working level; B3LYP is retired (about 58 s)

Before designing anything we needed a level of theory we could trust for this anion. We followed the route the literature recommends: a coupled-cluster reference on our own geometries, then nine functionals in two basis sets with diffuse functions. The reference barrier is 23.86 kilocalories per mole in the larger basis. CAM-B3LYP sits 1.84 above it, and two double hybrids sit 2.36 and 2.52 below. B3LYP, the level of the earlier work, is 6.56 too low, and its highest occupied orbital lies above the vacuum level. So CAM-B3LYP is the working level, with the larger basis set as part of every design's test. It is a working choice: the benchmark cannot pick among the three nearest levels, and it does not test the barrier change itself.

## Slide 5. A bare positive charge can take an electron (about 64 s)

The main risk with point charges is that a positive charge next to an anion can pull one of its electrons away, and a standard calculation can hide this because a point charge carries no basis functions. So we tested it properly, with functions placed at the charge. A single charge takes electrons from 0.50 to 0.65 of an electron's charge, and a full charge does so even 9 ångström away, so distance alone does not make a charge safe. One to six charges of 0.25 together did not. That is why every charge in the search is capped at 0.25, and why every design must pass five tests, in both basis sets: relocation, dipole, orbital gap, stability, and whether the dianion still holds its second electron. A design that passes is a survivor: a candidate, not a result.

## Slide 6. The optimiser: a first-order map and an exact search (about 61 s)

The optimiser in plain terms. To first order, a small charge changes the barrier by the charge times the difference between the electrostatic potential of the transition state and that of the reactant at its position. We compute that difference at 2626 grid sites. It is the idea of the catalytic field that Szefczyk and co-workers applied to this enzyme. For each number of charges, the search then finds the arrangement with the best score under fixed rules, no two charges closer than 3.25 ångström and the charges summing to zero or more, and proves that no better arrangement exists. The score is a proxy: for the survivors the measured lowering is 1.03 to 1.17 times what it predicted. It knows nothing about reliability or electron loss; those are measured for every design.

## Slide 7. Where the charges sit, to scale (about 25 s)

This is what two designs look like, to scale. On the left, a six-charge survivor that holds under every test so far; on the right, the ten-charge design with the largest lowering. Positive charges, in blue, sit by the ether oxygen whose carbon-oxygen bond breaks; negative charges, in orange, sit by the ring carboxylate.

## Slide 8. 18 of 27 survive; the electron hold gives way first (about 56 s)

What the search found: three designs at each of nine numbers of charges, from 3 to 20. Up to ten charges all eighteen survive, and the two basis sets agree within 0.04 to 0.14 kilocalories per mole. The lowering grows with the number of charges, to 13.02 with ten. What gives way first is the hold on the last electron: it falls from 1.25 electron volts without charges to about zero with twelve, and all three twelve-charge designs fail there. With fifteen, the larger basis set shows a failure the smaller one does not. One omission, in the direction of a lower barrier: the search left out a small classical shell term worth 0.17 to 0.33 per design. It changes no outcome.

## Slide 9. Harder tests: five hold, the five largest are not settled (about 69 s)

Then the survivors went through harder tests. First, the force: each adds 2.4 to 8.8 kilocalories per mole per ångström to the gradient on the frozen substrate, and a first-order map of that force agrees with direct calculation, so the next search can limit it. Second, functions at the positive charges of the ten survivors with the largest lowering, at two functionals. Five hold. The five with the largest lowering are not settled: at CAM-B3LYP their atoms give up 0.35 to 0.88 of an electron at the reactant, at omega-B97X-V only 0.03 to 0.05. Two of them gain more than our threshold of 0.3127 electron volts, one by only 0.0031. CAM-B3LYP is known to over-bind shared electrons, which may explain the disagreement, but that is not tested. Third, behind a helium wall all ten remain survivors, each lowering 0.15 to 0.26 smaller. The harder tests tell against the largest lowerings.

## Slide 10. Designs beat chance; ωB97X-V mostly agrees (about 70 s)

The last calculation is now in. It repeats the search with a map built at a second functional, omega-B97X-V, and with the older B3LYP map, and it ranks the search's designs against random ones. At omega-B97X-V the map agrees very closely with ours, a correlation of 0.9977, and the search places 17 of its 27 designs again; at seven of the nine numbers of charges its best design is ours. The B3LYP map, which also uses a smaller basis set, gives different designs at seven of nine numbers, but they score within 0.29 kilocalories per mole of our best on our own map. And every one of the 27 designs beats all ten thousand random designs of both kinds at its number of charges, the weakest by 0.57 to 4.71. All of this is first order: the designs are placed and scored, not measured, and nothing is kept or dropped on it.

## Slide 11. Limitations, and which way they push (about 38 s)

The limitations, each with its direction. The geometries are frozen, so the substrate cannot respond to the charges; how much of the lowering survives is the pilot's question. It is one frame of thirty. It is the gas phase: a medium would screen the charges, so we expect the real lowering to be smaller. The point charges stand for no atom, and the wall's test against real ions could not be formed. And no production level of theory has been chosen yet.

## Slide 12. Conclusions and next steps (about 72 s)

To conclude. Established: B3LYP is unsuitable for this dianion, the dianion holds its second electron, and an exact search finds designs with three to ten charges that pass every reliability test. Provisional: five designs of five to eight charges hold under the harder test, lowering the frozen barrier by 6.96 to 10.76; they are the best candidates to relax. At first order, the search's designs beat random placement, and a second functional places mostly the same ones. Not known: whether any lowering survives relaxation, a medium or other frames. Next comes a pilot relaxation of three survivors, then a second search with a force limit, and only then the cross-check and the coupled-cluster reference on what remains. Three decisions are open for discussion: whether a design that is not settled may still be quoted, whether the pilot keeps the ten-charge design, and whether to repeat the wall test with a longer time limit. Thank you.
