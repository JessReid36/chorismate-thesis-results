"""v10.1 -> v11 of the short document: D60's result entered (Claude, 26 Nov 2026). Every replacement must match once."""
import sys
src, dst = sys.argv[1], sys.argv[2]
t = open(src).read()
def R(a, b, n=1):
    global t
    c = t.count(a)
    assert c == n, (c, a[:90])
    t = t.replace(a, b)

# header and status
R("**Reading copy of 26 November 2026, version 10.1, prepared for Jessica’s discussion with her supervisor on 27 November.** It replaces versions 9 and 10 of the same day. It says what is running, what comes next,",
  "**Reading copy of 26 November 2026, version 11, prepared for Jessica’s discussion with her supervisor on 27 November.** It replaces version 10.1 of the same day. It says what has just come in, what comes next,")
R("at commit `268a91de` (listed at the end) and is labelled measured, derived, computed or estimate; the state of D60, which is still running, comes from Jessica’s printouts of 26 November and is said to. The seven figures are drawn",
  "at commit `173668c6` (listed at the end) and is labelled measured, derived, computed or estimate. The eight figures are drawn")
R("is now in the library and has been read.",
  "is now in the library and has been read. Version 11 enters D60’s result, committed on 26 November (results `173668c6`): D56’s search with the map at ωB97X-V and with the older B3LYP map, and D56’s designs against random designs (a new point 9 at the front, a new section 6.6 with Figure 8, and section 9). What is not known yet is now section 6.7, and one cross-reference to it is corrected. No other number changes.")

# the position
R("### The position, in nine points", "### The position, in ten points")
R("9. **No barrier here is quoted as catalytic.** The catalytic verdict is the relaxed chain of the criteria, not a frozen number. A pilot relaxation of three survivors is next (section 6.6).",
  "9. **At first order, a second functional places mostly the same designs, and every design beats chance** (D60). With the map at ωB97X-V/def2-SVPD, which agrees closely with the working map (Pearson 0.9977), D56’s search places 17 of its 27 designs again, and at seven of the nine numbers of charges its best design is D56’s first-ranked. With the older B3LYP map, at def2-SVP, it places different designs at seven of the nine numbers, which give up 0.06 to 0.29 kcal/mol against D56’s best when scored on the working map (derived). Each of D56’s 27 designs scores lower than all 10 000 random designs of each of two kinds. D60’s pre-registration: \"Nothing here names, keeps or drops a design\" (section 6.6).\n"
  "10. **No barrier here is quoted as catalytic.** The catalytic verdict is the relaxed chain of the criteria, not a frozen number. A pilot relaxation of three survivors is next (section 6.7).")

# what came in
R("### What is running (Jessica’s printouts of 26 November)", "### What came in on 26 November")
i = t.index("- **D60, the search across functionals and against random designs, is running.**")
j = t.index("### What is next, in order")
t = t[:i] + ("- **Collected and committed on 26 November: D60** (section 6.6), at results `173668c6`. Its first step on the PC took 3 h 38 min as a whole (Jessica’s printout of 26 November), where its pre-registration estimated \"about one to one and a half hours\". "
             "The estimate repeated Claude’s estimate for D56’s search rather than the 1 h 36 min that search took on the PC (her printout of 24 November); the error is Claude’s, no reading depends on it, and D60 NOTE 1, sent for commit on 26 November, records it.\n\n") + t[j:]

# next, in order
R("1. **Collect D60** by its committed reader (running).\n2. **The pilot relaxation", "1. **The pilot relaxation")
R("\n3. **The second search** (Amendment 13, item 6)", "\n2. **The second search** (Amendment 13, item 6)")
R("\n4. **A dated amendment on which designs get the cross-check", "\n3. **A dated amendment on which designs get the cross-check")
R("\n5. **Bring the consolidated write-up up to date**", "\n4. **Bring the consolidated write-up up to date**")

# points to discuss
R("D60 now asks whether a search at ωB97X-V places the same designs.",
  "At first order a search at ωB97X-V places mostly the same designs as at the working functional (D60, section 6.6).")

