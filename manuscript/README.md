# Hanna's OEIS A389474 FORMULA (3) and companion congruences

The note proves the six conjectures in OEIS A389474 FORMULA (3), (4),
A389475 FORMULA (4.a), (4.b), and A389472 COMMENTS (odd-index parity and
the residue class `3n-1` modulo three). The defining equations and initial
values are part of each statement. The normalized rational solutions of the
first two equations exist uniquely and have integer coefficients.
If `D` is the normalized A350432 series, every rational-seed solution of
the A389472 equation is `C_s=x+sD^2`. The product for `D` proves that
its convergence radius, and that of `C_s` for nonzero `s`, is
`(sqrt(5)-1)/2`. Every integer seed retains both coefficient congruences.
The note also proves the companion reversion and iteration formulas of
A273095 and the product and reversion formulas of A350432.

## Files

- `note.tex`, `note.pdf`: complete proofs and an explicit source-coverage table.
- `metadata.json`: creators, license and original problem IDs.
- `scientific-coverage.json`: exact posing locators and declaration-by-declaration scope.
- `verify.py`, `source_terms.json`: dependency-free exact coefficient checks.
- `checks.json`: the checker's deterministic output at degree 96.

## Rebuild

Use Tectonic **0.17.0**:

```
tectonic note.tex
```

Alternatively, run `pdflatex note.tex` twice. The bibliography is included in
`note.tex`; BibTeX and external bibliography files are unnecessary.

Python **3.10 or later**, with no third-party packages, reproduces the finite
checks:

```
python3 verify.py --degree 96 > checks.json
```

The expected result is `"status": "PASS"`. Checks cover the three nonlinear equations
through degree 97 and the linear equations through degree 96; they match the
24, 23 and 41 displayed coefficients of A389474, A389475 and A389472.
They also match 34 coefficients of A273095 and 43 of A350432. Through
degree 96 they check the companion product (seven factors), all-seed
factorization for seeds `-2,0,1,3`, five two-sided series inverses, the
reversion formulas, A273095 iterations `r=0,...,7`, the twice-iterated
A389472 identity and the Catalan comparison.
The powers for the characteristic-three congruence range from 0 through 33.
For powers at least 33 both sides vanish through degree 96 by their order.
The powers of the square congruence modulo nine range from 0 through 49;
for powers at least 49 both sides vanish through degree 96.
All-index assertions follow from the proofs, not from the finite cutoff.

## Mathematical sources

The primary posing sources are `https://oeis.org/A389474` (FORMULA (3), (4)),
`https://oeis.org/A389475` (FORMULA (4.a), (4.b)), and
`https://oeis.org/A389472` (COMMENTS). The corresponding entry versions are
11, 8 and 7. `source_terms.json` records the official OEIS source mirror and
the exact source-file hashes for the displayed coefficients.

The note links four pinned Lean files and maps their declarations to the six
conjectures. The coefficient construction, unit-factor identity, Frobenius
congruences, binomial descent and reversion identities have complete written
proofs. The higher even-power congruence, product, all-seed factorization,
analytic radii, additional reversion consequences and A273095 identities
have written proofs; the finite checker covers the ranges stated in
`checks.json`. The four linked Lean files cover the six congruence
conjectures, rather than these additional statements. The radii follow
from the convergence and divergence proof, not from a finite cutoff.

## Creators and license

Haobo Ma — ChronoAI Pte Ltd, Singapore.

Wenlin Zhang — National University of Singapore; ChronoAI Pte Ltd, Singapore.

CC BY 4.0 (`cc-by-4.0`).