# 5.3 table
R("| the same search at another functional | **being measured** | D60 repeats D56's search with the map at ωB97X-V/def2-SVPD and with the committed map at B3LYP-D3BJ/def2-SVP (Amendment 14) |",
  "| the same search at another functional | **supported, at first order** | with the map at ωB97X-V/def2-SVPD D56's search places 17 of its 27 designs again; with the committed map at B3LYP-D3BJ/def2-SVP it places 3 of 27, and its best designs give up 0.06 to 0.29 kcal/mol on the working map (derived; D60, Amendment 14) |\n"
  "| the search against random designs | **supported, at first order** | each of D56's 27 designs scores lower than all 10 000 random designs of each of two kinds at its number of charges (D60) |")

# 5.5
R("and compare the arrangements (Amendment 9). Under way: D60.", "and compare the arrangements (Amendment 9). Done at first order: D60 (section 6.6).")
R("- **Relax.** The pilot of three survivors is next (section 6.5).", "- **Relax.** The pilot of three survivors is next (section 6.7).")

# new 6.6, old 6.6 -> 6.7
new66 = """### 6.6 The search at a second functional, and against random designs (D60)

D60 (Amendment 14) asked two things of the map D56's search ranks by, at first order, on the same frame and grid and under D56's rules: does the search place the same designs when the map is computed at another functional, and do D56's designs beat random placement? Its control measured the two runs of the working map again, with energies within 1e-11 Eh of D33's, and its runs at ωB97X-V reproduced D37's, so "THE MAP AT wB97X-V IS USED." Its first search, with the working map, gave D56's 27 designs again (gate GV.6).

- **The maps** (measured, over the 1488 sites that admit a charge, kcal/mol per e). Against the working map, the map at ωB97X-V/def2-SVPD has Pearson 0.9977, Spearman 0.9920, mean difference 0.1488 and largest 0.3262; the committed B3LYP-D3BJ/def2-SVP map has Pearson 0.9763, Spearman 0.9358, mean difference 0.4588 and largest 1.1773.
- **At ωB97X-V the designs are PARTLY THE SAME at all nine numbers of charges, and 17 of D56's 27 are found again** (two of three at each number, one of three at 20). At seven numbers the search's best design is D56's first-ranked; at 12 it is S_n12_k2, and at 20 it is a new design, which scores 0.0661 kcal/mol less than S_n20_k1 on the working map (derived).
- **At B3LYP they are DIFFERENT DESIGNS at seven numbers and PARTLY THE SAME at 5 and 6; 3 of 27 are found again.** Scored on the working map, its best design at each of the seven gives up 0.0617 to 0.2851 kcal/mol against D56's best (derived). The two maps differ in the basis set as well as the functional, so this comparison mixes the two; the one at ωB97X-V changes the functional alone.
- **Every one of D56's 27 designs beats 100.00 % of the random designs of both kinds** (10 000 of each at each number of charges, seed 20261125). Kind (i) puts charges of 0.25 e, each with a random sign its site admits, on random sites with the spacing; kind (ii) puts the best charges D56's rules allow on random sites. D56's weakest design at each number lies 0.5733 to 4.7051 kcal/mol below the best random design of kind (ii) (derived), and 4716 to 9979 of the 10 000 of kind (ii) at each number carry a charge smaller than 0.25 e, which none of D56's designs does.
- **What it cannot say.** D60's pre-registration: "A design that a map places is placed by that map, not measured at that functional; a design found again at another map is not confirmed by that, and one not found again is not refuted by that." Its direction: "no reading here moves a reported barrier."

![Figure 8](figs/S10_second_functional.png)

**Figure 8.** D60 at first order (derived from `d60_designs.tsv` and `d60_null.tsv`). A: of D56's three designs at each number of charges, how many the search with each other map places again, with the same sites and the same charges. B: each other map's best design, scored on the working map, minus D56's best there (kcal/mol); zero means the same design or an equal score. C: D56's three designs at each number of charges against 10 000 random designs of each kind; each bar runs from the median random design to the best one.

### 6.7 What is not known yet"""
R("### 6.6 What is not known yet", new66)
R("- **Whether another functional would place the same designs, and how D56’s designs compare with random ones** at first order. D60 measures both; it is running.\n", "")
R("- **Whether the five survivors that are not settled with functions keep their electrons** (section 6.5), and whether the working functional or ωB97X-V is right where they disagree.\n",
  "- **Whether the five survivors that are not settled with functions keep their electrons** (section 6.5), and whether the working functional or ωB97X-V is right where they disagree.\n- **Whether the designs that the other maps place measure as they score.** D60 placed and scored them at first order; none was run.\n")

# section 9
R("- Behind a helium wall on their positive charges all ten keep the word SURVIVOR, each lowering smaller by 0.15 to 0.26 kcal/mol (D59).\n",
  "- Behind a helium wall on their positive charges all ten keep the word SURVIVOR, each lowering smaller by 0.15 to 0.26 kcal/mol (D59).\n"
  "- At first order, with the map at ωB97X-V D56's search places 17 of its 27 designs again; with the older B3LYP map at def2-SVP it places different designs at seven of nine numbers of charges, which give up 0.06 to 0.29 kcal/mol on the working map; and each of D56's designs scores lower than all 10 000 random designs of two kinds (D60).\n")
R("- Whether another functional would place the same designs, and whether D56’s designs beat random ones by more than chance (D60, running).\n",
  "- Whether the designs the other maps place would measure as they score: D60 scored them at first order and ran none.\n")

# sources
R("All under `phase2.2/` of the results repository at commit `268a91de`.", "All under `phase2.2/` of the results repository at commit `173668c6`, except D60 NOTE 1.")
R("| the second functional and the random designs (D60) | `cs_stage6/STAGE6_AMENDMENT14_20261125.txt`, `STAGE6_DIAGNOSTIC60_20261125.txt` |",
  "| the second functional and the random designs (D60; front, section 6.6, Figure 8) | `cs_stage6/STAGE6_AMENDMENT14_20261125.txt`, `STAGE6_DIAGNOSTIC60_20261125.txt`, `STAGE6_DIAGNOSTIC60_RESULT_20261126.txt`; `d60_designs.tsv`, `d60_null.tsv`; the time estimate: `STAGE6_DIAGNOSTIC60_NOTE1_20261126.txt`, sent for commit on 26 November |")
R("The state of D60 is from Jessica’s printouts of 26 November and is in no committed file yet, as is the time D56’s search took on the PC (her printout of 24 November).",
  "The time D56’s search took on the PC (Jessica’s printout of 24 November) and the time D60’s first step took (her printout of 26 November) are in no committed file of `173668c6`.")

# the check
R("On 26 November four scripts, kept with this document’s source, compared the text with the results repository at commit `268a91de`, the commit of D61’s result.",
  "On 26 November five scripts, kept with this document’s source, compared the text with the results repository at commit `173668c6`, the commit of D60’s result.")
R("- **Figures.** Figures 1 to 7, redrawn from this commit, are byte for byte those of version 8.1. Version 10 uses the same files and changes only the wording of Figure 1’s caption.",
  "- **D60, independently.** A fifth script (`indep_check_d60.py`) reads D60's committed ORCA outputs and tables with its own parsing and none of the committed reader's functions. It recomputes the four energies against D33's and D37's, the potentials against D33's, the map at ωB97X-V from the raw potentials, the 1488 sites, the four comparisons of the maps, the scores of all 81 designs on the three maps and their keeping of D56's rules, the counts of designs found again, and the agreement of the random-design summary: 46 checks, 0 differences. It first differed in four entries of one column, because it took the column as the lowest of D56's three designs where the result gives D56's first-ranked; the script was corrected, not the result.\n"
  "- **Figures.** Figures 1 to 7, redrawn from this commit, are byte for byte those of version 8.1. Version 10 uses the same files and changes only the wording of Figure 1’s caption. Figure 8 is new in version 11 and drawn from `d60_designs.tsv` and `d60_null.tsv` by `make_fig7.py`, whose printed output holds the derived numbers of section 6.6.")
R("a fifth script (`verify_lit_v10.py`)", "a sixth script (`verify_lit_v10.py`)")
R("Whole numbers, counts and times were not traced by a script, and the state of D60 is not in any committed file. All four scripts are Claude’s;",
  "Whole numbers, counts and times were not traced by a script. All six scripts are Claude’s;")
open(dst, "w").write(t)
print("v11 written", len(t))
